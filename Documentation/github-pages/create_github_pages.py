import pathlib
import re
from os.path import dirname, join, realpath
from subprocess import PIPE, run

import markdown

from make_plots import make_plots

CUR_DIR = dirname(realpath(__file__))
BASE_DIR = dirname(dirname(CUR_DIR))

# Read in README:
with open(join(BASE_DIR, "README.md")) as f:
    readme = f.read()

readme = readme.replace("```python", "```")

# Create Bokeh plots:
plots = make_plots()

#Replace pictures with HTML plots:
for plotname, plot in plots.items():
    readme = re.sub(r"!\[{plotname}\]\(.+\)".format(plotname=plotname), f"----{plotname}----", readme)

html = markdown.markdown(readme, extensions=["markdown.extensions.fenced_code"])

for plotname, plot in plots.items():
    html = re.sub(f"<p>----{plotname}----</p>", plot, html)

with open(join(CUR_DIR, "test.html"), "w") as f:
    f.write(html)
