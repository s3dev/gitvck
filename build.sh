#!/usr/bin/env bash

# Define directories to be deleted.
pkg="gitvck"
outdirs=("build" "dist" "${pkg}.egg-info")

# Delete current build/dist directories.
printf "\nDeleting build directories ...\n"
for d in ${outdirs[@]}; do
    if [ -d ${d} ]; then
        printf "Deleting %s\n" "${d}"
        rm -rf ./"${d}"
    fi
done
printf "Done.\n\n"

# Create requirements file.
printf "Creating the requirements file ...\n"
preqs --replace .
printf "Done.\n\n"

# Create the wheel install file.
printf "Creating source dist ...\n"
python -m build --sdist --wheel --no-isolation
printf "Done.\n\n"

printf "Setup complete.\n\n"

