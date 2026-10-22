
def calculate_escalation(
    priority_score,
    sentiment
):

    if priority_score >= 80:

        return "High"

    if (
        priority_score >= 60
        and sentiment in [
            "Negative",
            "Very Negative"
        ]
    ):

        return "High"

    if priority_score >= 40:

        return "Medium"

    return "Low"
