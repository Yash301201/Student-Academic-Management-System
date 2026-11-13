FILE_NAME = "plain.txt"
students = {}
courses = {
    # Engineering and technology
    "B.Tech CSE": (
        "Python", "SQL", "Maths", "DBMS",
        "Data Structures", "Operating Systems", "Computer Networks",
        "Software Engineering", "Web Development", "Cloud Computing",
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
        "Signals and Systems", "Communication Systems",
        "Microprocessors", "VLSI Design", "Embedded Systems",
    ),
    "B.Tech EEE": (
        "Circuit Theory", "Electrical Machines", "Power Systems",
        "Power Electronics", "Control Systems", "Electrical Measurements",
        "Renewable Energy", "Electric Drives",
    ),
    "B.Tech Mechanical Engineering": (
        "Engineering Mechanics", "Engineering Drawing",
        "Thermodynamics", "Fluid Mechanics", "Heat Transfer",
        "Manufacturing Technology", "Machine Design", "CAD and CAM",
    ),
    "B.Tech Civil Engineering": (
        "Engineering Mechanics", "Surveying", "Structural Analysis",
        "Geotechnical Engineering", "Concrete Technology",
        "Transportation Engineering", "Environmental Engineering",
        "Construction Management",
    ),
    "B.Tech Biotechnology": (
        "Cell Biology", "Biochemistry", "Microbiology", "Genetics",
        "Molecular Biology", "Bioprocess Engineering",
        "Immunology", "Bioinformatics",
    ),
    "B.Tech Robotics and Automation": (
        "Python", "Engineering Mechanics", "Control Systems",
        "Sensors and Actuators", "Embedded Systems", "Robot Kinematics",
        "Industrial Automation", "Computer Vision",
    ),

    # Science and computer applications
    "B.Sc Computer Science": (
        "Python", "C Programming", "Data Structures", "DBMS",
        "Operating Systems", "Computer Networks", "Web Development",
    ),
    "B.Sc Mathematics": (
        "Calculus", "Linear Algebra", "Differential Equations",
        "Probability", "Numerical Methods", "Real Analysis",
        "Abstract Algebra",
    ),
    "B.Sc Physics": (
        "Classical Mechanics", "Optics", "Electromagnetism",
        "Thermodynamics", "Quantum Mechanics", "Electronics",
        "Experimental Physics",
    ),
    "B.Sc Chemistry": (
        "Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry",
        "Analytical Chemistry", "Environmental Chemistry",
        "Industrial Chemistry", "Laboratory Techniques",
    ),
    "B.Sc Statistics": (
        "Probability", "Descriptive Statistics", "Statistical Inference",
        "Regression Analysis", "Sampling Methods",
        "Design of Experiments", "Time Series Analysis",
    ),
    "BCA": (
        "C Programming", "Python", "Java", "Data Structures",
        "DBMS", "Computer Networks", "Web Development",
        "Software Engineering",
    ),
    "MCA": (
        "Advanced Java", "Python", "Advanced DBMS",
        "Design and Analysis of Algorithms", "Web Application Development",
        "Cloud Computing", "Software Testing", "Information Security",
    ),

    # Commerce, management, and humanities
    "B.Com General": (
        "Financial Accounting", "Business Economics", "Business Law",
        "Corporate Accounting", "Cost Accounting", "Income Tax",
        "Auditing", "Business Communication",
    ),
    "B.Com Computer Applications": (
        "Financial Accounting", "Business Economics", "Business Law",
        "Computerized Accounting", "SQL", "E-Commerce",
        "Spreadsheet Applications", "Web Design",
    ),
    "BBA": (
        "Principles of Management", "Business Communication",
        "Marketing Management", "Human Resource Management",
        "Financial Management", "Operations Management",
        "Entrepreneurship",
    ),
    "B.A. English": (
        "British Literature", "Indian Writing in English",
        "American Literature", "Literary Criticism", "Linguistics",
        "Creative Writing", "Communication Skills",
    ),
    "B.A. Economics": (
        "Microeconomics", "Macroeconomics", "Public Finance",
        "Development Economics", "International Economics",
        "Statistics for Economics", "Econometrics",
    ),
}
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
        for minimum, grade in [(90, "A+"), (80, "A"), (70, "B"), (60, "C"), (50, "D")]:
            if self.average() >= minimum:
                return grade
        return "F"
    def attendance(self):
        if self.total_classes == 0:
            return 0
        return self.attended_classes / self.total_classes * 100
def save_students():
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        for s in students.values():
            marks = ";".join(f"{subject}:{mark}" for subject, mark in s.marks.items())
            file.write(
                f"{s.student_id}|{s.name}|{s.course}|{marks}|"
                f"{s.attended_classes}|{s.total_classes}\n"
            )
