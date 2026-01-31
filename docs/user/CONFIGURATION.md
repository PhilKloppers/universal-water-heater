# Configuration Reference

This document describes all configuration options and settings available in the Universal Water Heater custom integration.

## Integration Configuration

### Initial Setup Options

These options are configured during initial setup via the Home Assistant UI.

#### Device Settings

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| **Device Name** | string | Yes | - | Friendly name for the integration instance |
| **Normal Temperature** | float | Yes | 65.0 | Target temperature for normal mode (40-80°C) |
| **Eco Temperature** | float | Yes | 55.0 | Target temperature for eco mode (40-80°C) |
| **Maximum Temperature** | float | Yes | 75.0 | Maximum allowed temperature (50-85°C) |
| **Hysteresis** | float | Yes | 4.0 | Temperature difference for switching (0.1-5°C) |

#### Entity Source Configuration

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| **Water Temperature Source** | entity_id | Yes | Sensor entity providing temperature reading |
| **Heater Switch Source** | entity_id | Yes | Switch entity for the heater switch to mirror |
| **Power Source** | entity_id | No | Sensor entity providing power consumption (optional) |
| **Voltage Source** | entity_id | No | Sensor entity providing voltage (optional) |
| **Current Source** | entity_id | No | Sensor entity providing current (amperage) (optional) |

### Advanced Options

These options are configured in the Options flow after initial setup.

#### Battery-Aware Heating

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| **Battery-Aware** | boolean | No | False | Enable battery-aware heating control |
| **Battery Stop Threshold** | float | No | 20.0 | Stop heating when battery SoC drops below this percentage (5-95%) |
| **Battery Resume Threshold** | float | No | 35.0 | Resume heating when battery SoC rises above this percentage (10-100%, must be > stop threshold) |
| **Battery SoC Entity** | entity_id | No | - | Battery state of charge sensor entity (required if battery-aware enabled) |

**How Battery-Aware Heating Works:**

When enabled, the heater will automatically pause heating when your battery state of charge drops below the configured stop threshold. Heating will only resume once the battery charges above the resume threshold. This prevents the heater from draining your battery during low-charge situations.

The integration monitors battery SoC in real-time, responding to every 0.1% change for immediate reaction to battery conditions.

**Example Scenario:**
- Stop threshold: 20%
- Resume threshold: 35%
- Battery at 25% → Heater turns off at 20%
- Battery charges to 32% → Heater stays off
- Battery reaches 36% → Heater can turn on again

This hysteresis prevents rapid on/off cycling around a single threshold.

#### Optimised Mode Scheduling

Optimised mode provides intelligent heating control based on time of day or solar generation:

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| **Use Solar Control** | boolean | No | False | Choose between solar-based (True) or time-based (False) control |

**Time-Based Control (when Use Solar Control = False):**

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| **Normal Mode Start** | time | No | - | Start time for normal temperature heating |
| **Normal Mode End** | time | No | - | End time for normal temperature heating |
| **Eco Mode Start** | time | No | - | Start time for eco temperature heating |
| **Eco Mode End** | time | No | - | End time for eco temperature heating |

**Solar-Based Control (when Use Solar Control = True):**

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| **Sun Entity ID** | entity_id | No | - | Sun entity (automatically created by Home Assistant) |
| **Sun Angle** | float | No | 0 | Sun elevation threshold in degrees (0-80°) |

**How Optimised Mode Works:**

When you select Optimised mode, the integration uses your chosen strategy to determine target temperature:

- **Time-Based Strategy:**
  - During Normal mode hours: Heats to normal temperature
  - During Eco mode hours: Heats to eco temperature
  - Outside both ranges: Turns heater OFF completely (saves maximum energy)
  - All times use your Home Assistant timezone
  - Time ranges are validated to prevent overlaps
  - Supports midnight-crossing ranges (e.g., 22:00-06:00)

- **Solar-Based Strategy:**
  - Sun elevation > threshold: Heats to normal temperature (sun is generating power)
  - Sun elevation < threshold: Heats to eco temperature
  - Ideal for solar panel systems - heat when excess power is available
  - Angle threshold adjustable from 0° (horizon) to 80° (high sun)

**Example Time-Based Schedule:**

- Normal mode: 06:00-08:00 (morning heating for showers)
- Eco mode: 17:00-19:00 (evening preparation)
- Rest of day: OFF (heater completely disabled)

**Example Solar-Based:**

- Sun angle threshold: 45°
- Sun above 45°: Normal temp (strong solar generation)
- Sun below 45°: Eco temp (reduced generation)

Both strategies work alongside battery-aware mode - if battery drops below threshold, heater turns off regardless of schedule.

