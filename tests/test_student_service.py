"""Unit tests for Student Management business logic and validation."""
import pytest
from database.db import db
from app.services.student_service import StudentService
from app.models.student import Student


@pytest.fixture(autouse=True)
def run_around_tests():
    """Reset database state before and after each test."""
    db.reset()
    yield
    db.reset()


def test_add_student_success():
    """Verify successfully registering a student."""
    student = StudentService.add_student(
        student_id="S201",
        name="Diana Prince",
        email="diana.prince@university.edu",
        department="Computer Science",
        semester=1
    )
    assert student["student_id"] == "S201"
    assert student["name"] == "Diana Prince"
    assert student["email"] == "diana.prince@university.edu"
    assert student["department"] == "Computer Science"
    assert student["semester"] == 1


def test_add_duplicate_student_id_fails():
    """Verify duplicate student ID is rejected with ValueError."""
    with pytest.raises(ValueError, match="already exists"):
        StudentService.add_student(
            student_id="S101",
            name="Alice Duplicate",
            email="new.alice@university.edu",
            department="Computer Science"
        )


def test_add_duplicate_student_email_fails():
    """Verify duplicate student email is rejected."""
    with pytest.raises(ValueError, match="already exists"):
        StudentService.add_student(
            student_id="S999",
            name="Another Person",
            email="alice.chen@university.edu",  # Already belongs to S101
            department="Data Science"
        )


def test_student_validation_errors():
    """Verify missing fields and malformed email trigger validation errors."""
    with pytest.raises(ValueError, match="Student ID is mandatory"):
        StudentService.add_student("", "Valid Name", "val@univ.edu", "CS")

    with pytest.raises(ValueError, match="Student name is mandatory"):
        StudentService.add_student("S500", "", "val@univ.edu", "CS")

    with pytest.raises(ValueError, match="valid student email"):
        StudentService.add_student("S500", "Valid Name", "invalid-email-string", "CS")

    with pytest.raises(ValueError, match="Department is mandatory"):
        StudentService.add_student("S500", "Valid Name", "val@univ.edu", "")

    with pytest.raises(ValueError, match="positive integer"):
        StudentService.add_student("S500", "Valid Name", "val@univ.edu", "CS", semester=-1)


def test_get_student_success_and_missing():
    """Verify retrieving existing and non-existent students."""
    student = StudentService.get_student("S101")
    assert student is not None
    assert student["name"] == "Alice Chen"

    non_existent = StudentService.get_student("S999")
    assert non_existent is None


def test_list_students_and_filtering():
    """Verify student listing, department filtering, and query search."""
    all_students = StudentService.list_students()
    assert len(all_students) >= 3

    cs_students = StudentService.list_students(department="Computer Science")
    assert all(s["department"] == "Computer Science" for s in cs_students)

    sem2_students = StudentService.list_students(semester=2)
    assert len(sem2_students) == 1
    assert sem2_students[0]["student_id"] == "S103"

    searched = StudentService.list_students(query="Martinez")
    assert len(searched) == 1
    assert searched[0]["student_id"] == "S102"


def test_update_student_success_and_validation():
    """Verify updating student attributes."""
    updated = StudentService.update_student(
        student_id="S102",
        name="Robert Martinez Jr.",
        department="Robotics Engineering"
    )
    assert updated["name"] == "Robert Martinez Jr."
    assert updated["department"] == "Robotics Engineering"
    assert updated["email"] == "bob.martinez@university.edu"

    with pytest.raises(ValueError, match="not found"):
        StudentService.update_student("S999", name="Ghost")


def test_delete_student_with_active_enrollments_fails():
    """Verify deleting a student who has active enrollments is blocked."""
    # S101 has active enrollments in initial seed data
    with pytest.raises(ValueError, match="Cannot delete student 'S101' with active course enrollments"):
        StudentService.delete_student("S101")


def test_delete_student_without_enrollments_success():
    """Verify successfully deleting a student without active enrollments."""
    # S103 has no active enrollments in seed data
    result = StudentService.delete_student("S103")
    assert result is True
    assert StudentService.get_student("S103") is None

    with pytest.raises(ValueError, match="not found"):
        StudentService.delete_student("S999")


def test_student_model_from_dict():
    """Verify Student model serialization and deserialization."""
    raw = {
        "student_id": "S888",
        "name": "Evelyn Harper",
        "email": "evelyn@univ.edu",
        "department": "Physics",
        "semester": 3
    }
    model = Student.from_dict(raw)
    assert model.student_id == "S888"
    assert model.to_dict()["department"] == "Physics"
