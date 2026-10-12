"""Enrollment entity model."""
from datetime import datetime, timezone


class Enrollment:
    """Represents a student's registration in an academic course."""

    def __init__(self, enrollment_id: str, student_id: str, course_id: str,
                 semester: int, enrolled_at: str = None, status: str = "ENROLLED"):
        self.enrollment_id = str(enrollment_id).strip()
        self.student_id = str(student_id).strip()
        self.course_id = str(course_id).strip()
        self.semester = int(semester)
        self.enrolled_at = enrolled_at or datetime.now(timezone.utc).isoformat()
        self.status = str(status).strip().upper()
        self.validate()

    def validate(self):
        """Validate required enrollment fields."""
        if not self.enrollment_id:
            raise ValueError("Enrollment ID is mandatory.")
        if not self.student_id:
            raise ValueError("Student ID is mandatory.")
        if not self.course_id:
            raise ValueError("Course ID is mandatory.")
        if self.semester < 1:
            raise ValueError("Semester must be a positive integer.")
        if self.status not in ["ENROLLED", "DROPPED"]:
            raise ValueError("Enrollment status must be 'ENROLLED' or 'DROPPED'.")

    def to_dict(self):
        """Serialize enrollment model to dictionary."""
        return {
            "enrollment_id": self.enrollment_id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "semester": self.semester,
            "enrolled_at": self.enrolled_at,
            "status": self.status
        }
