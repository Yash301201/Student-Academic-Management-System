# Student Academic Management System

A lightweight student records application with both a command-line interface and a Streamlit web interface. Track student profiles, marks, attendance, grades, rankings, and academic summaries.

<p align="center">
  <a href="https://yash301201-student-academic-management-sys-streamlit-app-teu5oq.streamlit.app/"><strong>Launch the live Streamlit app →</strong></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/Yash301201/Student-Academic-Management-System"><strong>View source code</strong></a>
</p>

## Overview

The application supports 23 programmes and majors across engineering, science, commerce, management, and humanities. Student records are stored in the repository's `plain.txt` data file.

### Features

- Register students and assign a programme
- Enter and update subject marks and attendance
- View individual student reports with averages, grades, and attendance
- Rank students, identify top performers, and find students with averages below 50
- Review an academic summary
- Use the same student record logic from the CLI or web interface

## Live application

Open the deployed app here:

**[Student Academic Management System — Streamlit](https://yash301201-student-academic-management-sys-streamlit-app-teu5oq.streamlit.app/)**

## Run locally

Requires Python 3. Install the dependencies and start the Streamlit interface:

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

To use the command-line interface instead:

```bash
python python_project.py
```

## Project structure

| File | Description |
| --- | --- |
| `streamlit_app.py` | Streamlit web interface |
| `python_project.py` | Student record logic and command-line interface |
| `plain.txt` | Pipe-delimited student records used for persistence |
| `requirements.txt` | Python package dependencies |
| `test.py` | Small example for parsing subject-mark strings |

## Student record format

Each record is stored on one line using pipe-delimited fields. Subject marks are separated by semicolons:

```text
ST101|Ravi Kumar|B.Tech CSE|Python:95.0;SQL:90.0|48|50
```

The fields are student ID, name, programme, subject-mark pairs, classes attended, and total classes.

## Data and deployment

The app reads and writes records to `plain.txt`. This is file-based storage rather than a database; the local file is used when running locally, and hosted file persistence depends on the Streamlit hosting environment. Avoid entering sensitive or real student information in a public demo.

## License

No license is currently specified for this repository.
