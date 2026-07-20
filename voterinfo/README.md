# VoterInfo — Voter Registration Guide & Polling Booth Locator

A GovTech web application (MCA Final Year / Mini Project) built with **Python, Django, MongoDB, Bootstrap 5, and Django REST Framework**. VoterInfo helps Indian citizens check voter registration eligibility, locate their polling booth, learn the registration process, view required documents, and file polling-booth complaints.

> ⚠️ **Educational Disclaimer:** This is an academic demo project, not an official government website. It is not affiliated with the Election Commission of India. All logos are labeled placeholders.

---

## 1. Features

- 🏠 Modern, responsive, government-inspired homepage with hero banner, feature cards, and dashboard-style stats
- 📍 **Booth Locator** — find a polling booth by 6-digit PIN Code
- ✅ **Eligibility Checker** — auto-calculates age from Date of Birth and validates Aadhaar format
- 📖 **Registration Guide** — step-by-step voter registration walkthrough
- 📄 **Required Documents** — checklist of documents needed to register
- 🚩 **Complaint Form** — file and track polling-booth complaints (stored in MongoDB)
- 🔌 **REST API** (Django REST Framework) for Booths, Complaints, and Eligibility
- 🛠️ **Custom Admin Dashboard** — manage Booths, Complaints, Users, and Statistics (MongoDB-aware, since Django's default admin only manages SQL models)
- 🌓 Dark mode toggle, live search, toast notifications, loading spinner, CSV export
- 🧵 Background data import using Python `threading` (with live status polling)
- 🔒 Regex validation for Aadhaar (12 digits), PIN Code (6 digits), Mobile Number (10 digits)
- ✅ Unit tests for core business logic (`core/tests.py`)

---

## 2. Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Django 5 |
| Database | MongoDB (via MongoEngine) |
| Auth / Admin storage | SQLite (Django's built-in auth/session tables only) |
| API | Django REST Framework |
| Frontend | HTML5, CSS3, Bootstrap 5, vanilla JavaScript |
| Icons | Bootstrap Icons |
| Fonts | Poppins (headings) + Noto Sans (body) |

**Why two databases?** Django's authentication, sessions, and admin log tables need a relational database, so SQLite is used for that (zero setup). All *application* data — Polling Booths and Complaints — is stored in MongoDB via MongoEngine, exactly as the project spec requires. This is a standard, well-documented pattern for Django + MongoDB projects.

---

## 3. Folder Structure

```
voterinfo/
├── manage.py
├── requirements.txt
├── .gitignore
├── README.md
├── voterinfo/                  # Django project package
│   ├── settings.py             # Django + MongoDB (MongoEngine) config
│   ├── urls.py                 # Root URLconf
│   └── wsgi.py
└── core/                       # Main Django app
    ├── constants.py            # Unit 1: dictionaries, lists, conditional logic
    ├── booth_locator.py        # Unit 2: functions, custom exceptions, datetime
    ├── validators.py           # Unit 3: regex validation (Aadhaar/PIN/Mobile)
    ├── oop_models.py           # Unit 3: PollingBooth, Voter, EligibilityChecker classes
    ├── data_importer.py        # Unit 3: threading (background booth import)
    ├── mongo_models.py         # Unit 4: MongoEngine Documents (MongoDB collections)
    ├── models.py                # (empty — app data lives in MongoDB, see mongo_models.py)
    ├── forms.py                 # Django forms with regex validators
    ├── views.py                  # Unit 5: page views (Home, Booth Locator, etc.)
    ├── dashboard_views.py        # Custom Admin Dashboard (staff-only)
    ├── urls.py                   # App URLconf (pages + dashboard)
    ├── serializers.py            # DRF serializers
    ├── api_views.py              # DRF API views (Booth/Complaint/Eligibility)
    ├── api_urls.py               # API URLconf
    ├── admin.py
    ├── apps.py
    ├── tests.py                  # Unit tests (no live MongoDB required)
    ├── management/commands/
    │   └── seed_data.py          # `python manage.py seed_data`
    ├── templates/core/
    │   ├── base.html, home.html, booth_locator.html, eligibility_checker.html,
    │   │   registration_guide.html, required_documents.html, complaint_form.html,
    │   │   about.html, 404.html, 500.html
    │   └── dashboard/
    │       ├── dashboard_base.html, login.html, dashboard_home.html,
    │       │   dashboard_booths.html, dashboard_complaints.html,
    │       │   dashboard_users.html, dashboard_stats.html
    └── static/core/
        ├── css/style.css
        ├── js/script.js
        └── img/
```

---

## 4. Installation & Setup

### Prerequisites
- Python 3.10+
- MongoDB installed and running locally (default `localhost:27017`), **or** a MongoDB Atlas connection string
- pip / virtualenv

### Steps

```bash
# 1. Clone / unzip the project and enter the folder
cd voterinfo

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply Django's own migrations (auth/admin/sessions — SQLite)
python manage.py migrate

# 5. Create an admin/staff account (for the Admin Dashboard + /admin/)
python manage.py createsuperuser

# 6. Seed MongoDB with sample polling booth data
python manage.py seed_data

# 7. Run the development server
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** in your browser.

### Running Tests

```bash
python manage.py test core
```

---

## 5. MongoDB Setup

**Option A — Local MongoDB**
1. Install MongoDB Community Server for your OS.
2. Start the service: `mongod` (or via your OS service manager).
3. VoterInfo connects to `mongodb://localhost:27017/voterinfo_db` by default — no further config needed.

**Option B — MongoDB Atlas (cloud)**
Edit `voterinfo/settings.py` and replace the `mongoengine.connect(...)` call:

```python
mongoengine.connect(
    db="voterinfo_db",
    host="mongodb+srv://<username>:<password>@<cluster-url>/voterinfo_db?retryWrites=true&w=majority",
    alias="default",
)
```

Collections used: `polling_booths`, `complaints` (created automatically on first write).

---

## 6. Running the Project

| Command | Purpose |
|---|---|
| `python manage.py runserver` | Start the dev server at `localhost:8000` |
| `python manage.py seed_data` | Populate MongoDB with sample booths |
| `python manage.py createsuperuser` | Create an admin/staff login |
| `python manage.py test core` | Run unit tests |

**Key URLs**

| Page | URL |
|---|---|
| Home | `/` |
| Booth Locator | `/booth-locator/` |
| Eligibility Checker | `/eligibility-checker/` |
| Registration Guide | `/registration-guide/` |
| Required Documents | `/required-documents/` |
| Complaint Form | `/complaint-form/` |
| About | `/about/` |
| Admin Dashboard | `/dashboard/` (staff login required) |
| Django Admin | `/admin/` |

---

## 7. API Documentation

Base URL: `/api/`

### Polling Booth API
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/booths/` | List all booths (paginated) |
| GET | `/api/booths/<pin_code>/` | Get booth(s) by PIN Code |
| POST | `/api/booths/` | Create a booth |
| PUT | `/api/booths/detail/<booth_number>/` | Update a booth |
| DELETE | `/api/booths/detail/<booth_number>/` | Delete a booth |

**Sample POST body:**
```json
{
  "booth_name": "Zilla Parishad Primary School",
  "booth_number": "NSK-101",
  "address": "Trimbak Road, Nashik",
  "pin_code": "422003",
  "officer_name": "Ramesh Patil",
  "contact_number": "9876543210",
  "area_name": "Trimbak"
}
```

### Complaint API
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/complaints/` | File a complaint |
| GET | `/api/complaints/` | List complaints (paginated) |
| PUT | `/api/complaints/<complaint_id>/status/` | Update complaint status |
| DELETE | `/api/complaints/<complaint_id>/` | Delete a complaint |

### Eligibility API
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/eligibility/` | `{ "dob": "2000-01-01", "aadhaar": "123456789012" }` → `{ age, is_eligible, message }` |

All endpoints return JSON and validate input using regex rules (PIN Code: 6 digits, Mobile: 10 digits, Aadhaar: 12 digits).

---

## 8. Code Quality

- PEP 8-compliant, commented, modular code
- Clear separation of concerns: domain logic (`oop_models.py`, `booth_locator.py`) is decoupled from the MongoDB persistence layer (`mongo_models.py`) and from Django views
- Custom exceptions (`InvalidPincodeError`, `BoothNotFoundError`, `MissingRecordError`, `InvalidInputError`) for readable error handling
- Logging configured to console + `voterinfo.log`
- Unit tests cover regex validators, booth lookup, age calculation, and eligibility logic

---

## 9. Future Enhancements

- OTP-based mobile verification for complaint submission
- Integration with real ECI/NVSP APIs (where publicly available)
- Multi-language support (Hindi, regional languages) using Django i18n
- Email/SMS notifications on complaint status updates
- Map-based booth locator with geolocation
- Role-based access control for multiple admin levels (State/District/Booth level)
- Dockerized deployment with docker-compose (Django + MongoDB)

---

## 10. Screenshots

_Add screenshots here after running the project locally, e.g.:_
- `docs/screenshots/home.png`
- `docs/screenshots/booth-locator.png`
- `docs/screenshots/eligibility-checker.png`
- `docs/screenshots/admin-dashboard.png`

---

## 11. License

This project is released for **educational purposes** under the MIT License. See below.

```
MIT License

Copyright (c) 2026 VoterInfo Academic Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```
