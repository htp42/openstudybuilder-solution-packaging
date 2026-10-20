#!/bin/sh
# Import protocol datasets into a running OSB, one folder of protocol_imports/
# per dataset. The database image build calls this with the PROTOCOL_IMPORTS
# build arg (set for the extended variant); it also works by hand.
#
# Each dataset folder provides build_dataset.py, fixups.py, preflight.py and
# import.env, whose API_BASE_URL says which OSB to load into.
#
# Run from import_sponsor_data/:
#     sh protocol_imports/import_protocols.sh eCS-DS-001 [more datasets]
#
# Stops at the first failing step: the preflight finds a missing name, or the
# study is incomplete after the import.
set -eu

for name in "$@"; do
    dir="protocol_imports/$name"
    echo "=== Protocol dataset $name ==="
    uv run python "$dir/build_dataset.py"
    uv run python "$dir/fixups.py" prepare
    uv run python "$dir/preflight.py"
    uv run --env-file "$dir/import.env" python -m importers.run_import_compounds
    uv run --env-file "$dir/import.env" python -m importers.run_import_mockdatajson
    uv run python "$dir/fixups.py" finish
done
