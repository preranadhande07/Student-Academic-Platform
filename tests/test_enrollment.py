"""Unit and integration tests for Course Enrollment, Credit Limits, and Schedule Conflicts."""
import pytest
from database.db import db
from app.services.student_service import EnrollmentService, CourseService, StudentService
from app.models.enrollment import Enrollment


@pytest.fixture(autouse=True)
def run_around_tests():
    """Reset database state before and after each test."""
    db.reset()
    yield
    db.reset()


def test_enrollment_lifecycle_success():
    """Verify standard enrollment of student into an available course."""
    # S102 enrolls in CS102 (4 credits)
    enrollment = EnrollmentService.enroll_student("S102", "CS102")
    assert enrollment["status"] == "ENROLLED"
    assert enrollment["student_id"] == "S102"
    assert enrollment["course_id"] == "CS102"
    assert enrollment["semester"] == 1


def test_duplicate_enrollment_rejected():
    """Verify business rule: A student cannot enroll in the same course twice."""
    # S101 is already enrolled in CS101 in seed data
    with pytest.raises(ValueError, match="already enrolled in course 'CS101'"):
        EnrollmentService.enroll_student("S101", "CS101")


def test_enrollment_nonexistent_student_rejected():
    """Verify business rule: Student must exist before enrollment."""
    with pytest.raises(ValueError, match="Student 'S999' not found"):
        EnrollmentService.enroll_student("S999", "CS101")


def test_enrollment_nonexistent_course_rejected():
    """Verify business rule: Course must exist before enrollment."""
    with pytest.raises(ValueError, match="Course 'CS999' not found"):
        EnrollmentService.enroll_student("S101", "CS999")


def test_credit_limit_18_enforcement():
    """Verify business rule: Maximum 18 credits per semester. Reject if exceeded."""
    # S103 is enrolled in 0 courses initially in semester 1
    # Create courses with specific credits
    CourseService.add_course("TEST1", "Course 1", "F101", credits=6, semester=1, schedule="Mon 08:00-09:00")
    CourseService.add_course("TEST2", "Course 2", "F101", credits=6, semester=1, schedule="Tue 08:00-09:00")
    CourseService.add_course("TEST3", "Course 3", "F101", credits=5, semester=1, schedule="Wed 08:00-09:00")
    CourseService.add_course("TEST4", "Course 4", "F101", credits=4, semester=1, schedule="Thu 08:00-09:00")

    # Enroll in 6 + 6 + 5 = 17 credits
    EnrollmentService.enroll_student("S103", "TEST1")  # 6 credits
    EnrollmentService.enroll_student("S103", "TEST2")  # 12 credits
    EnrollmentService.enroll_student("S103", "TEST3")  # 17 credits

    # Attempt to enroll in TEST4 (4 credits) -> 17 + 4 = 21 > 18 -> MUST BE REJECTED!
    with pytest.raises(ValueError, match="Credit limit exceeded for semester 1"):
        EnrollmentService.enroll_student("S103", "TEST4")


def test_credit_limit_exact_18_allowed():
    """Verify student can enroll up to exactly 18 credits."""
    StudentService.add_student("S300", "Max Credit Student", "max@univ.edu", "CS", semester=1)
    CourseService.add_course("C18A", "Course A", "F101", credits=6, semester=1, schedule="Time A")
    CourseService.add_course("C18B", "Course B", "F101", credits=6, semester=1, schedule="Time B")
    CourseService.add_course("C18C", "Course C", "F101", credits=6, semester=1, schedule="Time C")

    # 6 + 6 + 6 = 18 exactly
    e1 = EnrollmentService.enroll_student("S300", "C18A")
    e2 = EnrollmentService.enroll_student("S300", "C18B")
    e3 = EnrollmentService.enroll_student("S300", "C18C")

    assert e1["status"] == "ENROLLED"
    assert e2["status"] == "ENROLLED"
    assert e3["status"] == "ENROLLED"


def test_schedule_conflict_detection():
    """Verify business rule: Reject enrollment if course has conflicting schedule."""
    # S101 is enrolled in CS101 which has schedule "Mon 09:00-10:30"
    # Course CS104 also has schedule "Mon 09:00-10:30"
    with pytest.raises(ValueError, match="Schedule conflict detected"):
        EnrollmentService.enroll_student("S101", "CS104")


def test_drop_course_lifecycle():
    """Verify student can drop an enrolled course and free up credits."""
    # S101 is enrolled in CS101
    drop_record = EnrollmentService.drop_course("S101", "CS101")
    assert drop_record["status"] == "DROPPED"

    # Now S101 can enroll in CS104 without schedule conflict since CS101 is DROPPED
    new_enrollment = EnrollmentService.enroll_student("S101", "CS104")
    assert new_enrollment["status"] == "ENROLLED"
    assert new_enrollment["course_id"] == "CS104"

    # Dropping non-enrolled course raises error
    with pytest.raises(ValueError, match="No active enrollment found"):
        EnrollmentService.drop_course("S101", "CS105")


def test_list_enrollments_filtering():
    """Verify enrollment listing and filtering by student and course."""
    enrollments = EnrollmentService.list_enrollments(student_id="S101")
    assert len(enrollments) >= 2

    s102_enrollments = EnrollmentService.list_enrollments(student_id="S102")
    assert len(s102_enrollments) == 1
    assert s102_enrollments[0]["course_id"] == "EE101"

    course_enrollments = EnrollmentService.list_enrollments(course_id="CS101")
    assert len(course_enrollments) >= 1


def test_enrollment_model_validation():
    """Verify Enrollment model validation checks."""
    with pytest.raises(ValueError, match="Enrollment ID is mandatory"):
        Enrollment(enrollment_id="", student_id="S101", course_id="CS101", semester=1)

    with pytest.raises(ValueError, match="Enrollment status must be 'ENROLLED' or 'DROPPED'"):
        Enrollment(enrollment_id="ENR-1", student_id="S101", course_id="CS101",
                   semester=1, status="UNKNOWN")
