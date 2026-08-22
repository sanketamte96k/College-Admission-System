# 🎓 College Management & Administration System

A comprehensive, production-grade **College Management & Administration ERP System** designed to centralize and streamline institutional operations. The platform provides end-to-end administration for student admissions, official enrollment with unique ZPRN generation, department and course management, year-wise and semester-wise academics, attendance tracking, fee collection with ledger generation, examination and grade processing, library transactions with student validation, bus transport management, targeted notice broadcasting, institutional analytics, and system-wide configurations.

[![Version](https://img.shields.io/badge/version-2.0.0--ERP-blue.svg)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.11%2B-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.1.3-black.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/mysql-8.0-orange.svg)](https://www.mysql.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Deployment](https://img.shields.io/badge/deployed_on-Railway-0B0D0E.svg)](https://railway.app/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

---

## 🌐 Live Demo

🚀 **[Live Application](PASTE_RAILWAY_URL_HERE)**

*(Deploy production environment variables via Railway dashboard before accessing the live instance).*

---

## ✨ Key Features

### 🎓 Student & Admission Management
* **Admissions Lifecycle**: Full applicant registration workflow with multi-step validation (Application Submission ➔ Document Verification ➔ Officer Approval / Rejection with Remarks ➔ Fee Payment ➔ Enrollment).
* **Official Student Records**: Seamless promotion of approved applicants into permanent institutional student records.
* **Official ZPRN Identification**: Automatic generation of unique institutional Permanent Registration Numbers (e.g., `124BT10420`, `124IT10892`) upon official admission.
* **Search & Multi-Filter**: Real-time student search and filtering by department, admission category (CAP, Management, NRI), gender, academic year, and status.
* **Academic Organization**: Organizes students by academic year (e.g., `2026-27`), year of study (First Year to Final Year), and semester (1 to 8).
* **Student Self-Service Portal**: Authenticated applicant/student portal for tracking admission progress, updating verified contact information, and viewing academic standings.
* **Document Management**: Secure upload and standardized naming for passport photographs, 10th marksheets, 12th marksheets, and leaving certificates.

### 🏛️ Academic Management
* **Departments**: Complete department administration including department codes, Head of Department (HOD) details, intake capacity, and contact information.
* **Courses & Degree Programs**: Curriculum management across undergraduate (B.Tech) and postgraduate programs, including duration, total semesters, and annual fee allocations.
* **Year & Semester Structure**: Structured curriculum hierarchy mapping courses to academic semesters.
* **Attendance Management**: Daily attendance tracking with bulk upsert capabilities, percentage calculation, and automated low-attendance warnings for records below 75%.
* **Examinations**: Comprehensive exam management supporting Mid-Term, End-Term, and Internal Assessment cycles.
* **Examination Schedules & Subjects**: Subject creation with credit weights and exam scheduling across semesters.
* **Results & Grading**: Marks recording, automatic grade calculation, and semester report generation.

### 💰 Fees & Payments
* **Dynamic Fee Structures**: Program-specific tuition, development, and administrative fee configuration.
* **Student Fee Ledgers**: Individual student financial ledgers tracking total dues, total paid amounts, and remaining balances.
* **Payment Recording**: Support for multiple transaction modes including UPI, Net Banking, Credit/Debit Cards, Demand Draft (DD), and Cash.
* **Payment History & Receipts**: Instant chronological payment history with downloadable official PDF receipts.
* **Automatic Status Updates**: Real-time status transitions (`Pending` ➔ `Partially Paid` ➔ `Paid`) based on cleared dues.
* **Collection Tracking**: Institutional revenue aggregation and fee collection breakdowns across departments.

### 📚 Library Management
* **Book Catalog**: Comprehensive cataloging with ISBN, title, author, category, total copies, available stock, and shelf location.
* **Issue & Return Workflows**: Fast book checkout and check-in workflows.
* **Student Eligibility Validation**: Strict verification restricting book issuance exclusively to officially enrolled students with an active ZPRN.
* **ZPRN Identification**: Real-time validation of student credentials before issuing library assets.
* **Transaction & Fine Tracking**: Automated due date calculations, overdue status alerts, and late return fine processing.

### 🚌 Transport Management
* **Fleet Administration**: Bus profile management including vehicle numbers, capacity, driver contacts, and maintenance tracking.
* **Route Management**: Route definitions with pickup stops, departure timings, and fee structures.
* **Student Transport Passes**: Bus pass allocation linked directly to student records and route capacity.
* **Capacity & Roster Tracking**: Live occupancy metrics per route to prevent overbooking.

### 📢 Notice Management
* **Authoring & Publishing**: Rich notice creation supporting instant publishing, draft mode, and scheduled releases.
* **Audience Segmentation**: Target broadcasts to specific groups (All, Students, Faculty, Staff).
* **Departmental Targeting**: Filter notices for specific departments or broadcast institution-wide.
* **Priority & Pinned Notices**: High-priority alerts and pinned bulletins for urgent institutional announcements.
* **Lifecycle Management**: Auto-expiration, archiving, and deletion controls.

### 📊 Reports & Analytics
* **Executive Dashboard**: High-level institutional metrics and operational summary cards.
* **Student Demographics**: Statistical distribution across gender, admission categories, and departments.
* **Admission Metrics**: Real-time application funnel analytics and conversion trends.
* **Academic Analytics**: Departmental attendance trends, examination pass ratios, and grade distribution.
* **Financial Analytics**: Total fee revenue, pending collections, and payment method breakdowns.
* **Data Export**: Multi-format data exports supporting Excel/CSV and printable PDF documents.

### ⚙️ System Settings
* **General ERP Configuration**: Institution name, college code, official contact details, and branding.
* **Academic Parameters**: Current academic session and semester settings.
* **Administrator Profile & Security**: Admin account management with secure Werkzeug password hashing.
* **Notifications & Mail**: SMTP configuration for automated transactional emails and admission alerts.
* **System Maintenance**: Database connection status, health diagnostics, and operational logs.

---

## 🖥️ Dashboard

The administrative dashboard serves as the central control room, offering real-time visibility into college operations:

* **Total Students**: Active enrolled student headcount across all departments.
* **New Admissions**: Count of newly submitted, verified, and approved applications.
* **Attendance Overview**: Institution-wide attendance rate with highlight on low-attendance alerts.
* **Pending Fees**: Total outstanding fee balances requiring collection.
* **Pending Applications**: Queue of admission applications awaiting verification or approval.
* **Active Departments**: Operational status and student intake utilization per department.
* **Administrative Quick Actions**: Instant shortcuts to verify students, record payments, mark attendance, issue library books, and post notices.
* **Enrollment Analytics**: Interactive Chart.js visual charts displaying monthly admission trends, department distributions, and fee collection summaries.

---

## 🛠️ Tech Stack

| Layer | Technology | Details |
|---|---|---|
| **Frontend** | HTML5, CSS3, JavaScript | Modern Glassmorphism UI, Responsive Grid Layout |
| **Data Visualization** | Chart.js | Interactive charts for analytics and dashboards |
| **Client PDF Export** | jsPDF | Client-side application form & summary PDF export |
| **Backend** | Python 3.11+, Flask 3.1.3 | Modular Application Factory with Flask Blueprints |
| **ORM / Data Layer** | SQLAlchemy 2.0 / Flask-SQLAlchemy 3.1.1 | Pythonic ORM with connection pooling and query optimization |
| **Database** | MySQL 8.0 (PyMySQL 1.1.1) | Relational database with transactional integrity and foreign keys |
| **Server PDF Generation** | ReportLab 5.0.0 | Official downloadable fee receipts and financial statements |
| **Email Service** | Flask-Mail 0.10.0 | Transactional SMTP notifications for admission updates |
| **Security** | Werkzeug 3.1.8 | Secure password hashing, session management & protection |
| **WSGI Server** | Gunicorn 22.0.0 | Production HTTP server with pre-fork worker model |
| **Containerization** | Docker, Docker Compose | Multi-container setup with isolated application and database |
| **Cloud Deployment** | Railway | Production PaaS deployment with automated container builds |
| **Testing** | Pytest, Python unittest | Automated test suite covering all ERP workflows |
| **Version Control** | Git & GitHub | Automated CI/CD workflow via GitHub Actions |

---

## 🏗️ Project Architecture

```mermaid
flowchart TD
    subgraph Clients["User & Administrative Clients"]
        Admin["🏛️ Admin / Staff Browser"]
        Student["🎓 Student / Applicant Browser"]
    end

    subgraph Frontend["Frontend UI Layer (Static & Dynamic)"]
        UI_Pages["HTML5 Templates (Glassmorphism UI)"]
        UI_Scripts["Vanilla JS Controllers (view.js, script.js, student.js)"]
        UI_Charts["Chart.js & jsPDF Engines"]
    end

    subgraph Deployment["Container & Cloud Infrastructure"]
        Railway["☁️ Railway Cloud Platform"]
        Docker["🐳 Docker Container (python:3.11-slim)"]
        Gunicorn["⚡ Gunicorn WSGI Server (4 Workers, 2 Threads)"]
    end

    subgraph Backend["Flask Application Factory (backend/app.py)"]
        AuthBP["🔑 Auth Blueprint"]
        StudentBP["🎓 Student & Admission BP"]
        AcademicBP["🏛️ Dept & Course BP"]
        AttendanceBP["📅 Attendance BP"]
        FeeBP["💰 Fee & Payment BP"]
        ExamBP["📝 Examination BP"]
        LibraryBP["📚 Library BP"]
        TransportBP["🚌 Transport BP"]
        NoticeBP["📢 Notice BP"]
        AnalyticsBP["📊 Analytics BP"]
        SettingBP["⚙️ Settings BP"]
    end

    subgraph Services["Business Logic Layer (Services)"]
        StudentService["Student & ZPRN Service"]
        PaymentService["Payment & Receipt Service"]
        AttendanceService["Attendance Service"]
        LibraryService["Library Service"]
        ExamService["Examination Service"]
        NoticeService["Notice Service"]
        MailService["Flask-Mail Service"]
    end

    subgraph DataLayer["Persistence Layer"]
        ORM["SQLAlchemy ORM (PyMySQL)"]
        MySQL[("🗄️ MySQL 8.0 Database\n(Persistent Volume)")]
    end

    Admin --> UI_Pages
    Student --> UI_Pages
    UI_Pages <--> UI_Scripts
    UI_Scripts <--> UI_Charts

    UI_Scripts -- "REST API (JSON / Multipart)" --> Gunicorn
    Railway --> Docker --> Gunicorn
    Gunicorn --> Backend

    Backend --> Services
    Services --> ORM
    ORM --> MySQL
```

---

## 📁 Project Structure

```text
College-Admission-System/
├── .github/
│   └── workflows/
│       └── main.yml                  # GitHub Actions CI/CD Pipeline
├── backend/
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py                 # Environment configurations (Dev, Prod, Test)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── admin.py                  # Administrator model & authentication
│   │   ├── attendance.py             # Daily attendance records
│   │   ├── course.py                 # Course & degree program models
│   │   ├── database.py               # SQLAlchemy instance
│   │   ├── department.py             # Department specifications & intake
│   │   ├── exam_mark.py              # Subject-wise marks & grades
│   │   ├── examination.py            # Examination sessions & schedules
│   │   ├── library_book.py           # Library catalog & inventory
│   │   ├── library_transaction.py    # Book issue, return & fine records
│   │   ├── notice.py                 # Notices, bulletins & target filters
│   │   ├── payment.py                # Fee transactions & receipts
│   │   ├── seat_matrix.py            # Admission seat allocation
│   │   ├── setting.py                # Institutional & ERP configuration
│   │   ├── student.py                # Student master, admission & ZPRN model
│   │   ├── subject.py                # Academic subjects & credit system
│   │   ├── ticket.py                 # Helpdesk & query tickets
│   │   └── transport.py              # Buses, routes, stops & transport passes
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── admin_erp_routes.py       # ERP dashboard summary endpoints
│   │   ├── ai_routes.py              # Assistant endpoints
│   │   ├── analytics_routes.py       # Dashboard analytics & data export
│   │   ├── attendance_routes.py      # Attendance marking & reporting
│   │   ├── auth_routes.py            # Admin & student session authentication
│   │   ├── course_routes.py          # Course CRUD endpoints
│   │   ├── department_routes.py      # Department CRUD endpoints
│   │   ├── examination_routes.py     # Exam creation, marks entry & results
│   │   ├── library_routes.py         # Book catalog, issue, return & ZPRN validation
│   │   ├── notice_routes.py          # Notice authoring, publish & archive
│   │   ├── payment_routes.py         # Fee records, payment history & PDF receipts
│   │   ├── setting_routes.py         # System configuration endpoints
│   │   ├── student_routes.py         # Admission CRUD, ZPRN & student profiles
│   │   ├── ticket_routes.py          # Support ticket routes
│   │   └── transport_routes.py       # Bus routes, stops & student passes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py             # Assistant computation helpers
│   │   ├── analytics_service.py      # Aggregation logic & statistics
│   │   ├── attendance_service.py     # Attendance business logic & validation
│   │   ├── course_service.py         # Course business logic
│   │   ├── department_service.py     # Department management logic
│   │   ├── email_service.py          # Transactional email dispatcher
│   │   ├── examination_service.py    # Exam scheduling & marks processing
│   │   ├── library_service.py        # Library validation & issue logic
│   │   ├── notice_service.py         # Notice scheduling & broadcasting
│   │   ├── payment_service.py        # Payment reconciliation & ledger
│   │   ├── receipt_service.py        # ReportLab PDF receipt generator
│   │   ├── seat_service.py           # Seat matrix calculator
│   │   ├── setting_service.py        # Configuration persistence
│   │   ├── student_service.py        # Admission workflow & ZPRN generation
│   │   └── transport_service.py      # Fleet, route & pass management
│   ├── tests/
│   │   ├── test_admissions_module.py # Admission module test cases
│   │   ├── test_ai_erp.py            # Integration tests
│   │   ├── test_courses_module.py    # Course module test cases
│   │   ├── test_departments_module.py# Department test cases
│   │   ├── test_erp.py               # Comprehensive ERP workflow test suite
│   │   ├── test_examinations_module.py# Exam & grading tests
│   │   ├── test_fees_module.py       # Fee ledger & payment tests
│   │   ├── test_library_module.py    # Library & ZPRN verification tests
│   │   ├── test_notice_module.py     # Notice lifecycle tests
│   │   ├── test_settings_module.py   # Settings & configuration tests
│   │   ├── test_transport_module.py  # Transport & bus pass tests
│   │   └── test_zprn_generation.py   # Official ZPRN format & uniqueness tests
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── decorators.py             # Authentication & RBAC decorators
│   │   ├── logger.py                 # Rotating file logger setup
│   │   └── validators.py             # Input sanitization & security validators
│   ├── app.py                        # Flask Application Factory
│   └── wsgi.py                       # WSGI entrypoint for Gunicorn
├── frontend/
│   ├── images/                       # UI icons and visual assets
│   ├── index.html                    # Public Student Admission Application Form
│   ├── login.html                    # Administrative Login Portal
│   ├── login.css                     # Dedicated styling for login views
│   ├── student-login.html            # Student & Applicant Login Portal
│   ├── student-dashboard.html        # Student Self-Service Dashboard & Timeline
│   ├── script.js                     # Application form controller & validation
│   ├── student.js                    # Student portal controller
│   ├── style.css                     # Main ERP Glassmorphism design system
│   ├── view.html                     # Administrative Master ERP Portal
│   └── view.js                       # Admin ERP controller & AJAX dispatcher
├── Dockerfile                        # Multi-stage production container image
├── docker-compose.yml                # Multi-container orchestration (Flask + MySQL)
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variables template (Safe for VCS)
├── .gitignore                        # Git exclusion rules
└── README.md                         # Project documentation
```

---

## 🚀 Local Installation & Setup

### 1. Prerequisites
* **Python 3.11+**
* **MySQL Server 8.0+**
* **Git**

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/College-Admission-System.git
cd College-Admission-System
```

### 3. Create & Activate Virtual Environment
```bash
# On Windows:
python -m venv venv
venv\Scripts\activate

# On Linux/macOS:
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create a local `.env` file by copying the template:
```bash
cp .env.example .env
```

Configure your local MySQL credentials inside `.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_local_mysql_password
DB_NAME=college_management_db
SECRET_KEY=your_local_secret_key
FLASK_ENV=dev
```

### 6. Initialize Database & Run Application
Create the MySQL database if it does not already exist:
```sql
CREATE DATABASE college_management_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Start the Flask development server:
```bash
python backend/app.py
```

Or run via the production WSGI entry point:
```bash
python backend/wsgi.py
```

### 7. Access Application in Browser
* **Admission Application Form**: [http://localhost:5000/](http://localhost:5000/)
* **Admin ERP Portal**: [http://localhost:5000/login.html](http://localhost:5000/login.html) *(Default: `admin` / `admin123`)*
* **Student Self-Service Portal**: [http://localhost:5000/student-login.html](http://localhost:5000/student-login.html)

---

## 🐳 Docker Deployment

To run the entire stack (Flask Application + MySQL Database) using Docker Compose:

```bash
docker-compose up --build
```

The application will be accessible at `http://localhost:5000` with the MySQL service orchestrated automatically.

---

## ☁️ Production Deployment (Railway)

The application is fully containerized and production-ready for **Railway**.

### Railway Environment Variables Reference

Configure the following environment variables securely in your Railway project settings:

| Variable Name | Required | Description | Example / Default |
|---|---|---|---|
| `FLASK_ENV` | Yes | Flask execution environment | `prod` |
| `SECRET_KEY` | Yes | Cryptographic key for session signature | `long_random_secure_secret_key` |
| `DATABASE_URL` | Optional | Complete MySQL / PostgreSQL connection string | `mysql+pymysql://user:pass@host:port/dbname` |
| `DB_HOST` | Yes* | MySQL Database hostname (if not using DATABASE_URL) | Provided by Railway MySQL service |
| `DB_PORT` | Yes* | MySQL Database port | `3306` |
| `DB_USER` | Yes* | MySQL Database user | Provided by Railway MySQL service |
| `DB_PASSWORD` | Yes* | MySQL Database password | Provided by Railway MySQL service |
| `DB_NAME` | Yes* | MySQL Database name | `railway` or `college_management_db` |
| `PORT` | Optional | Application listening port (Railway sets automatically) | `5000` |
| `MAIL_SERVER` | Optional | SMTP mail host for notifications | `smtp.gmail.com` |
| `MAIL_PORT` | Optional | SMTP mail port | `587` |
| `MAIL_USE_TLS` | Optional | Enable TLS for email | `True` |
| `MAIL_USERNAME` | Optional | SMTP sender address | `admin@college.edu.in` |
| `MAIL_PASSWORD` | Optional | SMTP app password | `your_smtp_app_password` |

> [!IMPORTANT]
> Never commit actual production database passwords or `SECRET_KEY` to GitHub. Always inject production secrets through Railway's Environment Variables dashboard.

---

## 🧪 Automated Testing

Execute the comprehensive automated test suite covering authentication, admissions, ZPRN generation, fees, attendance, library, examinations, notices, and settings:

```bash
# Run complete ERP test suite
python backend/tests/test_erp.py

# Run ZPRN generation & library validation test suite
python backend/tests/test_zprn_generation.py

# Or execute via pytest
pytest backend/tests/
```

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
