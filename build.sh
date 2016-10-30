#!/bin/bash

D="$(dirname -- "$(realpath -- "$0")")"

if [ ! -d "$D/env" ]
then
	virtualenv -p python2 "$D/env"
fi

"$D/env/bin/pip" install --upgrade pip -r "$D/requirements.txt"

if [ ! -d "$D/resources/lib" ]
then
	mkdir -p "$D/resources/lib" 
fi
cp -a "$D/env/lib/python2.7/site-packages/"{babelfish,bs4,dateutil,guessit,rebulk,tusubtitulo.py} "$D/resources/lib"

if [ -e "$D.zip" ]
then
	rm "$D.zip"
fi
(
	cd "$D"
	zip -x 'env/*' -x '.git*' -r "$D".zip .
)
