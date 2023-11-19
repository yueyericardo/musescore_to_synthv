import os
import argparse
from pathlib import Path
from . import musescore_parser


def write_to_file(file_name, data):
    with open(file_name, "w") as write_file:
        write_file.write(data)


def prompt_overwrite(file_path):
    """Prompt the user to overwrite an existing file."""
    response = (
        input(f"The file {file_path} already exists. Overwrite? (y/n): ")
        .strip()
        .lower()
    )
    return response == "y"


def convert(readfile, writefile, use_hr_dict, verbose=False):
    parser = musescore_parser.XMLParser(
        readfile, verbose=verbose, use_hr_dict=use_hr_dict
    )
    parser.parse_xml()
    write_to_file(writefile, parser.output_string)


def main():
    parser = argparse.ArgumentParser(description="Your script description")
    parser.add_argument("readfile", type=str, help="Path to the input file")
    parser.add_argument(
        "writefile", type=str, nargs="?", help="Path to the output file"
    )
    parser.add_argument("-d", "--dict", action="store_true", help="Use dictionary flag")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose flag")

    args = parser.parse_args()

    # Check if the input file exists
    if not os.path.exists(args.readfile):
        raise FileNotFoundError(f"The file {args.readfile} does not exist.")

    # If writefile is not provided, use readfile's name with .svp extension
    if args.writefile is None:
        args.writefile = Path(args.readfile).with_suffix(".s5p")

    # Check if the writefile exists and prompt for overwrite
    writefile_path = Path(args.writefile)
    if writefile_path.exists():
        if not prompt_overwrite(writefile_path):
            print("Operation cancelled.")
            exit()

    convert(args.readfile, args.writefile, args.dict, args.verbose)


if __name__ == "__main__":
    main()
