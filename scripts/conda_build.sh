#!/bin/bash
set -e

# Set working directory to script directory: 
cd "$(dirname "$0")"

# Create directories for build process
rm -rf conda
mkdir conda
pushd conda
mkdir pandas-bokeh

conda config --set anaconda_upload no

# Create meta.yaml file that defines conda build process with the release version number:
echo "Specify Pandas-Bokeh release for which conda packages should be build:"
read release_version
cat ../pandas-bokeh/meta_base.yaml | sed "s/release_version/$release_version/g" >> pandas-bokeh/meta.yaml

# Create Conda package for Linux-64:
for i in 6 7 8
   do
      conda-build pandas-bokeh --python 3.$i --output-folder conda-bld
   done

# Create Conda package for all platforms:
conda convert --platform all conda-bld/linux-64/pandas-bokeh*.tar.bz2 -o conda-bld


# Upload all conda files to Anaconda:
anaconda login
find conda-bld/ -name *.tar.bz2 | while read file
do
    echo $file
    anaconda upload $file
done

popd