# Zeal College Admission Management ERP System 🎓

A production-grade, enterprise-ready **College Admission Management ERP System** built with Flask, MySQL, SQLAlchemy, HTML5, CSS3, and JavaScript.

![Version](https://img.shields.io/badge/version-2.0.0--ERP-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-green.svg)
![Flask](https://img.shields.io/badge/flask-3.1.3-black.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)

---

## 🚀 System Overview & Features

* **Admin Portal & Authentication**: Secure Werkzeug password hashing, Flask session protection, 30-min session timeout, and Remember Me support (30-day session). Default admin: `admin` / `admin123`.
* **Student Portal & Status Tracking**: Applicants log in using **Application ID** and **Date of Birth** to view admission progress across a 5-step timeline (**Submitted ➔ Documents Verified ➔ Officer Approval ➔ Fee Payment ➔ Confirmed**).
* **Restricted Profile Editing**: Students can update only contact information (mobile, email, address); academic marks and course details remain strictly immutable.
* **Document Upload & Storage System**: Auto-renames files to `studentID_docname.ext` for Passport Photos, 10th Marksheets, 12th Marksheets, and Leaving Certificates.
* **Professional PDF Generator**: Client-side A4 PDF generator using `jsPDF` featuring college branding, passport photo embedding, structured data grids, document checklists, and signature blocks (`Admission_<StudentName>.pdf`).
* **Analytics Dashboard**: 6 Top Metric Cards, 4 Interactive `Chart.js` charts (Department Bar, Gender Ratio Doughnut, 6-Month Line Trend, Admission Type Pie), Key Statistics panel, and real-time AJAX updates.
* **Excel Data Export**: Client-side CSV/Excel exporter.
* **Email Notification System**: `Flask-Mail` integration sending responsive HTML confirmation emails to students (**Pending Verification**) and instant alerts to administrators (`ADMIN_EMAIL`) with graceful fallback if SMTP is offline.
* **Multi-Filter & Pagination**: Live search by name, department, admission type, and gender dropdown filters with paginated REST API support (`GET /api/students?page=1&limit=10`).
* **Security & Hardening**: XSS sanitization, SQL Injection prevention via SQLAlchemy ORM, security headers (`X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`), IP rate limiting, and rotating file logging (`logs/app.log`, `logs/error.log`).

---

## 📂 Architecture & Directory Structure

```
College-Admission-System/
├── backend/
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py               # Development, Production & Testing configs
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py             # SQLAlchemy instance
│   │   ├── admin.py                # Admin model & password hashing
│   │   └── student.py              # Student model & status field
│   ├── services/
│   │   ├── __init__.py
│   │   ├── email_service.py        # Flask-Mail HTML notifications
│   │   ├── student_service.py      # Student CRUD & validation logic
│   │   └── analytics_service.py    # Analytics computation logic
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py          # Admin & Student authentication endpoints
│   │   ├── student_routes.py       # Student CRUD & profile endpoints
│   │   └── analytics_routes.py    # Analytics & dashboard endpoints
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── decorators.py           # Auth decorators (@admin_required, @student_required)
│   │   ├── validators.py           # XSS sanitization & IP rate limiting
│   │   └── logger.py               # Rotating file logging setup
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_erp.py             # Automated unit & integration test suite
│   ├── app.py                      # Flask Application Factory & Blueprints
│   ├── wsgi.py                     # Production WSGI launcher (Gunicorn / Waitress)
│   └── uploads/                    # Secure student document storage
├── frontend/                       # Static assets & HTML templates
│   ├── index.html                  # Admission Application Form
│   ├── view.html                   # Admin Management Portal & Analytics Dashboard
│   ├── login.html                  # Admin Login Page
│   ├── student-login.html          # Student Login Page
│   ├── student-dashboard.html      # Student Status Portal & Timeline
│   ├── script.js                   # Application Form Handler
│   ├── view.js                     # Admin Portal & Chart.js Controller
│   ├── student.js                  # Student Portal Controller
│   └── style.css                   # Global UI & Glassmorphism Design System
├── Dockerfile                      # Production Docker Build Specification
├── docker-compose.yml              # Multi-container orchestration (Flask + MySQL)
├── requirements.txt                # Python Production Dependencies
└── README.md                       # Complete System Documentation
```

---

## 🛠️ Installation & Setup Guide

### 1. Prerequisites
- Python 3.11+
- MySQL Server 8.0+
- Git

### 2. Clone Repository & Environment Setup
```bash
git clone https://github.com/your-username/College-Admission-System.git
cd College-Admission-System
```

### 3. Virtual Environment & Dependencies
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Database Setup
Create MySQL Database:
```sql
CREATE DATABASE college_admission_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Set Environment Variables (or create `.env` file):
```env
FLASK_ENV=dev
SECRET_KEY=zeal_college_production_erp_secret_2026
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=YourPassword@123
MYSQL_DB=college_admission_db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=admin@zeal.edu.in
MAIL_PASSWORD=your_app_password
```

### 5. Run Application
```bash
python backend/app.py
```
Access in Browser:
- Admission Form: `http://localhost:5000/`
- Admin Portal: `http://localhost:5000/login.html` (Username: `admin`, Password: `admin123`)
- Student Portal: `http://localhost:5000/student-login.html`

---

## 📡 REST API Documentation

### Authentication APIs
* `POST /api/login`: Admin sign in (`username`, `password`, `remember`).
* `POST /api/logout`: Destroy admin session.
* `POST /api/student-login`: Student portal sign in (`application_id`, `dob`).
* `POST /api/student-logout`: Destroy student session.
* `GET /api/check-auth`: Verify current session status & user type.

### Student Management APIs
* `GET /api/students`: Fetch paginated student records (`?page=1&limit=10&search=john&dept=Computer+Engineering`).
* `GET /api/students/<id>`: Fetch full single student details by ID.
* `POST /api/students`: Submit new admission application form with multipart document uploads.
* `PUT /api/students/<id>`: Update existing student record & replace uploaded documents.
* `DELETE /api/students/<id>`: Delete student record & cleanup associated files from `backend/uploads/`.

### Student Portal APIs
* `GET /api/student/profile`: Fetch authenticated student's profile details.
* `PUT /api/student/profile`: Update contact details (`mobile`, `altMobile`, `email`, `address`, `city`, `state`, `pincode`). Rejects attempts to edit marks or department.

### Analytics API
* `GET /api/dashboard`: Fetch total counts, department stats, gender ratios, monthly trends, and averages.

---

## 🗄️ Database Schema

### `students` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INT | Primary Key, Auto Increment | Application ID |
| `fullName` | VARCHAR(100) | NOT NULL | Student Full Name |
| `fatherName` | VARCHAR(100) | NOT NULL | Father's Name |
| `motherName` | VARCHAR(100) | NOT NULL | Mother's Name |
| `dob` | VARCHAR(20) | NOT NULL | Date of Birth (YYYY-MM-DD) |
| `gender` | VARCHAR(20) | NOT NULL | Gender |
| `bloodGroup` | VARCHAR(10) | NOT NULL | Blood Group |
| `mobile` | VARCHAR(20) | NOT NULL | Mobile Number |
| `altMobile` | VARCHAR(20) | NULL | Alternate Mobile |
| `email` | VARCHAR(100) | NOT NULL | Email Address |
| `aadhaar` | VARCHAR(20) | NOT NULL | Aadhaar Number |
| `address` | TEXT | NOT NULL | Residential Address |
| `city` | VARCHAR(50) | NOT NULL | City |
| `state` | VARCHAR(50) | NOT NULL | State |
| `pincode` | VARCHAR(10) | NOT NULL | Pincode |
| `nationality` | VARCHAR(50) | NOT NULL | Nationality |
| `board10` | VARCHAR(100) | NOT NULL | 10th Board Name |
| `percentage10` | FLOAT | NOT NULL | 10th Percentage |
| `board12` | VARCHAR(100) | NOT NULL | 12th Board Name |
| `percentage12` | FLOAT | NOT NULL | 12th Percentage |
| `entranceExam` | VARCHAR(50) | NOT NULL | Entrance Exam Name |
| `entranceScore` | FLOAT | NOT NULL | Entrance Exam Score |
| `department` | VARCHAR(100) | NOT NULL | Academic Department |
| `admissionType` | VARCHAR(50) | NOT NULL | CAP / Management / NRI |
| `photo` | VARCHAR(255) | NULL | Passport Photo Filename |
| `marksheet10` | VARCHAR(255) | NULL | 10th Marksheet Filename |
| `marksheet12` | VARCHAR(255) | NULL | 12th Marksheet Filename |
| `leavingCertificate` | VARCHAR(255) | NULL | Leaving Certificate Filename |
| `status` | VARCHAR(50) | DEFAULT 'Pending Verification' | Admission Status |
| `created_at` | DATETIME | DEFAULT Current Timestamp | Registration Timestamp |

### `admins` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INT | Primary Key, Auto Increment | Admin ID |
| `username` | VARCHAR(50) | Unique, NOT NULL | Login Username |
| `email` | VARCHAR(100) | Unique, NOT NULL | Admin Email |
| `password_hash` | VARCHAR(255) | NOT NULL | Hashed Password (Werkzeug) |
| `created_at` | DATETIME | DEFAULT Current Timestamp | Account Creation Timestamp |

---

## 🐳 Docker & Cloud Deployment Guide

### Docker Compose Deployment
Run multi-container app + MySQL database locally:
```bash
docker-compose up --build -d
```

### Deploy to Render / Railway
1. Push project repository to GitHub.
2. Create a **Web Service** on Render or Railway.
3. Connect repository and configure build parameters:
   - **Environment**: Python / Docker
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT backend.wsgi:app`
4. Set Environment Variables (`MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`, `SECRET_KEY`).

### Deploy to PythonAnywhere
1. Upload code or clone repository via Web Console.
2. Create virtual environment and install `requirements.txt`.
3. In PythonAnywhere **Web** tab, configure WSGI file pointing to `backend/wsgi.py`.
4. Reload app.

---

## 🧪 Testing

Execute automated unit & integration test suite:
```bash
python backend/tests/test_erp.py
```

---

## 📄 License
This project is licensed under the **MIT License**.
