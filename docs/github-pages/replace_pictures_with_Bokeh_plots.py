"""This script takes the README.md file of the currrent working directory or
given via the parameter --readme_file and replaces
all Bokeh images with interactivet Bokeh plots."""
import argparse
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
    print(f"Replace image {plotname}")
    if re.search(r"!\[{plotname}\]\(.+\)".format(plotname=plotname), readme):
        to_replace = re.search(
            r"!\[{plotname}\]\(.+\)".format(plotname=plotname), readme
        ).group()
        readme = readme.replace(to_replace, f'<div align="center">\n\n{plot}\n\n</div>')
    else:
        raise KeyError(
            f"No image with name '{plotname}' has been found in the README file '{readme_file}'."
        )

# Replace path to remaining pictures:
readme = readme.replace(r"![](docs/Images/Pandas-Bokeh-Logo.png)", "")
readme = readme.replace(r"docs/Images/", "Images/")

with open(readme_file, "w") as f:
    f.write(readme)
