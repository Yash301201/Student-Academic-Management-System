import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import student_backend as project


class StudentAndValidationTests(unittest.TestCase):
    def test_missing_results_are_distinct_from_real_zeroes(self):
        unassessed = project.Student("S1", "A Student", "B.Tech CSE")
        all_zero = project.Student("S2", "B Student", "B.Tech CSE", {"Python": 0.0})
        no_attendance = project.Student("S3", "C Student", "B.Tech CSE")
        zero_attendance = project.Student("S4", "D Student", "B.Tech CSE", attended_classes=0, total_classes=10)

        self.assertIsNone(unassessed.average())
        self.assertEqual(unassessed.grade(), "Not Available")
        self.assertEqual(all_zero.average(), 0.0)
        self.assertEqual(all_zero.grade(), "F")
        self.assertIsNone(no_attendance.attendance())
        self.assertEqual(zero_attendance.attendance(), 0.0)

    def test_grade_boundaries_and_non_finite_marks(self):
        expectations = {100: "A+", 90: "A+", 89.99: "A", 80: "A", 70: "B", 60: "C", 50: "D", 49: "F", 0: "F"}
        for mark, expected in expectations.items():
            with self.subTest(mark=mark):
                student = project.Student("S1", "A Student", "B.Tech CSE", {"Python": float(mark)})
                self.assertEqual(student.grade(), expected)
        for mark in (float("nan"), float("inf"), float("-inf"), -0.1, 100.1):
            with self.subTest(mark=mark):
                with self.assertRaises(ValueError):
                    project.validate_mark(mark)

    def test_attendance_bounds(self):
        self.assertEqual(project.validate_attendance(0, 10), (0, 10))
        self.assertEqual(project.validate_attendance(10, 10), (10, 10))
        for attended, total in ((-1, 10), (11, 10), (0, -1), (1.5, 2)):
            with self.subTest(attended=attended, total=total):
                with self.assertRaises(ValueError):
                    project.validate_attendance(attended, total)

    def test_course_and_identity_are_canonicalized(self):
        self.assertEqual(project.validate_student_fields(" s001 ", "  Ana  ", "b.tech cse"), ("S001", "Ana", "B.Tech CSE"))
        with self.assertRaises(ValueError):
            project.validate_student_fields("S1", "   ", "B.Tech CSE")
        with self.assertRaises(ValueError):
            project.validate_student_fields("S1", "Ana", "Unknown Course")


class StudentStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.path = Path(self.temp_dir.name) / "plain.txt"
        self.store = project.StudentStore(self.path)

    def test_new_installation_and_atomic_save_reload(self):
        self.assertFalse(self.store.load().file_exists)
        self.store.add_student("s001", " Ana ", "B.Tech CSE")
        self.store.update_mark("S001", "Python", 0)
        self.store.update_attendance("S001", 0, 10)
        result = self.store.load()
        self.assertTrue(result.can_write)
        self.assertEqual(result.students["S001"].marks, {"Python": 0.0})
        self.assertEqual(result.students["S001"].attendance(), 0.0)
        self.assertTrue(self.store.backup_path.exists())

    def test_bad_rows_are_reported_and_not_overwritten_without_recovery(self):
        original = (
            "S1|Ada|B.Tech CSE|Python:95|8|10\n"
            "S2|Lin|B.Tech CSE|Python:200|1|10\n"
            "broken row\n"
        )
        self.path.write_text(original, encoding="utf-8")
        result = self.store.load()
        self.assertEqual(list(result.students), ["S1"])
        self.assertEqual([issue.row for issue in result.issues], [2, 3])
        with self.assertRaises(project.DataIntegrityError):
            self.store.add_student("S3", "Grace", "B.Tech CSE")
        self.assertEqual(self.path.read_text(encoding="utf-8"), original)

    def test_explicit_recovery_keeps_valid_rows_and_original_backup(self):
        original = (
            "S1|Ada|B.Tech CSE|Python:95|8|10\n"
            "S2|Lin|B.Tech CSE|Python:200|1|10\n"
            "broken row\n"
        )
        self.path.write_text(original, encoding="utf-8")
        recovered, backup = self.store.recover()
        self.assertEqual(list(recovered.students), ["S1"])
        self.assertEqual(backup.read_text(encoding="utf-8"), original)
        self.assertTrue(self.store.load().can_write)
        self.assertIn("S1|Ada|B.Tech CSE|Python:95|8|10", self.path.read_text(encoding="utf-8"))
        self.store.add_student("S3", "Grace", "B.Tech CSE")
        self.assertIn("S3", self.store.load().students)
        self.assertEqual(backup.read_text(encoding="utf-8"), original)

    def test_invalid_course_blank_name_and_duplicate_subject_are_rejected(self):
        self.path.write_text(
            "S1|   |B.Tech CSE||0|0\n"
            "S2|Lin|Unknown Course||0|0\n"
            "S3|Kai|B.Tech CSE|Python:80;python:90|1|2\n",
            encoding="utf-8",
        )
        result = self.store.load()
        self.assertEqual(len(result.students), 0)
        self.assertEqual(len(result.issues), 3)

    def test_failed_atomic_replace_preserves_file_and_old_records(self):
        self.store.add_student("S1", "Ada", "B.Tech CSE")
        original = self.path.read_bytes()
        with patch.object(self.store, "_backup_unlocked", return_value=None):
            with patch.object(project.os, "replace", side_effect=PermissionError("read-only")):
                with self.assertRaises(PermissionError):
                    self.store.add_student("S2", "Lin", "B.Tech CSE")
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(set(self.store.load().students), {"S1"})

    def test_ranking_uses_competition_ties_and_keeps_provisional_records(self):
        students = {
            "S1": project.Student("S1", "Ada", "B.Tech CSE", {"Python": 90}),
            "S2": project.Student("S2", "Lin", "B.Tech IT", {"Python": 90, "SQL": 90}),
            "S3": project.Student("S3", "Kai", "B.Tech CSE", {"Python": 80}),
        }
        self.assertEqual([(rank, student.student_id) for rank, student in project.rank_students(students)], [(1, "S1"), (1, "S2"), (3, "S3")])
        self.assertFalse(students["S1"].assessment_complete())


if __name__ == "__main__":
    unittest.main()
