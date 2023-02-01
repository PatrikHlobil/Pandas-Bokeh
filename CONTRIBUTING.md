
# How to contribute to `Pandas-Bokeh`

Fork the Git Repository and clone it to your machine:

    git clone https://github.com/<username>/Pandas-Bokeh.git

Go into the cloned repository folder and create and activate a Python >= 3.6 virtual environment via venv:

    python3 -m venv venv
    source venv/bin/activate (Linux/Mac)
    venv\Scripts\activate (Windows)

or `conda`:

    conda create --name PandasBokeh python=3.x   # x >= 3.6
    conda activate PandasBokeh

Install `Pandas-Bokeh` in the *editable* mode from the local source:

    pip install -e .

Install test requirements via:

    pip install -r Tests/requirements_test.txt

Make sure that the tests run:

    pytest Tests

Now, setup the precommit hooks via:

    pip install pre-commit
    pre-commit install

Now, before every commit you make to your repository, it will automatically apply black and flake8 on your files to ensure code structure and quality.

# Contributors

[Patrik Hlobil](https://github.com/PatrikHlobil)

    Maintainer and main developer of "Pandas Bokeh"

[munehiro-k](https://github.com/munehiro-k)

 * Pull Request [#16](https://github.com/PatrikHlobil/Pandas-Bokeh/pull/16): *escape column names in default hovertool_string of stacked bar plots*
 
[wwymak](https://github.com/wwymak)

 * Pull Request [#25](https://github.com/PatrikHlobil/Pandas-Bokeh/pull/25): *add option to customize colorbar tick formatting*

[zifeo](https://github.com/zifeo)

 * Pull Request [#29](https://github.com/PatrikHlobil/Pandas-Bokeh/pull/29): *Add holes support for geojson * 

[gjeusel](https://github.com/gjeusel)

 * Pull request [#27](https://github.com/PatrikHlobil/Pandas-Bokeh/pull/27): *Add step plot*

[ashton-sidhu](https://github.com/ashton-sidhu)

 * Pull request[#41](https://github.com/PatrikHlobil/Pandas-Bokeh/pull/41) *Add autoscaling*
 * Pull request[#42](https://github.com/PatrikHlobil/Pandas-Bokeh/pull/42) *Add rangetool*

[lamourj](https://github.com/lamourj)

 * Pull request[#49](https://github.com/PatrikHlobil/Pandas-Bokeh/pull/49) *Speedup GeoDaraframe Plotting*

[verdimrc](https://github.com/verdimrc)

 * Pull request[#96](https://github.com/PatrikHlobil/Pandas-Bokeh/pull/96) *fix problem when passing string-values to `bins`*

[vroger11](https://github.com/vroger11)

 * Pull request[#115](https://github.com/PatrikHlobil/Pandas-Bokeh/pull/115)  *Fix longitude and latitude values checking*
