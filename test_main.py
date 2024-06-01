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








if __name__ == '__main__':
    unittest.main()
