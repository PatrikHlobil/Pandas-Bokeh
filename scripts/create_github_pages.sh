#!/bin/bash
set -e

# Set working directory to script directory parent: 
cd "$(dirname "$0")"
cd ..

# Clone markdown to HTML Repo:
rm -rf github-pages-tmp
mkdir github-pages-tmp

# Copy README.md file:
cp README.md github-pages-tmp/README.md

# Replace Bokeh Images with Bokeh HTML Plots:
python docs/github-pages/replace_pictures_with_Bokeh_plots.py --readme_file github-pages-tmp/README.md

# Convert markdown to html:
python -m markdown -x fenced_code github-pages-tmp/README.md -f github-pages-tmp/README.html

# Add Bootstrap template theme:
python docs/github-pages/apply_template_theme_to_readme.py --readme_file github-pages-tmp/README.html

rm -rf 




