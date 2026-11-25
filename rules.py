"""Pure irrigation logic: no AWS calls, so it is easy to test."""

# Soil moisture range (%) per crop. Illustrative values: tune for your soil.
CROPS = {
    "wheat": (30, 60),
    "maize": (35, 65),
    "tomato": (45, 75),
}
HEAT_LIMIT_C = 38


def validate(reading):
    """Return a cleaned reading, or raise ValueError."""
    try:
        clean = {
            "field_id": str(reading["field_id"]),
            "crop": str(reading["crop"]).lower(),
            "soil_moisture": float(reading["soil_moisture"]),
            "temperature_c": float(reading["temperature_c"]),
            "timestamp": str(reading["timestamp"]),
        }
    except (KeyError, TypeError) as err:
        raise ValueError(f"missing or invalid field: {err}") from err

    if clean["crop"] not in CROPS:
        raise ValueError(f"unknown crop: {clean['crop']}")
    if not 0 <= clean["soil_moisture"] <= 100:
        raise ValueError("soil_moisture must be between 0 and 100")
    if not -30 <= clean["temperature_c"] <= 60:
        raise ValueError("temperature_c must be between -30 and 60")
    return clean


def evaluate(reading):
    """Return (status, list of advice messages) for a validated reading."""
    low, high = CROPS[reading["crop"]]
    moisture = reading["soil_moisture"]
    status, advice = "OK", []

    if moisture < low:
        status = "IRRIGATE"
        advice.append(f"Soil moisture {moisture}% is below {low}%. Start irrigation.")
    elif moisture > high:
        status = "TOO_WET"
        advice.append(f"Soil moisture {moisture}% is above {high}%. Stop irrigation.")

    if reading["temperature_c"] > HEAT_LIMIT_C:
        if status == "OK":
            status = "HEAT_STRESS"
        advice.append(f"Temperature {reading['temperature_c']} C: heat stress risk.")

    return status, advice
