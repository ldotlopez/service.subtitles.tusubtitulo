#!/bin/bash

D="$(realpath -- "$0")"  # realpath of this script
D="$(dirname -- "$D")"   # resources/scripts
D="$(dirname -- "$D")"   # resources
D="$(dirname -- "$D")"   # project path
ME="$(basename -- "$D")" # name of the project
BUILD="$D/build"         # build path
BUILD_SH="$D/resources/scripts/build.sh"   # build.sh script

bash $BUILD_SH
rsync --delete -a "$BUILD/$ME/"  "$HOME/.kodi/addons/$ME/"
cp "$D/addon-devel.xml" "$HOME/.kodi/addons/$ME/addon.xml"

