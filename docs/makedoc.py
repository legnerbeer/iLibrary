#!/usr/bin/env python3
from pathlib import Path
import shutil
from pdoc import pdoc

# 1. Define paths relative to this script
# .parent points to the folder containing this script (e.g., your 'docs_scripts' folder)
script_dir = Path(__file__).parent.resolve()

# Define the root of your GitHub repo (one level up from the script folder)
root_path = script_dir.parent

# Path to your source code: root/src
src_folder = root_path / "app" / "iLibrary" /"src"

# Path to the output: root/docs/reference
out = root_path / "docs" / "reference"

def generate_docs():
    # Clean up old documentation
    if out.exists():
        print(f"Cleaning up old docs at: {out}")
        shutil.rmtree(out)

    print(f"Generating docs from: {src_folder}")
    print(f"Outputting to: {out}")

    # 2. Generate for your project
    # pdoc will crawl the src_folder and generate HTML by default
    pdoc(src_folder, output_directory=out)

    # 3. Optional: Rename for MkDocs if you are using the MkDocs-Material logic
    # for f in out.glob("**/*.html"):
    #     f.rename(f.with_suffix(".md"))

if __name__ == "__main__":
    generate_docs()