"""
Course: CSC 560 - Database Systems Implementation, Fall 2022
Instructor: Dr. McCann

Assignment: Program #2 - External Multi-Way Merge Sort
Due Date: Oct 6th, 2022, at the beginning of class

Author: Zirui Huang

Description:
    This script is to implement the external sort-merge algorithm to sort CSV files on the attribute selected
by the user, and to write out the sorted file. The user needs to provide the following arguments:

    1. the complete pathname of the CSV file whose lines are being sorted
    2. The # of the field on which the file is to be sorted (where the first field is field 1)
    3. R, the Pass 0 run-length (# of records to be sorted per group)
    4. W, the "way" for Passes 1 - n (maximum initial # of runs being merged at a time)

    The algorithm runs as follows:
        For Pass 0:
            The script reads R lines from the provided CSV file at a time. Sorting these R lines using the provided
        field, and write out the sorted lines to file "run0-[r].csv". Until the records in the CSV file are exhausted.

        For Pass 1 - n:
            The script merge-sorts every W run files from the last pass, and write out the sorted lines to file
        "run[p]-[r].csv"。Until all run files from the last pass are exhausted.
            Eventually, there is only one run file. Adding headers to this file, the script writes out the sorted
        CSV file.

Operational requirements: Python 3.8.10
External libraries: None

"""

import sys
import os
import math
from contextlib import ExitStack


def merge_sort(files, field, r):
    """
    This function is to mimic the merge-sort process in Passes 1 - n. We feed the function with W run files from last
    pass, and get sorted records composed of records from these W run files.
    :param files: a list of run files (quantity = W)
    :param field: the field used for sorting
    :param r: the maximum number of records can be loaded in a block
    :return: a list of records from run files but in sorted order
    """
    sorted_run = []  # sorted_run: the list of records to be returned
    run = [[] for _ in range(len(files))]  # run: the blocks for all run files

    # For each run file, we read "r" records.
    for i in range(len(files)):
        for _ in range(r):
            try:
                run[i] += [next(files[i])]
            except StopIteration:
                break

    indices = [0 for _ in range(len(run))]  # indices: the current pointer at each block

    # When all indices equal to -1, all records in run files are exhausted.
    # But before that, we need to compare the values pointed by pointers.
    while indices.count(-1) != len(run):
        # Find the record with the smallest value by comparing the values pointed by pointers
        smallest_group = -1
        smallest_value = 'null'
        for i in range(len(run)):
            if indices[i] == -1:
                continue
            value = run[i][indices[i]].strip().split(',')[field - 1]
            if value < smallest_value or smallest_value == 'null':
                smallest_group = i
                smallest_value = value
        # Load the record with the smallest value into the list to be returned
        sorted_run += [run[smallest_group][indices[smallest_group]]]
        # Move the pointer to the next record
        indices[smallest_group] += 1
        # If the pointer points to the last element in the block
        if indices[smallest_group] == len(run[smallest_group]):
            # Trying loading another block
            run[smallest_group] = []
            for _ in range(r):
                try:
                    run[smallest_group] += [next(files[smallest_group])]
                except StopIteration:
                    break
            # If there is no records left in this run file, then let the pointer point to null
            if len(run[smallest_group]) == 0:
                indices[smallest_group] = -1
            # If there are still records, then let the pointer point to the first record
            else:
                indices[smallest_group] = 0

    return sorted_run


def main(filepath, field, r, w):
    """
    The main function implements the external multi-way merge sort according to the following arguments, and writes out
    the records to CSV file named with suf-fix "-sorted".
    :param filepath: the complete pathname of the CSV file whose lines are being sorted
    :param field: the field used for sorting
    :param r: the Pass 0 run-length (# of records to be sorted per group)
    :param w: the "way" for Passes 1 - n (maximum initial # of runs being merged at a time)
    :return: null
    """

    # Read original csv files
    file = open(filepath, 'r')
    lines = file.readlines()  # lines: all lines in the original csv files
    header = lines[0]  # header: the header of CSV file

    # Create folder to store intermediate run files
    path = './runs/'  # path: the folder to store intermediate run files
    if not os.path.exists(path):
        # Create a new directory because it does not exist
        os.makedirs(path)
        print("The directory for runs is created!")

    # Pass 0
    # Determine the number of runs in Pass 0
    num_runs = math.ceil((len(lines) - 1) / r)  # num_runs: # runs in Pass 0
    for i in range(num_runs):
        # For each run in Pass 0, read r records
        run = lines[(1 + r * i): min((1 + r * (i + 1)), len(lines))]
        run = [item.strip().split(',') for item in run]
        # Sort these r records using internal sorting algorithm
        run.sort(key=lambda x: x[field - 1])
        # Write out the sorted records to run0-[r].csv files
        with open(path + r'run%d-%d.csv' % (0, i), 'w') as fp:
            for sublist in run:
                fp.write("%s\n" % ','.join(sublist))
    print("Pass %d created %d runs." % (0, num_runs))

    # Pass 1 - n
    cur_pass = 1  # cur_pass: the current pass number
    while num_runs > 1:  # Stop until the number of runs is 1
        num_runs_cur = math.ceil(num_runs / w)  # num_runs_cur: the number of runs for the current pass
        for i in range(num_runs_cur):
            # For each run, read w run files from last run
            filenames = [path + r'run%d-%d.csv' % (cur_pass - 1, j) for j in range(i * w, min((i + 1) * w, num_runs))]
            with ExitStack() as stack:
                files = [stack.enter_context(open(fname, 'r')) for fname in filenames]
                # Call function merge_sort() to do merge-sort on w run files
                sorted_run = merge_sort(files, field, r)
            # Write the sorted run files into csv files
            with open(path + r'run%d-%d.csv' % (cur_pass, i), 'w') as fp:
                for sublist in sorted_run:
                    fp.write("%s" % sublist)
        # Update the number of runs
        num_runs = num_runs_cur
        print("Pass %d created %d runs." % (cur_pass, num_runs))
        # Update the current pass
        cur_pass += 1

    # Verification
    # Read the last run file
    file = open(path + r'run%d-%d.csv' % (cur_pass - 1, 0), 'r')
    lines = file.readlines()

    # Check if the value of the latter record is greater than or equal to the one of the former record
    for i in range(1, len(lines)):
        assert lines[i - 1].strip().split(',')[field - 1] <= lines[i].strip().split(',')[field - 1]

    # Add header to the last run file to construct new csv file
    lines = [header] + lines
    filename_old = os.path.basename(filepath)
    filename_new = '.'.join(filename_old.split('.')[:-1]) + '-sorted.' + filename_old.split('.')[-1]
    with open(filename_new, 'w') as fp:
        for sublist in lines:
            fp.write("%s" % sublist)

    print("The completed file's name is \"%s\"." % filename_new)
    print("It contains %d lines" % (len(lines) - 1))
    print("VERIFIED: The completed file is in sorted order by field %d." % field)


if __name__ == '__main__':
    fn = sys.argv[1]
    Field = int(sys.argv[2])
    R = int(sys.argv[3])
    W = int(sys.argv[4])
    if os.path.exists(fn):
        print("Processing file: " + fn)
        main(fn, Field, R, W)
    else:
        print("File does not exist!")