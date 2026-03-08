#!/usr/bin/env python3
from pathlib import Path
import shutil
from pdoc import pdoc, render

# 1. Define your paths
here = Path(__file__).parent
# Change "api" to whatever folder name you want in MkDocs
out = here / "docs" / "reference"
# Change "my_package" to the name of your folder containing .py files
src_folder = "../app/iLibrary/src"

if out.exists():
    shutil.rmtree(out)

# 2. Configure (Optional)
# If you don't have a 'pdoc-template' folder, comment this line out
# render.configure(template_directory=here / "pdoc-template")

# 3. Generate for YOUR project
# Replace "your_project_name" with your actual package/module name
pdoc(src_folder, output_directory=out)

# # 4. Rename for MkDocs
# for f in out.glob("**/*.html"):
#     f.rename(f.with_suffix(".md"))