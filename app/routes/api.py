"""REST API Endpoints for Student Record & Academic Management Platform."""
from flask import Blueprint, request, jsonify
from app.services.student_service import (
    StudentService,
    FacultyService,
    CourseService,
    EnrollmentService,
    GradeService
)

api_bp = Blueprint("api", __name__)


# ---------------------------------------------------------
# Health Check Endpoint (Liveness / Readiness for K8s & Docker)
# ---------------------------------------------------------
@api_bp.route("/health", methods=["GET"])
def healthcheck():
    """Liveness and readiness endpoint for Kubernetes & Docker healthchecks."""
    return jsonify({
        "status": "UP",
        "service": "Enterprise Student Record & Academic Management Platform",
        "version": "1.0.0"
    }), 200


# ---------------------------------------------------------
# Student Management APIs
# ---------------------------------------------------------
@api_bp.route("/students", methods=["GET"])
def list_students():
    """Retrieve list of students with optional query filters."""
    dept = request.args.get("department")
    sem = request.args.get("semester")
    q = request.args.get("q")
    semester_val = int(sem) if sem and sem.isdigit() else None

    students = StudentService.list_students(department=dept, semester=semester_val, query=q)
    return jsonify({"count": len(students), "students": students}), 200


@api_bp.route("/students", methods=["POST"])
def register_student():
    """Register a new student."""
    data = request.get_json() or {}
    try:
        student = StudentService.add_student(
            student_id=data.get("student_id"),
            name=data.get("name"),
            email=data.get("email"),
            department=data.get("department"),
            semester=data.get("semester", 1)
        )
        return jsonify({"message": "Student registered successfully", "student": student}), 201
    except ValueError as e:
        err = str(e)
        status_code = 409 if "already exists" in err.lower() else 400
        return jsonify({"error": err}), status_code
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@api_bp.route("/students/<student_id>", methods=["GET"])
def get_student(student_id):
    """Retrieve a single student by student_id."""
    student = StudentService.get_student(student_id)
    if not student:
        return jsonify({"error": f"Student '{student_id}' not found."}), 404
    return jsonify(student), 200


@api_bp.route("/students/<student_id>", methods=["PUT"])
def update_student(student_id):
    """Update student record."""
    data = request.get_json() or {}
    try:
        student = StudentService.update_student(
            student_id=student_id,
            name=data.get("name"),
            email=data.get("email"),
            department=data.get("department"),
            semester=data.get("semester")
        )
        return jsonify({"message": "Student updated successfully", "student": student}), 200
    except ValueError as e:
        err = str(e)
        if "not found" in err.lower():
            return jsonify({"error": err}), 404
        status_code = 409 if "already exists" in err.lower() else 400
        return jsonify({"error": err}), status_code


@api_bp.route("/students/<student_id>", methods=["DELETE"])
def delete_student(student_id):
    """Delete a student record."""
    try:
        StudentService.delete_student(student_id)
        return jsonify({"message": f"Student '{student_id}' deleted successfully."}), 200
    except ValueError as e:
        err = str(e)
        if "not found" in err.lower():
            return jsonify({"error": err}), 404
        return jsonify({"error": err}), 400


@api_bp.route("/students/<student_id>/gpa", methods=["GET"])
def get_student_gpa(student_id):
    """Calculate and return cumulative or semester GPA for a student."""
    sem = request.args.get("semester")
    semester_val = int(sem) if sem and sem.isdigit() else None
    try:
        gpa_record = GradeService.calculate_gpa(student_id=student_id, semester=semester_val)
        return jsonify(gpa_record), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


# ---------------------------------------------------------
# Faculty Management APIs
# ---------------------------------------------------------
@api_bp.route("/faculty", methods=["GET"])
def list_faculty():
    """Retrieve list of faculty instructors."""
    dept = request.args.get("department")
    faculty_list = FacultyService.list_faculty(department=dept)
    return jsonify({"count": len(faculty_list), "faculty": faculty_list}), 200


