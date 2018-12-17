# SCOIR Technical Interview for Back-End Engineers
This repo contains an exercise intended for Back-End Engineers.

## How-To
I wrote this assignment in Python 3, targeting a Linux environment.  The only library it needs, other than the standard libraries, is `pyinotify`.  You can install this with `pip`, or else create a full "pipenv" virtual environment.  To create the pipenv virtual environment:

1. `pipenv --three`  This creates a new Python 3 virtual environment.
2. `pipenv install pyinotify`  This installs the necessary library.
3. `pipenv shell`  This launches a shell with the virtual environment's settings.
4. `python3 csv_to_json.py -h` This shows the program's help page, and verifies the dependencies are set up correctly.

If all those steps work, you can invoke the program with:
`python3 csv_to_json.py`
(You can optionally set the input, error, and output directories, as described on the help page.)

## Assumptions
* The code to monitor a directory for changes is OS-dependent.  I assumed we're going to be running on a Linux server (with kernel >= 2.6.13), so I used 'pyinotify'.
* In the errors CSV, the spec says that 'LINE_NUM' should be "the number of the record which was invalid".  I'm assuming that means "the literal line number, like you'd see in a text editor." i.e. the first line of data after the header would be line 2.
* If a given row of the input CSV is invalid, the spec says that the code should record the "error message," singular. There could be multiple errors -- I just arbitrarily took the first one.  (In real life, we could update the format of the error CSV to allow for multiple errors.)
* I'd like to have better logic for input files that aren't a valid CSV file at all.  The validation still sort of works, in the sense that it complains that each line after the first doesn't have an INTERNAL_ID, which is true.  (INTERNAL_ID is the first column it checks, and we're only looking at the first error, per above.)
* I think it would be more robust to first check that the CSV input is valid at all, before we start checking individual rows.  I tried setting the `csv.DictReader` to strict mode, hoping it would raise an exception for invalid CSVs that we could then handle: 
  https://docs.python.org/3.5/library/csv.html#csv.Dialect.strict
...but strict mode isn't as strict as the documentation says it is.  I can't get it to raise an exception, no matter what crazy input I give it.  If I had more time, I could dig further into this.
* The spec says, "once the application starts it watches input-directory for any new files that need to be processed." It doesn't explicitly say what to do with CSV files that are already in the input directory when the program starts; I assumed we want to process those too.
* The spec says, "files will be considered new if the file name has not been recorded as processed before."  I assume we mean, "recorded as processed" during a given run of the program.  In other words, if we stop and restart the program, I assume we're supposed to forget the "already seen" list.


## Instructions
1. Fork this repo.
1. Using technology of your choice, complete [the assignment](./Assignment.md).
1. Update this README with
    * a `How-To` section containing any instructions needed to execute your program.
    * an `Assumptions` section containing documentation on any assumptions made while interpreting the requirements.
1. Before the deadline, submit a pull request with your solution.

## Expectations
1. Please take no more than 8 hours to work on this exercise. Complete as much as possible and then submit your solution.
1. This exercise is meant to showcase how you work. With consideration to the time limit, do your best to treat it like a production system.
