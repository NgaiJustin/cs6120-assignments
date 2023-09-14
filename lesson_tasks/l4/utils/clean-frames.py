"""Remove all non png files, non gif from a directory. This is useful for cleaning up the working directory 
after running the dataflow analysis. Because for some reason graphviz will create a bunch of non-png
files even though I specify the format as png."""

import argparse
import os
from pathlib import Path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "dir",
        help="The directory to clean",
        type=str,
    )
    args = parser.parse_args()

    dir = Path(args.dir)
    if not dir.is_dir():
        raise Exception("Working directory is not a directory")

    # Confirm that the user wants to delete all non-png files
    n = len(
        [
            file
            for file in os.listdir(dir)
            if not file.endswith(".png") and not file.endswith(".gif")
        ]
    )
    if n == 0:
        print("No files to delete")
        exit(0)

    print(f"Cleaning directory: {dir}")
    print(f"Found {n} non-png files:")
    for file in sorted(os.listdir(dir)):
        if not file.endswith(".png") and not file.endswith(".gif"):
            print(f"  - {file}")
    print("Do you want to delete all non-png files? [y/n]")
    overwrite = input()
    if overwrite.lower() == "y":
        # delete all files in the directory
        for file in sorted(os.listdir(dir)):
            if not file.endswith(".png") and not file.endswith(".gif"):
                os.remove(os.path.join(dir, file))
