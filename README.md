# 📝 FormBuilder

> A Django-based platform for creating dynamic forms, building multi-step workflows, collecting responses, and generating reports and analytics.

FormBuilder is a collaborative web application built with **Django** and **Django REST Framework**.

The project provides a platform where users can create customizable forms, organize forms into multi-step processes, share public or password-protected forms and processes, collect submissions, and analyze collected data through reporting APIs.

---

## 🎯 Project Overview

FormBuilder is built around four main concepts:

```text
                 ┌──────────────┐
                 │     User     │
                 └──────┬───────┘
                        │
              ┌─────────┴─────────┐
              ↓                   ↓
        ┌───────────┐       ┌───────────┐
        │   Forms   │       │ Processes │
        └─────┬─────┘       └─────┬─────┘
              │                   │
              ↓                   ↓
        ┌───────────┐       ┌───────────┐
        │ Questions │       │   Steps   │
        └─────┬─────┘       └─────┬─────┘
              │                   │
              └─────────┬─────────┘
                        ↓
                ┌──────────────┐
                │ Submissions  │
                └──────┬───────┘
                       ↓
                ┌──────────────┐
                │   Reports    │
                └──────────────┘
```

A form can contain multiple questions, while a process can combine multiple forms into an ordered workflow.

---

# ✨ Main Features

## 📋 Dynamic Forms

Authenticated users can create and manage their own forms.

Each form supports:

* Title and description
* Categories
* Public or private access
* Optional password protection
* Unique slug
* Questions
* Question ordering
* Soft deletion

Forms automatically receive a unique slug based on their title, allowing them to be accessed through a readable URL.

Forms and questions are owned by their creator, and authenticated API operations are restricted accordingly.

---

## ❓ Questions

Forms can contain multiple questions.

Each question supports:

* Question title
* Question type
* Required / optional state
* Ordering
* Question options
* Automatic ordering when no order is provided

Question ordering is enforced per form, preventing duplicate positions within the same form.

---

## 🗂️ Categories

Users can create categories and assign forms or processes to them.

Categories provide a way to organize larger numbers of forms and processes.

Each category belongs to its creator, and users can only manage their own categories.

---

# 🔄 Process Management

A process allows multiple forms to be combined into an ordered workflow.

For example:

```text
Process
   │
   ├── Step 1 → Personal Information Form
   │
   ├── Step 2 → Address Form
   │
   ├── Step 3 → Additional Information Form
   │
   └── Step 4 → Confirmation Form
```

Each process supports:

* Title
* Description
* Categories
* Process type
* Public/private access
* Optional password protection
* Ordered process steps
* Soft deletion

A form can be reused in different processes while maintaining a defined order inside each process.

---

# 🔐 Public & Private Access

Forms and processes can be configured as either public or private.

### Public

Public resources can be accessed without providing a password.

### Private

Private resources require the correct password before access is granted.

Passwords are stored using Django's password hashing utilities rather than being stored as plain text.

Form access can also generate a temporary JWT-based access token for independent private form access.

---

# 📥 Submissions & Process Execution

The submission system handles the actual execution of processes and collection of form responses.

### Process Execution

A `ProcessExecution` represents a user's execution of a process.

It tracks:

* Process
* User
* Execution status
* Current step
* Start time
* Completion time

An active user cannot have multiple simultaneous executions of the same process.

### Form Submission

Each `FormSubmission` represents a completed or submitted form within an execution.

It stores:

* Form
* Process execution
* User
* Submitter IP
* Submission time
* Review status

The system prevents duplicate submissions of the same form within a process execution.

---

# 📝 Answers

Answers are stored separately from form submissions.

Each answer is connected to:

```text
FormSubmission
      │
      └── Answer
             │
             └── Question
```

The system supports multiple answer storage formats:

* Text
* Number
* JSON

Database constraints ensure that an answer contains exactly one of these value types.

---

# 📊 Reports & Analytics

The project includes a reporting layer for analyzing forms and processes.

Current reporting functionality includes:

### Form Reports

Provides information such as:

* Form title
* Submission count
* Visit count

### Process Reports

Provides:

* Process title
* Response count
* Visit count

### Submission Reports

Provides submitted responses organized by question.

### Question Aggregation

The system can calculate different types of statistics depending on the question type.

For example:

```text
Numeric Questions
    ├── Average
    ├── Minimum
    └── Maximum

Choice Questions
    ├── Option A → 42
    ├── Option B → 27
    └── Option C → 11
```

Reporting responses are cached to reduce repeated database calculations.

---

# 📈 Visit Tracking

FormBuilder tracks visits to forms and processes.

Visit logs store:

* Visited object
* Visitor
* Visitor IP
* Visit timestamp

The reporting system uses these logs to calculate visit statistics for forms and processes.

---

# ⏰ Scheduled Reports

The project also includes a scheduled-report model supporting different reporting frequencies:

* Daily
* Weekly
* Monthly

Scheduled reports can be associated with either forms or processes.

---

# 🔐 Authentication

FormBuilder includes a custom user authentication system.

The custom `User` model extends Django's `AbstractUser` and adds:

* Phone number
* Email
* Birth date

The authentication API supports:

* User registration
* Phone number validation
* OTP generation
* OTP verification
* OTP expiration
* OTP rate limiting
* Username/password login
* Token authentication
* Profile retrieval
* Profile update
* Logout

OTP verification is connected to the registration flow so that a user must have a recently verified phone number before completing registration.

