"""Unit tests for Grades, Marks Management, and GPA Calculations."""
import pytest
from database.db import db
from app.services.student_service import GradeService, EnrollmentService
from app.models.grade import Grade


@pytest.fixture(autouse=True)
def run_around_tests():
    """Reset database state before and after each test."""
    db.reset()
    yield
    db.reset()


def test_add_grade_success():
    """Verify recording grade for an actively enrolled course."""
    # S101 is enrolled in CS102 (seed data)
    grade_rec = GradeService.add_grade(
        student_id="S101",
        course_id="CS102",
        grade="B",
        semester=1
    )
    assert grade_rec["student_id"] == "S101"
    assert grade_rec["course_id"] == "CS102"
    assert grade_rec["grade"] == "B"
    assert grade_rec["grade_points"] == 3.0


def test_add_grade_for_non_enrolled_course_fails():
    """Verify recording a grade for a course the student never enrolled in is rejected."""
    # S101 is NOT enrolled in EE101
    with pytest.raises(ValueError, match="is not enrolled in course 'EE101'"):
        GradeService.add_grade("S101", "EE101", "A")


def test_add_grade_for_nonexistent_student_or_course_fails():
    """Verify invalid student or course IDs are rejected."""
    with pytest.raises(ValueError, match="Student 'S999' not found"):
        GradeService.add_grade("S999", "CS101", "A")

    with pytest.raises(ValueError, match="Course 'CS999' not found"):
        GradeService.add_grade("S101", "CS999", "A")


def test_invalid_grade_letter_rejected():
    """Verify invalid grade letters like 'X', 'Z' are rejected."""
    with pytest.raises(ValueError, match="Invalid grade 'Z'"):
        GradeService.add_grade("S101", "CS101", "Z")


def test_grade_update_idempotency():
    """Verify recording a grade again updates the existing grade record."""
    # Initial seed grade for S101 in CS101 is 'A' (4.0)
    updated = GradeService.add_grade("S101", "CS101", "B")
    assert updated["grade"] == "B"
    assert updated["grade_points"] == 3.0

    # Verify no duplicate grade records created
    grades = GradeService.get_grades(student_id="S101", course_id="CS101")
    assert len(grades) == 1


def test_gpa_calculation_single_course():
    """Verify GPA calculation for a student with one course."""
    # S101 has CS101 (4 credits, 'A'=4.0)
    gpa_data = GradeService.calculate_gpa("S101")
    assert gpa_data["student_id"] == "S101"
    assert gpa_data["gpa"] == 4.0
    assert gpa_data["total_graded_credits"] == 4


def test_gpa_calculation_weighted_multiple_courses():
    """Verify weighted GPA calculation across courses with different credit values."""
    # S101: CS101 is 4 credits ('A' = 4.0 points => 16 quality points)
    # Now add CS102: 4 credits with grade 'B' = 3.0 points => 12 quality points
    GradeService.add_grade("S101", "CS102", "B")

    # Enroll and grade in CS103: 3 credits with grade 'C' = 2.0 points => 6 quality points
    EnrollmentService.enroll_student("S101", "CS103")
    GradeService.add_grade("S101", "CS103", "C")

    # Total quality points = 16 + 12 + 6 = 34
    # Total credits = 4 + 4 + 3 = 11
    # Expected GPA = 34 / 11 = 3.0909... -> 3.09
    gpa_data = GradeService.calculate_gpa("S101")
    assert gpa_data["total_graded_credits"] == 11
    assert gpa_data["gpa"] == 3.09


def test_gpa_calculation_with_failing_grade():
    """Verify GPA calculation incorporates failing grades ('F' = 0.0 points)."""
    # S102 is enrolled in EE101 (4 credits)
    GradeService.add_grade("S102", "EE101", "F")

    gpa_data = GradeService.calculate_gpa("S102")
    assert gpa_data["gpa"] == 0.0
    assert gpa_data["total_graded_credits"] == 4


def test_gpa_calculation_zero_grades():
    """Verify GPA returns 0.0 for students with no recorded grades."""
    # S103 has no grades recorded
    gpa_data = GradeService.calculate_gpa("S103")
    assert gpa_data["gpa"] == 0.0
    assert gpa_data["total_graded_credits"] == 0


def test_grade_model_points_mapping():
    """Verify Grade model point mapping and validation."""
    assert Grade.calculate_points("A") == 4.0
    assert Grade.calculate_points("B") == 3.0
    assert Grade.calculate_points("C") == 2.0
    assert Grade.calculate_points("D") == 1.0
    assert Grade.calculate_points("F") == 0.0

    with pytest.raises(ValueError, match="Invalid grade"):
        Grade(grade_id="G1", student_id="S1", course_id="C1", grade="INVALID", semester=1)
