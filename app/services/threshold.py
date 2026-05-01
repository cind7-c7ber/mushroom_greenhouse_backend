THRESHOLDS = {
    "temperature": {
        "setpoint": 25.0,
        "optimal": (23.0, 26.0),
        "watch_low": (20.0, 22.9),
        "watch_high": (26.1, 30.0),
        "critical_low": (-10.0, 19.9),
        "critical_high": (30.1, 60.0),
        "unit": "°C",
    },
    "humidity": {
        "setpoint": 85.0,
        "optimal": (80.0, 90.0),
        "watch_low": (70.0, 79.9),
        "watch_high": (90.1, 95.0),
        "critical_low": (0.0, 69.9),
        "critical_high": (95.1, 100.0),
        "unit": "%",
    },
    "light": {
        "setpoint": 150.0,
        "optimal": (130.0, 170.0),
        "watch_low": (100.0, 129.9),
        "watch_high": (170.1, 220.0),
        "critical_low": (0.0, 99.9),
        "critical_high": (220.1, 200000.0),
        "unit": "lux",
    },
    "moisture": {
        "setpoint": 65.0,
        "optimal": (60.0, 70.0),
        "watch_low": (50.0, 59.9),
        "watch_high": (70.1, 80.0),
        "critical_low": (0.0, 49.9),
        "critical_high": (80.1, 100.0),
        "unit": "%",
    },
    "co2": {
        "setpoint": 400.0,
        "optimal": (350.0, 800.0),
        "watch_low": (200.0, 349.9),
        "watch_high": (800.1, 1500.0),
        "critical_low": (0.0, 199.9),
        "critical_high": (1500.1, 10000.0),
        "unit": "ppm",
    },
}


def classify_value(parameter: str, value: float) -> dict:
    rules = THRESHOLDS[parameter]

    for band in ["optimal", "watch_low", "watch_high", "critical_low", "critical_high"]:
        low, high = rules[band]
        if low <= value <= high:
            if band == "optimal":
                severity = "normal"
            elif band.startswith("watch"):
                severity = "watch"
            else:
                severity = "critical"

            return {
                "parameter": parameter,
                "value": value,
                "severity": severity,
                "band": band,
                "setpoint": rules["setpoint"],
                "unit": rules["unit"],
            }

    return {
        "parameter": parameter,
        "value": value,
        "severity": "unknown",
        "band": "unknown",
        "setpoint": rules["setpoint"],
        "unit": rules["unit"],
    }