---

# 🔌 REST API

The backend is built around Django REST Framework.

Current API namespaces are:

```text
/api/accounts/
/api/form/
/api/process/
/api/submission/
/api/reports/
```

These correspond to the main application domains of the project.

### Authentication

```text
POST   /api/accounts/send-otp/
POST   /api/accounts/verify-otp/
POST   /api/accounts/register/
POST   /api/accounts/login/
POST   /api/accounts/logout/

GET    /api/accounts/profile/
PATCH  /api/accounts/profile/update/
```

### Forms

```text
GET/POST    /api/form/categories/
GET/PUT/DELETE /api/form/categories/<id>/

GET/POST    /api/form/forms/
GET/PUT/DELETE /api/form/forms/<id>/

POST        /api/form/<slug>/access/
GET         /api/form/<slug>/

GET/POST    /api/form/forms/<form_id>/questions/
GET/PUT/DELETE /api/form/questions/<id>/
```

### Processes

```text
GET/POST    /api/process/processes/
GET/PUT/DELETE /api/process/processes/<id>/

GET/POST    /api/process/processes/<process_id>/steps/
GET/PUT/DELETE /api/process/processes/<process_id>/steps/<id>/

POST        /api/process/access/<process_id>/
```

### Submissions

The submission application uses Django REST Framework ViewSets and routers:

```text
/api/submission/executions/
/api/submission/submissions/
```

Both process executions and submissions support creation, listing, and retrieval. Form submissions can also be marked as reviewed by the form creator.

### Reports

```text
GET/POST /api/reports/scheduled-reports/
GET      /api/reports/visit-logs/

GET      /api/reports/forms/<form_id>/
GET      /api/reports/forms/<form_id>/submissions/
GET      /api/reports/forms/<form_id>/aggregates/

GET      /api/reports/process/<process_id>/
```

---

# 🏗️ Project Architecture

The project is divided into separate Django applications based on domain responsibilities:

```text
FormBuilder/
│
├── FormBuilder/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── user/
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── form/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   └── urls.py
│
├── process/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── submission/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── constants.py
│   └── urls.py
│
├── reports/
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── views.py
│   └── urls.py
│
├── documents/
│
├── manage.py
├── requirements.txt
└── README.md
```

---

# 🛠️ Technology Stack

| Technology                   | Usage                           |
| ---------------------------- | ------------------------------- |
| Python                       | Backend programming             |
| Django 6.1.1                 | Web framework                   |
| Django REST Framework 3.18.1 | REST API                        |
| SQLite                       | Development database            |
| Django Token Authentication  | API authentication              |
| JWT                          | Temporary protected form access |
| Django Cache                 | Report caching                  |
| Git                          | Version control                 |
| GitHub                       | Collaboration                   |

The current project configuration uses SQLite and Django's local-memory cache during development.

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/ShayanNsA/FormBuilder.git
cd FormBuilder
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

The current requirements include Django 6.1.1 and Django REST Framework 3.18.1.

---

## 4. Apply migrations

```bash
python manage.py migrate
```

---

## 5. Create a superuser

```bash
python manage.py createsuperuser
```

---

## 6. Run the development server

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

---

# 🧪 Testing

The project contains automated tests, including authentication API tests.

Run all tests:

```bash
python manage.py test
```

Or run tests for a specific application:

```bash
python manage.py test user
```

---

# 🔒 Security Considerations

The project currently uses token authentication for protected REST API endpoints.

Additional security-related functionality includes:

* Password hashing
* OTP expiration
* OTP rate limiting
* User-specific resource access
* Protected authenticated endpoints
* Password-protected forms and processes
* Temporary JWT access tokens

The current repository configuration is intended for development and should be hardened before production deployment. In particular, production deployment should use a secure secret key, disable debug mode, configure allowed hosts, and use a production-ready database and cache.

---

# 🗺️ Project Roadmap

The project is under active development.

Potential future improvements include:

* Enhanced form builder UI
* More question types
* More advanced workflow capabilities
* Guest submission improvements
* Advanced analytics
* Scheduled report execution
* Report exports
* Improved frontend experience
* Production database configuration
* Production caching
* API documentation
* Deployment configuration

---

# 👥 Team Project

FormBuilder is being developed as a collaborative project.

The project is structured into independent Django applications so that different team members can work on different parts of the system while keeping responsibilities separated.

The main application domains are:

```text
User
 │
 ├── Form
 │    └── Question
 │
 ├── Process
 │    └── ProcessStep
 │
 ├── Submission
 │    ├── ProcessExecution
 │    ├── FormSubmission
 │    └── Answer
 │
 └── Reports
      ├── Visit Logs
      ├── Form Reports
      └── Process Reports
```

---

# 📌 Project Status

🚧 **FormBuilder is currently under active development.**

The core backend architecture, user authentication, form management, process management, submission handling, and reporting components are currently implemented and are being continuously improved.

The project is evolving toward a complete platform for building dynamic forms and multi-step workflows, collecting responses, and extracting useful information from the collected data.

---

## 💡 Vision

FormBuilder aims to make building digital forms and workflows simple and reusable.

Instead of developing a separate system for every questionnaire, registration process, survey, or workflow, users should be able to build what they need using the platform itself.

```text
Create
  ↓
Customize
  ↓
Connect
  ↓
Share
  ↓
Collect
  ↓
Analyze
```

### FormBuilder

**Build forms. Create workflows. Collect data. Generate insights.**