@api_bp.route("/faculty", methods=["POST"])
def register_faculty():
    """Register a new faculty instructor."""
    data = request.get_json() or {}
    try:
        faculty = FacultyService.add_faculty(
            faculty_id=data.get("faculty_id"),
            name=data.get("name"),
            email=data.get("email"),
            department=data.get("department"),
            title=data.get("title", "Professor")
        )
        return jsonify({"message": "Faculty registered successfully", "faculty": faculty}), 201
    except ValueError as e:
        err = str(e)
        status_code = 409 if "already exists" in err.lower() else 400
        return jsonify({"error": err}), status_code


@api_bp.route("/faculty/<faculty_id>", methods=["GET"])
def get_faculty(faculty_id):
    """Retrieve faculty instructor details."""
    faculty = FacultyService.get_faculty(faculty_id)
    if not faculty:
        return jsonify({"error": f"Faculty '{faculty_id}' not found."}), 404
    return jsonify(faculty), 200


@api_bp.route("/faculty/<faculty_id>", methods=["PUT"])
def update_faculty(faculty_id):
    """Update faculty instructor details."""
    data = request.get_json() or {}
    try:
        faculty = FacultyService.update_faculty(
            faculty_id=faculty_id,
            name=data.get("name"),
            email=data.get("email"),
            department=data.get("department"),
            title=data.get("title")
        )
        return jsonify({"message": "Faculty updated successfully", "faculty": faculty}), 200
    except ValueError as e:
        err = str(e)
        if "not found" in err.lower():
            return jsonify({"error": err}), 404
        status_code = 409 if "already exists" in err.lower() else 400
        return jsonify({"error": err}), status_code


@api_bp.route("/faculty/<faculty_id>", methods=["DELETE"])
def delete_faculty(faculty_id):
    """Delete a faculty instructor."""
    try:
        FacultyService.delete_faculty(faculty_id)
        return jsonify({"message": f"Faculty '{faculty_id}' deleted successfully."}), 200
    except ValueError as e:
        err = str(e)
        if "not found" in err.lower():
            return jsonify({"error": err}), 404
        return jsonify({"error": err}), 400


# ---------------------------------------------------------
# Course Management APIs
# ---------------------------------------------------------
@api_bp.route("/courses", methods=["GET"])
def list_courses():
    """Retrieve catalog courses."""
    dept = request.args.get("department")
    sem = request.args.get("semester")
    q = request.args.get("q")
    semester_val = int(sem) if sem and sem.isdigit() else None

    courses = CourseService.list_courses(semester=semester_val, department=dept, query=q)
    return jsonify({"count": len(courses), "courses": courses}), 200


@api_bp.route("/courses", methods=["POST"])
def add_course():
    """Add a new course to the curriculum."""
    data = request.get_json() or {}
    try:
        course = CourseService.add_course(
            course_id=data.get("course_id"),
            course_name=data.get("course_name"),
            faculty_id=data.get("faculty_id"),
            credits=int(data.get("credits", 3)),
            semester=int(data.get("semester", 1)),
            schedule=data.get("schedule", "TBA")
        )
        return jsonify({"message": "Course added successfully", "course": course}), 201
    except ValueError as e:
        err = str(e)
        status_code = 409 if "already exists" in err.lower() else 400
        return jsonify({"error": err}), status_code


@api_bp.route("/courses/<course_id>", methods=["GET"])
def get_course(course_id):
    """Retrieve course details."""
    course = CourseService.get_course(course_id)
    if not course:
        return jsonify({"error": f"Course '{course_id}' not found."}), 404
    return jsonify(course), 200


@api_bp.route("/courses/<course_id>", methods=["PUT"])
def update_course(course_id):
    """Update course attributes."""
    data = request.get_json() or {}
    try:
        course = CourseService.update_course(
            course_id=course_id,
            course_name=data.get("course_name"),
            faculty_id=data.get("faculty_id"),
            credits=data.get("credits"),
            semester=data.get("semester"),
            schedule=data.get("schedule")
        )
        return jsonify({"message": "Course updated successfully", "course": course}), 200
    except ValueError as e:
        err = str(e)
        if "not found" in err.lower():
            return jsonify({"error": err}), 404
        return jsonify({"error": err}), 400


