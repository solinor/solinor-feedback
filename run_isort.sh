#!/bin/bash
set -e
isort --diff --check --recursive improve_stuff feedback *.py
