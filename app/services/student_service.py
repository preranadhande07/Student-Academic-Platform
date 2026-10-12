"""Enterprise Academic and Student Service Layer.

Encapsulates all core business rules for students, faculty, courses,
enrollments, credit limits, schedule conflicts, grades, and GPA calculations.
"""
from datetime import datetime, timezone
from database.db import db
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.course import Course
from app.models.grade import Grade


MAX_SEMESTER_CREDITS = 18


class StudentService:
    """Manages student lifecycle and academic operations."""

    @staticmethod
    def add_student(student_id: str, name: str, email: str, department: str, semester: int = 1):
        """Register a new student with validation."""
        student_obj = Student(student_id=student_id, name=name, email=email,
                              department=department, semester=semester)
        with db._lock:
            if student_obj.student_id in db.students:
                raise ValueError(f"Student with ID '{student_obj.student_id}' already exists.")
            # Check unique email
            for s in db.students.values():
                if s["email"] == student_obj.email:
                    raise ValueError(f"Student with email '{student_obj.email}' already exists.")

            record = student_obj.to_dict()
            db.students[student_obj.student_id] = record
            return record

    @staticmethod
    def get_student(student_id: str):
        """Retrieve student record by ID."""
        with db._lock:
            return db.students.get(str(student_id).strip())

    @staticmethod
    def list_students(department: str = None, semester: int = None, query: str = None):
        """Retrieve filtered or searched list of students."""
        with db._lock:
            students = list(db.students.values())

        if department:
            students = [s for s in students if s["department"].lower() == department.lower().strip()]
        if semester is not None:
            students = [s for s in students if s["semester"] == int(semester)]
        if query:
            q = query.lower().strip()
            students = [
                s for s in students
                if q in s["name"].lower() or q in s["student_id"].lower() or q in s["email"].lower()
            ]
        return students

    @staticmethod
    def update_student(student_id: str, name: str = None, email: str = None,
                       department: str = None, semester: int = None):
        """Update existing student attributes with validation."""
        with db._lock:
            sid = str(student_id).strip()
            if sid not in db.students:
                raise ValueError(f"Student '{sid}' not found.")

            student = db.students[sid]
            new_name = name.strip() if name is not None else student["name"]
            new_email = email.strip().lower() if email is not None else student["email"]
            new_dept = department.strip() if department is not None else student["department"]
            new_sem = int(semester) if semester is not None else student["semester"]

            # Validate changes through model
            updated_obj = Student(student_id=sid, name=new_name, email=new_email,
                                  department=new_dept, semester=new_sem)

            # Check email uniqueness against other students
            for other_id, s in db.students.items():
                if other_id != sid and s["email"] == updated_obj.email:
                    raise ValueError(f"Student with email '{updated_obj.email}' already exists.")

            student.update(updated_obj.to_dict())
            return student

    @staticmethod
    def delete_student(student_id: str):
        """Delete student record ensuring no active enrollments exist."""
        with db._lock:
            sid = str(student_id).strip()
            if sid not in db.students:
                raise ValueError(f"Student '{sid}' not found.")

            active_enrollments = [
                e for e in db.enrollments
                if e["student_id"] == sid and e["status"] == "ENROLLED"
            ]
            if active_enrollments:
                raise ValueError(
                    f"Cannot delete student '{sid}' with active course enrollments "
                    f"({len(active_enrollments)} active courses)."
                )

            del db.students[sid]
            # Clean up dropped enrollments and grades associated with this student
            db.enrollments[:] = [e for e in db.enrollments if e["student_id"] != sid]
            db.grades[:] = [g for g in db.grades if g["student_id"] != sid]
            return True


