# Project Architecture and Technical Overview

## Executive overview

**Student Academic Management System** is a Python student-record management application with both a command-line interface and an interactive **Streamlit** web interface. It allows instructors to register students, record subject marks and attendance, calculate academic averages and grades, and review rankings, toppers, low-performing students, and summary metrics. Both interfaces use the same backend logic and file-backed persistence layer.

**Repository:** https://github.com/Yash301201/Student-Academic-Management-System  
**Live demo:** https://yash301201-student-academic-management-sys-streamlit-app-teu5oq.streamlit.app/

## Architecture

```text
                +---------------------+
                |  CLI / Streamlit UI |
                +----------+----------+
                           |
                           v
                +---------------------+
                |  student_backend.py |
                |  Student + Store    |
                |  validation/reports |
                +----------+----------+
                           |
                           v
                +---------------------+
                | plain.txt (local)   |
                | lock / backups      |
                +---------------------+
```

- **Presentation:** `python_project.py` launches the menu-driven CLI; `streamlit_app.py` renders the web pages.
- **Domain model:** The `Student` dataclass calculates averages, grades, attendance, and assessment coverage.
- **Service and storage:** `StudentStore` parses and validates the text format, coordinates edits using file locks, and writes via atomic file replacement.
- **Verification:** `test_storage.py` covers grade and attendance boundaries, validation, backup/recovery, persistence, and rankings.

No SQL database, REST API, authentication service, or cloud persistence guarantee is part of this implementation.

## Academic workflows

| Feature | Behavior |
| --- | --- |
| Student registration | Assign a unique, normalized student ID, name, and one of 24 predefined programmes |
| Subject catalogue | View required subjects; the programme catalogue is fixed |
| Marks | Enter or replace 0–100 scores, with historically recorded subject labels preserved |
| Attendance | Store attended and total class counts and calculate percentages |
| Individual reports | Show entered-mark average, grade, required-subject coverage, marks, and attendance |
| Rankings and toppers | Rank assessed students by entered-mark average with competition ties (1, 1, 3) |
| Performance alerts | Identify assessed students averaging below 50 |
| Summary | Report programme coverage, assessed/unassessed students, rankings and outliers |

Averages based on incomplete marks are **provisional**. Missing marks are not zeros. Cross-course comparisons are informational, not a standardized academic ranking.

## Data model

Each `plain.txt` record has six pipe-separated fields:

```text
ST101|Ravi Kumar|B.Tech CSE|Python:95;SQL:90|48|50
```

**Fields:** student ID, student name, programme, semicolon-separated subject:mark pairs, attended classes, and total classes.

**Grades:** A+ (90–100), A (80–<90), B (70–<80), C (60–<70), D (50–<60), F (<50). No marks: Not Available.

**Attendance:** attended / total × 100. No total classes recorded: Not recorded.

## Data quality and resilience

Input validation enforces nonempty identities, known programmes, unique IDs, finite marks in range, and whole-number attendance counts where attended ≤ total. Invalid saved rows are reported with line numbers. Editing is blocked until the user explicitly recovers accepted records. Recovery keeps the original file in `plain.txt.recovery.bak`. Normal writes create a rolling `plain.txt.bak` and use locking plus atomic replacement to reduce lost-update and partial-write risks.

## Local setup

Requires **Python 3.10+**.

```bash
git clone https://github.com/Yash301201/Student-Academic-Management-System.git
cd Student-Academic-Management-System
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Or run the CLI with `python python_project.py`. Optionally copy `plain.txt.example` to `plain.txt` for fictional demo data.

## Validation

```bash
python -m unittest -v
```

## Limitations and future enhancements

- File storage is suited to a local demo; persistence on hosted Streamlit instances depends on the host filesystem.
- Course/subject catalogues cannot be edited in the running application.
- Ranking across programmes is not normalized by course difficulty or subject completeness.
- There is no authentication or role-based access control; **do not use real student records in the public demo**.
- Future work could add managed database persistence, role-based access, audit trails, exports, and fully standardized performance comparisons.

## Interview-ready explanation

> I built a Student Academic Management System in Python with both CLI and Streamlit interfaces. Both call a shared backend that validates student information, calculates marks, grades and attendance, and produces rankings and reports. I used a structured TXT file rather than a database and implemented file locking, backups, explicit recovery and atomic writes to handle data integrity. I also added automated tests for boundary cases, malformed records and persistence. The project demonstrates Python OOP, validation, storage design, and practical reporting.
