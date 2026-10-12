"""Models package for Student Record & Academic Management Platform."""
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.grade import Grade

__all__ = ["Student", "Faculty", "Course", "Enrollment", "Grade"]
