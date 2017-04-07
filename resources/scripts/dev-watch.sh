#!/bin/bash

D="$(realpath -- "$0")"  # realpath of this script
D="$(dirname -- "$D")"   # resources/scripts
D="$(dirname -- "$D")"   # resources
D="$(dirname -- "$D")"   # project path
ME="$(basename -- "$D")" # name of the project

while :
do
	inotifywait -e modify "$D/service.py" "$D/resources/lib/legacy.py"
	cp "$D/service.py" "$HOME/.kodi/addons/service.subtitles.misubtitulo/service.py"
	cp "$D/resources/lib/legacy.py" "$HOME/.kodi/addons/service.subtitles.misubtitulo/resources/lib/legacy.py"
	find  "$HOME/.kodi/addons/service.subtitles.misubtitulo/" -name '*pyc' -exec rm {} \;
	# tail -f ~/.kodi/temp/kodi.log 
done

