#!/bin/bash
set -e

# Set working directory to script directory parent: 
cd "$(dirname "$0")"
cd ..

# Create Python wheels:
rm -rf build
rm -rf dist
python setup.py sdist bdist_wheel

# Upload to Pypi:
echo "Upload to PYPI: " && ls dist/*.tar.gz
twine upload dist/*