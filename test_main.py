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





if __name__ == '__main__':
    unittest.main()
