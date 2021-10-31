#!/bin/sh
./$1/bin/coverage run --source src/node/ext/yaml -m node.ext.yaml.tests
./$1/bin/coverage report
./$1/bin/coverage html
