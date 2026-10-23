
def classify_complaint(title, description):

    # Combine title and description
    text = (
        title + " " + description
    ).lower()

    # --------------------------------------------------
    # DEPARTMENT PATTERNS
    # --------------------------------------------------

    department_patterns = {

        "Electrical": [

            # Fan / light
            "fan not working",
            "fan is not working",
            "fan gone",
            "fan stopped",
            "fan stopped working",
            "no fan",
            "light not working",
            "light is not working",
            "bulb not working",
            "bulb is not working",

            # Power
            "no electricity",
            "no power",
            "power gone",
            "current gone",
            "electricity gone",
            "power cut",
            "power problem",

            # Electrical equipment
            "switch not working",
            "switch is broken",
            "plug not working",
            "socket not working",
            "wire broken",
            "wire is broken",
            "broken wire",
            "electric wire",
            "electric problem",
            "electricity problem",
            "electrical problem",
            "electric shock",
            "getting shock",

            # General terms
            "electricity",
            "electrical",
            "electric",
            "current",
            "voltage",
            "wiring"
        ],


        "Maintenance": [

            # Building
            "building problem",
            "building damaged",
            "wall broken",
            "wall damaged",
            "ceiling broken",
            "ceiling damaged",
            "roof leaking",
            "roof broken",

            # Doors / windows
            "door broken",
            "door not working",
            "window broken",
            "window not working",

            # Furniture
            "chair broken",
            "chair damaged",
            "table broken",
            "table damaged",
            "bench broken",
            "desk broken",

            # Water / plumbing
            "water leaking",
            "water leak",
            "water coming",
            "pipe broken",
            "pipe leaking",
            "tap broken",
            "tap not working",
            "no water",
            "water problem",

            # Other infrastructure
            "lift not working",
            "elevator not working",
            "classroom problem",
            "room problem",
            "floor damaged",

            # General terms
            "maintenance",
            "building",
            "door",
            "window",
            "wall",
            "ceiling",
            "roof",
            "pipe",
            "leak"
        ],


        "IT Support": [

            # Internet
            "wifi not working",
            "wifi is not working",
            "wi-fi not working",
            "internet not working",
            "internet is not working",
            "net not working",
            "net is not working",
            "no wifi",
            "no internet",
            "wifi gone",
            "internet gone",
            "network problem",
            "network not working",

            # Computer
            "computer not working",
            "computer is not working",
            "computer stopped",
            "laptop not working",
            "system not working",
            "computer problem",
            "laptop problem",

            # Printer
            "printer not working",
            "printer problem",
            "printer is broken",

            # Login / password
            "cannot login",
            "can't login",
            "login problem",
            "password problem",
            "forgot password",
            "account problem",

            # General
            "software problem",
            "server problem",
            "email problem",
            "it problem",
            "internet",
            "wifi",
            "network",
            "computer",
            "laptop",
            "printer",
            "login"
        ],


        "Housekeeping": [

            # Cleaning
            "room dirty",
            "classroom dirty",
            "floor dirty",
            "place dirty",
            "very dirty",
            "not clean",
            "not cleaned",
            "room not clean",
            "classroom not clean",
            "cleaning problem",

            # Garbage
            "garbage not removed",
            "garbage everywhere",
            "garbage problem",
            "trash everywhere",
            "waste everywhere",
            "dust everywhere",

            # Toilet / washroom
            "toilet dirty",
            "toilet not clean",
            "washroom dirty",
            "washroom not clean",
            "bathroom dirty",
            "bathroom not clean",
            "toilet problem",
            "washroom problem",

            # Smell
            "bad smell",
            "bad smell in room",
            "bad smell in toilet",
            "stinking",
            "smell problem",

            # General
            "cleaning",
            "clean",
            "dirty",
            "garbage",
            "trash",
            "dust",
            "toilet",
            "washroom",
            "bathroom",
            "waste",
            "sanitation",
            "hygiene"
        ],


        "Academic": [

            # Teacher / faculty
            "teacher problem",
            "teacher issue",
            "faculty problem",
            "faculty issue",
            "teacher not coming",
            "faculty not coming",

            # Class
            "class problem",
            "class issue",
            "lecture problem",
            "lecture issue",
            "class cancelled",

            # Exam / marks
            "exam problem",
            "exam issue",
            "marks problem",
            "marks issue",
            "wrong marks",
            "marks not updated",

            # Attendance
            "attendance problem",
            "attendance issue",
            "attendance not updated",
            "wrong attendance",

            # Timetable
            "timetable problem",
            "timetable issue",
            "wrong timetable",

            # Assignment / subject
            "assignment problem",
            "subject problem",
            "lab problem",
            "academic problem",

            # General
            "teacher",
            "faculty",
            "exam",
            "marks",
            "attendance",
            "subject",
            "timetable",
            "lecture",
            "assignment",
            "academic"
        ],


        "Security": [

            # Theft
            "my bag stolen",
            "bag stolen",
            "phone stolen",
            "laptop stolen",
            "money stolen",
            "someone stole",
            "stolen",
            "theft",

            # Safety
            "not safe",
            "unsafe",
            "danger",
            "dangerous",
            "safety problem",
            "security problem",

            # CCTV
            "camera not working",
            "cctv not working",
            "cctv problem",
            "security camera",

            # People / incidents
            "fight",
            "fighting",
            "intruder",
            "unknown person",
            "threat",
            "harassment",

            # General
            "security",
            "safety",
            "theft",
            "stolen",
            "cctv",
            "camera",
            "intruder"
        ]
    }


    # --------------------------------------------------
    # CALCULATE DEPARTMENT SCORES
    # --------------------------------------------------

    scores = {}

    for department, patterns in department_patterns.items():

        score = 0

        for pattern in patterns:

            if pattern in text:

                # Longer phrases are stronger evidence
                if len(pattern.split()) >= 3:
                    score += 3
                else:
                    score += 1

        scores[department] = score


    # --------------------------------------------------
    # FIND BEST DEPARTMENT
    # --------------------------------------------------

    best_department = max(
        scores,
        key=scores.get
    )


    # --------------------------------------------------
    # NO MATCH
    # --------------------------------------------------

    if scores[best_department] == 0:

        best_department = "Maintenance"


    return best_department
