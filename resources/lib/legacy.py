# -*- encoding: utf-8 -*-

import unicodedata
import urllib

from os import path

import xbmc


def normalize(s):
    return unicodedata.normalize(
        'NFKD', unicode(unicode(s, 'utf-8'))
        ).encode('ascii', 'ignore')


def get_file_info():
    item = {}
    item['temp'] = False
    item['rar'] = False
    item['year'] = xbmc.getInfoLabel("VideoPlayer.Year")
    item['season'] = str(xbmc.getInfoLabel("VideoPlayer.Season"))
    item['episode'] = str(xbmc.getInfoLabel("VideoPlayer.Episode"))
    item['tvshow'] = normalize(
        xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))
    item['title'] = normalize(
        xbmc.getInfoLabel("VideoPlayer.OriginalTitle"))
    # Full path of a playing file
    item['file_original_path'] = urllib.unquote(
        xbmc.Player().getPlayingFile().decode('utf-8'))
    item['3let_language'] = []
    item['2let_language'] = []

    # for lang in languages:
    #     item['3let_language'].append(
    #         xbmc.convertLanguage(lang, xbmc.ISO_639_2))
    #     item['2let_language'].append(
    #         xbmc.convertLanguage(lang, xbmc.ISO_639_1))

    # No original title, get just Title
    if item['title'] == "":
        item['title'] = normalize(xbmc.getInfoLabel("VideoPlayer.Title"))

    # Check if season is "Special"
    if item['episode'].lower().find("s") > -1:
        item['season'] = "0"
        item['episode'] = item['episode'][-1:]

    if item['file_original_path'].find("http") > -1:
        item['temp'] = True

    elif (item['file_original_path'].find("rar://") > -1):
        item['rar'] = True
        item['file_original_path'] = path.dirname(
            item['file_original_path'][6:])

    elif (item['file_original_path'].find("stack://") > -1):
        stackPath = item['file_original_path'].split(" , ")
        item['file_original_path'] = stackPath[0][8:]

    item['filename'] = path.basename(item['file_original_path'])

    return item
