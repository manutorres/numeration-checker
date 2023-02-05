import os
import re
from pathlib import Path
from argparse import ArgumentParser


# Organizes a folder by numerical order by concatenating an additional
# zero as needed, keeping a 00-99 order

# Adds the amount of zeros needed to match the length received
def add_trailing_zeros(number: str, length: int) -> str:
    return ((length - len(number)) * '0') + number


class DirectorySorter:
    def __init__(self, directory="", recursive=True, testmode=True, suffix=False):
        self.directory = directory if directory != "" else os.getcwd()
        self.recursive = recursive
        self.testmode = testmode
        self.suffix = suffix


    def detect_numbering_max_length(self, path, pattern):
        max = 0
        for file_path in path.glob(pattern):
            raw_filename = file_path.name.split('.')[0]
            print("Nombre de archivo crudo:", raw_filename)

            num_pattern = "\d+$" if self.suffix else "^\d+"
            match = re.search(num_pattern, raw_filename)
            if match is None:
                continue
            num = int(match.group())
            print("Numero en el nombre de archivo:", num)

            max = num if num > max else max

        print("Numero maximo:", max)
        return len(str(max))


    def numeric_rename(self, directory, filename, num_length):
        fullpath = os.path.join(directory, filename)

        name, *extension = filename.rsplit('.', 1)
        extension = "." + extension[0] if extension else ""

        num_pattern = "\d+$" if self.suffix else "^\d+"
        match = re.search(num_pattern, name)
        if match is None:
            return

        num = match.group()
        extended_num = add_trailing_zeros(num, num_length)

        new_filename = re.sub(num, extended_num, name) + extension

        print(filename, "===>", new_filename)
        new_fullpath = os.path.join(directory, new_filename)
        if not self.testmode:
            os.rename(fullpath, new_fullpath)


    def numeric_rename_old(self, directory, filename):
        fullpath = os.path.join(directory, filename)
        # Add extra 0 and at the beginning
        new_filename = re.sub("^[0-9][-\s]", f"0{filename[0:2]}", filename)
        # Add extra space to numbers that already have two digits
        new_filename = re.sub("^[0-9][0-9]-", f"{new_filename[0:2]} -", new_filename)
        print(filename, "===>", new_filename)
        new_fullpath = os.path.join(directory, new_filename)
        if not self.testmode:
            os.rename(fullpath, new_fullpath)


    def recursive_sort(self, directory):
        for filename in os.listdir(directory):
            full_path = os.path.join(directory, filename)
            # print(full_path)
            if os.path.isdir(full_path):
                # Apply renaming recursively inside the directory
                self.recursive_sort(full_path)
            # Rename whether it's a file or directory
            self.numeric_rename(directory, filename)


    # Using Path module
    def sort(self):
        path = Path(self.directory)

        # Add extra **/ to the pattern to make the renaming recursive
        # If recursive = True, numbering will be considered globally (trailing zeros may be applied)
        # Depending on suffix, numbers will be searched for before or after the rest of the filename
        pattern = ("**/" if self.recursive else "") + "*"

        # Detect max numbering to apply trailing zeros correspondingly
        num_length = self.detect_numbering_max_length(path, pattern)

        for file_path in path.glob(pattern):
            self.numeric_rename(file_path.parent.resolve(), file_path.name, num_length)


    # Not Pythonic implementation (manual recursion)
    # def sort(self):
    #     # Apply sorting recursively
    #     if self.recursive:
    #         self.recursive_sort(self.directory)
    #     else:
    #         # Sort the base directory
    #         for filename in os.listdir(self.directory):
    #             # Rename whether it's a file or directory
    #             self.numeric_rename(self.directory, filename)



parser = ArgumentParser()
parser.add_argument("-d", "--directory", dest="basedir", metavar="DIR", default="",
                    help="Specify the directory to sort (default current folder).\n"
                         "Use -d \"./testfolder\" to sort the included test folder")
parser.add_argument("-r", "--recursive",
                    action="store_true", dest="recursive", default=False,
                    help="Apply the sorting recursively to all subfolders and files")
parser.add_argument("-t", "--test",
                    action="store_true", dest="testmode", default=False,
                    help="Use the test mode to test renaming without actually applying it")
parser.add_argument("-s", "--suffix",
                    action="store_true", dest="suffix", default=False,
                    help="Indicates that the numeration comes at the end of the filename")


args = parser.parse_args()

# To sort testfolder: -r -d "./testfolder"
basedir = args.basedir if args.basedir != "" else os.getcwd()
recursive = args.recursive
testmode = args.testmode
suffix = args.suffix

# TODO Extend to any number of files (currently 0-99)
# TODO Migrate to Path completely

sorter = DirectorySorter(basedir, recursive, testmode, suffix)
sorter.sort()
# press = input("Enter to EXIT")
