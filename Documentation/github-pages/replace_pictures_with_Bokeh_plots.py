"""This script takes the README.md file of the currrent working directory or
given via the parameter --readme_file and replaces 
all Bokeh images with interactivet Bokeh plots."""
import argparse
import pathlib
import re
import sys
from os.path import dirname, join, realpath

from make_plots import make_plots

sys.path.append(dirname(realpath(__file__)))


parser = argparse.ArgumentParser(
    description="Replace all Bokeh images with interactivet Bokeh plots."
)
parser.add_argument(
    "--readme_file",
    dest="readme_file",
    default="README.md",
    help="Path to README.md file",
)
readme_file = parser.parse_args().readme_file

# Read in README:
with open(readme_file) as f:
    readme = f.read()

# Create Bokeh plots:
plots = make_plots()

# Replace pictures with HTML plots:
for plotname, plot in plots.items():
    readme = re.sub(r"!\[{plotname}\]\(.+\)".format(plotname=plotname), plot, readme)


with open(readme_file, "w") as f:
    f.write(readme)
