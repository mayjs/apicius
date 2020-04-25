#!/bin/bash -l
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
/home/may/.local/bin/pipenv run python hook_server.py -c ../server_config.json
