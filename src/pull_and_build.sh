#!/bin/bash
# $1: src_path
# $2: dest_path

pushd .
cd $1
git pull
popd
pipenv run python build_web.py -s "$1" -d "$2"
