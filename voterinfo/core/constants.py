"""
core/constants.py
------------------
UNIT 1 - PYTHON FUNDAMENTALS: Dictionaries, Lists, Conditional Statements.

This module demonstrates core Python data structures used throughout
the VoterInfo application, plus the simple eligibility conditional logic
required by the project spec.
"""

# ------------------------------------------------------------------
# 1. DICTIONARIES - Sample Polling Booth information
# ------------------------------------------------------------------
SAMPLE_BOOTH_RECORD = {
    "pin_code": "422003",
    "booth_name": "Zilla Parishad Primary School, Trimbak Road",
    "address": "Near Gram Panchayat Office, Trimbak Road, Nashik",
    "officer_name": "Mr. Ramesh Patil",
    "booth_number": "NSK-101",
}

# A small in-memory seed dataset (dictionaries), used by management
# command `seed_data` to populate MongoDB for demo purposes.
SEED_BOOTHS = [
    {
        "booth_name": "Zilla Parishad Primary School",
        "booth_number": "NSK-101",
        "address": "Trimbak Road, Nashik, Maharashtra",
        "pin_code": "422003",
        "officer_name": "Ramesh Patil",
        "contact_number": "9876543210",
        "area_name": "Trimbak",
    },
    {
        "booth_name": "Municipal High School",
        "booth_number": "MUM-205",
        "address": "Andheri West, Mumbai, Maharashtra",
        "pin_code": "400058",
        "officer_name": "Sunita Deshmukh",
        "contact_number": "9876500001",
        "area_name": "Andheri",
    },
    {
        "booth_name": "Government Higher Secondary School",
        "booth_number": "PUN-310",
        "address": "Shivaji Nagar, Pune, Maharashtra",
        "pin_code": "411005",
        "officer_name": "Anil Kulkarni",
        "contact_number": "9876500002",
        "area_name": "Shivaji Nagar",
    },
    {
        "booth_name": "Community Hall Booth",
        "booth_number": "DEL-402",
        "address": "Connaught Place, New Delhi",
        "pin_code": "110001",
        "officer_name": "Priya Sharma",
        "contact_number": "9876500003",
        "area_name": "Connaught Place",
    },
    {
        "booth_name": "Sarvajanik Vidyalaya",
        "booth_number": "BLR-118",
        "address": "Koramangala, Bengaluru, Karnataka",
        "pin_code": "560034",
        "officer_name": "Suresh Rao",
        "contact_number": "9876500004",
        "area_name": "Koramangala",
    },
]

# ------------------------------------------------------------------
# 2. LISTS - Voter eligibility criteria
# ------------------------------------------------------------------
VOTER_ELIGIBILITY_CRITERIA = [
    "Must be an Indian Citizen",
    "Must be 18 years of age or older on the qualifying date",
    "Must have a valid Address Proof",
    "Must possess Aadhaar Card or EPIC (Voter ID) Number",
    "Must not be disqualified under any law (unsound mind / electoral offence)",
]

REQUIRED_DOCUMENTS = [
    {"name": "Aadhaar Card", "purpose": "Identity & Address Proof"},
    {"name": "Passport size Photograph", "purpose": "For Voter ID / EPIC"},
    {"name": "Address Proof (Utility Bill / Rent Agreement)", "purpose": "Residence verification"},
    {"name": "Age Proof (Birth Certificate / 10th Marksheet)", "purpose": "Age verification"},
    {"name": "Form 6 (Application for new voter)", "purpose": "Official NVSP registration form"},
]

REGISTRATION_STEPS = [
    {
        "step": 1,
        "title": "Check Your Eligibility",
        "description": "Confirm you are an Indian citizen, aged 18+ as of the qualifying date, "
                        "and ordinarily resident of the constituency.",
    },
    {
        "step": 2,
        "title": "Gather Required Documents",
        "description": "Keep your Aadhaar Card, address proof, age proof, and a passport-size "
                        "photograph ready.",
    },
    {
        "step": 3,
        "title": "Fill Form 6 Online",
        "description": "Visit the official NVSP portal and fill Form 6 for new voter registration.",
    },
    {
        "step": 4,
        "title": "Upload Documents",
        "description": "Upload scanned copies of your documents and photograph as per guidelines.",
    },
    {
        "step": 5,
        "title": "Submit & Track Application",
        "description": "Submit the form and note your reference ID to track application status online.",
    },
    {
        "step": 6,
        "title": "BLO Verification",
        "description": "A Booth Level Officer (BLO) may visit for field verification of your details.",
    },
    {
        "step": 7,
        "title": "Receive Your EPIC",
        "description": "On approval, your Voter ID (EPIC) card will be issued and your name added "
                        "to the electoral roll.",
    },
]

COMPLAINT_CATEGORIES = [
    "Booth Location Issue",
    "Long Waiting Queue",
    "EVM / VVPAT Malfunction",
    "Missing Name in Voter List",
    "Accessibility Issue (Ramp/Wheelchair)",
    "Staff Misconduct",
    "Other",
]


# ------------------------------------------------------------------
# 3. CONDITIONAL STATEMENTS - Eligibility check
# ------------------------------------------------------------------
def check_basic_eligibility(age: int) -> str:
    """
    Simple conditional check as required by the project spec (Unit 1).

    If age >= 18 -> "Eligible for Voter Registration"
    Else         -> "Not Eligible Yet"
    """
    if age >= 18:
        return "Eligible for Voter Registration"
    else:
        return "Not Eligible Yet"
