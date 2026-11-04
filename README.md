# Student Academic Management System

A Python command-line application for managing student records, course subjects, marks, attendance, grades, rankings, and academic performance summaries. Student records are saved in a plain text file.

## Features
- Register students and manage course subjects
- Enter or update student marks and attendance
- Calculate averages, grades, and attendance percentages
- Search for students and view individual academic reports
- Identify toppers and rank students by average marks
- Identify students whose average is below 50
- Generate an academic summary report
- Save and load records from `plain.txt`

## Requirements
- Python 3 (standard library only)

## Run
```bash
python python_project.py
```

The application loads records from `plain.txt` on startup and displays an interactive menu. Follow the numbered prompts to manage records. Changes to marks, attendance, and student registration are saved to the text file.

## Project files
- `python_project.py`: main command-line application
- `plain.txt`: example student records and file-based persistence
- `test.py`: small demonstration of parsing subject-mark strings

## Data format
Each student is stored as a pipe-delimited line:

```text
ST101|Ravi Kumar|B.Tech CSE|Python:95.0;SQL:90.0|48|50
```

Fields: student ID, name, course, subject-mark pairs, classes attended, total classes.

**Note:** The course/subject management menu maintains subjects in memory; subjects without student marks are not independently persisted. `test.py` is a parsing example rather than an automated test suite.
