#!/bin/bash

# Small script for freezing Python libraries in a more custom way

####################
# IMPORTANT: This script is thought to be invoked from the ROOT of the project.
####################

source "conf/project.conf"
source "$VENV_ACTIVATE"

pip freeze | grep -v 'pkg-resources==0.0.0' > "$REQUIREMENTS_FILE"

deactivate
