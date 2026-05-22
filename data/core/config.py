VOLUME_GUIDELINES = {
    "Rygg":      {"min": 10, "optimal": 14, "max": 20},
    "Bröst":     {"min": 10, "optimal": 12, "max": 20},
    "Ben":       {"min": 10, "optimal": 16, "max": 20},
    "Axlar":     {"min": 8,  "optimal": 12, "max": 20},
    "Armar":     {"min": 8,  "optimal": 12, "max": 18},
    "Mage":      {"min": 8,  "optimal": 10, "max": 16},
    "Kondition": {"min": 3,  "optimal": 5,  "max": 7},
}

ACWR_ZONES = {
    "undertraining": (0, 0.8),
    "optimal": (0.8, 1.3),
    "caution": (1.3, 1.5),
    "danger": (1.5, 999)
}
