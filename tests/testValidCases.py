from csv_to_json import process_file
import unittest
import json


class TestValidCase(unittest.TestCase):

    def test_valid(self):
        output, errors_for_csv = process_file('inputFiles/valid.csv')
        target_output_file = open('targetOutputs/valid.json', 'r')
        target_output = json.load(target_output_file)

        self.assertEqual(output[0], target_output)  # Deep compare of 2 data structures
        target_output_file.close()

    def test_valid_3_lines(self):
        output, errors_for_csv = process_file('inputFiles/valid_3_lines.csv')
        self.assertEqual(len(output), 3)

        target_output_file = open('targetOutputs/valid_3_lines.json', 'r')
        target_output = json.load(target_output_file)

        self.assertEqual(output, target_output)  # Deep compare of 2 data structures
        target_output_file.close()


if __name__ == '__main__':
    unittest.main()
