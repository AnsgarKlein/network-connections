#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd -P)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"

# Change directory to project root
cd "$PROJECT_ROOT" || exit 1

RESOURCE_DIR='tests/resources'
CONNECTION_SCRIPT="./network_connections.py"

# Test all resources one by one
for resource in "$RESOURCE_DIR/"*; do
    $CONNECTION_SCRIPT "$resource" 2> /dev/null > /dev/null
    test_result=$?

    test_failed='false'
    if [[ "$test_result" -eq 0 ]] ;then
        printf "%-75s\e[0;32m%s\e[0m\n" "Testing ${resource} ..." "OK"
    else
        printf "%-75s\e[0;31m%s\e[0m\n" "Testing ${resource} ..." "FAIL"
        test_failed='true'
    fi
done


# Exit with error code if a single test failed
if [[ "$test_failed" = 'true' ]]; then
    exit 1
fi