class FacultyService:
    """Manages faculty instructors."""

    @staticmethod
    def add_faculty(faculty_id: str, name: str, email: str, department: str, title: str = "Professor"):
        """Register a new faculty instructor."""
        faculty_obj = Faculty(faculty_id=faculty_id, name=name, email=email,
                              department=department, title=title)
        with db._lock:
            if faculty_obj.faculty_id in db.faculty:
                raise ValueError(f"Faculty with ID '{faculty_obj.faculty_id}' already exists.")
            for f in db.faculty.values():
                if f["email"] == faculty_obj.email:
                    raise ValueError(f"Faculty with email '{faculty_obj.email}' already exists.")

            record = faculty_obj.to_dict()
            db.faculty[faculty_obj.faculty_id] = record
            return record

    @staticmethod
    def get_faculty(faculty_id: str):
        """Retrieve faculty instructor by ID."""
        with db._lock:
            return db.faculty.get(str(faculty_id).strip())

    @staticmethod
    def list_faculty(department: str = None):
        """List all faculty, optionally filtered by department."""
        with db._lock:
            faculty_list = list(db.faculty.values())
        if department:
            faculty_list = [f for f in faculty_list if f["department"].lower() == department.lower().strip()]
        return faculty_list

    @staticmethod
    def update_faculty(faculty_id: str, name: str = None, email: str = None,
                       department: str = None, title: str = None):
        """Update faculty member details."""
        with db._lock:
            fid = str(faculty_id).strip()
            if fid not in db.faculty:
                raise ValueError(f"Faculty '{fid}' not found.")

            f = db.faculty[fid]
            new_name = name.strip() if name is not None else f["name"]
            new_email = email.strip().lower() if email is not None else f["email"]
            new_dept = department.strip() if department is not None else f["department"]
            new_title = title.strip() if title is not None else f["title"]

            updated_obj = Faculty(faculty_id=fid, name=new_name, email=new_email,
                                  department=new_dept, title=new_title)

            for other_id, other_f in db.faculty.items():
                if other_id != fid and other_f["email"] == updated_obj.email:
                    raise ValueError(f"Faculty with email '{updated_obj.email}' already exists.")

            f.update(updated_obj.to_dict())
            return f

    @staticmethod
    def delete_faculty(faculty_id: str):
        """Delete faculty member ensuring they are not currently assigned to courses."""
        with db._lock:
            fid = str(faculty_id).strip()
            if fid not in db.faculty:
                raise ValueError(f"Faculty '{fid}' not found.")

            assigned_courses = [c for c in db.courses.values() if c["faculty_id"] == fid]
            if assigned_courses:
                raise ValueError(f"Cannot delete faculty '{fid}' assigned to active courses.")

            del db.faculty[fid]
            return True


class CourseService:
    """Manages course catalog and scheduling."""

    @staticmethod
    def add_course(course_id: str, course_name: str, faculty_id: str,
                   credits: int, semester: int = 1, schedule: str = "TBA"):
        """Add a course to catalog after verifying assigned faculty exists."""
        with db._lock:
            fid = str(faculty_id).strip()
            if fid not in db.faculty:
                raise ValueError(f"Assigned faculty '{fid}' does not exist.")

            course_obj = Course(course_id=course_id, course_name=course_name,
                                faculty_id=fid, credits=credits,
                                semester=semester, schedule=schedule)

            if course_obj.course_id in db.courses:
                raise ValueError(f"Course with ID '{course_obj.course_id}' already exists.")

            record = course_obj.to_dict()
            db.courses[course_obj.course_id] = record
            return record

    @staticmethod
    def get_course(course_id: str):
        """Retrieve course by ID."""
        with db._lock:
            return db.courses.get(str(course_id).strip())

    @staticmethod
    def list_courses(semester: int = None, department: str = None, query: str = None):
        """Search and list courses."""
        with db._lock:
            courses = list(db.courses.values())

        if semester is not None:
            courses = [c for c in courses if c["semester"] == int(semester)]
        if query:
            q = query.lower().strip()
            courses = [
                c for c in courses
                if q in c["course_name"].lower() or q in c["course_id"].lower()
            ]
        return courses

    @staticmethod
    def update_course(course_id: str, course_name: str = None, faculty_id: str = None,
                      credits: int = None, semester: int = None, schedule: str = None):
        """Update existing course details."""
        with db._lock:
            cid = str(course_id).strip()
            if cid not in db.courses:
                raise ValueError(f"Course '{cid}' not found.")

            c = db.courses[cid]
            new_name = course_name.strip() if course_name is not None else c["course_name"]
            new_fid = faculty_id.strip() if faculty_id is not None else c["faculty_id"]
            if new_fid not in db.faculty:
                raise ValueError(f"Assigned faculty '{new_fid}' does not exist.")

            new_credits = int(credits) if credits is not None else c["credits"]
            new_sem = int(semester) if semester is not None else c["semester"]
            new_sched = schedule.strip() if schedule is not None else c["schedule"]

            updated_obj = Course(course_id=cid, course_name=new_name, faculty_id=new_fid,
                                 credits=new_credits, semester=new_sem, schedule=new_sched)

            c.update(updated_obj.to_dict())
            return c

    @staticmethod
    def delete_course(course_id: str):
        """Delete course from catalog if no active student enrollments exist."""
        with db._lock:
            cid = str(course_id).strip()
            if cid not in db.courses:
                raise ValueError(f"Course '{cid}' not found.")

            active_enrollments = [
                e for e in db.enrollments
                if e["course_id"] == cid and e["status"] == "ENROLLED"
            ]
            if active_enrollments:
                raise ValueError(f"Cannot delete course '{cid}' with active student enrollments.")

            del db.courses[cid]
            return True


