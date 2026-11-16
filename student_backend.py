"""Student academic management model, reliable text storage, and CLI."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
import math
import os
from pathlib import Path
import shutil
import tempfile


DATA_FILE = Path(__file__).resolve().with_name("plain.txt")
BACKUP_FILE = DATA_FILE.with_suffix(DATA_FILE.suffix + ".bak")
LOCK_FILE = DATA_FILE.with_suffix(DATA_FILE.suffix + ".lock")

courses = {
    "B.Tech CSE": (
        "Python", "SQL", "Maths", "DBMS", "Data Structures",
        "Operating Systems", "Computer Networks", "Software Engineering",
        "Web Development", "Cloud Computing",
    ),
    "B.Tech IT": (
        "Python", "SQL", "Maths", "DBMS", "Computer Networks",
        "Operating Systems", "Web Development", "Information Security",
        "Cloud Computing", "IT Project Management",
    ),
    "B.Tech AI": (
        "Python", "SQL", "Maths", "DBMS", "Machine Learning",
        "Probability and Statistics", "Deep Learning",
        "Natural Language Processing", "Computer Vision", "AI Ethics",
    ),
    "Chemical Engineering": (
        "Heat Transfer", "Thermodynamic", "Chemical Reaction",
        "Fluid Mechanics", "Mass Transfer", "Process Control",
        "Plant Design", "Process Safety",
    ),
    "B.Tech Data Science": (
        "Python", "SQL", "Linear Algebra", "Statistics",
        "Data Visualization", "Machine Learning", "Big Data Analytics",
        "Data Engineering", "Time Series Analysis",
    ),
    "B.Tech Cyber Security": (
        "Python", "Operating Systems", "Computer Networks",
        "Cryptography", "Network Security", "Ethical Hacking",
        "Digital Forensics", "Secure Coding", "Incident Response",
    ),
    "B.Tech ECE": (
        "Circuit Theory", "Analog Electronics", "Digital Electronics",
        "Signals and Systems", "Communication Systems", "Microprocessors",
        "VLSI Design", "Embedded Systems",
    ),
    "B.Tech EEE": (
        "Circuit Theory", "Electrical Machines", "Power Systems",
        "Power Electronics", "Control Systems", "Electrical Measurements",
        "Renewable Energy", "Electric Drives",
    ),
    "B.Tech Mechanical Engineering": (
        "Engineering Mechanics", "Engineering Drawing", "Thermodynamics",
        "Fluid Mechanics", "Heat Transfer", "Manufacturing Technology",
        "Machine Design", "CAD and CAM",
    ),
    "B.Tech Civil Engineering": (
        "Engineering Mechanics", "Surveying", "Structural Analysis",
        "Geotechnical Engineering", "Concrete Technology",
        "Transportation Engineering", "Environmental Engineering",
        "Construction Management",
    ),
    "B.Tech Biotechnology": (
        "Cell Biology", "Biochemistry", "Microbiology", "Genetics",
        "Molecular Biology", "Bioprocess Engineering", "Immunology",
        "Bioinformatics",
    ),
    "B.Tech Robotics and Automation": (
        "Python", "Engineering Mechanics", "Control Systems",
        "Sensors and Actuators", "Embedded Systems", "Robot Kinematics",
        "Industrial Automation", "Computer Vision",
    ),
    "B.Sc Computer Science": (
        "Python", "C Programming", "Data Structures", "DBMS",
        "Operating Systems", "Computer Networks", "Web Development",
    ),
    "B.Sc Mathematics": (
        "Calculus", "Linear Algebra", "Differential Equations",
        "Probability", "Numerical Methods", "Real Analysis", "Abstract Algebra",
    ),
    "B.Sc Physics": (
        "Classical Mechanics", "Optics", "Electromagnetism", "Thermodynamics",
        "Quantum Mechanics", "Electronics", "Experimental Physics",
    ),
    "B.Sc Chemistry": (
        "Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry",
        "Analytical Chemistry", "Environmental Chemistry", "Industrial Chemistry",
        "Laboratory Techniques",
    ),
    "B.Sc Statistics": (
        "Probability", "Descriptive Statistics", "Statistical Inference",
        "Regression Analysis", "Sampling Methods", "Design of Experiments",
        "Time Series Analysis",
    ),
    "BCA": (
        "C Programming", "Python", "Java", "Data Structures", "DBMS",
        "Computer Networks", "Web Development", "Software Engineering",
    ),
    "MCA": (
        "Advanced Java", "Python", "Advanced DBMS",
        "Design and Analysis of Algorithms", "Web Application Development",
        "Cloud Computing", "Software Testing", "Information Security",
    ),
    "B.Com General": (
        "Financial Accounting", "Business Economics", "Business Law",
        "Corporate Accounting", "Cost Accounting", "Income Tax", "Auditing",
        "Business Communication",
    ),
    "B.Com Computer Applications": (
        "Financial Accounting", "Business Economics", "Business Law",
        "Computerized Accounting", "SQL", "E-Commerce",
        "Spreadsheet Applications", "Web Design",
    ),
    "BBA": (
        "Principles of Management", "Business Communication",
        "Marketing Management", "Human Resource Management",
        "Financial Management", "Operations Management", "Entrepreneurship",
    ),
    "B.A. English": (
        "British Literature", "Indian Writing in English", "American Literature",
        "Literary Criticism", "Linguistics", "Creative Writing",
        "Communication Skills",
    ),
    "B.A. Economics": (
        "Microeconomics", "Macroeconomics", "Public Finance",
        "Development Economics", "International Economics",
        "Statistics for Economics", "Econometrics",
    ),
}


class DataIntegrityError(Exception):
    """Raised when a damaged source file needs explicit recovery first."""


@dataclass
class Student:
    student_id: str
    name: str
    course: str
    marks: dict[str, float] = field(default_factory=dict)
    attended_classes: int = 0
    total_classes: int = 0

    def average(self) -> float | None:
        if not self.marks:
            return None
        return sum(self.marks.values()) / len(self.marks)

    def grade(self) -> str:
        average = self.average()
        if average is None:
            return "Not Available"
        for minimum, grade in ((90, "A+"), (80, "A"), (70, "B"), (60, "C"), (50, "D")):
            if average >= minimum:
                return grade
        return "F"

    def attendance(self) -> float | None:
        if self.total_classes == 0:
            return None
        return self.attended_classes / self.total_classes * 100

    def assessed_required_subjects(self) -> int:
        required = {subject.casefold() for subject in courses[self.course]}
        return sum(subject.casefold() in required for subject in self.marks)

    def expected_subjects(self) -> int:
        return len(courses[self.course])

    def assessment_complete(self) -> bool:
        marked = {subject.casefold() for subject in self.marks}
        required = {subject.casefold() for subject in courses[self.course]}
        return bool(required) and required.issubset(marked)


@dataclass(frozen=True)
class LoadIssue:
    row: int
    reason: str


@dataclass
class LoadResult:
    students: dict[str, Student] = field(default_factory=dict)
    issues: list[LoadIssue] = field(default_factory=list)
    file_exists: bool = False
    read_error: str | None = None

    @property
    def can_write(self) -> bool:
        return not self.issues and self.read_error is None


def normalize_student_id(value: str) -> str:
    student_id = value.strip().upper()
    if not student_id or "|" in student_id:
        raise ValueError("Enter a nonblank student ID without the | character.")
    return student_id


def validate_student_fields(student_id: str, name: str, course: str) -> tuple[str, str, str]:
    student_id = normalize_student_id(student_id)
    name = name.strip()
    if not name or "|" in name:
        raise ValueError("Enter a nonblank student name without the | character.")
    course = course.strip()
    canonical_course = next((item for item in courses if item.casefold() == course.casefold()), None)
    if canonical_course is None:
        raise ValueError("Choose a course from the available catalogue.")
    return student_id, name, canonical_course


def validate_subject(subject: str) -> str:
    subject = subject.strip()
    if not subject or any(character in subject for character in "|;:"):
        raise ValueError("Enter a subject name without |, ;, or : characters.")
    return subject


def validate_mark(value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or not 0 <= value <= 100:
        raise ValueError("Marks must be a finite number from 0 to 100.")
    return value


def validate_attendance(attended: int, total: int) -> tuple[int, int]:
    if isinstance(attended, bool) or isinstance(total, bool):
        raise ValueError("Attendance values must be whole numbers.")
    if not isinstance(attended, int) or not isinstance(total, int):
        raise ValueError("Attendance values must be whole numbers.")
    if total < 0 or attended < 0 or attended > total:
        raise ValueError("Use nonnegative counts, with attended classes no greater than total classes.")
    return attended, total


@contextmanager
def _exclusive_lock(lock_path: Path):
    """Lock across processes on Windows and POSIX systems."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+b") as lock_file:
        if os.name == "nt":
            import msvcrt

            lock_file.seek(0)
            if not lock_file.read(1):
                lock_file.write(b"0")
                lock_file.flush()
            lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


