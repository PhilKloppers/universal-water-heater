# Getting Started with Universal Water Heater

This guide will help you install and set up the Universal Water Heater custom integration for Home Assistant.

## Prerequisites

- Home Assistant 2026.7.0 or newer
- HACS (Home Assistant Community Store) installed
- Network connectivity to [external service/device]

## Installation

### Via HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/PhilKloppers/universal-water-heater`
6. Set category to "Integration"
7. Click "Add"
8. Find "Universal Water Heater" in the integration list
9. Click "Download"
10. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/PhilKloppers/universal-water-heater/releases)
2. Extract the `universal_water_heater` folder from the archive
3. Copy it to `custom_components/universal_water_heater/` in your Home Assistant configuration directory
4. Restart Home Assistant

## Initial Setup

After installation, add the integration:

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Universal Water Heater"
4. Follow the configuration steps:

### Step 1: Enter Device Name

Enter a friendly name for your device:

- **Device Name:** A descriptive name for this integration instance

Click **Submit** to proceed.

### Step 2: Configure Entity Sources

Configure which entities provide data for your device (optional):

- **Water Temperature Source:** Select a temperature entity to track water temperature
- **Power Source:** Select a power consumption entity
- **Voltage Source:** Select a voltage entity
- **Current Source:** Select a current entity
- **Heater Switch Source:** Select a switch to mirror and control

All fields are optional and can be configured later. Click **Submit** to complete setup.

## What Gets Created

After successful setup, the integration creates:

### Devices

- **Device Name:** Main device representing your connected service/hardware
  - Model information
  - Software version
  - Configuration URL (link to device web interface)

### Entities

The integration creates the following entity types:

#### Sensors
- Water Temperature (linked to source entity)
- Power Consumption (linked to source entity)
- Voltage (linked to source entity)
- Current (linked to source entity)

#### Binary Sensors
- API Connectivity status

#### Switches
- Heater Switch (linked to source entity, bidirectional)

#### Select
- Mode (Normal, Optimised, Eco, Off)

#### Numbers
- Temperature (Normal) - 40-80°C, default 65°C
- Temperature (Eco) - 40-80°C, default 55°C
- Temperature (Max) - 50-85°C, default 75°C
- Hysteresis - 0.1-5°C, default 4°C

## First Steps

### Dashboard Cards

Add entities to your dashboard:

1. Go to your dashboard
2. Click **Edit Dashboard** → **Add Card**
3. Choose card type (e.g., "Entities", "Glance")
4. Select entities from "Universal Water Heater"

Example entities card:

```yaml
type: entities
title: Universal Water Heater
entities:
  - sensor.device_name_water_temperature
  - sensor.device_name_power
  - sensor.device_name_voltage
  - sensor.device_name_current
  - select.device_name_mode
  - number.device_name_normal_temperature
  - number.device_name_eco_temperature
  - switch.device_name_heater_switch
```

### Automations

Use the integration in automations:

**Example - Trigger on sensor change:**

```yaml
automation:
  - alias: "React to sensor value"
    trigger:
      - trigger: state
        entity_id: sensor.device_name_sensor
    action:
      - action: notify.notify
        data:
          message: "Sensor changed to {{ trigger.to_state.state }}"
```

**Example - Control switch based on time:**

```yaml
automation:
  - alias: "Turn on in morning"
    trigger:
      - trigger: time
        at: "07:00:00"
    action:
      - action: switch.turn_on
        target:
          entity_id: switch.device_name_switch
```

## Troubleshooting

### Setup Failed

If setup fails:

1. Verify the device name is entered correctly
2. Ensure Home Assistant can reach your entities
3. Check Home Assistant logs for detailed error messages

### Entities Not Updating

If entities show "Unavailable" or don't update:

1. Verify the source entities you configured still exist
2. Check that source entities are available (not unavailable)
3. Review logs: **Settings** → **System** → **Logs**
4. Try reloading the integration

### Debug Logging

Enable debug logging to troubleshoot issues:

```yaml
logger:
  default: warning
  logs:
    custom_components.universal_water_heater: debug
```

Add this to `configuration.yaml`, restart, and reproduce the issue. Check logs for detailed information.

## Next Steps

- See [CONFIGURATION.md](./CONFIGURATION.md) for detailed configuration options
- See [EXAMPLES.md](./EXAMPLES.md) for more automation examples
- Report issues at [GitHub Issues](https://github.com/PhilKloppers/universal-water-heater/issues)

## Support

For help and discussion:

- [GitHub Discussions](https://github.com/PhilKloppers/universal-water-heater/discussions)
- [Home Assistant Community Forum](https://community.home-assistant.io/)
