"""Course entity model."""


class Course:
    """Represents an academic course offered in a curriculum."""

    def __init__(self, course_id: str, course_name: str, faculty_id: str,
                 credits: int, semester: int = 1, schedule: str = "TBA"):
        self.course_id = str(course_id).strip()
        self.course_name = str(course_name).strip()
        self.faculty_id = str(faculty_id).strip()
        self.credits = int(credits)
        self.semester = int(semester)
        self.schedule = str(schedule).strip()
        self.validate()

    def validate(self):
        """Validate required attributes and constraints."""
        if not self.course_id:
            raise ValueError("Course ID is mandatory.")
        if not self.course_name:
            raise ValueError("Course name is mandatory.")
        if not self.faculty_id:
            raise ValueError("Faculty ID assignment is mandatory.")
        if self.credits < 1 or self.credits > 6:
            raise ValueError("Course credits must be between 1 and 6.")
        if self.semester < 1:
            raise ValueError("Semester must be a positive integer.")
        if not self.schedule:
            raise ValueError("Schedule information is mandatory.")

    def to_dict(self):
        """Serialize course model to dictionary."""
        return {
            "course_id": self.course_id,
            "course_name": self.course_name,
            "faculty_id": self.faculty_id,
            "credits": self.credits,
            "semester": self.semester,
            "schedule": self.schedule
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create a Course instance from a dictionary."""
        return cls(
            course_id=data.get("course_id"),
            course_name=data.get("course_name"),
            faculty_id=data.get("faculty_id"),
            credits=data.get("credits", 3),
            semester=data.get("semester", 1),
            schedule=data.get("schedule", "TBA")
        )