@api_bp.route("/courses/<course_id>", methods=["DELETE"])
def delete_course(course_id):
    """Delete a course from catalog."""
    try:
        CourseService.delete_course(course_id)
        return jsonify({"message": f"Course '{course_id}' deleted successfully."}), 200
    except ValueError as e:
        err = str(e)
        if "not found" in err.lower():
            return jsonify({"error": err}), 404
        return jsonify({"error": err}), 400


# ---------------------------------------------------------
# Enrollment Management APIs
# ---------------------------------------------------------
@api_bp.route("/enrollments", methods=["GET"])
def list_enrollments():
    """Retrieve course enrollments."""
    sid = request.args.get("student_id")
    cid = request.args.get("course_id")
    sem = request.args.get("semester")
    semester_val = int(sem) if sem and sem.isdigit() else None

    enrollments = EnrollmentService.list_enrollments(
        student_id=sid, course_id=cid, semester=semester_val
    )
    return jsonify({"count": len(enrollments), "enrollments": enrollments}), 200


@api_bp.route("/enrollments", methods=["POST"])
def enroll_student():
    """Enroll a student in a course with validation of duplicate, credit limit, and conflict."""
    data = request.get_json() or {}
    sid = data.get("student_id")
    cid = data.get("course_id")
    if not sid or not cid:
        return jsonify({"error": "student_id and course_id are required fields."}), 400

    try:
        enrollment = EnrollmentService.enroll_student(student_id=sid, course_id=cid)
        return jsonify({"message": "Enrollment successful", "enrollment": enrollment}), 201
    except ValueError as e:
        err = str(e)
        # 404 if student or course doesn't exist
        if "not found" in err.lower():
            return jsonify({"error": err}), 404
        # 409 if already enrolled or schedule conflict
        if "already enrolled" in err.lower() or "conflict" in err.lower():
            return jsonify({"error": err}), 409
        # 400 for credit limit exceeded or other validation errors
        return jsonify({"error": err}), 400


@api_bp.route("/enrollments/drop", methods=["POST"])
def drop_course():
    """Drop an enrolled course for a student."""
    data = request.get_json() or {}
    sid = data.get("student_id")
    cid = data.get("course_id")
    if not sid or not cid:
        return jsonify({"error": "student_id and course_id are required fields."}), 400

    try:
        record = EnrollmentService.drop_course(student_id=sid, course_id=cid)
        return jsonify({"message": "Course dropped successfully", "enrollment": record}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# ---------------------------------------------------------
# Grade & Marks Management APIs
# ---------------------------------------------------------
@api_bp.route("/grades", methods=["GET"])
def list_grades():
    """Retrieve grades, optionally filtered by student_id or course_id."""
    sid = request.args.get("student_id")
    cid = request.args.get("course_id")
    grades = GradeService.get_grades(student_id=sid, course_id=cid)
    return jsonify({"count": len(grades), "grades": grades}), 200


@api_bp.route("/grades", methods=["POST"])
def record_grade():
    """Record academic grade for an enrolled student course."""
    data = request.get_json() or {}
    sid = data.get("student_id")
    cid = data.get("course_id")
    grade = data.get("grade")
    sem = data.get("semester")

    if not sid or not cid or not grade:
        return jsonify({"error": "student_id, course_id, and grade are required."}), 400

    try:
        record = GradeService.add_grade(
            student_id=sid,
            course_id=cid,
            grade=grade,
            semester=int(sem) if sem is not None else None
        )
        return jsonify({"message": "Grade recorded successfully", "grade": record}), 201
    except ValueError as e:
        err = str(e)
        if "not found" in err.lower():
            return jsonify({"error": err}), 404
        return jsonify({"error": err}), 400
