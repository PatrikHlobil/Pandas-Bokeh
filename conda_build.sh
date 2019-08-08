#!/bin/bash
rm -rf conda
mkdir conda
pushd conda
conda skeleton pypi pandas-bokeh
for i in 6 7
do
   conda-build pandas-bokeh --python 3.$i --output-folder conda-package
done
popd
