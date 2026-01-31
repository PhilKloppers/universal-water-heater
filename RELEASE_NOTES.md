# Release Notes - v0.9.0-beta

## Universal Water Heater - Home Assistant Integration

A flexible Home Assistant custom integration for intelligent water heater control with battery awareness, optimised scheduling, and real-time temperature monitoring.

## What's New in v0.9.0-beta

### 🎯 Core Features

- **Real-Time Temperature Control** - Hysteresis-based heating control with immediate response to temperature changes (0.1°C resolution)
- **Multiple Operating Modes** - Normal, Eco, Optimised, and Off modes for different usage scenarios
- **Entity Mirroring** - Mirror existing temperature sensors and switch entities for seamless integration
- **Safety Features** - Automatic heater shutoff on overtemperature or entity unavailability with automatic recovery

### 🔋 Battery-Aware Heating

- Automatically pause heating when battery state of charge drops below configurable threshold
- Hysteresis control prevents rapid on/off cycling (separate stop and resume thresholds)
- Real-time battery monitoring with instant response to SoC changes

### ⏰ Optimised Mode Scheduling

Choose between two intelligent heating strategies:

- **Time-Based Control** - Schedule heating for specific hours (e.g., morning showers, evening preparation)
  - Normal mode during configured hours
  - Eco mode during alternative hours
  - Heater OFF outside both ranges for maximum energy savings
  - Supports midnight-crossing time ranges
  - Timezone-aware using Home Assistant's configured timezone

- **Solar-Based Control** - Heat based on sun elevation (ideal for solar panel systems)
  - Normal temperature when sun is above configured angle threshold (0-80°)
  - Eco temperature when sun is below threshold
  - Leverages Home Assistant's sun entity

### 🎛️ Configuration

- **Multi-Step Config Flow** - Intuitive setup process with conditional flows based on selected features
- **Options Flow** - Reconfigure settings after initial setup
- **Entity Source Management** - Add, change, or remove optional power/voltage/current sensors dynamically
- **Validation** - Time range overlap detection, threshold validation, and entity availability checking

### 📊 Monitoring & Diagnostics

- **Status Sensor** - Real-time system health with configuration attributes
- **Dynamic Attributes** - Status sensor exposes active control strategy and configuration
- **Automatic Status Updates** - Normal, Overtemp, Error, and Off states with automatic recovery
- **Diagnostic Data** - Comprehensive troubleshooting information with automatic redaction of sensitive data

### 🔧 Services

- `evaluate_control_logic` - Manually trigger control logic evaluation
- `set_target_temperature` - Update Normal mode target temperature
- `set_eco_temperature` - Update Eco mode target temperature

## Installation

Install via HACS or manually from the [repository](https://github.com/PhilKloppers/universal-water-heater).

See [Getting Started Guide](docs/user/GETTING_STARTED.md) for detailed setup instructions.

## Configuration

See [Configuration Reference](docs/user/CONFIGURATION.md) for complete documentation of all options.

## Known Limitations

- This is a **beta release** - thorough testing recommended before production use
- Single config entry per integration instance
- Requires existing temperature sensor and switch entities (does not communicate directly with hardware)

## Feedback & Support

This integration is under active development. Your feedback helps improve it!

- 🐛 **Found a bug?** [Report it here](https://github.com/PhilKloppers/universal-water-heater/issues/new?labels=bug&template=bug_report.md)
- 💡 **Have a feature idea?** [Request it here](https://github.com/PhilKloppers/universal-water-heater/issues/new?labels=enhancement&template=feature_request.md)
- 📖 **Documentation unclear?** [Let us know](https://github.com/PhilKloppers/universal-water-heater/issues/new?labels=documentation)

## Requirements

- Home Assistant 2026.1.0 or newer
- Existing temperature sensor entity (for water temperature)
- Existing switch entity (for heater control)

## Changelog

### v0.9.0-beta (2026-01-31)

**Added:**
- Initial beta release
- Real-time temperature monitoring and control logic
- Battery-aware heating with configurable thresholds
- Optimised mode with time-based and solar-based scheduling
- Timezone-aware time comparisons
- Multi-step configuration flow
- Status sensor with dynamic attributes
- Comprehensive documentation

**Technical:**
- Event-driven architecture using `async_track_state_change_event`
- Hysteresis control to prevent rapid cycling
- Midnight-crossing time range support
- Automatic status recovery from error conditions
- Time range overlap validation

---

**Enjoy smarter water heating! 🚿⚡**
