from pathlib import Path

import streamlit as st
import python_project as project

st.set_page_config(page_title="Student Academic Management System", layout="wide")

# Load plain.txt from the project folder.
project.FILE_NAME = Path(__file__).resolve().with_name("plain.txt")
project.students.clear()
project.load_students()

st.html("""
<style>
/* Campus photo with a light overlay so the content stays readable */
[data-testid="stAppViewContainer"] {
    background-color: #f1f5f9;
    background-image:
        linear-gradient(rgba(241, 245, 249, 0.93), rgba(241, 245, 249, 0.97)),
        url("https://www.clarkconstruction.com/sites/default/files/styles/relevant_markets/public/2023-06/Seismic%20Improvement%20Image.jpg?h=0b709920&itok=Yg64twFk");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #e4edf7;
    border-right: 1px solid #cbd5e1;
}

/* Library photo behind the page title */
.academic-banner {
    padding: clamp(24px, 5vw, 56px);
    margin-bottom: 20px;
    border-radius: 16px;
    background-color: #142e4a;
    background-image:
        linear-gradient(90deg, rgba(12, 30, 53, 0.94), rgba(12, 30, 53, 0.65)),
        url("https://www.cervezasalhambra.com/storage/app/uploads/public/653/a4d/306/653a4d306c510249210933.jpg");
    background-size: cover;
    background-position: center;
}

.academic-banner h1 {
    color: white;
    font-size: clamp(1.8rem, 4vw, 3rem);
    line-height: 1.15;
    margin: 0;
    padding: 0;
}

/* Forms, summary metrics, and course expanders */
[data-testid="stForm"],
[data-testid="stMetric"],
[data-testid="stExpander"] {
    background-color: white;
    border: 1px solid #d5dee8;
    border-radius: 12px;
}

[data-testid="stMetric"] {
    padding: 16px;
}

/* Action buttons */
[data-testid="stButton"] button,
[data-testid="stFormSubmitButton"] button {
    background-color: #0f766e;
    color: white;
    border: 1px solid #0f766e;
    border-radius: 8px;
}

[data-testid="stButton"] button:hover,
[data-testid="stFormSubmitButton"] button:hover {
    background-color: #115e59;
    color: white;
}
</style>

<div class="academic-banner">
    <h1>Student Academic Management System</h1>
</div>
""")

menu = [
    "1. Register Student",
    "2. View College Courses and Subjects",
    "3. Enter / Update Marks",
    "4. Update Attendance",
    "5. Search Student / View Report",
    "6. Identify Topper",
    "7. Student Rankings",
    "8. Low-Performing Students",
    "9. Generate Academic Summary Report",
]


def show_rankings(ranked_students):
    st.subheader("Student Rankings")
    if not ranked_students:
        st.info("No students have marks yet.")
        return

    rows = []
    for rank, student in enumerate(ranked_students, start=1):
        rows.append({
            "Rank": rank,
            "Student ID": student.student_id,
            "Name": student.name,
            "Course": student.course,
            "Average": f"{student.average():.2f}",
            "Grade": student.grade(),
        })
    st.table(rows)


def show_toppers(ranked_students):
    st.subheader("Topper(s)")
    if not ranked_students:
        st.info("No marks available to identify a topper.")
        return

    highest = ranked_students[0].average()
    for student in ranked_students:
        if student.average() == highest:
            st.success(
                f"{student.name} ({student.student_id}) · Average {highest:.2f}"
            )


def show_low_performers(ranked_students):
    st.subheader("Low-Performing Students")
    rows = [
        {
            "Student ID": student.student_id,
            "Name": student.name,
            "Average": f"{student.average():.2f}",
        }
        for student in ranked_students
        if student.average() < 50
    ]
    if rows:
        st.table(rows)
    else:
        st.info("No low-performing students found.")


# if st.session_state.get("exited"):
#     st.success("Session ended. Your submitted changes are saved.")
#     if st.button("Reopen App"):
#         st.session_state.exited = False
#         st.rerun()
#     st.stop()

page = st.sidebar.radio("Choose an option", menu, key="menu_option")
option = menu.index(page) + 1

