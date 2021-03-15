"""This script takes the README.md file of the currrent working directory or
given via the parameter --readme_file and inserts this into the Bootstrap template."""
import argparse
import os

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(CUR_DIR)

parser = argparse.ArgumentParser(
    description="Replace all Bokeh images with interactivet Bokeh plots."
)
parser.add_argument(
    "--readme_file",
    dest="readme_file",
    default="README.html",
    help="Path to README.md file",
)
readme_file = parser.parse_args().readme_file

with open(readme_file) as f:
    body = f.read()

with open(os.path.join(CUR_DIR, "template.html")) as f:
    template = f.read()

with open(os.path.join(PARENT_DIR, "index.html"), "w") as f:
    f.write(template.format(body=body))
