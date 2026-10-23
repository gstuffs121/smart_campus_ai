from ai.emergency_detector import detect_emergency

result = detect_emergency(
    "Sparking wire in laboratory",
    "Students reported electrical sparks near a desk."
)

print(result)

assert result["is_emergency"] is True
assert "Electrical danger" in result["detected_types"]

normal_result = detect_emergency(
    "Broken classroom fan",
    "The fan is not working properly."
)

print(normal_result)

assert normal_result["is_emergency"] is False

print("All emergency detector tests passed!")
