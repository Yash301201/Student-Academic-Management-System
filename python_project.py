FILE_NAME = "plain.txt"

class Student:
    def __init__(self, student_id, name, course):
        self.student_id = student_id
        self.name = name
        self.course = course
        self.marks = {}
        self.attended_classes = 0
        self.total_classes = 0

    def average(self):
        return sum(self.marks.values()) / len(self.marks) if self.marks else 0

    def grade(self):
        if not self.marks:
            return "Not Available"
        avg = self.average()
        if avg >= 90:
            return "A+"
        elif avg >= 80:
            return "A"
        elif avg >= 70:
            return "B"
        elif avg >= 60:
            return "C"
        elif avg >= 50:
            return "D"
        return "F"

    def attendance(self):
        if self.total_classes == 0:
            return 0
        return self.attended_classes / self.total_classes * 100

students = {}
courses = {}

def save_students():
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        for s in students.values():
            marks = ";".join(
                f"{subject}:{mark}" for subject, mark in s.marks.items()
            )
            file.write(
                f"{s.student_id}|{s.name}|{s.course}|{marks}|"
                f"{s.attended_classes}|{s.total_classes}\n"
            )

def load_students():
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    data = line.rstrip("\n").split("|")
                    if len(data) != 6:
                        continue
                    sid, name, course, marks_text, attended, total = data
                    s = Student(sid.upper(), name, course)
                    if marks_text:
                        for item in marks_text.split(";"):
                            subject, mark = item.rsplit(":", 1)
                            mark = float(mark)
                            if not subject or not 0 <= mark <= 100:
                                raise ValueError
                            s.marks[subject] = mark
                    s.attended_classes = int(attended)
                    s.total_classes = int(total)
                    if (not sid or not name or not course
                            or s.total_classes < 0
                            or s.attended_classes < 0
                            or s.attended_classes > s.total_classes
                            or s.student_id in students):
                        continue
                    students[s.student_id] = s
                    courses.setdefault(course, set()).update(s.marks.keys())
                except (ValueError, TypeError):
                    print("Skipped an invalid record in the data file.")
    except FileNotFoundError:
        pass

def register_student():
    sid = input("Student ID: ").strip().upper()
    if not sid or "|" in sid:
        print("Enter a valid student ID.")
        return
    if sid in students:
        print("Student ID already exists!")
        return
    name = input("Student name: ").strip()
    course = input("Course name: ").strip()
    if not name or not course or any("|" in value for value in (name, course)):
        print("Name and course cannot be empty or contain '|'.")
        return
    students[sid] = Student(sid, name, course)
    courses.setdefault(course, set())
    save_students()
    print("Student registered successfully!")

def manage_courses_subjects():
    course = input("Course name: ").strip()
    if not course or "|" in course:
        print("Enter a valid course name.")
        return
    courses.setdefault(course, set())
    subject = input("Subject name to add: ").strip()
    if not subject or any(c in subject for c in ":;|"):
        print("Enter a valid subject name without : ; or |.")
        return
    courses[course].add(subject)
    print(f"Subject '{subject}' added to course '{course}'.")
    print("Available subjects:", ", ".join(sorted(courses[course])))

def enter_marks():
    sid = input("Student ID: ").strip().upper()
    s = students.get(sid)
    if s is None:
        print("Student not found! Register the student first.")
        return
    subject = input("Subject name: ").strip()
    if not subject or any(c in subject for c in ":;|"):
        print("Enter a valid subject name without : ; or |.")
        return
    try:
        mark = float(input("Marks (0-100): "))
        if not 0 <= mark <= 100:
            print("Marks must be between 0 and 100!")
            return
    except ValueError:
        print("Enter a valid number!")
        return
    s.marks[subject] = mark
    courses.setdefault(s.course, set()).add(subject)
    save_students()
    print("Marks saved successfully!")

def update_attendance():
    sid = input("Student ID: ").strip().upper()
    s = students.get(sid)
    if s is None:
        print("Student not found! Register the student first.")
        return
    try:
        total = int(input("Total classes: "))
        attended = int(input("Classes attended: "))
        if total < 0 or attended < 0 or attended > total:
            print("Invalid attendance values!")
            return
    except ValueError:
        print("Enter whole numbers only!")
        return
    s.total_classes = total
    s.attended_classes = attended
    save_students()
    print("Attendance saved successfully!")

def search_student():
    sid = input("Student ID: ").strip().upper()
    s = students.get(sid)
    if s is None:
        print("Student not found!")
        return
    print("\n--- STUDENT ACADEMIC REPORT ---")
    print("ID:", s.student_id)
    print("Name:", s.name)
    print("Course:", s.course)
    print("Marks:", s.marks if s.marks else "No marks entered")
    print(f"Average: {s.average():.2f}")
    print("Grade:", s.grade())
    print(f"Attendance: {s.attendance():.2f}%")
    print(f"Classes attended: {s.attended_classes}/{s.total_classes}")

def show_topper():
    ranked = [s for s in students.values() if s.marks]
    if not ranked:
        print("No marks available to identify a topper.")
        return
    highest = max(s.average() for s in ranked)
    toppers = [s for s in ranked if s.average() == highest]
    print("\n--- TOPPER(S) ---")
    for s in toppers:
        print(f"{s.name} | {s.student_id} | Average: {s.average():.2f}")

def show_rankings():
    ranked = [s for s in students.values() if s.marks]
    ranked.sort(key=lambda s: s.average(), reverse=True)
    if not ranked:
        print("No students have marks yet!")
        return
    print("\n--- STUDENT RANKINGS ---")
    for rank, s in enumerate(ranked, start=1):
        print(
            f"{rank}. {s.name} | {s.course} | "
            f"Average: {s.average():.2f} | Grade: {s.grade()}"
        )

def show_low_performers():
    found = False
    print("\n--- LOW-PERFORMING STUDENTS ---")
    for s in students.values():
        if s.marks and s.average() < 50:
            print(f"{s.name} | Average: {s.average():.2f}")
            found = True
    if not found:
        print("No low-performing students found!")

def generate_academic_report():
    if not students:
        print("No student records available.")
        return
    print("\n========== ACADEMIC SUMMARY ==========")
    print("Total students:", len(students))
    print("Total courses:", len({s.course for s in students.values()}))
    print("Students with marks:", sum(bool(s.marks) for s in students.values()))
    show_rankings()
    show_topper()
    show_low_performers()

def main():
    load_students()
    print(f"Loaded {len(students)} student record(s).")
    while True:
        print("""
===== STUDENT ACADEMIC MANAGEMENT SYSTEM =====
1. Register Student
2. Course and Subject Management
3. Enter / Update Marks
4. Update Attendance
5. Search Student / View Report
6. Identify Topper
7. Student Rankings
8. Low-Performing Students
9. Generate Academic Summary Report
10. Exit
""")
        choice = input("Enter your choice (1-10): ").strip()
        if choice == "1":
            register_student()
        elif choice == "2":
            manage_courses_subjects()
        elif choice == "3":
            enter_marks()
        elif choice == "4":
            update_attendance()
        elif choice == "5":
            search_student()
        elif choice == "6":
            show_topper()
        elif choice == "7":
            show_rankings()
        elif choice == "8":
            show_low_performers()
        elif choice == "9":
            generate_academic_report()
        elif choice == "10":
            save_students()
            print("All data saved. Goodbye!")
            break
        else:
            print("Invalid choice! Enter a number from 1 to 10.")

if __name__ == "__main__":
    main()
