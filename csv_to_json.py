import argparse
import csv
import json
import os
import pyinotify
import re


def is_int(possible_i):
    try:
        i = int(possible_i)
        return True
    except:
        return False


def validate(row):
    """
    Validates that the given row has certain values, per the spec

    Input: a dictionary with the keys below (MIDDLE_NAME being optional)
    Output: A list of validation errors.  An empty list, if the row is valid.

    INTERNAL_ID: 8 digit positive integer.  Cannot be empty.
    FIRST_NAME: 15 character max string. Cannot be empty.
    MIDDLE_NAME: 15 character max string.  Can be empty.
    LAST_NAME: 15 character max string. Cannot be empty.
    PHONE_NUM: string that matches this pattern: ###-###-####. Cannot be empty.
    """

    errors = []

    # INTERNAL_ID: 8 digit positive integer.  Cannot be empty.
    if 'INTERNAL_ID' not in row or row['INTERNAL_ID'] == '':
        errors.append("Row must have an INTERNAL_ID.")
    elif not is_int(row['INTERNAL_ID']):
        errors.append("INTERNAL_ID must be an integer.")
    elif len(row['INTERNAL_ID']) != 8:
        errors.append("INTERNAL_ID must be 8 digits long.")

    # FIRST_NAME: 15 character max string. Cannot be empty.
    if 'FIRST_NAME' not in row or row['FIRST_NAME'] == '':
        errors.append("Row must have a FIRST_NAME.")
    elif len(row['FIRST_NAME']) > 15:
        errors.append("FIRST_NAME can be 15 letters max.")

    # MIDDLE_NAME: 15 character max string.  Can be empty.
    if 'MIDDLE_NAME' in row:
        if len(row['MIDDLE_NAME']) > 15:
            errors.append("MIDDLE_NAME can be 15 letters max.")

    # LAST_NAME: 15 character max string. Cannot be empty.
    # We /could/ refactor the FIRST_NAME and LAST_NAME checks to be one function,
    # since they're basically the same, but this is easy enough.
    if 'LAST_NAME' not in row or row['LAST_NAME'] == '':
        errors.append("Row must have a LAST_NAME.")
    elif len(row['LAST_NAME']) > 15:
        errors.append("LAST_NAME can be 15 letters max.")

    # PHONE_NUM: string that matches this pattern: ###-###-####. Cannot be empty.
    if 'PHONE_NUM' not in row or row['PHONE_NUM'] == '':
        errors.append("Row must have a PHONE_NUM.")
    elif not re.match('^\d{3}\-\d{3}\-\d{4}$', row['PHONE_NUM']):
        errors.append("PHONE_NUM must be in the format ###-###-####.")

    # Done checking all conditions.  Return the (possibly empty) list.
    return errors


def format_output(row):
    """
    Format a given row's output the way we want.

    :param row: a dictionary object containing the data from a row of the input CSV.
    :return: a dictionary object containing the desired output format (suitable for serialization to JSON)
    """
    person = { 'id': int(row['INTERNAL_ID']),
               'name': { 'first': row['FIRST_NAME'],
                         'last':  row['LAST_NAME'],
                        },
               'phone': row['PHONE_NUM']
              }
    if 'MIDDLE_NAME' in row and row['MIDDLE_NAME']:
        person['name']['middle'] = row['MIDDLE_NAME']

    return person


def process_file(filename):
    """
    Validate, process, and then delete an input CSV file.
    :param filename: The input CSV file
    :return: [ [list of valid output records], [list of error records] ]
    """
    output = []
    errors_for_csv = []

    infile = open(filename, 'r')
    # DictReader automatically takes first line as dictionary keys.
    # The "strict" option isn't actually very strict.  No matter what invalid input I give the DictReader,
    # I can't get it to raise an exception like the documentation says it will:
    # https://docs.python.org/3.5/library/csv.html#csv.Dialect.strict
    reader = csv.DictReader(infile, strict=True)

    for row in reader:
        errors = validate(row)
        if errors:
            # The spec says that 'LINE_NUM' should be "the number of the record which was invalid".
            # I'm assuming that means "the literal line number, like you'd see in a text editor."
            # i.e. the first line of data after the header would be line 2.
            errors_for_csv.append([reader.line_num, errors[0]])
        else:
            output.append(format_output(row))

    infile.close()
    return output, errors_for_csv


