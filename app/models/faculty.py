"""Faculty entity model."""


class Faculty:
    """Represents a faculty instructor in the academic institution."""

    def __init__(self, faculty_id: str, name: str, email: str, department: str, title: str = "Professor"):
        self.faculty_id = str(faculty_id).strip()
        self.name = str(name).strip()
        self.email = str(email).strip().lower()
        self.department = str(department).strip()
        self.title = str(title).strip()
        self.validate()

    def validate(self):
        """Validate required attributes and format."""
        if not self.faculty_id:
            raise ValueError("Faculty ID is mandatory.")
        if not self.name:
            raise ValueError("Faculty name is mandatory.")
        if not self.email or "@" not in self.email:
            raise ValueError("A valid faculty email address is mandatory.")
        if not self.department:
            raise ValueError("Department is mandatory.")
        if not self.title:
            raise ValueError("Academic title/designation is mandatory.")

    def to_dict(self):
        """Serialize faculty model to dictionary."""
        return {
            "faculty_id": self.faculty_id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "title": self.title
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create a Faculty instance from a dictionary."""
        return cls(
            faculty_id=data.get("faculty_id"),
            name=data.get("name"),
            email=data.get("email"),
            department=data.get("department"),
            title=data.get("title", "Professor")
        )
