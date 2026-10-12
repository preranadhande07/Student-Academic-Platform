"""Integration tests for REST API endpoints using Flask test client."""
import pytest
from app import create_app
from database.db import db


@pytest.fixture
def client():
    """Create a test client with clean isolated database state."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        db.reset()
        yield client
        db.reset()


# ---------------- Health Check ---------------- #

def test_healthcheck_endpoint(client):
    """Verify healthcheck endpoint returns 200 and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "UP"
    assert "Student Record" in data["service"]
    assert data["version"] == "1.0.0"


# ---------------- Student Endpoints ---------------- #

def test_api_list_students(client):
    """Verify listing students returns seed dataset."""
    response = client.get("/api/students")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] >= 3
    assert len(data["students"]) >= 3


def test_api_register_student_success_and_conflict(client):
    """Verify student creation, 201 Created and 409 Conflict."""
    payload = {
        "student_id": "S700",
        "name": "Grace Hopper",
        "email": "grace.hopper@navy.mil",
        "department": "Computer Science",
        "semester": 1
    }
    # Success 201
    res1 = client.post("/api/students", json=payload)
    assert res1.status_code == 201
    assert res1.get_json()["student"]["name"] == "Grace Hopper"

    # Duplicate 409
    res2 = client.post("/api/students", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.get_json()["error"]


def test_api_register_student_validation_error(client):
    """Verify malformed student payload returns 400 Bad Request."""
    bad_payload = {
        "student_id": "S701",
        "name": "",  # Missing name
        "email": "invalid-email"
    }
    response = client.post("/api/students", json=bad_payload)
    assert response.status_code == 400


def test_api_get_student_by_id(client):
    """Verify get student returns 200 for existing, 404 for missing."""
    res_ok = client.get("/api/students/S101")
    assert res_ok.status_code == 200
    assert res_ok.get_json()["name"] == "Alice Chen"

    res_missing = client.get("/api/students/NONEXISTENT")
    assert res_missing.status_code == 404


def test_api_update_student(client):
    """Verify updating student returns 200."""
    res = client.put("/api/students/S102", json={"department": "Bioengineering"})
    assert res.status_code == 200
    assert res.get_json()["student"]["department"] == "Bioengineering"

    res_404 = client.put("/api/students/S999", json={"name": "Ghost"})
    assert res_404.status_code == 404


def test_api_delete_student(client):
    """Verify delete student rules: 400 if active enrollments, 200 if clear."""
    # S101 has active enrollments -> 400
    res_blocked = client.delete("/api/students/S101")
    assert res_blocked.status_code == 400

    # S103 has no active enrollments -> 200
    res_ok = client.delete("/api/students/S103")
    assert res_ok.status_code == 200

    # Missing -> 404
    res_404 = client.delete("/api/students/S999")
    assert res_404.status_code == 404


def test_api_student_gpa_endpoint(client):
    """Verify retrieving student GPA returns 200."""
    res = client.get("/api/students/S101/gpa")
    assert res.status_code == 200
    data = res.get_json()
    assert "gpa" in data
    assert data["student_id"] == "S101"

    res_404 = client.get("/api/students/S999/gpa")
    assert res_404.status_code == 404


# ---------------- Faculty Endpoints ---------------- #

def test_api_faculty_endpoints(client):
    """Verify faculty listing, registration, and retrieval."""
    res_list = client.get("/api/faculty")
    assert res_list.status_code == 200
    assert res_list.get_json()["count"] >= 3

    new_faculty = {
        "faculty_id": "F501",
        "name": "Dr. Donald Knuth",
        "email": "knuth@stanford.edu",
        "department": "Computer Science",
        "title": "Professor Emeritus"
    }
    res_post = client.post("/api/faculty", json=new_faculty)
    assert res_post.status_code == 201

    res_get = client.get("/api/faculty/F501")
    assert res_get.status_code == 200

    res_missing = client.get("/api/faculty/F999")
    assert res_missing.status_code == 404


# ---------------- Course Endpoints ---------------- #

def test_api_course_endpoints(client):
    """Verify course listing, creation, and detail retrieval."""
    res_list = client.get("/api/courses")
    assert res_list.status_code == 200
    assert res_list.get_json()["count"] >= 5

    new_course = {
        "course_id": "CS301",
        "course_name": "Cloud Native Engineering",
        "faculty_id": "F101",
        "credits": 4,
        "semester": 3,
        "schedule": "Wed 10:00-11:30"
    }
    res_post = client.post("/api/courses", json=new_course)
    assert res_post.status_code == 201

    res_get = client.get("/api/courses/CS301")
    assert res_get.status_code == 200

    res_missing = client.get("/api/courses/CS999")
    assert res_missing.status_code == 404

    # Update course
    res_put = client.put("/api/courses/CS301", json={"credits": 3})
    assert res_put.status_code == 200
    assert res_put.get_json()["course"]["credits"] == 3

    # Delete course without enrollments
    res_del = client.delete("/api/courses/CS301")
    assert res_del.status_code == 200

    # Delete course with enrollments fails
    res_del_fail = client.delete("/api/courses/CS101")
    assert res_del_fail.status_code == 400


def test_api_faculty_update_and_delete(client):
    """Verify faculty update and delete via API."""
    res_post = client.post("/api/faculty", json={
        "faculty_id": "F900",
        "name": "Dr. Barbara Liskov",
        "email": "liskov@mit.edu",
        "department": "Computer Science",
        "title": "Professor"
    })
    assert res_post.status_code == 201

    res_put = client.put("/api/faculty/F900", json={"title": "Institute Professor"})
    assert res_put.status_code == 200
    assert res_put.get_json()["faculty"]["title"] == "Institute Professor"

    res_del = client.delete("/api/faculty/F900")
    assert res_del.status_code == 200

    # Deleting faculty with active courses fails
    res_del_fail = client.delete("/api/faculty/F101")
    assert res_del_fail.status_code == 400


# ---------------- Enrollment Endpoints ---------------- #

def test_api_enrollment_success_and_rules(client):
    """Verify enrollment endpoint handles 201, 409 conflict, and 404."""
    # S102 enrolls in CS102 -> 201
    res_ok = client.post("/api/enrollments", json={"student_id": "S102", "course_id": "CS102"})
    assert res_ok.status_code == 201

    # Duplicate enrollment -> 409 Conflict
    res_duplicate = client.post("/api/enrollments", json={"student_id": "S101", "course_id": "CS101"})
    assert res_duplicate.status_code == 409

    # Schedule conflict -> 409 Conflict (CS104 conflicts with CS101 for S101)
    res_conflict = client.post("/api/enrollments", json={"student_id": "S101", "course_id": "CS104"})
    assert res_conflict.status_code == 409

    # Non-existent student -> 404 Not Found
    res_missing_s = client.post("/api/enrollments", json={"student_id": "S999", "course_id": "CS101"})
    assert res_missing_s.status_code == 404

    # Missing payload fields -> 400
    res_missing_fields = client.post("/api/enrollments", json={})
    assert res_missing_fields.status_code == 400

    # List enrollments
    res_list = client.get("/api/enrollments?student_id=S101")
    assert res_list.status_code == 200
    assert res_list.get_json()["count"] >= 2


def test_api_drop_course_endpoint(client):
    """Verify dropping a course via API."""
    res = client.post("/api/enrollments/drop", json={"student_id": "S101", "course_id": "CS101"})
    assert res.status_code == 200
    assert res.get_json()["enrollment"]["status"] == "DROPPED"

    # Missing fields -> 400
    res_bad = client.post("/api/enrollments/drop", json={})
    assert res_bad.status_code == 400


# ---------------- Grade Endpoints ---------------- #

def test_api_grade_endpoints(client):
    """Verify recording and fetching grades."""
    # S101 is enrolled in CS102; record grade 'B'
    payload = {
        "student_id": "S101",
        "course_id": "CS102",
        "grade": "B",
        "semester": 1
    }
    res_post = client.post("/api/grades", json=payload)
    assert res_post.status_code == 201

    res_list = client.get("/api/grades?student_id=S101")
    assert res_list.status_code == 200
    assert res_list.get_json()["count"] >= 2

    # Validation errors -> 400
    res_bad_grade = client.post("/api/grades", json={
        "student_id": "S101",
        "course_id": "CS102",
        "grade": "INVALID"
    })
    assert res_bad_grade.status_code == 400

    res_missing_payload = client.post("/api/grades", json={})
    assert res_missing_payload.status_code == 400


def test_api_index_template(client):
    """Verify web UI index page returns HTML 200."""
    res = client.get("/")
    assert res.status_code == 200
    assert b"Student Record & Academic Management Platform" in res.data
