#!/bin/bash
rm -rf conda
mkdir conda
pushd conda
conda config --set anaconda_upload no
conda skeleton pypi pandas-bokeh
for i in 6 7
do
   conda-build pandas-bokeh --python 3.$i --output-folder conda-bld
done
conda convert --platform all conda-bld/linux-64/pandas-bokeh*.tar.bz2 -o conda-bld

find conda-bld/ -name *.tar.bz2 | while read file
do
    echo $file
    anaconda upload $file
done

popd