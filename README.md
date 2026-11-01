# Seitron Smart for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-blue.svg)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/simonegrazioso/ha-seitron-smart?include_prereleases&color=blue)](https://github.com/simonegrazioso/ha-seitron-smart/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Validate](https://github.com/simonegrazioso/ha-seitron-smart/actions/workflows/validate.yaml/badge.svg)](https://github.com/simonegrazioso/ha-seitron-smart/actions/workflows/validate.yaml)

Custom component for [Home Assistant](https://www.home-assistant.io/) providing cloud integration for **Seitron Smart** connected thermostats.

Tested and validated on **Seitron Wi-Time Wall**; architecturally compatible with devices supported by the Seitron Smart IoT platform (such as Wi-Time and Hygge).

---

## Supported Features

- **HVAC Modes & Thermostat Operation**:
  - `auto` (**Crono / Programma**): Runs the weekly scheduled temperature program configured on the thermostat.
  - `heat` (**Manuale Riscaldamento**): Sets manual heating mode at the desired target temperature.
  - `cool` (**Manuale Raffrescamento**): Sets manual cooling/air conditioning mode.
  - `off` (**Spento / Antigelo**): Turns off active heating/cooling, switching the thermostat to frost-protection mode (antifreeze at 5.0 °C).
- **Turn On / Turn Off**:
  - `turn_on`: Turns on the thermostat, defaulting to `auto` (Crono scheduled program).
  - `turn_off`: Turns off the thermostat into `off` (frost protection mode).
- **Target Temperature**: Adjustable setpoint from 5.0 °C to 35.0 °C with 0.1 °C precision.
- **Current Temperature**: Real-time ambient room temperature reporting with 0.1 °C resolution.
- **HVAC Action Telemetry**: Real-time operating status (`heating`, `cooling`, `idle`, `off`).
- **Optimistic UI Updates & Cloud Sync**: Local state updates immediately upon interaction, with a 1-second cloud synchronization delay before polling to eliminate UI toggle bounce.
- **Device Registry Integration**: Automatically populates manufacturer (*Seitron s.p.a.*), model (*Wi-Time Wall*, etc.), unique MAC address (`gmac`), and firmware version.

---

## Requirements

- Home Assistant **2024.1.0** or newer.
- An active account in the **Seitron Smart** mobile app with paired thermostats.

---

## Installation

### Option 1: Via HACS (Recommended)

1. Open **HACS** in your Home Assistant dashboard.
2. Click the three dots icon in the top right corner and choose **Custom repositories**.
3. Enter:
   - **Repository**: `https://github.com/simonegrazioso/ha-seitron-smart`
   - **Type**: `Integration`
4. Click **Add**.
5. Locate **Seitron Smart** in the integration list and click **Download**.
6. Restart Home Assistant.

### Option 2: Manual Installation

1. Download the repository source or latest release archive.
2. Copy the `custom_components/seitron` directory into your Home Assistant `<config_dir>/custom_components/` directory:
   ```text
   config/
   └── custom_components/
       └── seitron/
           ├── __init__.py
           ├── api.py
           ├── application_credentials.py
           ├── climate.py
           ├── config_flow.py
           ├── const.py
           ├── manifest.json
           ├── strings.json
           └── translations/
               ├── en.json
               └── it.json
   ```
3. Restart Home Assistant.

---

## Configuration

1. In Home Assistant, navigate to **Settings** → **Devices & Services** → **Integrations**.
2. Click **Add Integration** and search for **Seitron Smart**.
3. Follow the on-screen OAuth2 authorization flow to link your Seitron account.
4. Once completed, your thermostat will appear under your device list with its corresponding `climate` entity.

---

## Architecture & How It Works

The integration interacts with the Seitron Smart cloud services:

1. **Authentication (`oauth2.seitron.xyz`)**: Uses Home Assistant's native OAuth2 implementation (`application_credentials` / `config_entry_oauth2_flow`).
2. **Device State & Commands (`hassio.seitron.xyz`)**: An internal `DataUpdateCoordinator` queries the Seitron API every 60 seconds to refresh device status, target setpoints, and heating/cooling state.
3. **Entities**: Automatically registers each discovered thermostat as a standard `climate` entity (`climate.<thermostat_name>`).

---

## Debugging

To enable detailed logging for troubleshooting API or communication issues, add the following to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.seitron: debug
    pyseitron: debug
```

---

## Author & Attribution

- **Integration Author & Maintainer**: Simone Grazioso ([@simonegrazioso](https://github.com/simonegrazioso))
- **Underlying Library**: [`pyseitron`](https://github.com/seitronspa/pyseitron) (v0.0.1), originally authored by Stefano Vardanega (Seitron S.p.A.).

> **Disclaimer**: This is an independent, non-official community project and is not maintained, endorsed, or supported by Seitron S.p.A. All product and company names are trademarks™ or registered® trademarks of their respective holders.

---

## License

This project is licensed under the [MIT License](LICENSE).
