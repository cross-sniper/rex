import os
import argparse
from typing import Union, List, ByteString

parser = argparse.ArgumentParser()
parser.add_argument(
    "-s", "--sourceDir", help="Directory to look for files", required=True
)
parser.add_argument(
    "-o",
    "--output",
    help="Name of the .rex file that will be generated or extracted from",
    required=True,
)
parser.add_argument(
    "-m",
    "--mode",
    help="Mode of operation: 'create' to create a .rex file, 'extract' to extract from a .rex file",
    required=True,
)
args = parser.parse_args()

if not os.path.isdir(args.sourceDir) and args.mode == "create":
    print("Not a valid directory")
    exit(1)


class Header:
    def __init__(self, name: str, size: int, data: ByteString):
        self.name = name
        self.size = size
        self.data = data

    def toData(self) -> ByteString:
        # Create the header in the format [<name>:<size>]
        header_str = f"[{self.name}:{self.size}]\n".encode("utf-8")

        # Combine the header and data
        return header_str + self.data + b"\n"

    def __repr__(self):
        return f"<RexHeader size: {self.size}, name: {self.name}>"


def read_file(name: str) -> ByteString:
    # Determine if the file is binary by checking its extension
    binary_extensions: List[str] = [".png", ".jpg", ".zip", ".exe", ".dll"]
    mode = "rb" if any(name.lower().endswith(ext) for ext in binary_extensions) else "r"
    try:
        with open(name, mode) as f:
            data = f.read()
    except UnicodeDecodeError as e:
        print(f"error: {e}, falling back to byte mode")
        mode = "rb"
        with open(name, mode) as f:
            data = f.read()

    # Convert text data to bytes if the file was opened in text mode
    if isinstance(data, str):
        data = data.encode("utf-8")

    return data


def create(name: str, dir: str):
    headers = []
    for dirpath, _, filenames in os.walk(dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            data = read_file(filepath)
            header = Header(name=filepath, size=len(data), data=data)
            headers.append(header)

    # Write headers and data to .rex file
    with open(name, "wb") as f:
        for header in headers:
            f.write(header.toData())

    print(f"Files have been saved to {name}")


def extract(file: str):
    with open(file, "rb") as f:
        while True:
            # Read the header line
            header_line = f.readline().decode("utf-8").strip()
            if not header_line:
                break  # End of file

            # Parse the header to get the name and size
            if header_line.startswith("[") and header_line.endswith("]"):
                header_content = header_line[1:-1]  # Remove the brackets
                name, size = header_content.split(":")
                size = int(size)

                # Create directories if they don't exist
                os.makedirs(os.path.dirname(name), exist_ok=True)

                # Read the data of the specified size
                data = f.read(size)

                # Write the data to a file
                with open(name, "wb") as out_file:
                    out_file.write(data)

                # Skip the newline after the data
                f.read(1)

    print(f"Files have been extracted from {file}")

if __name__ == "__main__":
    if args.mode == "create":
        create(args.output, args.sourceDir)
    elif args.mode == "extract":
        extract(args.output)
    else:
        print("Invalid mode selected. Use 'create' or 'extract'.")
