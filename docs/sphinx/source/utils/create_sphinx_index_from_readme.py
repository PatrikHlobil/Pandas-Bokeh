"""This script takes the README.md file of the currrent working directory or
given via the parameter --readme_file and replaces
all Bokeh images with interactivet Bokeh plots."""
import argparse
import re
from pathlib import Path

import click
from make_plots import make_and_return_plots


def _replace_images_with_bokeh_plots(plots, readme):
    for plotname, plot in plots.items():
        print(f"Replace image {plotname}")
        if re.search(r"!\[{plotname}\]\(.+\)".format(plotname=plotname), readme):
            to_replace = re.search(
                r"!\[{plotname}\]\(.+\)".format(plotname=plotname), readme
            ).group()
            readme = readme.replace(
                to_replace, f'<div align="center">\n\n{plot}\n\n</div>'
            )
        else:
            raise KeyError(
                f"No image with name '{plotname}' has been found in the README file."
            )
    return readme


def remove_interactive_docs_section(readme):
    readme = readme.replace(
        r"""---
## Interactive Documentation

Please visit:

https://patrikhlobil.github.io/Pandas-Bokeh/

for an interactive version of the documentation below, where you can **play with the dynamic Bokeh plots**.
""",
        "",
    )
    return readme


@click.command()
@click.option(
    "--input-directory",
    "-i",
    help="Directory containing the input README.md file",
    type=click.Path(exists=True),
)
@click.option(
    "--output-directory",
    "-o",
    help="Directory to output the index.md Sphinx File",
    type=click.Path(),
)
def main(input_directory, output_directory):
    with open(Path(input_directory) / "README.md") as f:
        readme = f.read()
    plots = make_and_return_plots()
    readme = _replace_images_with_bokeh_plots(plots, readme)
    readme = remove_interactive_docs_section(readme)
    readme = readme.replace(r"](docs/Images/", "](_static/Images/")
    with open(Path(output_directory) / "index.md", "w") as f:
        f.write(readme)


if __name__ == "__main__":
    main()
