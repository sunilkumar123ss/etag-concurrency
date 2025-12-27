import threading
import unittest
from main import VersionedDocument, PreconditionFailed, PreconditionRequired


class ETagTests(unittest.TestCase):
    def test_matching_tag_updates(self):
        doc = VersionedDocument({"x": 1})
        _, tag = doc.get()
        new_tag = doc.replace({"x": 2}, tag)
        self.assertNotEqual(new_tag, tag)
        self.assertEqual(doc.get(), ({"x": 2}, new_tag))

    def test_stale_write_does_not_replace(self):
        doc = VersionedDocument({"x": 1})
        _, tag = doc.get()
        doc.replace({"x": 2}, tag)
        with self.assertRaises(PreconditionFailed): doc.replace({"x": 3}, tag)
        self.assertEqual(doc.get()[0], {"x": 2})

    def test_missing_and_weak_tags_rejected(self):
        doc = VersionedDocument({})
        with self.assertRaises(PreconditionRequired): doc.replace({}, None)
        with self.assertRaises(PreconditionFailed): doc.replace({}, "W/" + doc.get()[1])

    def test_get_returns_detached_snapshot(self):
        original = {"items": [1]}
        doc = VersionedDocument(original)
        original["items"].append(2)
        value, _ = doc.get()
        value["items"].append(3)
        self.assertEqual(doc.get()[0], {"items": [1]})

    def test_aba_and_no_op_still_change_version(self):
        doc = VersionedDocument("a")
        _, first = doc.get()
        second = doc.replace("b", first)
        third = doc.replace("a", second)
        self.assertNotEqual(first, third)
        fourth = doc.replace("a", third)
        self.assertNotEqual(third, fourth)

    def test_invalid_json_does_not_mutate(self):
        doc = VersionedDocument({})
        before = doc.get()
        for value in ({"x": float("nan")}, {1: "bad"}, {"x": {1, 2}}):
            with self.subTest(value=value), self.assertRaises(ValueError): doc.replace(value, before[1])
            self.assertEqual(doc.get(), before)

    def test_two_writers_only_one_succeeds(self):
        doc = VersionedDocument(0)
        _, tag = doc.get()
        barrier = threading.Barrier(2)
        outcomes = []
        lock = threading.Lock()
        def writer(value):
            barrier.wait()
            try:
                doc.replace(value, tag)
                outcome = "updated"
            except PreconditionFailed:
                outcome = "stale"
            with lock: outcomes.append(outcome)
        threads = [threading.Thread(target=writer, args=(value,)) for value in (1, 2)]
        for thread in threads: thread.start()
        for thread in threads: thread.join()
        self.assertCountEqual(outcomes, ["updated", "stale"])


if __name__ == '__main__':
    unittest.main()
