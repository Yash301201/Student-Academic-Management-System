marks_text = "Python:95;SQL:90"

subjects = marks_text.split(";")
print(subjects)
for item in subjects:
    subject_data = item.split(":")
    print(subject_data)
