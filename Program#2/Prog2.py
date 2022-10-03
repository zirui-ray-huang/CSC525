import sys
import os
import math
from contextlib import ExitStack


def merge_sort(files, field, r):
    sorted_run = []
    run = [[] for _ in range(len(files))]

    for i in range(len(files)):
        for _ in range(r):
            try:
                run[i] += [next(files[i])]
            except StopIteration:
                break

    indices = [0 for _ in range(len(run))]

    while indices.count(-1) != len(run):
        smallest_group = -1
        smallest_value = 'null'
        for i in range(len(run)):
            if indices[i] == -1:
                continue
            value = run[i][indices[i]].strip().split(',')[field - 1]
            if value < smallest_value or smallest_value == 'null':
                smallest_group = i
                smallest_value = value
        sorted_run += [run[smallest_group][indices[smallest_group]]]
        indices[smallest_group] += 1
        if indices[smallest_group] == len(run[smallest_group]):
            run[smallest_group] = []
            for _ in range(r):
                try:
                    run[smallest_group] += [next(files[smallest_group])]
                except StopIteration:
                    break
            if len(run[smallest_group]) == 0:
                indices[smallest_group] = -1
            else:
                indices[smallest_group] = 0

    return sorted_run


def main(filepath, field, r, w):
    file = open(filepath, 'r')
    lines = file.readlines()
    header = lines[0]

    path = './runs/'
    if not os.path.exists(path):
        # Create a new directory because it does not exist
        os.makedirs(path)
        print("The directory for runs is created!")

    # Pass 0
    num_runs = math.ceil((len(lines) - 1) / r)
    for i in range(num_runs):
        run = lines[(1 + r * i): min((1 + r * (i + 1)), len(lines))]
        run = [item.strip().split(',') for item in run]
        run.sort(key=lambda x: x[field - 1])
        with open(path + r'run%d-%d.csv' % (0, i), 'w') as fp:
            for sublist in run:
                fp.write("%s\n" % ','.join(sublist))
    print("Pass %d created %d runs." % (0, num_runs))

    # Pass 1 - ?
    cur_pass = 1
    while num_runs > 1:
        num_runs_cur = math.ceil(num_runs / w)
        for i in range(num_runs_cur):
            filenames = [path + r'run%d-%d.csv' % (cur_pass - 1, j) for j in range(i * w, min((i + 1) * w, num_runs))]
            with ExitStack() as stack:
                files = [stack.enter_context(open(fname, 'r')) for fname in filenames]
                sorted_run = merge_sort(files, field, r)
            with open(path + r'run%d-%d.csv' % (cur_pass, i), 'w') as fp:
                for sublist in sorted_run:
                    fp.write("%s" % sublist)
        num_runs = num_runs_cur
        print("Pass %d created %d runs." % (cur_pass, num_runs))
        cur_pass += 1

    # Verification
    file = open(path + r'run%d-%d.csv' % (cur_pass - 1, 0), 'r')
    lines = file.readlines()

    for i in range(1, len(lines)):
        assert lines[i - 1].strip().split(',')[field - 1] <= lines[i].strip().split(',')[field - 1]

    lines = [header] + lines
    filename_old = os.path.basename(filepath)
    filename_new = '.'.join(filename_old.split('.')[:-1]) + '-sorted.' + filename_old.split('.')[-1]
    with open(os.path.join(os.path.dirname(filepath), filename_new), 'w') as fp:
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