"""Config flow for Elephas Projector."""

from __future__ import annotations

import ipaddress
from typing import Any

import voluptuous as vol
from homeassistant.components import network
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers.service_info.dhcp import DhcpServiceInfo

from .const import CONF_MAC, DEFAULT_NAME, DOMAIN
from .protocol import (
    ElephasProjector,
    async_discover_projectors,
    async_scan_projectors,
)


class ElephasConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle an Elephas Projector config flow."""

    VERSION = 1

    def __init__(self) -> None:
        self._discovered_host: str | None = None
        self._discovered_mac: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            if not await ElephasProjector(host).async_is_online():
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=DEFAULT_NAME, data={CONF_HOST: host}
                )
        else:
            discovered = await async_discover_projectors()
            if not discovered:
                discovered = await self._async_scan_local_networks()
            self._discovered_host = next(iter(sorted(discovered)), None)

        schema = vol.Schema(
            {vol.Required(CONF_HOST, default=self._discovered_host or ""): str}
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_dhcp(
        self, discovery_info: DhcpServiceInfo
    ) -> ConfigFlowResult:
        host = discovery_info.ip
        mac = discovery_info.macaddress.lower()
        self._discovered_host = host
        self._discovered_mac = mac
        await self.async_set_unique_id(mac)
        self._abort_if_unique_id_configured(updates={CONF_HOST: host, CONF_MAC: mac})

        for entry in self._async_current_entries():
            if entry.data.get(CONF_HOST) == host:
                return self.async_abort(reason="already_configured")
        if not await ElephasProjector(host).async_is_online():
            return self.async_abort(reason="cannot_connect")
        self.context["title_placeholders"] = {"name": discovery_info.hostname or host}
        return await self.async_step_dhcp_confirm()

    async def async_step_dhcp_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title=DEFAULT_NAME,
                data={CONF_HOST: self._discovered_host, CONF_MAC: self._discovered_mac},
            )
        self._set_confirm_only()
        return self.async_show_form(
            step_id="dhcp_confirm",
            description_placeholders={"host": self._discovered_host or ""},
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            if not await ElephasProjector(host).async_is_online():
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_HOST: host}
                )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {vol.Required(CONF_HOST, default=entry.data[CONF_HOST]): str}
            ),
            errors=errors,
        )

    async def _async_scan_local_networks(self) -> set[str]:
        """Scan at most one /24 per active Home Assistant adapter."""
        candidates: set[str] = set()
        for adapter in await network.async_get_adapters(self.hass):
            if not adapter["enabled"]:
                continue
            for configured in adapter["ipv4"]:
                address = ipaddress.ip_address(configured["address"])
                if address.is_loopback or address.is_link_local:
                    continue
                prefix = max(configured["network_prefix"], 24)
                subnet = ipaddress.ip_network(f"{address}/{prefix}", strict=False)
                candidates.update(str(host) for host in subnet.hosts())
        return await async_scan_projectors(candidates)
