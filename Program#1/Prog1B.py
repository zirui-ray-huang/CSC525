import sys
import os


def tuple_in_record(record):
    """
    This function is for converting record structure into a tuple of field values
    :param record: the record structure in characters
    :return: the tuple of field values (name, type, date, quantity)
    """

    # extract bitmap
    bitmap = record[8:12]

    # For each field, first check the corresponding value in bitmap
    # type
    if bitmap[0] == "0":
        chip_type = record[12:15]
    else:
        chip_type = ""

    # date
    if bitmap[1] == "0":
        date = record[15:25]
    else:
        date = ""

    # name
    if bitmap[2] == "0":
        name_offset = int(record[:2])
        name_length = int(record[2:4])
        name = record[name_offset: (name_offset + name_length)]
    else:
        name = ""

    # quantity
    if bitmap[3] == "0":
        quantity_offset = int(record[4:6])
        quantity_length = int(record[6:8])
        quantity = record[quantity_offset: (quantity_offset + quantity_length)]
    else:
        quantity = ""

    return name, chip_type, date, quantity


def records_in_block(block):
    """
    This function is to print filed values for records in a block
    :param block: the block structure in characters
    :return: null
    """
    records = []
    num_records = int(block[:3])
    for i in range(num_records):
        offset = int(block[(6 + 6 * i): (6 + 6 * i + 3)])
        length = int(block[(9 + 6 * i): (9 + 6 * i + 3)])
        record = tuple_in_record(block[offset: (offset + length)])  # extract the field values for each record
        records += [record]

    print("{:<40} {:<5} {:<15} {:<5}".format('Product', 'Type', "Release Date", "Transistors (million)"))
    for record in records:
        print("{:<40} {:<5} {:<15} {:<5}".format(record[0], record[1], record[2], record[3]))


def main(filepath):

    file = open(filepath, 'r')
    blocks = file.readlines()

    """
    Part 2
    """
    num_blocks = 0
    num_records = 0
    free_space = []
    for block in blocks:
        # 1. The total quantities of blocks and records contained within the DB file.
        num_blocks += 1
        num_records += int(block[:3])

        # 2. For each block, display its quantity of free space bytes.
        free_space += [int(block[3: 6]) - (int(block[:3]) * 6 + 6 - 1)]

    print("The total number of blocks: %d" % num_blocks)
    print("The total number of records: %d" % num_records)
    print("")
    print("Quantity of free space bytes: ")
    print("{:<8} {:<5}".format('Block#', '#Bytes'))
    for number, num_bytes in enumerate(free_space):
        print("{:<8} {:<5}".format(number, num_bytes))
    print("")

    # 3. The field values of the records held by the first block, displayed in insertion order (that is, the first
    # record displayed is the first record inserted)
    print("Records in the first block: ")
    block = blocks[0]
    records_in_block(block)
    print("")

    # 4. Same as (3), but for the records within the last block.
    print("Records in the last block: ")
    block = blocks[-1]
    records_in_block(block)
    print("")

    """
    Part 3
    """
    while True:
        # ask for user's inputs for M and N
        m = input("Enter M value: ")
        if not m.isdigit() or (m.isdigit() and int(m) == -1):
            break
        m = int(m)
        n = input("Enter N value: ")
        if not n.isdigit() or (n.isdigit() and int(n) == -1):
            break
        n = int(n)

        valid_records = []

        # iterate through blocks
        for block in blocks:
            num_records = int(block[:3])
            # iterate through records
            for i in range(num_records):
                offset = int(block[(6 + 6 * i): (6 + 6 * i + 3)])
                length = int(block[(9 + 6 * i): (9 + 6 * i + 3)])
                record = tuple_in_record(block[offset: (offset + length)])
                # save record if it saves the conditions on quantity
                if record[3].isdigit() and m <= int(record[3]) <= n:
                    valid_records += [record]

        # print the records satisfying the filtering criteria
        print("Records with # Transistors between %d and %d" % (m, n))
        print("{:<40} {:<5} {:<15} {:<5}".format('Product', 'Type', "Release Date", "Transistors (million)"))
        for record in valid_records:
            print("{:<40} {:<5} {:<15} {:<5}".format(record[0], record[1], record[2], record[3]))
        print("")


if __name__ == '__main__':
    fn = sys.argv[1]
    if os.path.exists(fn):
        print("Processing file: " + fn)
        main(fn)
    else:
        print("File does not exist!")


