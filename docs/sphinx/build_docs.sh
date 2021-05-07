#!/bin/bash
set -e


CUR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
pushd $CUR_DIR
  pip install -r requirements_docs.txt
  python source/utils/create_sphinx_index_from_readme.py -i ../../ -o .
  make html
popd
