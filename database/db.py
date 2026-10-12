"""Thread-safe in-memory database store for Enterprise Student Record Platform."""
import threading


class Database:
    """Thread-safe in-memory singleton database store."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Database, cls).__new__(cls)
                cls._instance._init_db()
            return cls._instance

    def _init_db(self):
        self.students = {}
        self.faculty = {}
        self.courses = {}
        self.enrollments = []
        self.grades = []
        self._seed_initial_data()

    def _seed_initial_data(self):
        # Seed default students
        self.students["S101"] = {
            "student_id": "S101",
            "name": "Alice Chen",
            "email": "alice.chen@university.edu",
            "department": "Computer Science",
            "semester": 1
        }
        self.students["S102"] = {
            "student_id": "S102",
            "name": "Bob Martinez",
            "email": "bob.martinez@university.edu",
            "department": "Electrical Engineering",
            "semester": 1
        }
        self.students["S103"] = {
            "student_id": "S103",
            "name": "Carol Davis",
            "email": "carol.davis@university.edu",
            "department": "Computer Science",
            "semester": 2
        }

        # Seed default faculty
        self.faculty["F101"] = {
            "faculty_id": "F101",
            "name": "Dr. Alan Turing",
            "email": "alan.turing@university.edu",
            "department": "Computer Science",
            "title": "Professor"
        }
        self.faculty["F102"] = {
            "faculty_id": "F102",
            "name": "Dr. Ada Lovelace",
            "email": "ada.lovelace@university.edu",
            "department": "Computer Science",
            "title": "Associate Professor"
        }
        self.faculty["F103"] = {
            "faculty_id": "F103",
            "name": "Dr. Claude Shannon",
            "email": "claude.shannon@university.edu",
            "department": "Electrical Engineering",
            "title": "Professor"
        }

        # Seed default course catalog
        self.courses["CS101"] = {
            "course_id": "CS101",
            "course_name": "Introduction to Computer Science",
            "faculty_id": "F101",
            "credits": 4,
            "semester": 1,
            "schedule": "Mon 09:00-10:30"
        }
        self.courses["CS102"] = {
            "course_id": "CS102",
            "course_name": "Data Structures & Algorithms",
            "faculty_id": "F102",
            "credits": 4,
            "semester": 1,
            "schedule": "Tue 10:00-11:30"
        }
        self.courses["CS103"] = {
            "course_id": "CS103",
            "course_name": "Computer Architecture",
            "faculty_id": "F101",
            "credits": 3,
            "semester": 1,
            "schedule": "Wed 11:00-12:30"
        }
        self.courses["CS104"] = {
            "course_id": "CS104",
            "course_name": "Database Management Systems",
            "faculty_id": "F102",
            "credits": 3,
            "semester": 1,
            "schedule": "Mon 09:00-10:30"  # Same slot as CS101 for schedule conflict testing
        }
        self.courses["CS105"] = {
            "course_id": "CS105",
            "course_name": "Operating Systems",
            "faculty_id": "F101",
            "credits": 4,
            "semester": 1,
            "schedule": "Thu 14:00-15:30"
        }
        self.courses["EE101"] = {
            "course_id": "EE101",
            "course_name": "Circuit Analysis",
            "faculty_id": "F103",
            "credits": 4,
            "semester": 1,
            "schedule": "Mon 13:00-14:30"
        }

        # Seed initial enrollments
        self.enrollments.append({
            "enrollment_id": "ENR-0001",
            "student_id": "S101",
            "course_id": "CS101",
            "semester": 1,
            "enrolled_at": "2026-09-01T09:00:00",
            "status": "ENROLLED"
        })
        self.enrollments.append({
            "enrollment_id": "ENR-0002",
            "student_id": "S101",
            "course_id": "CS102",
            "semester": 1,
            "enrolled_at": "2026-09-01T09:05:00",
            "status": "ENROLLED"
        })
        self.enrollments.append({
            "enrollment_id": "ENR-0003",
            "student_id": "S102",
            "course_id": "EE101",
            "semester": 1,
            "enrolled_at": "2026-09-01T09:10:00",
            "status": "ENROLLED"
        })

        # Seed initial grade
        self.grades.append({
            "grade_id": "GRD-0001",
            "student_id": "S101",
            "course_id": "CS101",
            "grade": "A",
            "grade_points": 4.0,
            "semester": 1
        })

    def reset(self):
        """Helper to restore clean database state during test setup and teardowns."""
        with self._lock:
            self.students.clear()
            self.faculty.clear()
            self.courses.clear()
            self.enrollments.clear()
            self.grades.clear()
            self._seed_initial_data()


# Global thread-safe singleton instance
db = Database()
