
def calculate_priority(title, description, sentiment):

    text = (
        title + " " + description
    ).lower()

    score = 20

    # ==================================================
    # CRITICAL - Immediate safety or emergency
    # ==================================================

    critical_phrases = [

        "fire",
        "fire in building",
        "smoke in building",
        "electric shock",
        "getting electric shock",
        "someone got shock",
        "someone may get hurt",
        "students may get hurt",
        "people may get hurt",
        "danger to students",
        "danger for students",
        "life threatening",
        "life threat",
        "serious injury",
        "someone is injured",
        "student is injured",
        "accident happened",
        "gas leak",
        "major fire",
        "building on fire"
    ]

    critical_found = False

    for phrase in critical_phrases:

        if phrase in text:

            critical_found = True
            break


    # ==================================================
    # HIGH - Serious problem affecting many people
    # ==================================================

    high_phrases = [

        "urgent",
        "very urgent",
        "immediate attention",
        "needs immediate help",
        "needs immediate attention",
        "not safe",
        "unsafe",
        "dangerous",
        "serious problem",
        "very serious",
        "major problem",
        "major issue",
        "whole department",
        "entire department",
        "whole lab",
        "entire lab",
        "whole building",
        "entire building",
        "many students",
        "all students",
        "everyone is affected",
        "many people affected",
        "no electricity",
        "no power",
        "no water",
        "no internet",
        "internet completely down",
        "wifi completely down",
        "completely broken",
        "completely stopped"
    ]

    high_found = False

    for phrase in high_phrases:

        if phrase in text:

            high_found = True
            break


    # ==================================================
    # MEDIUM - Normal problem that needs attention
    # ==================================================

    medium_phrases = [

        "not working",
        "does not work",
        "doesn't work",
        "not working properly",
        "broken",
        "damaged",
        "problem",
        "issue",
        "failure",
        "fault",
        "leaking",
        "leak",
        "stopped working",
        "cannot use",
        "can't use",
        "unable to use",
        "needs repair",
        "needs fixing",
        "not available"
    ]

    medium_found = False

    for phrase in medium_phrases:

        if phrase in text:

            medium_found = True
            break


    # ==================================================
    # ADD SENTIMENT
    # ==================================================

    if sentiment == "Very Negative":

        score += 15

    elif sentiment == "Negative":

        score += 10


    # ==================================================
    # CALCULATE BASE SCORE
    # ==================================================

    if critical_found:

        score += 60

    elif high_found:

        score += 35

    elif medium_found:

        score += 15

    else:

        score += 0


    # ==================================================
    # EXTRA POINTS FOR MULTIPLE PEOPLE
    # ==================================================

    multiple_people = [

        "many students",
        "all students",
        "whole class",
        "entire class",
        "many people",
        "everyone",
        "multiple students",
        "students are affected"
    ]

    for phrase in multiple_people:

        if phrase in text:

            score += 10
            break


    # ==================================================
    # LIMIT SCORE
    # ==================================================

    score = min(score, 100)


    # ==================================================
    # PRIORITY LEVEL
    # ==================================================

    if score >= 75:

        level = "Critical"

    elif score >= 50:

        level = "High"

    elif score >= 30:

        level = "Medium"

    else:

        level = "Low"


    return score, level
