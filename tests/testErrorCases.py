from csv_to_json import process_file, write_errors_to_fh
import unittest
import tempfile


def write_and_reread_errors(errors, fh):
    write_errors_to_fh(errors, fh)
    fh.flush()
    fh.seek(0)
    return fh.readlines()


class TestErrorCases(unittest.TestCase):

    def setUp(self):
        self.temp_output_file = tempfile.TemporaryFile('w+')

    def tearDown(self):
        self.temp_output_file.close()
        self.target_output.close()

    def test_missing_internal_id(self):
        valid_records, errors_for_csv = process_file('inputFiles/missing_internal_id.csv')
        self.assertEqual(len(valid_records), 0)
        self.assertEqual(len(errors_for_csv), 1)
        written_lines = write_and_reread_errors(errors_for_csv, self.temp_output_file)

        self.target_output = open('targetOutputs/ERROR_missing_internal_id.csv')
        self.assertListEqual(written_lines, self.target_output.readlines())

    def test_invalid_internal_id(self):
        valid_records, errors_for_csv = process_file('inputFiles/invalid_internal_id.csv')
        self.assertEqual(len(valid_records), 0)
        self.assertEqual(len(errors_for_csv), 1)

        written_lines = write_and_reread_errors(errors_for_csv, self.temp_output_file)

        self.target_output = open('targetOutputs/ERROR_invalid_internal_id.csv')
        self.assertListEqual(written_lines, self.target_output.readlines())

    # We won't test every single validation we do, but the phone # is a regex, which
    # are especially prone to bugs
    def test_invalid_phone(self):
        valid_records, errors_for_csv = process_file('inputFiles/invalid_phone_num.csv')
        self.assertEqual(len(valid_records), 0)
        self.assertEqual(len(errors_for_csv), 1)

        written_lines = write_and_reread_errors(errors_for_csv, self.temp_output_file)

        self.target_output = open('targetOutputs/ERROR_invalid_phone.csv')
        self.assertListEqual(written_lines, self.target_output.readlines())


if __name__ == '__main__':
    unittest.main()
