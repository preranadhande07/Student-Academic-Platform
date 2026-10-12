"""Grade entity model and grade point conversion."""


GRADE_SCALE = {
    "A": 4.0,
    "B": 3.0,
    "C": 2.0,
    "D": 1.0,
    "F": 0.0
}


class Grade:
    """Represents a final letter grade and grade points for a completed course."""

    def __init__(self, grade_id: str, student_id: str, course_id: str,
                 grade: str, semester: int):
        self.grade_id = str(grade_id).strip()
        self.student_id = str(student_id).strip()
        self.course_id = str(course_id).strip()
        self.grade = str(grade).strip().upper()
        self.semester = int(semester)
        self.grade_points = self.calculate_points(self.grade)
        self.validate()

    @staticmethod
    def calculate_points(grade_letter: str) -> float:
        """Calculate numeric grade point from letter grade."""
        letter = str(grade_letter).strip().upper()
        if letter not in GRADE_SCALE:
            raise ValueError(f"Invalid grade '{grade_letter}'. Allowed grades are A, B, C, D, F.")
        return GRADE_SCALE[letter]

    def validate(self):
        """Validate required grade fields."""
        if not self.grade_id:
            raise ValueError("Grade ID is mandatory.")
        if not self.student_id:
            raise ValueError("Student ID is mandatory.")
        if not self.course_id:
            raise ValueError("Course ID is mandatory.")
        if self.grade not in GRADE_SCALE:
            raise ValueError(f"Invalid grade '{self.grade}'. Allowed grades are: {list(GRADE_SCALE.keys())}")
        if self.semester < 1:
            raise ValueError("Semester must be a positive integer.")

    def to_dict(self):
        """Serialize grade model to dictionary."""
        return {
            "grade_id": self.grade_id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "grade": self.grade,
            "grade_points": self.grade_points,
            "semester": self.semester
        }