def get_json_filename(input_filename):
    basename = os.path.basename(input_filename)
    basename = os.path.splitext(basename)[0] + '.json' # .csv => .json
    return os.path.join(OUTPUT_DIR, basename)


def get_error_filename(input_filename):
    basename = os.path.basename(input_filename)
    return os.path.join(ERROR_DIR, basename)


def write_output(output, output_filename):
    if len(output) == 0:
        return # Nothing to do

    print("Writing ", len(output), " records to '", output_filename, "'")
    out = open(output_filename, 'w')
    for rec in output:
        out.write(json.dumps(rec, sort_keys=True, indent=4))
    out.close()


def write_errors(errors_for_csv, error_filename):
    if len(errors_for_csv) == 0:
        return # Nothing to do

    print("Writing ", len(errors_for_csv), " errors to '", error_filename, "'")
    out = open(error_filename, 'w')
    writer = csv.writer(out)
    writer.writerow(["LINE_NUM", "ERROR_MSG"])
    writer.writerows(errors_for_csv)
    out.close()


def get_directories():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputdir", help="Directory to watch for input CSV files")
    parser.add_argument("--outputdir", help="Directory for output JSON files")
    parser.add_argument("--errordir", help="Directory for output error files (CSV format)")
    args = parser.parse_args()

    INPUT_DIR = args.inputdir if args.inputdir else 'input/'
    if not os.path.isdir(INPUT_DIR):
        print("Error: input directory '{}' doesn't exist.".format(INPUT_DIR))
        exit(1)

    ERROR_DIR = args.errordir if args.errordir else 'errors/'
    if not os.path.isdir(ERROR_DIR):
        print("Error: error directory '{}' doesn't exist.".format(ERROR_DIR))
        exit(1)

    OUTPUT_DIR = args.outputdir if args.outputdir else 'output/'
    if not os.path.isdir(OUTPUT_DIR):
        print("Error: output directory '{}' doesn't exist.".format(OUTPUT_DIR))
        exit(1)

    return [INPUT_DIR, ERROR_DIR, OUTPUT_DIR]


def consider_file(filename):
    print("Considering file:", filename)
    if filename in already_seen:
        print("Already saw this filename; ignoring")

    elif filename.endswith('csv'):
        print("New .csv file; processing")
        output, errors_for_csv = process_file(filename)
        write_output(output, get_json_filename(filename))
        write_errors(errors_for_csv, get_error_filename(filename))
        already_seen[filename] = True
        os.remove(filename)
        print("OK, processed and deleted")

    else:
        print("Not a .csv file; ignoring")


# Filenames we've already seen
already_seen = {}


class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event): # pyinotify's callback for when a new file is created
        consider_file(event.pathname)


############################################
# MAIN
############################################

INPUT_DIR, ERROR_DIR, OUTPUT_DIR = get_directories()
print("Input dir:", INPUT_DIR)
print("Error dir:", ERROR_DIR)
print("Output dir:", OUTPUT_DIR)

# First, process all the *.csv files in INPUT_DIR
all_files = os.listdir(INPUT_DIR)
all_files = [f for f in all_files if f.endswith('.csv')]
for f in all_files:
    consider_file(os.path.join(INPUT_DIR, f))

# Now that we've processed all the files that were there on startup,
# watch for new ones

# The watch manager stores the watches and provides operations on watches
wm = pyinotify.WatchManager()

handler = EventHandler()
notifier = pyinotify.Notifier(wm, handler)

wdd = wm.add_watch(INPUT_DIR, pyinotify.IN_CREATE)

print("Press Ctrl-C to exit...")
notifier.loop()
