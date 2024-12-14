#!/bin/bash
if [ "$(uname)" == "Linux" ] && [ "$(uname -m)" != "aarch64" ]; then
    cd test
    pytest -sv
    mypy test_mypy_classic_occ_bottle.py
fi
if [ "$(uname -m)" == "aarch64" ]; then
    cd test
    pytest -sv -k "not test_array1_of_gp and not test_array2_of_gp and not test_surface_derivative_eval"
    mypy test_mypy_classic_occ_bottle.py
fi
