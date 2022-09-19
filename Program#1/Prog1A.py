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
    This function is for converting a list of field values into record structure in characters
    :param ls: the list of field values [name, type, date, quantity]
    :return: record structure in characters
    """

    # extract values from the list
    name = ls[0]
    chip_type = ls[1]
    date = ls[2]
    quantity = ls[3]

    # create strings respectively for pairs, bitmap, and data
    # pairs + bitmap = metadata
    data = ""
    pairs = ""
    bitmap = ""

    """
    The record structure is in the form of:
        aabbccddeeeefffgggggggggghhhhhhiiiii
            where:
                aa: offset for name (2-digit characters); if name not available, replace by ".."
                bb: length for name (2-digit characters); if name not available, replace by ".."
                cc: offset for quantity of transistors (2-digit characters); if quantity not available, replace by ".."
                dd: length for quantity of transistors (2-digit characters); if quantity not available, replace by ".."
                eeee: bitmap respectively for type, date, name, quantity (4-byte characters)
                fff: chip type (3-byte characters); if not available, replace by "..."
                gggggggggg: date (10-byte characters); if not available, replace by ".........."
                hhhhhh: name (variable-length); if not available, discard this part
                iiiii: quantity (variable-length); if not available, discard this part
    """

    # chip_type
    if chip_type == "CPU" or chip_type == "GPU":
        data += chip_type
        bitmap += "0"
    else:
        data += "..."
        bitmap += "1"

    # date
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')  # valid value of date must match the date pattern
    if date_pattern.match(date):
        data += date
        bitmap += "0"
    else:
        data += ".........."
        bitmap += "1"

    # name
    name_offset = 8 + 4 + 3 + 10  # (offset, length) pairs + bitmap + "type" + "date" = 4 * 2 + 4 + 3 + 10
    name_length = len(name)
    if name_length == 0:
        pairs += "...."
        bitmap += "1"
    else:
        pairs += "%02d" % name_offset  # add leading 0's to offset
        pairs += "%02d" % name_length  # add leading 0's to length
        data += name
        bitmap += "0"

    # quantity
    quantity_pattern = re.compile(r'[0-9]+')  # valid value of quantity must be an integer
    if quantity_pattern.match(quantity):
        bitmap += "0"
        quantity_offset = name_offset + name_length
        quantity_length = len(quantity)
        data += quantity
        pairs += "%02d" % quantity_offset  # add leading 0's to offset
        pairs += "%02d" % quantity_length  # add leading 0's to length
    else:
        bitmap += "1"
        pairs += "...."

    return pairs + bitmap + data


def main(filepath):
    # Initialize variables
    blocks = []
    free_space_map = []
    block = ["0", "0", "0", "9", "9", "9"] + ["." for _ in range(1000 - 6)]  # empty block
    real_free_space = 1000 - 6  # the true number of free bytes
    free_space = 15  # the value for free-space map
    num_record = 0  # the number of records in the current block

    with open(filepath, 'r') as read_obj:
        csv_reader = reader(read_obj)
        total_record = 0
        next(csv_reader)  # skip column name row
        for row in csv_reader:
            total_record += 1
            record = record_structure(row)  # transfer the list of field values to the record structure in characters
            if len(record) > free_space / 16 * 1000:  # check if new block is needed
                blocks += [''.join(block)]  # save the current block
                free_space_map += [free_space]  # save the current free space value
                block = ["0", "0", "0", "9", "9", "9"] + ["." for _ in range(1000 - 6)]  # create empty block
                real_free_space = 1000 - 6  # reset the real number of free bytes
                num_record = 0  # reset the number of records in the current block
            free_space_end = int(''.join(block[3:6]))
            block[(free_space_end + 1 - len(record)): (free_space_end + 1)] = [*record]  # insert record structure
            block[3: 6] = [*str(free_space_end - len(record))]  # adjust free space end
            block[(6 + num_record * 6): (9 + num_record * 6)] = [*"%03d" % (free_space_end + 1 - len(record))]  # add record offset
            block[(9 + num_record * 6): (12 + num_record * 6)] = [*"%03d" % len(record)]  # add record length
            num_record += 1
            block[0: 3] = [*"%03d" % num_record]  # update the number of records in the block
            real_free_space -= (len(record) + 6)  # update the real number of free bytes
            free_space = int(real_free_space / 1000 * 16)  # update the value for free-space map

        blocks += [''.join(block)]
        free_space_map += [free_space]

    # Write blocks into a file
    with open(r'dbfile.txt', 'w') as fp:
        for block in blocks:
            fp.write("%s\n" % block)

    # Print related information
    print("Total number of record: %d" % total_record)
    print("Total number of blocks: %d" % len(free_space_map))
    print("")
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
