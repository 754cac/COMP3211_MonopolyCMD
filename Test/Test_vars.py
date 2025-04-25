import unittest
from vars import secure_random_string, is_valid_save_file_name, is_valid_type

class TestVarsFunctions(unittest.TestCase):

    def test_secure_random_string(self):
        result = secure_random_string(10)
        self.assertEqual(len(result), 10)
        self.assertTrue(all(c.isalnum() for c in result))

    def test_is_valid_save_file_name(self):
        self.assertTrue(is_valid_save_file_name("test.json"))
        self.assertFalse(is_valid_save_file_name("test.txt"))
        self.assertFalse(is_valid_save_file_name("testjson"))
        self.assertFalse(is_valid_save_file_name(""))

    def test_is_valid_type(self):
        self.assertTrue(is_valid_type("123", [int]))
        self.assertFalse(is_valid_type("abc", [int]))
        self.assertTrue(is_valid_type("", [int, True]))
        self.assertTrue(is_valid_type("123", [int, True]))

if __name__ == '__main__':
    unittest.main()