if option == 1:
    st.header("Register Student")

    course = st.selectbox("Course or major", list(project.courses))
    st.write("Subjects — " + ", ".join(project.courses[course]))

    with st.form("register"):
        student_id = st.text_input("Student ID").strip().upper()
        name = st.text_input("Student name").strip()
        submitted = st.form_submit_button("Register Student")

    if submitted:
        if not student_id or not name or "|" in student_id or "|" in name:
            st.error("Enter a valid student ID and name.")
        elif student_id in project.students:
            st.error("Student ID already exists.")
        else:
            project.students[student_id] = project.Student(student_id, name, course)
            project.save_students()
            st.success(f"{name} registered in {course}.")

elif option == 2:
    st.header("College Courses and Subjects")
    st.write(f"{len(project.courses)} programmes and majors available")

    for number, (course, subjects) in enumerate(project.courses.items(), start=1):
        with st.expander(f"{number}. {course}"):
            for subject in subjects:
                st.write(f"• {subject}")

elif option in (3, 4, 5):
    st.header(page)
    if not project.students:
        st.info("Register a student first.")
        st.stop()

    student_id = st.selectbox(
        "Select a student",
        list(project.students),
        format_func=lambda sid: f"{sid} — {project.students[sid].name}",
    )
    student = project.students[student_id]
    st.write(f"**Course** · {student.course}")

    if option == 3:
        subjects = list(project.courses.get(student.course, ()))
        subjects.extend(subject for subject in student.marks if subject not in subjects)

        if not subjects:
            st.info("No subjects are available for this course.")
            st.stop()

        subject = st.selectbox("Subject", subjects, key=f"subject_{student_id}")
        with st.form(f"marks_{student_id}_{subject}"):
            mark = st.number_input(
                "Marks (0–100)",
                min_value=0.0,
                max_value=100.0,
                value=float(student.marks.get(subject, 0)),
            )
            submitted = st.form_submit_button("Save Marks")

        if submitted:
            student.marks[subject] = mark
            project.save_students()
            st.success(f"Saved {mark:g} marks for {subject}.")

    elif option == 4:
        with st.form(f"attendance_{student_id}"):
            total = st.number_input(
                "Total classes", min_value=0, value=student.total_classes
            )
            attended = st.number_input(
                "Classes attended", min_value=0, value=student.attended_classes
            )
            submitted = st.form_submit_button("Save Attendance")

        if submitted:
            if attended > total:
                st.error("Classes attended cannot exceed total classes.")
            else:
                student.total_classes = total
                student.attended_classes = attended
                project.save_students()
                st.success(f"Attendance saved · {student.attendance():.2f}%")

    else:
        st.subheader(f"{student.name} ({student.student_id})")
        average, grade, attendance = st.columns(3)
        average.metric("Average", f"{student.average():.2f}" if student.marks else "—")
        grade.metric("Grade", student.grade())
        attendance.metric("Attendance", f"{student.attendance():.2f}%")
        st.write(f"Classes attended · {student.attended_classes}/{student.total_classes}")

        if student.marks:
            st.table([
                {"Subject": subject, "Marks": f"{mark:g}"}
                for subject, mark in student.marks.items()
            ])
        else:
            st.info("No marks entered yet.")

elif option in (6, 7, 8, 9):
    ranked_students = sorted(
        (student for student in project.students.values() if student.marks),
        key=lambda student: student.average(),
        reverse=True,
    )

    if option == 6:
        show_toppers(ranked_students)
    elif option == 7:
        show_rankings(ranked_students)
    elif option == 8:
        show_low_performers(ranked_students)
    else:
        st.header("Academic Summary")
        total, courses, with_marks = st.columns(3)
        total.metric("Total students", len(project.students))
        courses.metric(
            "Courses with enrolled students",
            len({student.course for student in project.students.values()}),
        )
        with_marks.metric("Students with marks", len(ranked_students))
        show_rankings(ranked_students)
        show_toppers(ranked_students)
        show_low_performers(ranked_students)

# else:
#     st.header("Exit")
#     st.info("Registration, marks, and attendance are saved when you submit each form.")

#     if st.button("End Session"):
#         st.session_state.exited = True
#         del st.session_state["menu_option"]
#         st.rerun()