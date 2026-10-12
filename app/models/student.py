"""Student entity model."""


class Student:
    """Represents a student enrolled in the academic institution."""

    def __init__(self, student_id: str, name: str, email: str, department: str, semester: int = 1):
        self.student_id = str(student_id).strip()
        self.name = str(name).strip()
        self.email = str(email).strip().lower()
        self.department = str(department).strip()
        self.semester = int(semester)
        self.validate()

    def validate(self):
        """Validate required attributes and format."""
        if not self.student_id:
            raise ValueError("Student ID is mandatory.")
        if not self.name:
            raise ValueError("Student name is mandatory.")
        if not self.email or "@" not in self.email:
            raise ValueError("A valid student email address is mandatory.")
        if not self.department:
            raise ValueError("Department is mandatory.")
        if self.semester < 1:
            raise ValueError("Semester must be a positive integer.")

    def to_dict(self):
        """Serialize student model to dictionary."""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "semester": self.semester
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create a Student instance from a dictionary."""
        return cls(
            student_id=data.get("student_id"),
            name=data.get("name"),
            email=data.get("email"),
            department=data.get("department"),
            semester=data.get("semester", 1)
        )
