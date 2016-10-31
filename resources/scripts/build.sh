#!/bin/bash

D="$(realpath -- "$0")"  # realpath of this script
D="$(dirname -- "$D")"   # resources/scripts
D="$(dirname -- "$D")"   # resources
D="$(dirname -- "$D")"   # project path
ME="$(basename -- "$D")" # name of the project
BUILD="$D/build"         # build path

# Delete previous build
if [ -d "$BUILD" ]
then
	rm -rf -- "$BUILD"
fi

# Create virtualenv and install deps
virtualenv -p python2 "$BUILD/env"
"$BUILD/env/bin/pip" install --upgrade pip -r "$D/requirements.txt"

# Create destdir
mkdir -p "$BUILD/$ME"
mkdir -p "$BUILD/$ME/resources/lib" 
cp -a \
	"$BUILD/env/lib/python2.7/site-packages/"{babelfish,bs4,dateutil,guessit,rebulk,tusubtitulo.py} \
	"$BUILD/$ME/resources/lib"
find "$BUILD/$ME/resources/lib" -name '*.pyc' -print0 | xargs -0 rm 

cp -a \
	addon.xml   \
	icon.png    \
	logo.png    \
	service.py  \
	LICENSE.txt \
	README.xml  \
	"$BUILD/$ME"
(cd "$BUILD"; zip -r "$ME.zip" "$ME" )
