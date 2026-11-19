from __future__ import annotations

import streamlit as st

import student_backend as project


st.set_page_config(page_title="Student Academic Management System", layout="wide")

st.html("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #f1f5f9;
    background-image: linear-gradient(rgba(241,245,249,.94), rgba(241,245,249,.98));
}
[data-testid="stSidebar"] { background-color: #e4edf7; border-right: 1px solid #cbd5e1; }
.academic-banner {
    padding: clamp(24px, 5vw, 56px); margin-bottom: 20px; border-radius: 16px;
    color: white; background: linear-gradient(110deg, #102a43, #176b70);
}
.academic-banner h1 { color: white; font-size: clamp(1.8rem, 4vw, 3rem); line-height: 1.15; margin: 0; }
[data-testid="stForm"], [data-testid="stMetric"], [data-testid="stExpander"] {
    background: white; border: 1px solid #d5dee8; border-radius: 12px;
}
[data-testid="stMetric"] { padding: 16px; }
[data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button {
    background: #0f766e; color: white; border: 1px solid #0f766e; border-radius: 8px;
}
[data-testid="stButton"] button:hover, [data-testid="stFormSubmitButton"] button:hover {
    background: #115e59; color: white;
}
</style>
<div class="academic-banner"><h1>Student Academic Management System</h1></div>
""")

store = project.StudentStore()
loaded = store.load()

if loaded.read_error:
    st.error(loaded.read_error)
    st.info("The file could not be read. The application is in read-only mode until the storage issue is resolved.")
    st.stop()

if loaded.issues:
    st.error("Some rows were rejected. Editing is disabled until you explicitly recover the accepted rows.")
    for issue in loaded.issues:
        st.write(f"Row {issue.row}: {issue.reason}")
    st.caption(f"Recovery first preserves the complete original file as `{store.recovery_backup_path.name}`. Rejected rows remain in that recovery backup for manual review.")
    if st.button("Back up file and recover accepted rows"):
        try:
            recovered, backup = store.recover()
            st.success(f"Recovered {len(recovered.students)} valid record(s). Original file saved to {backup}.")
            st.rerun()
        except (OSError, ValueError, project.DataIntegrityError) as error:
            st.error(f"Recovery failed; the original data file was preserved: {error}")

students = loaded.students
read_only = bool(loaded.issues)

menu = [
    "Register Student",
    "View Course and Subject Catalogue",
    "Enter / Update Marks",
    "Update Attendance",
    "Search Student / View Report",
    "Identify Topper(s)",
    "Student Rankings",
    "Low-Performing Students",
    "Academic Summary",
]
page = st.sidebar.radio("Choose an option", menu, key="menu_option")


def save_error_message(error: Exception) -> None:
    st.error(f"Change was not saved: {error}")
    st.caption("The previous file and the currently displayed records remain unchanged.")


def ranking_rows():
    rows = []
    for rank, student in project.rank_students(students):
        average = student.average()
        rows.append({
            "Rank": rank,
            "Student ID": student.student_id,
            "Name": student.name,
            "Programme": student.course,
            "Entered-mark average": f"{average:.2f}",
            "Grade": student.grade(),
            "Assessment": project._report_status(student),
        })
    return rows


def show_toppers():
    ranked = project.rank_students(students)
    if not ranked:
        st.info("No assessed students are available yet.")
        return
    st.caption("Topper comparison uses entered-mark averages and is provisional across different courses and subject sets.")
    highest = ranked[0][1].average()
    for _, student in ranked:
        if student.average() != highest:
            break
        st.success(f"{student.name} ({student.student_id}) · {highest:.2f} · {project._report_status(student)}")


if page == "Register Student":
    st.header(page)
    course = st.selectbox("Programme", list(project.courses))
    st.caption("Subjects: " + ", ".join(project.courses[course]))
    with st.form("register_student"):
        student_id = st.text_input("Student ID")
        name = st.text_input("Student name")
        submitted = st.form_submit_button("Register Student", disabled=read_only)
    if submitted:
        try:
            store.add_student(student_id, name, course)
            st.success(f"{name.strip()} registered and saved in {course}.")
            st.rerun()
        except (ValueError, OSError, project.DataIntegrityError) as error:
            save_error_message(error)

elif page == "View Course and Subject Catalogue":
    st.header("Course and Subject Catalogue")
    st.caption(f"Fixed catalogue · {len(project.courses)} programmes. Courses and subjects are predefined and cannot be edited in this application.")
    for number, (course, subjects) in enumerate(project.courses.items(), start=1):
        with st.expander(f"{number}. {course}"):
            st.write(" · ".join(subjects))

elif page in ("Enter / Update Marks", "Update Attendance", "Search Student / View Report"):
    st.header(page)
    if not students:
        st.info("No accepted student records are available.")
        st.stop()
    student_id = st.selectbox(
        "Select a student",
        sorted(students),
        format_func=lambda sid: f"{sid} — {students[sid].name}",
    )
    student = students[student_id]
    st.write(f"**Programme:** {student.course}")

    if page == "Enter / Update Marks":
        subject_options = list(project.courses[student.course])
        subject_options.extend(subject for subject in student.marks if subject not in subject_options)
        subject = st.selectbox("Subject", subject_options, key=f"subject_{student_id}")
        with st.form(f"marks_{student_id}_{subject}"):
            mark = st.number_input("Marks (0–100)", min_value=0.0, max_value=100.0, value=float(student.marks.get(subject, 0)))
            submitted = st.form_submit_button("Save Marks", disabled=read_only)
        if submitted:
            try:
                store.update_mark(student_id, subject, mark)
                st.success(f"Marks for {subject} saved successfully.")
                st.rerun()
            except (ValueError, OSError, project.DataIntegrityError) as error:
                save_error_message(error)

    elif page == "Update Attendance":
        with st.form(f"attendance_{student_id}"):
            total = st.number_input("Total classes", min_value=0, value=student.total_classes, step=1)
            attended = st.number_input("Classes attended", min_value=0, value=student.attended_classes, step=1)
            submitted = st.form_submit_button("Save Attendance", disabled=read_only)
        if submitted:
            try:
                store.update_attendance(student_id, int(attended), int(total))
                st.success("Attendance saved successfully.")
                st.rerun()
            except (ValueError, OSError, project.DataIntegrityError) as error:
                save_error_message(error)

    else:
        st.subheader(f"{student.name} ({student.student_id})")
        average_value = student.average()
        attendance_value = student.attendance()
        average_col, grade_col, attendance_col = st.columns(3)
        average_col.metric("Entered-mark average", f"{average_value:.2f}" if average_value is not None else "N/A")
        grade_col.metric("Grade", student.grade())
        attendance_col.metric("Attendance", f"{attendance_value:.2f}%" if attendance_value is not None else "Not recorded")
        st.caption(project._report_status(student))
        st.write(f"Classes attended · {student.attended_classes}/{student.total_classes}")
        if student.marks:
            st.table([{"Subject": subject, "Marks": f"{mark:g}"} for subject, mark in student.marks.items()])
        else:
            st.info("Marks not recorded.")

elif page in ("Identify Topper(s)", "Student Rankings", "Low-Performing Students", "Academic Summary"):
    st.header(page)
    if page == "Identify Topper(s)":
        show_toppers()
    elif page == "Student Rankings":
        st.caption("Provisional overall comparison: averages use marks entered so far. Different course or subject sets are not directly comparable as final results.")
        rows = ranking_rows()
        st.dataframe(rows, use_container_width=True, hide_index=True) if rows else st.info("No assessed students are available yet.")
    elif page == "Low-Performing Students":
        rows = [row for row in ranking_rows() if float(row["Entered-mark average"]) < 50]
        st.caption("Rule: assessed average below 50. Students with no marks are excluded.")
        st.dataframe(rows, use_container_width=True, hide_index=True) if rows else st.info("No assessed students have an average below 50.")
    else:
        total, programmes, assessed, unassessed = st.columns(4)
        total.metric("Students", len(students))
        programmes.metric("Programmes represented", len({student.course for student in students.values()}))
        assessed.metric("With marks", sum(bool(student.marks) for student in students.values()))
        unassessed.metric("Without marks", sum(not student.marks for student in students.values()))
        st.caption("Overall averages and rankings are provisional, use entered marks only, and may compare different subject sets.")
        rows = ranking_rows()
        if rows:
            st.subheader("Provisional rankings")
            st.dataframe(rows, use_container_width=True, hide_index=True)
            st.subheader("Topper(s)")
            show_toppers()
            st.subheader("Low performers · average below 50")
            low = [row for row in rows if float(row["Entered-mark average"]) < 50]
            st.dataframe(low, use_container_width=True, hide_index=True) if low else st.info("No assessed students have an average below 50.")
        else:
            st.info("No assessed students are available yet.")