class EnrollmentService:
    """Encapsulates student enrollment, credit caps, and conflict checking."""

    @staticmethod
    def enroll_student(student_id: str, course_id: str):
        """Enroll a student in a course enforcing all enterprise business rules.

        Business Rules:
        1. Student must exist in system.
        2. Course must exist in catalog.
        3. Student cannot enroll in the same course twice.
        4. Maximum 18 credits allowed per semester.
        5. Reject enrollment if course credits would exceed 18-credit limit.
        6. Reject enrollment if schedule conflicts with another course in the same semester.
        """
        with db._lock:
            sid = str(student_id).strip()
            cid = str(course_id).strip()

            student = db.students.get(sid)
            if not student:
                raise ValueError(f"Student '{sid}' not found.")

            course = db.courses.get(cid)
            if not course:
                raise ValueError(f"Course '{cid}' not found.")

            target_semester = course["semester"]

            # Rule 1 & 2: Active enrollments for this student in target semester
            student_semester_enrollments = [
                e for e in db.enrollments
                if e["student_id"] == sid and e["status"] == "ENROLLED"
            ]

            # Rule 3: Check duplicate enrollment
            for e in student_semester_enrollments:
                if e["course_id"] == cid:
                    raise ValueError(f"Student '{sid}' is already enrolled in course '{cid}'.")

            # Check semester specific active courses
            active_semester_courses = []
            for e in student_semester_enrollments:
                enrolled_course = db.courses.get(e["course_id"])
                if enrolled_course and enrolled_course["semester"] == target_semester:
                    active_semester_courses.append(enrolled_course)

            # Rule 4 & 5: Semester credit limitation (Max 18 credits)
            current_credits = sum(c["credits"] for c in active_semester_courses)
            projected_credits = current_credits + course["credits"]

            if projected_credits > MAX_SEMESTER_CREDITS:
                raise ValueError(
                    f"Enrollment rejected: Credit limit exceeded for semester {target_semester}. "
                    f"Current credits: {current_credits}, Course credits: {course['credits']}, "
                    f"Projected: {projected_credits} (Maximum allowed: {MAX_SEMESTER_CREDITS})."
                )

            # Rule 6: Schedule conflict checking
            target_schedule = course.get("schedule", "TBA").strip()
            if target_schedule and target_schedule != "TBA":
                for existing_c in active_semester_courses:
                    existing_schedule = existing_c.get("schedule", "TBA").strip()
                    if existing_schedule and existing_schedule != "TBA" and existing_schedule == target_schedule:
                        raise ValueError(
                            f"Schedule conflict detected: Course '{cid}' conflicts with enrolled course "
                            f"'{existing_c['course_id']}' at '{target_schedule}'."
                        )

            # Validated: Record enrollment
            enrollment_id = f"ENR-{len(db.enrollments) + 1:04d}"
            enrollment_record = {
                "enrollment_id": enrollment_id,
                "student_id": sid,
                "course_id": cid,
                "semester": target_semester,
                "enrolled_at": datetime.now(timezone.utc).isoformat(),
                "status": "ENROLLED"
            }
            db.enrollments.append(enrollment_record)
            return enrollment_record

    @staticmethod
    def drop_course(student_id: str, course_id: str):
        """Drop an enrolled course for a student."""
        with db._lock:
            sid = str(student_id).strip()
            cid = str(course_id).strip()

            active_enrollment = None
            for e in db.enrollments:
                if e["student_id"] == sid and e["course_id"] == cid and e["status"] == "ENROLLED":
                    active_enrollment = e
                    break

            if not active_enrollment:
                raise ValueError(f"No active enrollment found for student '{sid}' in course '{cid}'.")

            active_enrollment["status"] = "DROPPED"
            return active_enrollment

    @staticmethod
    def list_enrollments(student_id: str = None, course_id: str = None, semester: int = None):
        """List enrollments with optional filtering."""
        with db._lock:
            enrollments = [dict(e) for e in db.enrollments]

        if student_id:
            enrollments = [e for e in enrollments if e["student_id"] == str(student_id).strip()]
        if course_id:
            enrollments = [e for e in enrollments if e["course_id"] == str(course_id).strip()]
        if semester is not None:
            enrollments = [e for e in enrollments if e["semester"] == int(semester)]
        return enrollments


