# Elephas Projector for Home Assistant

A local-network Home Assistant integration for Elephas projectors that use the
XGIMI-compatible remote protocol. No cloud account or projector modification is
required.

## Features

- DHCP discovery for known Elephas hardware, plus UDP discovery during setup
- A `media_player` entity with power, volume, and mute controls
- Sleep, Home, Menu, and Source button entities
- A UI config flow and reconfiguration support
- Fully local communication

## Installation with HACS

1. In HACS, open **Integrations**, choose **Custom repositories**, and add
   `https://github.com/nworb-cire/elephas-ha` as an Integration.
2. Install **Elephas Projector** and restart Home Assistant.
3. Open **Settings → Devices & services**. Accept a discovered projector or
   choose **Add integration → Elephas Projector**.

The projector must be powered on for its initial connection test. If automatic
discovery does not find it, enter its IP address manually.

## Power behavior

Power-off has been verified on the target projector. Network power-on works only
while the projector keeps its network interface awake, normally in sleep mode.
A fully shut-down Wi-Fi projector requires its physical/Bluetooth remote. An
Ethernet connection may permit wake if the firmware offers a network-standby or
Wake-on-LAN setting.

## Protocol

- UDP discovery: port `8100`, payload `control` followed by byte `0x14`
- UDP session handshake: port `16750`, compact JSON action `20000`
- UDP remote keys: port `16735`, `KEYSSTATUS:<code>+1` then `+0`
- TCP status/control socket: port `30913`
- TCP `8080`: separate projector-hosted HTTP assets, not remote control

## Development

```sh
python -m unittest discover -s tests
```

This is an independent community integration and is not affiliated with
Elephas, XGIMI, or Home Assistant.
