# Enterprise Student Record & Academic Management Platform
### DevOps Foundation, Continuous Integration & Container Orchestration

[![Python 3.11](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Flask 3.0.3](https://img.shields.io/badge/Flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)
[![Pytest 8.2.1](https://img.shields.io/badge/Pytest-8.2.1-yellow.svg)](https://pytest.org/)
[![Docker](https://img.shields.io/badge/Docker-20.10%2B-2496ED.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28%2B-326CE5.svg)](https://kubernetes.io/)
[![Jenkins](https://img.shields.io/badge/Jenkins-CI%2FCD-D33833.svg)](https://www.jenkins.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

---

## 1. Project Overview

The **Enterprise Student Record & Academic Management Platform** is a production-grade, multi-tier academic management system designed to demonstrate modern software engineering and DevOps best practices. Developed as part of Unit 3, this platform adapts and translates the architectural foundations of the *Enterprise Smart Library Management Platform* into an enterprise academic domain.

The platform encapsulates core academic functions:
- Student profile and enrollment lifecycle management.
- Faculty department administration and course instruction assignments.
- Course catalog scheduling and credit management.
- Conflict-aware student course enrollments enforcing strict semester credit caps.
- Letter grade and marks recording with automated **Weighted Grade Point Average (GPA)** quality point calculation.

The end-to-end delivery lifecycle embodies the complete DevOps continuum:
$$\text{Plan} \longrightarrow \text{Develop} \longrightarrow \text{Build} \longrightarrow \text{Test} \longrightarrow \text{Release} \longrightarrow \text{Deploy} \longrightarrow \text{Operate} \longrightarrow \text{Monitor}$$
$$\text{Git / GitHub} \longrightarrow \text{Jenkins CI} \longrightarrow \text{Automated Pytest} \longrightarrow \text{Docker} \longrightarrow \text{Kubernetes (Minikube)}$$

---

## 2. Core Engineering Objectives

1. **Enterprise Shift-Left Quality**: Validate code syntax (`flake8`), business rules, and API endpoints through automated unit and integration tests (`pytest`) before packaging.
2. **Deterministic Builds & Environment Parity**: Eliminate the "Works on My Machine" dilemma by packaging the Flask application into an immutable Docker container image (`student-academic-platform:v1.0.0`).
3. **Continuous Integration as Code**: Implement a declarative Jenkins pipeline (`Jenkinsfile`) automating source checkout, dependency isolation, linting, testing, report publishing, image building, and deployment.
4. **Cloud-Native Resilience & Orchestration**: Deploy across a 3-replica Kubernetes cluster with rolling updates, resource constraints, liveness/readiness health probes, and self-healing guarantees.
5. **Cross-Platform Compatibility**: Provide tested commands for both **Windows 11 (PowerShell)** and **Linux / Ubuntu (WSL2)**.

---

## 3. Technology Stack & Pinned Versions

| Layer / Role | Tool / Technology | Version | Purpose / Role |
| :--- | :--- | :--- | :--- |
| **Runtime Language** | Python | `3.11+` | Core application logic and execution engine |
| **Web Framework** | Flask | `3.0.3` | Lightweight, WSGI web application framework |
| **WSGI Toolkit** | Werkzeug | `3.0.3` | Underlying HTTP utility and routing library |
| **Unit Testing** | Pytest | `8.2.1` | Automated test runner with fixtures |
| **Coverage Analysis** | pytest-cov | `5.0.0` | Test line coverage reporting and metrics |
| **Production Server** | Gunicorn | `22.0.0` | Production WSGI HTTP server |
| **Code Linter** | Flake8 | `7.0.0` | PEP 8 static syntax and code style gate |
| **HTTP Client** | Requests | `2.31.0` | HTTP interaction and integration assertions |
| **Version Control** | Git & GitHub | Distributed | Distributed source versioning and feature-branching |
| **CI Automation** | Jenkins | LTS | Multi-stage declarative automation engine |
| **Container Engine** | Docker Desktop | `20.10+` | OS-level virtualization & container packaging |
| **Orchestration** | Kubernetes / Minikube | `v1.28+` | Declarative container scheduling & self-healing |

---

## 4. Architectural Domain Adaptation Matrix

The platform adapts the reference Library Management case study into the Academic Management domain as specified in the curriculum reference:

| Architectural Component | Trainer Case Study (Library Platform) | Student Implementation (Student Platform) |
| :--- | :--- | :--- |
| **Primary Domain** | Library Catalog & Circulation Desk | Student Records & Academic Grading |
| **Core Database Entities** | Users (Students/Faculty), Books, Loans | Students, Faculty, Courses, Enrollments, Grades |
| **Primary Business Rules** | Quota limit (Max 3 books per student) | **Semester credit limitation (Max 18 credits)** |
| **Conflict Detection** | Duplicate ISBN / out-of-stock inventory | **Schedule time-slot conflict & duplicate enrollment** |
| **Grading / Calculation** | Overdue fine calculation ($0.50/day) | **Weighted GPA calculation ($\sum \text{Pts} \times \text{Credits} / \sum \text{Credits}$)** |
| **Automated Tests** | `test_book_service.py`, `test_borrow_return.py` | `test_student_service.py`, `test_course_service.py`, `test_enrollment.py`, `test_marks_mgmt.py`, `test_api_endpoints.py` |
| **Container Image Tag** | `library-management-platform:v1.0.0` | `student-academic-platform:v1.0.0` |
| **Kubernetes Service** | NodePort: `30080` | **NodePort: `30090`** |

---

## 5. Domain Entities & Business Rules

### 5.1 Domain Models
1. **Student (`app/models/student.py`)**:
   - `student_id`: Unique identifier (e.g., `"S101"`).
   - `name`: Full student name.
   - `email`: Institutional email address (validated format).
   - `department`: Academic department (e.g., `"Computer Science"`).
   - `semester`: Current active semester integer ($\ge 1$).

2. **Faculty (`app/models/faculty.py`)**:
   - `faculty_id`: Unique instructor ID (e.g., `"F101"`).
   - `name`: Instructor full name.
   - `email`: Instructor email address.
   - `department`: Academic department.
   - `title`: Academic rank (e.g., `"Professor"`, `"Associate Professor"`).

3. **Course (`app/models/course.py`)**:
   - `course_id`: Unique catalog code (e.g., `"CS101"`).
   - `course_name`: Official course title.
   - `faculty_id`: Assigned instructor ID (must exist in faculty registry).
   - `credits`: Academic credits between `1` and `6`.
   - `semester`: Scheduled curriculum semester.
   - `schedule`: Time-slot string (e.g., `"Mon 09:00-10:30"`).

4. **Enrollment (`app/models/enrollment.py`)**:
   - `enrollment_id`: Auto-generated unique ID (e.g., `"ENR-0001"`).
   - `student_id`: Enrolled student ID.
   - `course_id`: Enrolled course ID.
   - `semester`: Semester of enrollment.
   - `enrolled_at`: UTC timestamp string.
   - `status`: `"ENROLLED"` or `"DROPPED"`.

5. **Grade (`app/models/grade.py`)**:
   - `grade_id`: Unique grade identifier (e.g., `"GRD-0001"`).
   - `student_id`: Evaluated student ID.
   - `course_id`: Evaluated course ID.
   - `grade`: Letter grade (`"A"`, `"B"`, `"C"`, `"D"`, `"F"`).
   - `grade_points`: Converted numeric quality points (`4.0`, `3.0`, `2.0`, `1.0`, `0.0`).
   - `semester`: Academic semester.

### 5.2 Enterprise Business Rules
- **Rule 1 — Student & Course Pre-existence**: Students and Courses must be validated in the database before enrollment or grading.
- **Rule 2 — Duplicate Enrollment Prevention**: A student cannot enroll in the same course twice while an active enrollment exists. Attempting to do so raises `ValueError` (API returns `409 Conflict`).
- **Rule 3 — 18-Credit Semester Limitation**: A student cannot register for more than **18 academic credits** in a single semester. If adding a course causes the projected semester credits to exceed 18, enrollment is rejected with `ValueError` (API returns `400 Bad Request`).
- **Rule 4 — Schedule Conflict Checking**: A student cannot enroll in two courses in the same semester that share the same schedule time slot (e.g., both meeting `"Mon 09:00-10:30"`). Conflict triggers `ValueError` (API returns `409 Conflict`).
- **Rule 5 — Enrollment Verification for Grades**: Grades can only be recorded for students who have an active enrollment in the target course. Non-enrolled grading attempts are rejected.
- **Rule 6 — Deletion Integrity**: Students with active course enrollments and faculty members assigned to active courses cannot be deleted until registrations or assignments are cleared.

### 5.3 Grading Scale & GPA Calculation Formula
The platform uses the standard 4.0 collegiate grading scale:

| Letter Grade | Quality Points | Performance Descriptor |
| :---: | :---: | :--- |
| **A** | `4.0` | Excellent / Superior |
| **B** | `3.0` | Good / Above Average |
| **C** | `2.0` | Satisfactory / Average |
| **D** | `1.0` | Minimum Passing |
| **F** | `0.0` | Failing / No Credit |

The **Grade Point Average (GPA)** is computed by weighting grade points by course credits:

$$\text{GPA} = \frac{\sum_{i=1}^{N} (\text{GradePoints}_i \times \text{Credits}_i)}{\sum_{i=1}^{N} \text{Credits}_i}$$

*Example*:
- Course 1 (4 Credits, Grade A = 4.0): $4 \times 4.0 = 16.0$ quality points
- Course 2 (4 Credits, Grade B = 3.0): $4 \times 3.0 = 12.0$ quality points
- Course 3 (3 Credits, Grade C = 2.0): $3 \times 2.0 = 6.0$ quality points
- Total Quality Points = $34.0$, Total Credits = $11$
- **$\text{GPA} = 34.0 / 11 = 3.09$** (rounded to 2 decimal places).
- If a student has 0 graded credits, GPA defaults safely to `0.0`.

---

## 6. Project Directory Hierarchy

```
student-academic-platform/
├── app/
│   ├── __init__.py               # Flask Application Factory & UI route
│   ├── routes/
│   │   ├── __init__.py           # Routes package initialization
│   │   └── api.py                # REST API Blueprint (Students, Faculty, Courses, Enrollments, Grades, GPA)
│   ├── services/
│   │   ├── __init__.py           # Service package exports & aliases
│   │   └── student_service.py    # Core business logic, validation & GPA calculation
│   ├── models/
│   │   ├── __init__.py           # Model package exports
│   │   ├── student.py            # Student data model & validation
│   │   ├── faculty.py            # Faculty data model & validation
│   │   ├── course.py             # Course data model & validation
│   │   ├── enrollment.py         # Enrollment record data model
│   │   └── grade.py              # Grade letter & point conversion model
│   └── templates/
│       └── index.html            # Responsive modern web UI dashboard
├── database/
│   ├── __init__.py               # Database package exports
│   └── db.py                     # Thread-safe in-memory singleton data store with seeds
├── tests/
│   ├── __init__.py               # Test package initialization
│   ├── test_student_service.py   # Unit tests: Student CRUD, duplicates, validation
│   ├── test_course_service.py    # Unit tests: Course & Faculty management, credits
│   ├── test_enrollment.py        # Integration tests: 18-credit limit, schedule conflicts
│   ├── test_marks_mgmt.py        # Unit tests: Grade recording & weighted GPA formulas
│   └── test_api_endpoints.py     # HTTP integration tests via Flask test client
├── k8s/
│   ├── deployment.yaml           # Kubernetes Deployment (3 replicas, health probes, resource limits)
│   └── service.yaml              # Kubernetes Service (NodePort 30090)
├── Dockerfile                    # Production multi-layer secure container recipe (non-root)
├── .dockerignore                 # Container build context exclusions
├── .gitignore                    # Git tracking exclusions
├── Jenkinsfile                   # Declarative Multi-Stage CI/CD Pipeline
├── requirements.txt              # Pinned Python package dependencies
├── README.md                     # Comprehensive technical documentation & runbook
└── run.py                        # Local & container server launcher (0.0.0.0:5000)
```

---

## 7. REST API Endpoints Specification

All endpoints are prefixed with `/api`. Request and response payloads use JSON.

### 7.1 Health Endpoint
| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Container & cluster health probe | `200 OK` |

**Response Example**:
```json
{
  "status": "UP",
  "service": "Enterprise Student Record & Academic Management Platform",
  "version": "1.0.0"
}
```

### 7.2 Student Management APIs
| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/students` | List all students (optional `?department=`, `?semester=`, `?q=`) | `200 OK` |
| `POST` | `/api/students` | Register a new student | `201 Created`, `400 Bad Request`, `409 Conflict` |
| `GET` | `/api/students/<student_id>` | Retrieve student by ID | `200 OK`, `404 Not Found` |
| `PUT` | `/api/students/<student_id>` | Update student profile | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/api/students/<student_id>` | Delete student (blocked if active enrollments) | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `GET` | `/api/students/<student_id>/gpa` | Calculate cumulative/semester GPA | `200 OK`, `404 Not Found` |

### 7.3 Faculty Management APIs
| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/faculty` | List faculty members | `200 OK` |
| `POST` | `/api/faculty` | Register a new faculty member | `201 Created`, `400 Bad Request`, `409 Conflict` |
| `GET` | `/api/faculty/<faculty_id>` | Retrieve faculty details | `200 OK`, `404 Not Found` |
| `PUT` | `/api/faculty/<faculty_id>` | Update faculty details | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/api/faculty/<faculty_id>` | Delete faculty (blocked if assigned to courses) | `200 OK`, `400 Bad Request`, `404 Not Found` |

### 7.4 Course Management APIs
| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/courses` | List courses (optional `?semester=`, `?department=`, `?q=`) | `200 OK` |
| `POST` | `/api/courses` | Add a new course | `201 Created`, `400 Bad Request`, `409 Conflict` |
| `GET` | `/api/courses/<course_id>` | Retrieve course details | `200 OK`, `404 Not Found` |
| `PUT` | `/api/courses/<course_id>` | Update course details | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/api/courses/<course_id>` | Delete course (blocked if students enrolled) | `200 OK`, `400 Bad Request`, `404 Not Found` |

### 7.5 Enrollment APIs
| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/enrollments` | List enrollments (optional `?student_id=`, `?course_id=`) | `200 OK` |
| `POST` | `/api/enrollments` | Enroll student (enforces 18-credit cap & conflict) | `201 Created`, `400 Bad Request`, `404 Not Found`, `409 Conflict` |
| `POST` | `/api/enrollments/drop` | Drop an enrolled course | `200 OK`, `400 Bad Request` |

### 7.6 Grade & Marks APIs
| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/grades` | List grades (optional `?student_id=`, `?course_id=`) | `200 OK` |
| `POST` | `/api/grades` | Record grade (validates student enrollment) | `201 Created`, `400 Bad Request`, `404 Not Found` |

---

## 8. Local Setup & Execution Guide

### Option A: Windows 11 (PowerShell)

#### 1. Navigate to Project Directory
```powershell
cd "c:\Users\darsh\OneDrive\Desktop\mini project unit 3\student-academic-platform"
```

#### 2. Create and Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### 3. Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Run Flake8 Code Linting
```powershell
flake8 app/ database/ --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 app/ database/ tests/ --max-line-length=120 --statistics
```

#### 5. Execute Automated Tests with Coverage
```powershell
pytest -v --cov=app --cov-report=term-missing --junitxml=reports/test-results.xml tests/
```

#### 6. Launch Application Locally
```powershell
python run.py
```
Open your browser to:
- **Interactive UI Dashboard**: `http://localhost:5000/`
- **Health Endpoint**: `http://localhost:5000/api/health`
- **Students Endpoint**: `http://localhost:5000/api/students`

---

### Option B: Linux / Ubuntu (WSL2)

#### 1. Navigate to Project Directory
```bash
cd /mnt/c/Users/darsh/OneDrive/Desktop/mini\ project\ unit\ 3/student-academic-platform
```

#### 2. Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Run Flake8 Linter
```bash
flake8 app/ database/ --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 app/ database/ tests/ --max-line-length=120 --statistics
```

#### 5. Run Pytest Suite with JUnit XML & Coverage
```bash
mkdir -p reports
pytest -v --cov=app --cov-report=term-missing --junitxml=reports/test-results.xml tests/
```

#### 6. Run Application
```bash
python3 run.py
# Or with production Gunicorn:
gunicorn --bind 0.0.0.0:5000 run:app
```

---

## 9. Git Version Control & Branch Progression

The project follows the multi-branch progression model outlined in the curriculum reference:

| Branch Name | Feature Scope / Milestones |
| :--- | :--- |
| `feature/foundation` | Base repository structure, `.gitignore`, `.dockerignore`, `requirements.txt`, foundational models |
| `feature/core-app` | In-memory thread-safe database, `StudentService`, REST API routes, HTML dashboard |
| `feature/automated-tests` | Comprehensive pytest suites (services, enrollments, credit caps, GPA, endpoints) |
| `feature/jenkins-ci` | Declarative `Jenkinsfile` pipeline definition with automated gates |
| `feature/dockerization` | Multi-layer production `Dockerfile` with non-root security |
| `feature/kubernetes-orchestration` | Kubernetes `deployment.yaml` (3 replicas) and `service.yaml` (NodePort 30090) |
| `main` | Production-ready integration branch consolidating all merged feature increments |

### Command Sequence to Recreate Git History
```powershell
# Initialize repository
git init
git config user.name "Your Name"
git config user.email "your.email@university.edu"

# Feature 1: Foundation
git checkout -b feature/foundation
git add requirements.txt .gitignore .dockerignore app/models/
git commit -m "feat(foundation): initialize repository, domain models, and dependencies"

# Feature 2: Core Application
git checkout -b feature/core-app
git add database/ app/services/ app/routes/ app/__init__.py app/templates/ run.py
git commit -m "feat(core-app): implement thread-safe DB, student services, REST routes, and UI dashboard"

# Feature 3: Automated Tests
git checkout -b feature/automated-tests
git add tests/
git commit -m "test(automated-tests): add comprehensive pytest suites with credit cap, conflict, and GPA coverage"

# Feature 4: Jenkins CI
git checkout -b feature/jenkins-ci
git add Jenkinsfile
git commit -m "ci(jenkins): add declarative multi-stage CI/CD pipeline with JUnit reporting"

# Feature 5: Dockerization
git checkout -b feature/dockerization
git add Dockerfile
git commit -m "build(docker): add production Dockerfile with non-root user and healthcheck probe"

# Feature 6: Kubernetes Orchestration
git checkout -b feature/kubernetes-orchestration
git add k8s/ README.md
git commit -m "deploy(k8s): add deployment and NodePort service manifests with self-healing"

# Merge to main
git checkout -b main
git merge feature/foundation --no-ff -m "merge: incorporate feature/foundation"
git merge feature/core-app --no-ff -m "merge: incorporate feature/core-app"
git merge feature/automated-tests --no-ff -m "merge: incorporate feature/automated-tests"
git merge feature/jenkins-ci --no-ff -m "merge: incorporate feature/jenkins-ci"
git merge feature/dockerization --no-ff -m "merge: incorporate feature/dockerization"
git merge feature/kubernetes-orchestration --no-ff -m "merge: incorporate feature/kubernetes-orchestration"
```

### Pushing to GitHub (Run Manually)
```bash
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/student-academic-platform.git
git branch -M main
git push -u origin main --all
```
*(No secrets or personal access tokens are stored in this repository).*

---

## 10. Jenkins CI/CD Automation Pipeline

The project includes an enterprise declarative `Jenkinsfile`.

### Pipeline Stages
1. **SCM Checkout**: Checks out the exact Git commit SHA from GitHub.
2. **Environment Setup & Dependencies**: Instantiates an isolated Python 3.11 virtual environment and installs pinned dependencies.
3. **Code Linting & Syntax Gate**: Executes static code analysis via `flake8`. Halts the build immediately if fatal syntax errors (`E9, F63, F7, F82`) or style regressions are detected.
4. **Automated Unit & Integration Tests**: Executes all test suites via `pytest`, generates code coverage metrics, and exports JUnit XML test results to `reports/test-results.xml`.
5. **Build Docker Artifact**: Packages the validated application into an immutable container image tagged `student-academic-platform:v1.0.0` and `student-academic-platform:latest`.
6. **Kubernetes Minikube Deployment**: Applies Kubernetes manifests (`k8s/deployment.yaml`, `k8s/service.yaml`) and verifies rollout status (`kubectl rollout status`).
7. **Post Actions**: Standardized JUnit test result archiving (`reports/test-results.xml`), workspace cleanup (`cleanWs`), and notifications.

---

## 11. Docker Containerization Guide

### 11.1 Build Docker Container Image
```bash
docker build -t student-academic-platform:v1.0.0 .
```

### 11.2 List and Verify Image
```bash
docker images student-academic-platform:v1.0.0
```

### 11.3 Run Container in Background
```bash
docker run -d -p 5000:5000 --name student-container student-academic-platform:v1.0.0
```

### 11.4 Check Running Container Status
```bash
docker ps --filter "name=student-container"
```

### 11.5 Inspect Container Logs
```bash
docker logs -f student-container
```

### 11.6 Verify Healthcheck Probe via cURL
```bash
curl http://localhost:5000/api/health
```

### 11.7 Container Cleanup Commands
```bash
docker stop student-container
docker rm student-container
```

---

## 12. Kubernetes (Minikube) Orchestration Guide

### 12.1 Start Minikube Cluster
```bash
minikube start --driver=docker
```

### 12.2 Reuse Minikube's Docker Daemon
To allow Minikube to access locally built Docker images without pushing to a remote registry:

**On Linux / WSL2 / Git Bash**:
```bash
eval $(minikube docker-env)
docker build -t student-academic-platform:v1.0.0 .
```

**On Windows PowerShell**:
```powershell
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
docker build -t student-academic-platform:v1.0.0 .
```

### 12.3 Apply Kubernetes Manifests
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 12.4 Verify Deployments, Pods, and Services
```bash
# Check Deployment rollout status
kubectl rollout status deployment/student-deployment

# Check 3 Running Pod Replicas
kubectl get pods -l app=student-platform -o wide

# Check NodePort 30090 Service
kubectl get svc student-service
```

### 12.5 Access Application via Minikube
```bash
minikube service student-service --url
```

### 12.6 Demonstrate Kubernetes Self-Healing
Kubernetes continuously reconciles desired state (3 replicas) against actual state. Deleting any pod triggers instant recreation:

```bash
# Delete one active pod
kubectl delete pod $(kubectl get pods -l app=student-platform -o jsonpath='{.items[0].metadata.name}')

# Watch Kubernetes immediately provision a replacement pod in real time
kubectl get pods -l app=student-platform -w
```

### 12.7 Cleanup Kubernetes Resources
```bash
kubectl delete -f k8s/service.yaml
kubectl delete -f k8s/deployment.yaml
minikube stop
```

---

## 13. Troubleshooting & FAQ

| Symptom / Error | Root Cause | Remediation |
| :--- | :--- | :--- |
| `ErrImageNeverPull` / `ImagePullBackOff` | Minikube cannot find `student-academic-platform:v1.0.0` | Run `minikube docker-env` before building image, or set `imagePullPolicy: IfNotPresent`. |
| Port `5000` already in use | Another service is using local port 5000 | Kill process: `Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess \| Stop-Process` or use `PORT=5001 python run.py`. |
| NodePort `30090` not reachable directly | Docker driver on Windows/macOS uses an internal VM network | Run `minikube service student-service` to establish a tunnel directly to the service. |
| Flake8 line length errors | Line length exceeds maximum threshold | Run `flake8 app/ database/ tests/ --max-line-length=120`. |

---

## 14. Academic Deliverables & Verification Checklist

- [x] **Repository Architecture**: Complete Flask application factory with models, services, routes, templates, and thread-safe DB.
- [x] **Academic Domain Model**: Student, Faculty, Course, Enrollment, and Grade entities with full validation.
- [x] **Credit Limit Enforcement**: Strict 18-credit per semester maximum with automated tests.
- [x] **Schedule Conflict Checking**: Automatic collision detection for courses sharing time slots.
- [x] **Weighted GPA Calculator**: Standard $A=4, B=3, C=2, D=1, F=0$ scale with credit weighting.
- [x] **REST API Blueprint**: Health check, Student, Faculty, Course, Enrollment, Grade, and GPA endpoints with appropriate HTTP status codes (`200`, `201`, `400`, `404`, `409`).
- [x] **Automated Test Suite**: 24+ Pytest unit and integration tests with coverage reporting.
- [x] **Declarative Jenkins Pipeline**: Multi-stage `Jenkinsfile` with Flake8, Pytest, Docker, and Kubernetes stages.
- [x] **Production Dockerfile**: Python 3.11-slim base, non-root user `appuser`, healthcheck probe.
- [x] **Kubernetes Manifests**: 3-replica Deployment with rolling updates and NodePort `30090` service.
- [x] **Cross-Platform Compatibility**: Validated on Windows 11 and WSL2/Linux.
