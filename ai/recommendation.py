
def generate_recommendation(
    department,
    priority_level,
    escalation
):

    recommendations = {

        "Electrical":
            "Electrical maintenance team should inspect the affected electrical equipment.",

        "Maintenance":
            "Maintenance staff should inspect the reported infrastructure issue.",

        "IT Support":
            "IT support team should verify the network or computer system and restore service.",

        "Housekeeping":
            "Housekeeping staff should inspect and clean the reported area.",

        "Academic":
            "Academic administration should review the reported academic issue.",

        "Security":
            "Security personnel should investigate the reported safety concern."
    }

    recommendation = recommendations.get(
        department,
        "The responsible department should investigate the complaint."
    )

    if priority_level == "Critical":

        recommendation += (
            " Immediate attention is required."
        )

    elif priority_level == "High":

        recommendation += (
            " The complaint should be handled on priority."
        )

    if escalation == "High":

        recommendation += (
            " Escalation risk is high."
        )

    return recommendation
