# Universal Water Heater

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

<!--
Uncomment and customize these badges if you want to use them:

[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]
[![Discord][discord-shield]][discord]
-->

**✨ Develop in the cloud:** Want to contribute or customize this integration? Open it directly in GitHub Codespaces - no local setup required!

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/PhilKloppers/universal-water-heater?quickstart=1)

## ✨ Features

- **Easy Setup**: Simple configuration through the UI - no YAML required
- **Temperature Control**: Monitor water temperature with configurable target and eco modes
- **Power Monitoring**: Track power consumption, voltage, and current in real-time
- **Smart Modes**: Select between Normal, Optimised, Eco, or Off operating modes
- **Thermostat Control**: Configure temperature settings with hysteresis for precise control
- **Linked Switch**: Mirror and control an external switch entity
- **Options Flow**: Adjust settings like entity sources and debug logging after setup
- **Real-time Updates**: Linked entities update instantly when source entities change

**This integration will set up the following platforms.**

Platform | Description
-- | --
`sensor` | Water temperature, power, voltage, and current (linked to external entities)
`binary_sensor` | API connectivity status
`switch` | Heater switch (linked to external switch entity)
`select` | Operating mode selection (Normal, Optimised, Eco, Off)
`number` | Temperature control (normal, eco, maximum) and hysteresis settings

> **💡 Interactive Demo**: The linked sensor and switch entities demonstrate real-time synchronization:
>
> - **Linked Sensors** mirror temperature, power, voltage, and current from other entities
> - **Heater Switch** reflects the state of an external switch entity
> - Changes to source entities update the linked entities instantly
> - Toggling the heater switch updates the source entity bidirectionally

## 🚀 Quick Start

### Step 1: Install the Integration

**Prerequisites:** This integration requires [HACS](https://hacs.xyz/) (Home Assistant Community Store) to be installed.

Click the button below to open the integration directly in HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jpawlowski&repository=universal-water-heater&category=integration)

Then:

1. Click "Download" to install the integration
2. **Restart Home Assistant** (required after installation)

> **Note:** The My Home Assistant redirect will first take you to a landing page. Click the button there to open your Home Assistant instance.

<details>
<summary>**Manual Installation (Advanced)**</summary>

If you prefer not to use HACS:

1. Download the `custom_components/universal_water_heater/` folder from this repository
2. Copy it to your Home Assistant's `custom_components/` directory
3. Restart Home Assistant

</details>

### Step 2: Add and Configure the Integration

**Important:** You must have installed the integration first (see Step 1) and restarted Home Assistant!

#### Option 1: One-Click Setup (Quick)

Click the button below to open the configuration dialog:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=universal_water_heater)

Follow the setup wizard:

1. Enter your device name
2. Configure entity sources in the next step
3. Click Submit

That's it! The integration will start monitoring your device.

#### Option 2: Manual Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for "Universal Water Heater"
4. Follow the same setup steps as Option 1

### Step 3: Configure Entity Sources (Optional)

After setup, you can specify which entities this integration should track:

1. Go to **Settings** → **Devices & Services**
2. Find **Universal Water Heater**
3. Click **Configure** to set:
   - Water Temperature entity source
   - Power Consumption entity source
   - Voltage entity source
   - Current entity source
   - Heater Switch source entity
   - Enable debug logging

You can also **Reconfigure** your device anytime without removing the integration.

### Step 4: Start Using!

The integration creates several entities for monitoring and control:

- **Sensors**: Water temperature, power consumption, voltage, current (all linked to external entities)
- **Switch**: Heater Switch (linked to external switch entity)
- **Select**: Operating Mode (Normal, Optimised, Eco, Off)
- **Numbers**: Target Temperature (Normal), Temperature (Eco), Maximum Temperature, Hysteresis
- **Binary Sensor**: API Connectivity status

Find all entities in **Settings** → **Devices & Services** → **Universal Water Heater** → click on the device.

## Available Entities

### Sensors

- **Water Temperature**: Current water temperature reading (linked entity)
- **Power**: Power consumption in watts (linked entity)
- **Voltage**: Electrical voltage reading (linked entity)
- **Current**: Electrical current (amperage) reading (linked entity)

All sensor values are synchronized in real-time from their source entities.

### Binary Sensors

- **API Connectivity**: Shows connection status to the integration's data source
  - On: Connected and operational
  - Off: Disconnected or unavailable

### Switches

- **Heater Switch**: Controls and mirrors an external switch entity
  - Bidirectionally synced with source entity
  - Updates reflect immediately

### Select

- **Mode**: Operating mode selection
  - **Normal**: Standard heating mode
  - **Optimised**: Balanced operation
  - **Eco**: Energy-saving mode
  - **Off**: Heater off

### Numbers

- **Temperature (Normal)**: Set target temperature for Normal mode
  - Range: 40°C - 80°C (step: 1°C)
  - Default: 65°C
- **Temperature (Eco)**: Set target temperature for Eco mode
  - Range: 40°C - 80°C (step: 1°C)
  - Default: 55°C
  - Constraint: Cannot exceed Temperature (Normal) value