class GradeService:
    """Manages academic grades, marks conversion, and GPA computation."""

    @staticmethod
    def add_grade(student_id: str, course_id: str, grade: str, semester: int = None):
        """Record grade for an enrolled student course."""
        with db._lock:
            sid = str(student_id).strip()
            cid = str(course_id).strip()

            student = db.students.get(sid)
            if not student:
                raise ValueError(f"Student '{sid}' not found.")

            course = db.courses.get(cid)
            if not course:
                raise ValueError(f"Course '{cid}' not found.")

            # Validate enrollment
            has_enrolled = any(
                e["student_id"] == sid and e["course_id"] == cid
                for e in db.enrollments
            )
            if not has_enrolled:
                raise ValueError(f"Student '{sid}' is not enrolled in course '{cid}'.")

            course_semester = semester if semester is not None else course["semester"]

            # Validate letter grade and points
            grade_obj = Grade(
                grade_id=f"GRD-{len(db.grades) + 1:04d}",
                student_id=sid,
                course_id=cid,
                grade=grade,
                semester=course_semester
            )

            # Check if grade already exists for this student & course; update if so
            for existing_g in db.grades:
                if existing_g["student_id"] == sid and existing_g["course_id"] == cid:
                    existing_g["grade"] = grade_obj.grade
                    existing_g["grade_points"] = grade_obj.grade_points
                    existing_g["semester"] = grade_obj.semester
                    return existing_g

            record = grade_obj.to_dict()
            db.grades.append(record)
            return record

    @staticmethod
    def get_grades(student_id: str = None, course_id: str = None):
        """Retrieve grades for a student or course."""
        with db._lock:
            grades = [dict(g) for g in db.grades]

        if student_id:
            grades = [g for g in grades if g["student_id"] == str(student_id).strip()]
        if course_id:
            grades = [g for g in grades if g["course_id"] == str(course_id).strip()]
        return grades

    @staticmethod
    def calculate_gpa(student_id: str, semester: int = None) -> dict:
        """Calculate Cumulative or Semester Grade Point Average (GPA).

        GPA Formula: Sum(GradePoints * CourseCredits) / Sum(CourseCredits)
        Standard scale: A=4.0, B=3.0, C=2.0, D=1.0, F=0.0.
        """
        with db._lock:
            sid = str(student_id).strip()
            student = db.students.get(sid)
            if not student:
                raise ValueError(f"Student '{sid}' not found.")

            student_grades = [g for g in db.grades if g["student_id"] == sid]
            if semester is not None:
                student_grades = [g for g in student_grades if g["semester"] == int(semester)]

            total_quality_points = 0.0
            total_credits = 0
            breakdown = []

            for g in student_grades:
                course = db.courses.get(g["course_id"])
                credits = course["credits"] if course else 3
                quality_points = g["grade_points"] * credits
                total_quality_points += quality_points
                total_credits += credits

                breakdown.append({
                    "course_id": g["course_id"],
                    "course_name": course["course_name"] if course else "Unknown",
                    "grade": g["grade"],
                    "grade_points": g["grade_points"],
                    "credits": credits,
                    "quality_points": quality_points,
                    "semester": g["semester"]
                })

            gpa = round(total_quality_points / total_credits, 2) if total_credits > 0 else 0.0

            return {
                "student_id": sid,
                "student_name": student["name"],
                "department": student["department"],
                "gpa": gpa,
                "total_graded_credits": total_credits,
                "semester_filter": semester,
                "courses_evaluated": breakdown
            }


# Backwards-compatible aliases and unified service interface
AcademicService = StudentService
# Attach cross-cutting methods onto StudentService for single import convenience
StudentService.enroll_student = staticmethod(EnrollmentService.enroll_student)
StudentService.drop_course = staticmethod(EnrollmentService.drop_course)
StudentService.list_enrollments = staticmethod(EnrollmentService.list_enrollments)
StudentService.add_faculty = staticmethod(FacultyService.add_faculty)
StudentService.get_faculty = staticmethod(FacultyService.get_faculty)
StudentService.list_faculty = staticmethod(FacultyService.list_faculty)
StudentService.update_faculty = staticmethod(FacultyService.update_faculty)
StudentService.delete_faculty = staticmethod(FacultyService.delete_faculty)
StudentService.add_course = staticmethod(CourseService.add_course)
StudentService.get_course = staticmethod(CourseService.get_course)
StudentService.list_courses = staticmethod(CourseService.list_courses)
StudentService.update_course = staticmethod(CourseService.update_course)
StudentService.delete_course = staticmethod(CourseService.delete_course)
StudentService.add_grade = staticmethod(GradeService.add_grade)
StudentService.get_grades = staticmethod(GradeService.get_grades)
StudentService.calculate_gpa = staticmethod(GradeService.calculate_gpa)