class StudentStore:
    """Shared file-backed service used by both interfaces.

    Every mutation locks, reloads, validates, writes a same-directory temporary
    snapshot, backs up the previous file, and atomically replaces it.
    """

    def __init__(self, path: Path | str = DATA_FILE):
        self.path = Path(path).resolve()
        self.backup_path = self.path.with_suffix(self.path.suffix + ".bak")
        self.recovery_backup_path = self.path.with_suffix(self.path.suffix + ".recovery.bak")
        self.lock_path = self.path.with_suffix(self.path.suffix + ".lock")

    def load(self) -> LoadResult:
        try:
            with _exclusive_lock(self.lock_path):
                return self._read_unlocked()
        except OSError as error:
            return LoadResult(read_error=f"Could not read or lock {self.path}: {error}")

    def _read_unlocked(self) -> LoadResult:
        if not self.path.exists():
            return LoadResult(file_exists=False)
        result = LoadResult(file_exists=True)
        try:
            text = self.path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            result.read_error = f"Could not read {self.path}: {error}"
            return result

        for row_number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                result.issues.append(LoadIssue(row_number, "blank record"))
                continue
            fields = line.split("|")
            if len(fields) != 6:
                result.issues.append(LoadIssue(row_number, f"expected 6 pipe-delimited fields, found {len(fields)}"))
                continue

            raw_id, raw_name, raw_course, marks_text, raw_attended, raw_total = fields
            try:
                student_id, name, course = validate_student_fields(raw_id, raw_name, raw_course)
                if student_id in result.students:
                    raise ValueError(f"duplicate student ID {student_id}")
                attended = int(raw_attended)
                total = int(raw_total)
                validate_attendance(attended, total)

                marks: dict[str, float] = {}
                if marks_text.strip():
                    for item in marks_text.split(";"):
                        if ":" not in item:
                            raise ValueError(f"invalid mark entry {item!r}; expected Subject:mark")
                        raw_subject, raw_mark = item.rsplit(":", 1)
                        subject = validate_subject(raw_subject)
                        key = subject.casefold()
                        if any(existing.casefold() == key for existing in marks):
                            raise ValueError(f"duplicate subject label {subject!r}")
                        catalogue_subject = next(
                            (item for item in courses[course] if item.casefold() == key),
                            subject,
                        )
                        marks[catalogue_subject] = validate_mark(float(raw_mark))
                result.students[student_id] = Student(
                    student_id, name, course, marks, attended, total
                )
            except (ValueError, OverflowError) as error:
                result.issues.append(LoadIssue(row_number, str(error)))
        return result

    def _backup_unlocked(self, target: Path | None = None) -> Path | None:
        if not self.path.exists():
            return None
        target = target or self.backup_path
        descriptor, temp_name = tempfile.mkstemp(
            prefix=f".{target.name}.", suffix=".tmp", dir=self.path.parent
        )
        os.close(descriptor)
        temp_path = Path(temp_name)
        try:
            shutil.copy2(self.path, temp_path)
            os.replace(temp_path, target)
        except OSError:
            temp_path.unlink(missing_ok=True)
            raise
        return target

    def _next_recovery_backup_path(self) -> Path:
        candidate = self.recovery_backup_path
        counter = 1
        while candidate.exists():
            candidate = self.path.with_name(
                f"{self.path.name}.recovery.{counter}.bak"
            )
            counter += 1
        return candidate

    def _write_unlocked(self, students: dict[str, Student]) -> Path | None:
        self._validate_snapshot(students)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temp_name = tempfile.mkstemp(
            prefix=f".{self.path.name}.", suffix=".tmp", dir=self.path.parent
        )
        temp_path = Path(temp_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
                for student in students.values():
                    marks = ";".join(
                        f"{subject}:{mark:g}" for subject, mark in student.marks.items()
                    )
                    output.write(
                        f"{student.student_id}|{student.name}|{student.course}|{marks}|"
                        f"{student.attended_classes}|{student.total_classes}\n"
                    )
                output.flush()
                os.fsync(output.fileno())
            backup = self._backup_unlocked()
            os.replace(temp_path, self.path)
            return backup
        except OSError:
            temp_path.unlink(missing_ok=True)
            raise

    @staticmethod
    def _validate_snapshot(students: dict[str, Student]) -> None:
        normalized_ids: set[str] = set()
        for student in students.values():
            sid, name, course = validate_student_fields(
                student.student_id, student.name, student.course
            )
            if (
                sid != student.student_id
                or name != student.name
                or course != student.course
                or sid in normalized_ids
            ):
                raise ValueError("Student IDs in the save snapshot must be unique and normalized.")
            normalized_ids.add(sid)
            validate_attendance(student.attended_classes, student.total_classes)
            seen_subjects: set[str] = set()
            for subject, mark in student.marks.items():
                label = validate_subject(subject)
                if label != subject:
                    raise ValueError(f"Subject label {subject!r} must not include surrounding spaces.")
                key = label.casefold()
                if key in seen_subjects:
                    raise ValueError(f"Duplicate subject label {label!r} in save snapshot.")
                seen_subjects.add(key)
                validate_mark(mark)

    def _transaction(self, change) -> LoadResult:
        with _exclusive_lock(self.lock_path):
            current = self._read_unlocked()
            if current.read_error:
                raise OSError(current.read_error)
            if current.issues:
                raise DataIntegrityError(
                    "The data file contains rejected rows. Review them and use explicit recovery before editing."
                )
            updated = {key: Student(**vars(value)) for key, value in current.students.items()}
            change(updated)
            self._write_unlocked(updated)
            return LoadResult(students=updated, file_exists=True)

    def add_student(self, student_id: str, name: str, course: str) -> LoadResult:
        student_id, name, course = validate_student_fields(student_id, name, course)

        def change(students):
            if student_id in students:
                raise ValueError(f"Student ID {student_id} already exists.")
            students[student_id] = Student(student_id, name, course)

        return self._transaction(change)

    def update_mark(self, student_id: str, subject: str, mark: float) -> LoadResult:
        student_id = normalize_student_id(student_id)
        subject = validate_subject(subject)
        mark = validate_mark(mark)

        def change(students):
            student = students.get(student_id)
            if student is None:
                raise ValueError(f"Student {student_id} was not found.")
            options = list(courses[student.course]) + list(student.marks)
            canonical = next((item for item in options if item.casefold() == subject.casefold()), subject)
            student.marks[canonical] = mark

        return self._transaction(change)

    def update_attendance(self, student_id: str, attended: int, total: int) -> LoadResult:
        student_id = normalize_student_id(student_id)
        attended, total = validate_attendance(attended, total)

        def change(students):
            student = students.get(student_id)
            if student is None:
                raise ValueError(f"Student {student_id} was not found.")
            student.attended_classes = attended
            student.total_classes = total

        return self._transaction(change)

    def recover(self) -> tuple[LoadResult, Path]:
        """Explicitly keep valid rows and back up the complete original source."""
        with _exclusive_lock(self.lock_path):
            current = self._read_unlocked()
            if current.read_error:
                raise OSError(current.read_error)
            if not current.issues:
                raise ValueError("No damaged rows were found; recovery is not needed.")
            backup = self._backup_unlocked(self._next_recovery_backup_path())
            if backup is None:
                raise OSError("The original file could not be backed up.")
            self._write_unlocked_without_backup(current.students)
            return LoadResult(students=current.students, file_exists=True), backup

    def _write_unlocked_without_backup(self, students: dict[str, Student]) -> None:
        self._validate_snapshot(students)
        descriptor, temp_name = tempfile.mkstemp(
            prefix=f".{self.path.name}.", suffix=".tmp", dir=self.path.parent
        )
        temp_path = Path(temp_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
                for student in students.values():
                    marks = ";".join(
                        f"{subject}:{mark:g}" for subject, mark in student.marks.items()
                    )
                    output.write(
                        f"{student.student_id}|{student.name}|{student.course}|{marks}|"
                        f"{student.attended_classes}|{student.total_classes}\n"
                    )
                output.flush()
                os.fsync(output.fileno())
            os.replace(temp_path, self.path)
        except OSError:
            temp_path.unlink(missing_ok=True)
            raise


def rank_students(students: dict[str, Student]) -> list[tuple[int, Student]]:
    """Return competition ranks (1, 1, 3) for equal entered-mark averages."""
    ranked = sorted(
        (student for student in students.values() if student.marks),
        key=lambda student: (-student.average(), student.student_id),
    )
    output: list[tuple[int, Student]] = []
    previous_average = None
    previous_rank = 0
    for position, student in enumerate(ranked, start=1):
        average = student.average()
        if average != previous_average:
            previous_rank = position
            previous_average = average
        output.append((previous_rank, student))
    return output


def _report_status(student: Student) -> str:
    if not student.marks:
        return "Not assessed"
    status = "Complete" if student.assessment_complete() else "Provisional"
    return f"{status} ({student.assessed_required_subjects()}/{student.expected_subjects()} required subjects assessed)"


def show_course_catalogue() -> None:
    print(f"\n--- FIXED COURSE AND SUBJECT CATALOGUE ({len(courses)} programmes) ---")
    print("The catalogue is predefined; this application does not edit its courses or subjects.")
    for number, (course, subjects) in enumerate(courses.items(), start=1):
        print(f"{number}. {course}")
        print("   Subjects:", ", ".join(subjects))


def _show_rankings(students: dict[str, Student]) -> None:
    ranked = rank_students(students)
    if not ranked:
        print("No students have marks yet.")
        return
    print("Provisional overall comparison: averages use entered marks only and may cover different subjects.")
    for rank, student in ranked:
        average = student.average()
        print(
            f"{rank}. {student.student_id} | {student.name} | {student.course} | "
            f"Average: {average:.2f} | Grade: {student.grade()} | {_report_status(student)}"
        )


def _show_low_performers(students: dict[str, Student]) -> None:
    found = False
    for _, student in rank_students(students):
        if student.average() < 50:
            found = True
            print(
                f"{student.student_id} | {student.name} | Average: {student.average():.2f} | "
                f"{_report_status(student)}"
            )
    if not found:
        print("No assessed students have an average below 50.")


def _show_student_report(student: Student) -> None:
    print("\n--- STUDENT ACADEMIC REPORT ---")
    print("ID:", student.student_id)
    print("Name:", student.name)
    print("Course:", student.course)
    print("Assessment:", _report_status(student))
    print("Marks:", student.marks if student.marks else "Not recorded")
    average = student.average()
    print("Average:", f"{average:.2f}" if average is not None else "N/A")
    print("Grade:", student.grade())
    attendance = student.attendance()
    print("Attendance:", f"{attendance:.2f}%" if attendance is not None else "Not recorded (0 classes)")
    print(f"Classes attended: {student.attended_classes}/{student.total_classes}")


def run_cli() -> None:
    store = StudentStore()
    loaded = store.load()
    if loaded.read_error:
        print(f"ERROR: {loaded.read_error}")
        print("The data file could not be read. No changes are allowed.")
        return
    if loaded.issues:
        print("The existing data file has rejected rows:")
        for issue in loaded.issues:
            print(f"  Row {issue.row}: {issue.reason}")
        answer = input("Recover valid rows now? The original will be saved as plain.txt.recovery.bak (y/N): ").strip().casefold()
        if answer == "y":
            try:
                loaded, backup = store.recover()
                print(f"Recovery complete. Original source preserved at {backup}.")
            except (OSError, ValueError, DataIntegrityError) as error:
                print(f"Recovery failed; the original file was preserved: {error}")
        else:
            print("Read-only mode: the original file is unchanged. Review and recover it before editing.")
    print(f"Loaded {len(loaded.students)} accepted student record(s) from {store.path}.")

    actions = {
        "1": "Register Student",
        "2": "View Course and Subject Catalogue",
        "3": "Enter / Update Marks",
        "4": "Update Attendance",
        "5": "Search Student / View Report",
        "6": "Identify Topper(s)",
        "7": "Student Rankings",
        "8": "Low-Performing Students",
        "9": "Generate Academic Summary Report",
    }
    while True:
        print("\n===== STUDENT ACADEMIC MANAGEMENT SYSTEM =====")
        for number, label in actions.items():
            print(f"{number}. {label}")
        print("10. Exit")
        choice = input("Enter your choice (1-10): ").strip()
        students = loaded.students

        if choice == "10":
            print("Goodbye. Submitted changes have already been saved.")
            break
        if choice == "2":
            show_course_catalogue()
            continue
        if choice == "1":
            try:
                sid = normalize_student_id(input("Student ID: "))
                name = input("Student name: ").strip()
                show_course_catalogue()
                selected = input("Course number or exact course name: ").strip()
                course_list = list(courses)
                course = course_list[int(selected) - 1] if selected.isdigit() and 1 <= int(selected) <= len(course_list) else selected
                loaded = store.add_student(sid, name, course)
                print(f"Student {sid} registered and saved.")
            except (ValueError, OSError, DataIntegrityError) as error:
                print(f"Registration was not saved: {error}")
            continue
        if choice in ("3", "4", "5"):
            if not students:
                print("No accepted student records are available.")
                continue
            try:
                sid = normalize_student_id(input("Student ID: "))
            except ValueError as error:
                print(error)
                continue
            student = students.get(sid)
            if student is None:
                print(f"Student {sid} was not found.")
                continue
            if choice == "5":
                _show_student_report(student)
            elif choice == "3":
                subjects = list(courses[student.course])
                subjects.extend(subject for subject in student.marks if subject not in subjects)
                print("Subjects:", ", ".join(subjects))
                subject = input("Subject name: ").strip()
                try:
                    mark = validate_mark(float(input("Marks (0-100): ")))
                    loaded = store.update_mark(sid, subject, mark)
                    print(f"Marks for {subject} saved successfully.")
                except (ValueError, OSError, DataIntegrityError) as error:
                    print(f"Marks were not saved: {error}")
            else:
                try:
                    total = int(input("Total classes: "))
                    attended = int(input("Classes attended: "))
                    loaded = store.update_attendance(sid, attended, total)
                    print("Attendance saved successfully.")
                except (ValueError, OSError, DataIntegrityError) as error:
                    print(f"Attendance was not saved: {error}")
            continue
        if choice in ("6", "7", "8", "9"):
            ranked = rank_students(students)
            if choice == "6":
                if not ranked:
                    print("No marks available to identify a topper.")
                else:
                    highest = ranked[0][1].average()
                    print("Topper(s) by entered-mark average (provisional across different course sets):")
                    for _, student in ranked:
                        if student.average() != highest:
                            break
                        print(f"{student.student_id} | {student.name} | Average: {highest:.2f} | {_report_status(student)}")
            elif choice == "7":
                _show_rankings(students)
            elif choice == "8":
                _show_low_performers(students)
            else:
                print("\n========== ACADEMIC SUMMARY ==========")
                print("Total students:", len(students))
                print("Programmes with enrolled students:", len({student.course for student in students.values()}))
                print("Students with marks:", sum(bool(student.marks) for student in students.values()))
                print("Unassessed students:", sum(not student.marks for student in students.values()))
                print("Overall averages are provisional and use entered marks only.")
                print("\nRankings:")
                _show_rankings(students)
                print("\nLow performers (average below 50):")
                _show_low_performers(students)
            continue
        print("Invalid choice. Enter a number from 1 to 10.")


if __name__ == "__main__":
    run_cli()
