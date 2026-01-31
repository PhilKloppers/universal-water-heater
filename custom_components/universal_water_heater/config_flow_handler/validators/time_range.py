"""Validation helpers for config flow."""

from __future__ import annotations

from datetime import datetime, time


def validate_time_ranges_no_overlap(
    normal_start: str,
    normal_end: str,
    eco_start: str,
    eco_end: str,
) -> bool:
    """
    Validate that normal and eco time ranges do not overlap.

    Args:
        normal_start: Normal mode start time (HH:MM or HH:MM:SS)
        normal_end: Normal mode end time (HH:MM or HH:MM:SS)
        eco_start: Eco mode start time (HH:MM or HH:MM:SS)
        eco_end: Eco mode end time (HH:MM or HH:MM:SS)

    Returns:
        True if there is no overlap, False if ranges overlap

    """
    try:
        # Parse time strings
        def parse_time(time_str: str) -> time:
            """Parse time string in HH:MM or HH:MM:SS format."""
            if ":" in time_str and len(time_str.split(":")) == 3:
                return datetime.strptime(time_str, "%H:%M:%S").time()
            return datetime.strptime(time_str, "%H:%M").time()

        normal_start_time = parse_time(normal_start)
        normal_end_time = parse_time(normal_end)
        eco_start_time = parse_time(eco_start)
        eco_end_time = parse_time(eco_end)

        # Check if time is in range (handles midnight crossing)
        def is_in_range(check_time: time, range_start: time, range_end: time) -> bool:
            """Check if time is within range, handling midnight crossing."""
            if range_start <= range_end:
                # Normal range (e.g., 08:00 - 18:00)
                return range_start <= check_time <= range_end
            # Range crosses midnight (e.g., 22:00 - 06:00)
            return check_time >= range_start or check_time <= range_end

        # Check if eco range overlaps with normal range
        # Check if eco start or end is within normal range
        if is_in_range(eco_start_time, normal_start_time, normal_end_time):
            return False  # Overlap detected
        if is_in_range(eco_end_time, normal_start_time, normal_end_time):
            return False  # Overlap detected

        # Check if normal start or end is within eco range
        if is_in_range(normal_start_time, eco_start_time, eco_end_time):
            return False  # Overlap detected
        if is_in_range(normal_end_time, eco_start_time, eco_end_time):
            return False  # Overlap detected

    except (ValueError, TypeError):
        # If parsing fails, consider it invalid and return False
        return False
    else:
        return True  # No overlap
