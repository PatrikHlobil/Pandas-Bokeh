set -e

# Clone markdown to HTML Repo:
rm -rf markdown-to-html-github-style
git clone https://github.com/KrauseFx/markdown-to-html-github-style.git

# Copy README.md file:
cp README.md markdown-to-html-github-style/README.md

# Replace Bokeh Images with Bokeh HTML Plots:
python docs/github-pages/replace_pictures_with_Bokeh_plots.py --readme_file markdown-to-html-github-style/README.md

# Checkout correct commit of markdown-to-html-github-style & install dependencies & Convert Markdown to HTML:
pushd markdown-to-html-github-style
git checkout ab625768d13016b606f6a0070accaf7f407945ac
npm install
node convert.js
popd

# Add Bootstrap template theme:
python docs/github-pages/apply_template_theme_to_readme.py --readme_file markdown-to-html-github-style/README.html

# Copy HTML to final destination:
cp markdown-to-html-github-style/README.html docs/github-pages/pages/index.html



