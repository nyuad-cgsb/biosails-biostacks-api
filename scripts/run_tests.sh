#!/usr/bin/env bash

#set -x -e
echo "Beginning python tests"
find $(pwd)/dags -type f -name "*test*.py"  |  xargs -I {} python {}