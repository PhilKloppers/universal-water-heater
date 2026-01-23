# Configuration Reference

This document describes all configuration options and settings available in the Universal Water Heater custom integration.

## Integration Configuration

### Initial Setup Options

These options are configured during initial setup via the Home Assistant UI.

#### Device Settings

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| **Device Name** | string | Yes | - | Friendly name for the integration instance |

#### Entity Source Configuration

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| **Water Temperature Source** | entity_id | No | Sensor entity providing temperature reading |
| **Power Source** | entity_id | No | Sensor entity providing power consumption |
| **Voltage Source** | entity_id | No | Sensor entity providing voltage |
| **Current Source** | entity_id | No | Sensor entity providing current (amperage) |
| **Heater Switch Source** | entity_id | No | Switch entity for the heater switch to mirror |

### Options Flow (Reconfiguration)

After initial setup, you can modify settings:

1. Go to **Settings** → **Devices & Services**
2. Find "Universal Water Heater"
3. Click **Configure**
4. Modify settings
5. Click **Submit**

**Available options:**

- Enable debugging
- Custom icon
- Temperature entity source
- Power entity source
- Voltage entity source
- Current entity source
- Switch entity source

## Entity Configuration

### Entity Customization

Customize entities via the UI or `configuration.yaml`:

#### Via Home Assistant UI

1. Go to **Settings** → **Devices & Services** → **Entities**
2. Find and click the entity
3. Click the settings icon
4. Modify:
   - Entity ID
   - Name
   - Icon
   - Device class (for applicable entities)
   - Area assignment

#### Via configuration.yaml

```yaml
homeassistant:
  customize:
    sensor.device_name_sensor:
      friendly_name: "Custom Sensor Name"
      icon: mdi:custom-icon
      unit_of_measurement: "units"
```

### Disabling Entities

If you don't need certain entities:

1. Go to **Settings** → **Devices & Services** → **Entities**
2. Find the entity
3. Click it, then click **Settings** icon
4. Toggle **Enable entity** off

Disabled entities won't update or consume resources.

## Services

The integration provides the following services:

### `universal_water_heater.set_target_temperature`

Set the target temperature for Normal mode.

**Parameters:**
- `temperature` (required): Temperature in °C (40-80, validated against maximum temperature)

**Example:**

```yaml
service: universal_water_heater.set_target_temperature
data:
  temperature: 65
```

### `universal_water_heater.set_eco_temperature`

Set the target temperature for Eco mode.

**Parameters:**
- `temperature` (required): Temperature in °C (40-80, validated against maximum temperature and cannot exceed normal temperature)

**Example:**

```yaml
service: universal_water_heater.set_eco_temperature
data:
  temperature: 55
```

### Using Services in Automations

```yaml
automation:
  - alias: "Set temperatures based on time"
    trigger:
      - trigger: time
        at: "06:00:00"
    action:
      - action: universal_water_heater.set_target_temperature
        data:
          temperature: 65
      - action: universal_water_heater.set_eco_temperature
        data:
          temperature: 50
```

## Advanced Configuration

### Multiple Instances

You can add multiple instances of this integration for different devices:

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Universal Water Heater"
4. Configure with different connection details

Each instance creates separate entities with unique entity IDs.

## Troubleshooting Configuration

### Polling Behavior

The integration uses polling to fetch updates:

- **Minimum interval:** 30 seconds (prevents overloading the device)
- **Recommended interval:** 5 minutes (default)
- **Longer intervals:** Save resources but reduce responsiveness

Adjust based on your needs:

- Real-time monitoring: 30-60 seconds
- Regular updates: 5 minutes
- Slow-changing values: 15-30 minutes

## Diagnostic Data

The integration provides diagnostic data for troubleshooting:

1. Go to **Settings** → **Devices & Services**
2. Find "Universal Water Heater"
3. Click on the device
4. Click **Download Diagnostics**

Diagnostic data includes:

- Connection status
- Last update timestamp
- API response data
- Entity states
- Error history

**Privacy note:** Diagnostic data may contain sensitive information. Review before sharing.

## Blueprints

The integration works with Home Assistant Blueprints for reusable automations:

### Example Blueprint

```yaml
blueprint:
  name: Universal Water Heater Alert
  description: Send notification when sensor exceeds threshold
  domain: automation
  input:
    sensor_entity:
      name: Sensor
      selector:
        entity:
          domain: sensor
          integration: universal_water_heater
    threshold:
      name: Threshold
      selector:
        number:
          min: 0
          max: 100

trigger:
  - trigger: numeric_state
    entity_id: !input sensor_entity
    above: !input threshold

action:
  - action: notify.notify
    data:
      message: "Sensor exceeded threshold!"
```

## Configuration Examples

See [EXAMPLES.md](./EXAMPLES.md) for complete automation and dashboard examples.

## Troubleshooting Configuration

### Config Entry Fails to Load

If the integration fails to load after configuration:

1. Check Home Assistant logs for errors
2. Verify connection details are correct
3. Test connectivity from Home Assistant to the device
4. Try removing and re-adding the integration

### Options Don't Save

If configuration changes aren't persisted:

1. Check for validation errors in the UI
2. Ensure values are within allowed ranges
3. Review logs for detailed error messages
4. Try restarting Home Assistant

## Related Documentation

- [Getting Started](./GETTING_STARTED.md) - Installation and initial setup
- [Examples](./EXAMPLES.md) - Automation and dashboard examples
- [GitHub Issues](https://github.com/PhilKloppers/universal-water-heater/issues) - Report problems