def load_students():
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            for line in file:
                data = line.rstrip("\n").split("|")
                if len(data) != 6:
                    continue
                sid, name, course, marks_text, attended, total = data
                sid = sid.strip().upper()
                if not sid or not name or not course or sid in students:
                    continue
                s = Student(sid, name, course)
                try:
                    s.attended_classes = int(attended)
                    s.total_classes = int(total)
                    if not 0 <= s.attended_classes <= s.total_classes:
                        continue
                    if marks_text:
                        for item in marks_text.split(";"):
                            subject, value = item.rsplit(":", 1)
                            mark = float(value)
                            if not subject or not 0 <= mark <= 100:
                                raise ValueError
                            s.marks[subject] = mark
                except ValueError:
                    print("Skipped an invalid record in the data file.")
                    continue
                students[sid] = s
    except FileNotFoundError:
        pass
def select_option(options, prompt):
    choice = input(prompt).strip().casefold()
    for number, option in enumerate(options, start=1):
        if choice in (str(number), option.casefold()):
            return option
    return None
def manage_courses_subjects():
    print("\n--- COLLEGE COURSES AND SUBJECTS ---")
    for number, (course, subjects) in enumerate(courses.items(), start=1):
        print(f"{number}. {course}")
        print("   Subjects:", ", ".join(subjects))
def register_student():
    sid = input("Student ID: ").strip().upper()
    if not sid or "|" in sid:
        print("Enter a valid student ID.")
        return
    if sid in students:
        print("Student ID already exists!")
        return
    name = input("Student name: ").strip()
    if not name or "|" in name:
        print("Enter a valid student name.")
        return
    manage_courses_subjects()
    course = select_option(courses, "Select a course number or name: ")
    if course is None:
        print("Invalid course selection.")
        return
    students[sid] = Student(sid, name, course)
    save_students()
    print("Student registered successfully!")
def enter_marks():
    sid = input("Student ID: ").strip().upper()
    s = students.get(sid)
    if s is None:
        print("Student not found! Register the student first.")
        return
    subjects = list(courses.get(s.course, ()))
    subjects.extend(subject for subject in s.marks if subject not in subjects)
    if not subjects:
        print("No subjects are available for this course.")
        return
    print(f"\n--- SUBJECTS FOR {s.course} ---")
    for number, subject in enumerate(subjects, start=1):
        print(f"{number}. {subject}")
    subject = select_option(subjects, "Select a subject number or name: ")
    if subject is None:
        print("Invalid subject selection.")
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
    except ValueError:
        print("Enter whole numbers only!")
        return
    if not 0 <= attended <= total:
        print("Invalid attendance values!")
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
    print("\n--- TOPPER(S) ---")
    for s in ranked:
        if s.average() == highest:
            print(f"{s.name} | {s.student_id} | Average: {s.average():.2f}")
def show_rankings():
    ranked = sorted(
        (s for s in students.values() if s.marks),
        key=lambda s: s.average(), reverse=True
    )
    if not ranked:
        print("No students have marks yet!")
        return
    print("\n--- STUDENT RANKINGS ---")
    for rank, s in enumerate(ranked, start=1):
        print(f"{rank}. {s.name} | {s.course} | Average: {s.average():.2f} | Grade: {s.grade()}")
def show_low_performers():
    print("\n--- LOW-PERFORMING STUDENTS ---")
    low_performers = [s for s in students.values() if s.marks and s.average() < 50]
    for s in low_performers:
        print(f"{s.name} | Average: {s.average():.2f}")
    if not low_performers:
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
    actions = {
        "1": ("Register Student", register_student),
        "2": ("View College Courses and Subjects", manage_courses_subjects),
        "3": ("Enter / Update Marks", enter_marks),
        "4": ("Update Attendance", update_attendance),
        "5": ("Search Student / View Report", search_student),
        "6": ("Identify Topper", show_topper),
        "7": ("Student Rankings", show_rankings),
        "8": ("Low-Performing Students", show_low_performers),
        "9": ("Generate Academic Summary Report", generate_academic_report),
    }
    while True:
        print("\n===== STUDENT ACADEMIC MANAGEMENT SYSTEM =====")
        for number, (label, _) in actions.items():
            print(f"{number}. {label}")
        print("10. Exit\n")
        choice = input("Enter your choice (1-10): ").strip()
        if choice == "10":
            save_students()
            print("All data saved. Goodbye!")
            break
        if choice in actions:
            _, action = actions[choice]
            action()
        else:
            print("Invalid choice! Enter a number from 1 to 10.")
if __name__ == "__main__":
    main()