- **Temperature (Max)**: Set maximum temperature limit
  - Range: 50°C - 85°C (step: 1°C)
  - Default: 75°C
- **Hysteresis**: Thermostat hysteresis to prevent oscillation
  - Range: 0.1°C - 5°C (step: 1°C)
  - Default: 4°C

## Custom Services

The integration provides services for automation and control:

### `universal_water_heater.set_target_temperature`

Set the target temperature for Normal mode.

**Parameters:**
- `temperature` (required): Temperature in °C (40-80, validated against max temperature)

**Example:**

```yaml
service: universal_water_heater.set_target_temperature
data:
  temperature: 65
```

### `universal_water_heater.set_eco_temperature`

Set the target temperature for Eco mode.

**Parameters:**
- `temperature` (required): Temperature in °C (40-80, validated against max temperature and cannot exceed normal temperature)

**Example:**

```yaml
service: universal_water_heater.set_eco_temperature
data:
  temperature: 55
```

## Configuration Options

### During Setup

Name | Required | Description
-- | -- | --
Device Name | Yes | A friendly name for your device

### After Setup (Options)

You can change these anytime by clicking **Configure**:

Name | Default | Description
-- | -- | --
Custom Icon | (empty) | Optional custom icon for the device
Enable Debugging | Off | Enable extra debug logging
Water Temperature Entity | (optional) | Entity to track water temperature
Power Entity | (optional) | Entity to track power consumption
Voltage Entity | (optional) | Entity to track voltage
Current Entity | (optional) | Entity to track electrical current
Heater Switch Source | (optional) | Entity for the heater switch to mirror

## Troubleshooting

### Connection Issues

If the integration fails to load:

1. Check that your device name is entered correctly
2. Verify any entity sources you've configured still exist
3. Go to **Settings** → **Devices & Services** and click **Reconfigure**
2. Find **Universal Water Heater**
3. Click the **3 dots menu** → **Reconfigure**
4. Update configuration as needed
5. Click Submit

#### Connection Status

Monitor your connection status with the **API Connection** binary sensor:

- **On** (Connected): Integration is receiving data normally
- **Off** (Disconnected): Connection lost
  - Check the binary sensor attributes for diagnostic information
  - Check network connectivity

### Enable Debug Logging

To enable debug logging for this integration, add the following to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.universal_water_heater: debug
```

### Common Issues

#### Entity Source Issues

If your entity sources are not working:

1. Verify the entity ID exists in Home Assistant
2. Check that the entity is available and not unavailable
3. Go to **Settings** → **Devices & Services** → **Reconfigure** to update entity sources
4. Check the integration logs for error messages

#### Missing Entities

If expected entities are not showing:

1. Refresh the page in Home Assistant UI
2. Restart Home Assistant
3. Check integration diagnostics (Settings → Devices & Services → Universal Water Heater → 3 dots → Download diagnostics)

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request if you have suggestions or improvements.

### 🛠️ Development Setup

Want to contribute or customize this integration? You have two options:

#### Cloud Development (Recommended)

The easiest way to get started - develop directly in your browser with GitHub Codespaces:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/PhilKloppers/universal-water-heater?quickstart=1)

- ✅ Zero local setup required
- ✅ Pre-configured development environment
- ✅ Home Assistant included for testing
- ✅ 60 hours/month free for personal accounts

#### Local Development

Prefer working on your machine? You'll need:

- Docker Desktop
- VS Code with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

Then:

1. Clone this repository
2. Open in VS Code
3. Click "Reopen in Container" when prompted

Both options give you the same fully-configured development environment with Home Assistant, Python 3.13, and all necessary tools.

---

## 🤖 AI-Assisted Development

> **ℹ️ Transparency Notice**
>
> This integration was developed with assistance from AI coding agents (GitHub Copilot, Claude, and others). While the codebase follows Home Assistant Core standards, AI-generated code may not be reviewed or tested to the same extent as manually written code.
>
> AI tools were used to:
>
> - Generate boilerplate code following Home Assistant patterns
> - Implement standard integration features (config flow, coordinator, entities)
> - Ensure code quality and type safety
> - Write documentation and comments
>
> Please be aware that AI-assisted development may result in unexpected behavior or edge cases that haven't been thoroughly tested. If you encounter any issues, please [open an issue](../../issues) on GitHub.
>
> *Note: This section can be removed or modified if AI assistance was not used in your integration's development.*

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by [@PhilKloppers][user_profile]**

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/PhilKloppers/universal-water-heater.svg?style=for-the-badge
[commits]: https://github.com/PhilKloppers/universal-water-heater/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/PhilKloppers/universal-water-heater.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40PhilKloppers-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/PhilKloppers/universal-water-heater.svg?style=for-the-badge
[releases]: https://github.com/PhilKloppers/universal-water-heater/releases
[user_profile]: https://github.com/jpawlowski

<!-- Optional badge definitions - uncomment if needed:
[buymecoffee]: https://www.buymeacoffee.com/jpawlowski
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
-->
