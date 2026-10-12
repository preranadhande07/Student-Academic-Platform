"""Unit tests for Course and Faculty Management business logic and validation."""
import pytest
from database.db import db
from app.services.student_service import CourseService, FacultyService
from app.models.course import Course
from app.models.faculty import Faculty


@pytest.fixture(autouse=True)
def run_around_tests():
    """Reset database state before and after each test."""
    db.reset()
    yield
    db.reset()


def test_add_course_success():
    """Verify adding a course with a valid assigned faculty member."""
    course = CourseService.add_course(
        course_id="CS201",
        course_name="Machine Learning Fundamentals",
        faculty_id="F101",
        credits=4,
        semester=2,
        schedule="Wed 14:00-15:30"
    )
    assert course["course_id"] == "CS201"
    assert course["course_name"] == "Machine Learning Fundamentals"
    assert course["credits"] == 4
    assert course["schedule"] == "Wed 14:00-15:30"


def test_add_course_with_nonexistent_faculty_fails():
    """Verify course creation fails if assigned faculty does not exist."""
    with pytest.raises(ValueError, match="Assigned faculty 'F999' does not exist"):
        CourseService.add_course(
            course_id="CS202",
            course_name="Deep Learning",
            faculty_id="F999",
            credits=3,
            semester=2
        )


def test_add_duplicate_course_fails():
    """Verify duplicate course ID is rejected."""
    with pytest.raises(ValueError, match="already exists"):
        CourseService.add_course(
            course_id="CS101",
            course_name="Duplicate CS Course",
            faculty_id="F101",
            credits=4
        )


def test_course_credits_validation():
    """Verify credits must be between 1 and 6."""
    with pytest.raises(ValueError, match="Course credits must be between 1 and 6"):
        CourseService.add_course("CS99", "Zero Credit Course", "F101", credits=0)

    with pytest.raises(ValueError, match="Course credits must be between 1 and 6"):
        CourseService.add_course("CS99", "Excessive Credit Course", "F101", credits=7)


def test_get_and_list_courses():
    """Verify course retrieval and filtering."""
    c = CourseService.get_course("CS101")
    assert c is not None
    assert c["course_name"] == "Introduction to Computer Science"

    missing = CourseService.get_course("NONEXISTENT")
    assert missing is None

    sem1_courses = CourseService.list_courses(semester=1)
    assert len(sem1_courses) >= 5

    searched = CourseService.list_courses(query="Circuit")
    assert len(searched) == 1
    assert searched[0]["course_id"] == "EE101"


def test_update_course_success():
    """Verify updating course details."""
    updated = CourseService.update_course(
        course_id="CS103",
        course_name="Advanced Computer Architecture",
        credits=4
    )
    assert updated["course_name"] == "Advanced Computer Architecture"
    assert updated["credits"] == 4

    with pytest.raises(ValueError, match="Course 'CS999' not found"):
        CourseService.update_course("CS999", course_name="Phantom")


def test_delete_course_with_active_enrollments_fails():
    """Verify deleting a course with enrolled students is blocked."""
    # CS101 has active enrollments from S101
    with pytest.raises(ValueError, match="Cannot delete course 'CS101' with active student enrollments"):
        CourseService.delete_course("CS101")


def test_delete_course_without_enrollments_success():
    """Verify successfully deleting a course without enrolled students."""
    # CS105 has no student enrollments in seed data
    result = CourseService.delete_course("CS105")
    assert result is True
    assert CourseService.get_course("CS105") is None


# ---------------- Faculty Management Tests ---------------- #

def test_add_faculty_success_and_duplicates():
    """Verify faculty creation and duplicate rejection."""
    f = FacultyService.add_faculty(
        faculty_id="F201",
        name="Dr. Margaret Hamilton",
        email="margaret.hamilton@university.edu",
        department="Software Engineering",
        title="Distinguished Professor"
    )
    assert f["faculty_id"] == "F201"
    assert f["name"] == "Dr. Margaret Hamilton"

    with pytest.raises(ValueError, match="already exists"):
        FacultyService.add_faculty("F101", "Dr. Dupe", "dupe@univ.edu", "CS")


def test_faculty_validation_errors():
    """Verify required fields for faculty."""
    with pytest.raises(ValueError, match="Faculty ID is mandatory"):
        FacultyService.add_faculty("", "Name", "email@univ.edu", "CS")

    with pytest.raises(ValueError, match="valid faculty email"):
        FacultyService.add_faculty("F99", "Name", "bad-email", "CS")


def test_delete_faculty_assigned_to_course_fails():
    """Verify cannot delete faculty assigned to an active course."""
    # F101 is assigned to CS101, CS103, CS105
    with pytest.raises(ValueError, match="Cannot delete faculty 'F101' assigned to active courses"):
        FacultyService.delete_faculty("F101")


def test_delete_unassigned_faculty_success():
    """Verify deleting a faculty member with no course assignments."""
    FacultyService.add_faculty("F500", "Adjunct Professor", "adjunct@univ.edu", "Math")
    assert FacultyService.delete_faculty("F500") is True
    assert FacultyService.get_faculty("F500") is None


def test_course_and_faculty_models():
    """Verify model conversions."""
    c_model = Course.from_dict({
        "course_id": "CS777",
        "course_name": "Quantum Computing",
        "faculty_id": "F101",
        "credits": 3,
        "semester": 4,
        "schedule": "Fri 09:00-10:30"
    })
    assert c_model.course_id == "CS777"
    assert c_model.to_dict()["credits"] == 3

    f_model = Faculty.from_dict({
        "faculty_id": "F777",
        "name": "Dr. Katherine Johnson",
        "email": "kjohnson@nasa.gov",
        "department": "Applied Math",
        "title": "Lead Mathematician"
    })
    assert f_model.faculty_id == "F777"
    assert f_model.to_dict()["title"] == "Lead Mathematician"
