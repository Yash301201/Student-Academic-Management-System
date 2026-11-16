"""Small manual demonstration of the subject:mark text format."""

marks_text = "Python:95;SQL:90"

for item in marks_text.split(";"):
    subject, mark = item.rsplit(":", 1)
    print(f"{subject}: {mark}")
