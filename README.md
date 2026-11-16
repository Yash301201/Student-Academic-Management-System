Failed to create stream fd: Operation not permitted
Failed to create stream fd: Operation not permitted
Failed to create stream fd: Operation not permitted
# Student Academic Management System

A Core Python student-records application with a command-line interface and a Streamlit web interface. It records marks and attendance, calculates grades and averages, and produces individual and summary reports.

<p align="center">
  <a href="https://yash301201-student-academic-management-sys-streamlit-app-teu5oq.streamlit.app/"><strong>Open the live Streamlit app →</strong></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/Yash301201/Student-Academic-Management-System"><strong>Browse the source</strong></a>
</p>

## Features

- Register students in a predefined catalogue of **24 programmes**.
- Record and update marks for catalogue subjects and retained historical subjects.
- Track attended and total class counts.
- View student reports, grades, course-wise assessment coverage, rankings, toppers, and academic summaries.
- Run either the CLI or Streamlit interface against the same data file.
- Validate loaded records, report rejected row numbers, back up before replacement, and recover valid rows explicitly.

## Run locally

Requires Python 3.10 or later. Install the dependency and start the web interface:

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

To use the command-line interface:

```bash
python python_project.py
```

Both entry points resolve `plain.txt` beside `student_backend.py`, regardless of the current working directory. The file is created when the first student is registered. To load the fictional demo records first, copy `plain.txt.example` to `plain.txt`:

```bash
# macOS / Linux
cp plain.txt.example plain.txt

# Windows PowerShell
Copy-Item plain.txt.example plain.txt
```

The runtime file, its backups, and lock file are ignored by Git. Do not put real student information in a public demo or commit a runtime data file.

## Marks, grades, and comparisons

Grades use the average of the marks currently entered: A+ at 90 or above, A at 80–89.99, B at 70–79.99, C at 60–69.99, D at 50–59.99, and F below 50. No marks means the average and grade are **N/A / Not Available**; a genuine mark of zero is a real result and receives F.

An average is **provisional** until every required subject in that student's programme has a mark. Missing marks are not treated as zero. Ranking and topper views compare the entered-mark averages, so they are informational when students have different courses or assessment coverage. The ranking uses competition ties: `1, 1, 3`. Low performance means an assessed average **below 50**; a score of exactly 50 is not included. Students without marks are not ranked or classified as low-performing.

Attendance is attended classes divided by total classes. No recorded classes displays **Not recorded**, while zero attended out of ten classes displays **0%**.

## Data integrity and recovery

Records use this format:

```text
DEMO001|Alex Example|B.Tech CSE|Python:95;SQL:88|8|10
```

The fields are ID, name, programme, subject-mark pairs, classes attended, and total classes. IDs are normalized to uppercase; IDs and names must be nonblank; the programme must exist in the fixed catalogue; marks must be finite values from 0 to 100; attendance must be nonnegative and attended classes cannot exceed total classes. Duplicate IDs and duplicate subject names are rejected. Historical/custom subject labels are accepted so existing marks can be preserved; the average uses all entered marks, while coverage counts only required catalogue subjects.

On startup, an unreadable file is distinguished from a new installation. Malformed rows are reported with their line numbers, and normal edits are disabled while any row is rejected. The explicit **recover** action first saves the complete original file as `plain.txt.recovery.bak`, then writes the accepted records. Rejected source rows remain in this dedicated recovery backup even after later saves. A rolling `plain.txt.bak` is also made before each ordinary rewrite.

Writes are serialized across processes using a file lock. The application writes a validated snapshot to a temporary file beside the data file, flushes it, backs up the previous data, and then atomically replaces the original. A failed save reports the failure and leaves the previous data file intact; a successful message is shown only after replacement completes. Each mutation reloads the latest file while holding the lock, so concurrent CLI/web updates do not overwrite a stale snapshot.

The Streamlit deployment uses file-based storage, not a database. Its data persistence depends on the hosting platform's filesystem lifecycle; use it as a demonstration and avoid real student information.

## Course catalogue scope

The catalogue is fixed in code and provides course selection and subject lists. It does not support adding, editing, or removing courses or subjects. This keeps existing student records and marks from being orphaned by catalogue edits.

## Project files

| File | Purpose |
| --- | --- |
| `python_project.py` | CLI entry point |
| `student_backend.py` | Student model, validation, file storage, ranking policy, and shared service |
| `streamlit_app.py` | Streamlit interface using the shared backend service |
| `plain.txt.example` | Fictional demo fixture; copy to the ignored runtime file to use it |
| `plain.txt` | Local runtime data file; created beside the backend and ignored by Git |
| `test_storage.py` | Focused automated tests for validation, recovery, persistence, and reports |
| `marks_parser_demo.py` | Small manual parsing demonstration |
| `requirements.txt` | Streamlit dependency |

## Verify

Run the automated checks with the standard library:

```bash
python -m unittest -v
```

The checks cover grade and attendance boundaries, missing versus zero results, duplicate and malformed records, explicit recovery and backup preservation, failed atomic replacement, and tied provisional rankings.

## Example CLI session

After copying the demo fixture, run `python python_project.py` and select:

1. **5** to search for `DEMO001` and see the 91.50 average, current required-subject coverage, and 80% attendance.
2. **7** to inspect provisional rankings and their tie policy.
3. **10** to exit. Submitted edits are saved when each operation succeeds; exit does not rewrite the data file.

## Project challenges and learnings

- **Malformed text records:** Parsing each row into a temporary validated collection makes it possible to report exact row errors and preserve the original file during recovery.
- **Interrupted writes:** Same-directory temporary files, backups, atomic replacement, and process locks protect saved records and serialize updates from the two interfaces.
- **Missing assessment data:** Separating “not recorded” from a real zero avoids misleading grades, averages, and attendance percentages.
- **Shared application logic:** Both interfaces call the same model and storage service, keeping validation and persistence behavior consistent.
- **Ranking fairness:** Incomplete averages are labeled provisional and ties share a rank; the report explains that different subject sets are not final comparable outcomes.

## Data-file history note

Earlier repository revisions tracked a `plain.txt` file containing named records. Their origin has not been verified. The current tracked tree uses a clearly fictional fixture and ignores the local runtime file; earlier Git history may still contain prior versions. Review the repository history before sharing it if those earlier records could identify real people.

## License

No license is currently specified for this repository.
