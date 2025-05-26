import csv


def csv_to_data(file_path: str, line_handler):
    with open(file_path, mode='r') as f:
        reader = csv.DictReader(f)
        for line in reader:
            r = line_handler(line)
            if r is False:
                break


def csv_data(file_path: str):
    with open(file_path, mode='r') as f:
        reader = csv.DictReader(f)
        for line in reader:
            yield line


def get_cvs_data(file_path: str):
    result = []
    with open(file_path, mode='r') as f:
        reader = csv.DictReader(f)
        for line in reader:
            result.append(line)
    return result


def increase_csv_limit():
    import sys
    import csv
    maxInt = sys.maxsize

    while True:
        # decrease the maxInt value by factor 10
        # as long as the OverflowError occurs.

        try:
            csv.field_size_limit(maxInt)
            break
        except OverflowError:
            maxInt = int(maxInt / 10)
