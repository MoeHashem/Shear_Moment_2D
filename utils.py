import csv


def str_to_int(s: str) -> int|str:
    """
    Retruns integer if the string "s" represents an integer, otherwise returns original string
    """
    try:
        return int(s)
    except ValueError:
        return s

def str_to_float(s: str) -> float|str:
    """
    Retruns float if the string "s" represents a float, otherwise returns original string
    """

    try:
        return float(s)
    except ValueError:
        return s

def read_csv_file(file_name: str) -> list[list[str]]:
    """
    Reads the comma seperated data in a csv file (file_name.txt). 
    Retruns list of list of str ()
    """
    csv_acc = [] # File data goes here
    with open(file_name, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            csv_acc.append(line)
    return csv_acc