#### Debug Settings

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| **Enable Debug Logging** | boolean | No | False | Enable detailed debug logging for troubleshooting |
| **Custom Icon** | string | No | (empty) | Override default icon for entities |

### Options Flow (Reconfiguration)

After initial setup, you can modify entity source configuration and other settings:

1. Go to **Settings** → **Devices & Services**
2. Find "Universal Water Heater"
3. Click **Configure** to reconfigure device settings or reconfigure entity sources
4. Modify settings
5. Click **Submit**

**Device Settings (available during reconfiguration):**
- Device name
- Normal, eco, and maximum temperatures
- Hysteresis value

**Entity Source Configuration (available during reconfiguration):**
- Water temperature entity source (can be changed)
- Heater switch entity source (can be changed)
- Power entity source (can be added, changed, or removed)
- Voltage entity source (can be added, changed, or removed)
- Current entity source (can be added, changed, or removed)

When you clear an optional power/voltage/current entity source, the corresponding entity will be automatically removed from Home Assistant.

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

## Entities

### Status Sensor

The status sensor monitors the overall health and operating state of the system:

**States:**

- **Normal**: System operating normally within all parameters
- **Overtemp**: Temperature exceeded maximum allowed temperature
  - Heater is automatically turned off
  - User is warned when attempting to change mode
  - Status automatically recovers to Normal when temperature drops below normal temperature
- **Error**: One or more linked entities are unavailable or unresponsive
  - Heater is automatically turned off for safety
  - Status automatically recovers to Normal when all entities become available
- **Off**: Operating mode is set to Off

**Attributes:**

The status sensor provides the following attributes:

- `normal_temperature`: Target temperature for Normal mode
- `eco_temperature`: Target temperature for Eco mode
- `max_temperature`: Maximum allowed temperature (safety limit)
- `hysteresis`: Temperature differential for control logic
- `battery_threshold`: Stop heating threshold (if battery-aware enabled)
- `battery_resume_threshold`: Resume heating threshold (if battery-aware enabled)
- `optimised_control_type`: "time_based" or "solar" (if optimised mode configured)
- `normal_mode_start`: Start time for normal mode heating (if time-based control)
- `normal_mode_end`: End time for normal mode heating (if time-based control)
- `eco_mode_start`: Start time for eco mode heating (if time-based control)
- `eco_mode_end`: End time for eco mode heating (if time-based control)
- `sun_angle`: Sun elevation threshold in degrees (if solar control)

**Real-Time Monitoring:**

The integration monitors all linked entities continuously:

- Temperature changes trigger immediate control logic evaluation (every 0.1°C)
- Battery SoC changes trigger immediate evaluation (every 0.1%)
- Entity availability is checked on every state change
- Control logic automatically turns off heater when:
  - Temperature exceeds maximum temperature
  - Any required entity becomes unavailable
  - Battery SoC drops below threshold (if battery-aware enabled)

**Automatic Recovery:**

- From **Overtemp** → **Normal**: When temperature drops below normal temperature
- From **Error** → **Normal**: When all linked entities become available again
- Normal operation automatically resumes after recovery

### Temperature Control Behavior

**Hysteresis Control:**

The integration uses hysteresis to prevent rapid on/off cycling:

- **Heater ON**: Turns off when temperature reaches `target + hysteresis`
- **Heater OFF**: Turns on when temperature drops below `target - hysteresis`

**Example (Normal mode with target 65°C, hysteresis 4°C):**

- Heater turns OFF at 69°C (65 + 4)
- Heater turns ON at 61°C (65 - 4)
- Provides 8°C total hysteresis band to prevent cycling

**Safety Overrides:**

- Overtemperature always forces heater OFF (cannot be overridden)
- Entity unavailability always forces heater OFF (cannot be overridden)
- User retains full control of mode selection even during safety conditions
- Warnings are logged when mode changes during overtemperature

## Services

The integration provides the following services:

### `universal_water_heater.evaluate_control_logic`

Manually trigger temperature and battery-based control logic evaluation.

**Parameters:** None

**Example:**

```yaml
service: universal_water_heater.evaluate_control_logic
```

**When to use:**

- Test battery-aware heating behavior
- Force immediate control logic check after configuration changes
- Debug temperature or battery threshold configuration
- Verify heater control in response to current conditions

**Note:** Control logic runs automatically on every temperature change (0.1°C resolution) and battery state change (0.1% resolution), so manual triggering is typically only needed for testing or debugging. The integration also monitors entity availability continuously and automatically responds to unavailable entities.

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
- Entity states
- Configuration settings
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
