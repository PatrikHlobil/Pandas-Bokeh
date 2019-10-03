"""This script takes the README.md file of the currrent working directory or
given via the parameter --readme_file and inserts this into the Bootstrap template."""
import argparse
import re
import os

CUR_DIR = os.path.dirname(os.path.realpath(__file__))

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
    html = f.read()

body = re.search(r"<body>(.+)<\/body>", html, re.DOTALL).group(1)
body = re.sub(r"<style.+<\/style>", "", body, flags=re.DOTALL)

with open(os.path.join(CUR_DIR, "template.html")) as f:
    template = f.read()

with open(readme_file, "w") as f:
    f.write(template.format(body=body))