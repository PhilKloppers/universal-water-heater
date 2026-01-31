# Architectural and Design Decisions

This document records significant architectural and design decisions made during the development of this integration.

## Format

Each decision is documented with:

- **Date:** When the decision was made
- **Context:** Why this decision was necessary
- **Decision:** What was decided
- **Rationale:** Why this approach was chosen
- **Consequences:** Expected impacts and trade-offs

---

## Decision Log

### Use Real-Time Entity Monitoring

**Date:** 2026-01-30

**Context:** The integration needs to respond immediately to temperature and state changes rather than polling on a fixed schedule.

**Decision:** Use `async_track_state_change_event` to monitor entity states in real-time and execute control logic on every change.

**Rationale:**

- Immediate response to temperature changes (0.1°C resolution)
- No polling delay - control logic runs when needed
- Battery-aware mode requires instant response to battery SoC changes
- Better user experience with responsive automation

**Consequences:**

- Must handle rapid state updates efficiently
- Control logic must be fast and non-blocking
- Error handling critical to prevent event loop blocking
- More complex than simple polling approach

---

### Timezone-Aware Time Comparisons

**Date:** 2026-01-31

**Context:** Time-based optimised mode compares current time against user-configured time ranges. Users configure times in their local timezone, but Python's `datetime.now()` returns UTC.

**Decision:** Use Home Assistant's `dt_util.now()` for all time comparisons to get timezone-aware current time.

**Rationale:**

- Users think in local time when configuring schedules
- Home Assistant already manages timezone configuration
- `dt_util.now()` respects HA's configured timezone
- Eliminates confusion from UTC offset calculations

**Consequences:**

- Requires Home Assistant's dt utility module
- Time comparisons automatically respect user's timezone
- No manual timezone conversion needed
- Correctly handles DST transitions

---

### Optimised Mode Control Strategy

**Date:** 2026-01-30

**Context:** Need intelligent heating control that adapts to time of day or solar generation while preventing battery drain.

**Decision:** Implement dual-strategy optimised mode:

- **Time-based:** Normal temp during configured hours, eco temp or OFF outside those ranges
- **Solar:** Normal temp when sun elevation above threshold, eco temp below

**Rationale:**

- Time-based works for predictable schedules (morning heating, load shedding avoidance)
- Solar-based works with solar generation (heat when excess power available)
- Users can choose strategy that fits their setup
- Both strategies support ECO fallback or complete OFF when not in active range
- Prevents battery drain by turning heater completely OFF outside configured times

**Consequences:**

- Configuration UI needs conditional flows based on strategy selection
- Time range validation required to prevent overlaps
- Must handle midnight-crossing time ranges correctly
- Returns `None` target temperature to signal heater should be OFF
- More complex than simple temperature-only control

---

### Platform-Specific Directories

**Date:** 2026-11-29 (Template initialization)

**Context:** Integration supports multiple platforms (sensor, binary_sensor, switch, etc.).

**Decision:** Each platform gets its own directory with individual entity files.

**Rationale:**

- Clear organization as integration grows
- Easier to find specific entity implementations
- Supports multiple entities per platform cleanly
- Follows Home Assistant Core pattern

**Consequences:**

- More files/directories than single-file approach
- Platform `__init__.py` must import and register entities
- Slightly more initial setup overhead

---

### EntityDescription for Static Metadata

**Date:** 2026-11-29 (Template initialization)

**Context:** Entities have static metadata (name, icon, device class) that doesn't change.

**Decision:** Use `EntityDescription` dataclasses to define static entity metadata.

**Rationale:**

- Declarative and easy to read
- Type-safe with dataclasses
- Recommended Home Assistant pattern
- Separates static configuration from dynamic behavior

**Consequences:**

- Each entity type needs an EntityDescription
- Dynamic entities need custom handling
- Static and dynamic properties clearly separated

---

## Future Considerations

### State Restoration

**Status:** Not yet implemented

Consider implementing state restoration for switches and configurable settings to maintain state across Home Assistant restarts when the external device is unavailable.

### Multi-Device Support

**Status:** Not yet implemented

Current architecture assumes single device per config entry. If multi-device support is needed, coordinator data structure will need redesign to map device ID → data.

### Polling vs. Push

**Status:** Uses polling

Currently implements polling-based updates. If the API supports webhooks or WebSocket, consider implementing push-based updates for real-time responsiveness.

---

## Decision Review

These decisions should be reviewed periodically (suggested: quarterly or when major features are added) to ensure they still serve the integration's needs.
