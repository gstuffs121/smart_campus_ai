
import re

# Potentially dangerous campus complaint phrases.
EMERGENCY_PATTERNS = {
    "Fire or smoke": [
        r"\bfire\b",
        r"\bsmoke\b",
        r"\bbuilding is burning\b",
        r"\bflames?\b",
    ],
    "Electrical danger": [
        r"\belectric shock\b",
        r"\belectrocution\b",
        r"\blive wire\b",
        r"\bsparking wire\b",
        r"\bexposed wiring\b",
        r"\belectrical sparks?\b",
    ],
    "Gas leak": [
        r"\bgas leak\b",
        r"\bgas is leaking\b",
        r"\bgas smell\b",
        r"\bgas leakage\b",
    ],
    "Structural danger": [
        r"\bbuilding collapse\b",
        r"\bceiling is collapsing\b",
        r"\bwall is collapsing\b",
        r"\bstructural crack\b",
    ],
    "Immediate safety threat": [
        r"\bsevere flooding\b",
        r"\bpeople are trapped\b",
        r"\bperson is unconscious\b",
        r"\bmedical emergency\b",
    ],
}


def detect_emergency(title, description):
    """
    Flag complaints containing potential emergency indicators.

    This is a rule-based screening tool, not a trained AI model
    or a substitute for emergency services.
    """

    text = f"{title} {description}".lower()
    detected_types = []

    for emergency_type, patterns in EMERGENCY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                detected_types.append(emergency_type)
                break

    if detected_types:
        return {
            "is_emergency": True,
            "level": "URGENT REVIEW",
            "detected_types": detected_types,
            "message": (
                "Potential safety hazard detected. "
                "Notify the responsible campus team immediately "
                "and arrange human assessment."
            ),
        }

    return {
        "is_emergency": False,
        "level": "NORMAL REVIEW",
        "detected_types": [],
        "message": (
            "No configured emergency phrase was detected. "
            "Continue normal complaint prioritization."
        ),
    }
