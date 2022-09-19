from csv import reader
import re
import os
import sys

"""
Columns:
    1. product name (variable-length string)
    2. type ('CPU' or 'GPU', fixed-size string, 3 ASCII characters)
    3. date (fixed-size string, 10 ASCII characters)
    4. quantity of transistor (variable-length string)
"""


def record_structure(ls):
    """
    The offset and length values are all two-digit integers.
    bitmap: 4 characters

    type: 3 characters
    date: 10 characters
    :param ls: the list of field values [name, type, date, quantity]
    :return: record structure in characters
    """
    name = ls[0]
    chip_type = ls[1]
    date = ls[2]
    quantity = ls[3]

    data = ""
    pairs = ""
    bitmap = ""

    # chip_type
    if chip_type == "CPU" or chip_type == "GPU":
        data += chip_type
        bitmap += "0"
    else:
        data += "..."
        bitmap += "1"

    # date
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    if date_pattern.match(date):
        data += date
        bitmap += "0"
    else:
        data += ".........."
        bitmap += "1"

    # name
    name_offset = 11 + 3 + 10
    name_length = len(name)
    if name_length == 0:
        pairs += "...."
        bitmap += "1"
    else:
        pairs += "%02d" % name_offset
        pairs += "%02d" % name_length
        data += name
        bitmap += "0"

    # quantity
    quantity_pattern = re.compile(r'[0-9]+')
    if quantity_pattern.match(quantity):
        bitmap += "0"
        quantity_offset = name_offset + name_length
        quantity_length = len(quantity)
        data += quantity
        pairs += "%02d" % quantity_offset
        pairs += "%02d" % quantity_length
    else:
        bitmap += "1"
        pairs += "...."

    return pairs + bitmap + data


def main(filepath):
    blocks = []
    free_space_map = []
    block = ["0", "0", "0", "9", "9", "9"] + ["." for _ in range(1000 - 6)]
    free_space = 1000 - 6
    num_record = 0

    with open(filepath, 'r') as read_obj:
        csv_reader = reader(read_obj)
        total_record = 0
        next(csv_reader)
        # three-digit integer sizes and locations for record metadata
        # and # of entries in the block and the location of the last byte of the free space
        for row in csv_reader:
            total_record += 1
            record = record_structure(row)
            if len(record) < free_space:
                free_space_end = int(''.join(block[3:6]))
                block[(free_space_end + 1 - len(record)): (free_space_end + 1)] = [*record]
                block[3: 6] = [*str(free_space_end - len(record))]
                block[(6 + num_record * 6): (9 + num_record * 6)] = [*"%03d" % (free_space_end + 1 - len(record))]
                block[(9 + num_record * 6): (12 + num_record * 6)] = [*"%03d" % len(record)]
                num_record += 1
                block[0: 3] = [*"%03d" % num_record]
                free_space -= (len(record) + 6)
            else:
                blocks += [''.join(block)]
                free_space_map += [str(int(free_space / 1000 * 16))]
                block = ["0", "0", "0", "9", "9", "9"] + ["." for _ in range(1000 - 6)]
                free_space = 1000 - 6
                num_record = 0
        blocks += [''.join(block)]
        free_space_map += [str(int(free_space / 1000 * 16))]

    with open(r'C:\Users\Raymond\PycharmProjects\CSC560\Program#1\dbfile.txt', 'w') as fp:
        for block in blocks:
            fp.write("%s\n" % block)

    print("Total number of record: %d" % total_record)
    print("Total number of blocks: %d" % len(free_space_map))
    print("Free-space Map: ")
    print("{:<8} {:<5}".format('Block#', 'Fraction'))
    for number, frac in enumerate(free_space_map):
        print("{:<8} {:<5}".format(number, frac))


if __name__ == '__main__':
    fn = sys.argv[1]
    if os.path.exists(fn):
        print("Processing file: " + fn)
        main(fn)
    else:
        print("File does not exist!")
