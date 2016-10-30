# -*- coding: utf-8 -*-

import json
import os
import sys
import re
import shutil
import urllib

import xbmc
import xbmcvfs
import xbmcaddon
import xbmcgui
import xbmcplugin

__addon__ = xbmcaddon.Addon()
__scriptid__ = __addon__.getAddonInfo('id')

__cwd__ = xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")
__profile__ = xbmc.translatePath( __addon__.getAddonInfo('profile')).decode("utf-8")

__resource__ = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib')).decode("utf-8")
__temp__ = xbmc.translatePath(os.path.join(__profile__, 'temp')).decode("utf-8")

settings = xbmcaddon.Addon(id=__scriptid__)

sys.path.append(__resource__)

# Mi's
import urlparse
import unicodedata  # normalizeString
import tusubtitulo


__me__ = 'misubtitulo'


def normalizeString(str):
    return unicodedata.normalize(
        'NFKD', unicode(unicode(str, 'utf-8'))
        ).encode('ascii', 'ignore')

def search(languages=[], preferredlanguage=None):
    item = {}
    item['temp'] = False
    item['rar'] = False
    item['year'] = xbmc.getInfoLabel("VideoPlayer.Year")
    item['season'] = str(xbmc.getInfoLabel("VideoPlayer.Season"))
    item['episode'] = str(xbmc.getInfoLabel("VideoPlayer.Episode"))
    item['tvshow'] = normalizeString(
        xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))
    item['title'] = normalizeString(
        xbmc.getInfoLabel("VideoPlayer.OriginalTitle"))
    # Full path of a playing file
    item['file_original_path'] = urllib.unquote(
        xbmc.Player().getPlayingFile().decode('utf-8'))
    item['3let_language'] = []
    item['2let_language'] = []

    for lang in languages:
        item['3let_language'].append(
            xbmc.convertLanguage(lang, xbmc.ISO_639_2))
        item['2let_language'].append(
            xbmc.convertLanguage(lang, xbmc.ISO_639_1))

    # no original title, get just Title
    if item['title'] == "":
        item['title'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title"))

    # Check if season is "Special"
    if item['episode'].lower().find("s") > -1:
        item['season'] = "0"
        item['episode'] = item['episode'][-1:]

    if item['file_original_path'].find("http") > -1:
        item['temp'] = True

    elif (item['file_original_path'].find("rar://") > -1):
        item['rar'] = True
        item['file_original_path'] = os.path.dirname(
            item['file_original_path'][6:])

    elif (item['file_original_path'].find("stack://") > -1):
        stackPath = item['file_original_path'].split(" , ")
        item['file_original_path'] = stackPath[0][8:]

    by_filename = False
    for f in 'tvshow', 'season', 'episode':
        if f not in item or not item[f]:
            by_filename = True
            break

    api = tusubtitulo.API()

    if by_filename:
        print repr(os.path.basename(item['file_original_path']))
        subs = api.get_subtitles_from_filename(os.path.basename(item['file_original_path']))
    else:

        print(repr((item['tvshow'], item['season'], item['episode'])))
        subs = api.get_subtitles(item['tvshow'], item['season'], item['episode'])

    langs = {
        'es-es': {
            'full': 'Castellano',
            '2let': 'es'
        },
        'es-lat': {
            'full': 'Latino',
            '2let': 'es'
        }
    }

    print repr(subs)
    for sub in subs:
        if sub.language not in langs:
            print("Discard " + sub.language)
            continue

        uri = "plugin://%s/?action=download&url=%s&params=%s" % (
            __scriptid__,
            sub.url,
            urllib.quote(json.dumps(sub.params))
        )
        print(uri)

        listitem = xbmcgui.ListItem(
            label=langs[sub.language]['full'],
            label2=sub.title,
            thumbnailImage=langs[sub.language]['2let']
        )

        listitem.setProperty("sync",  'false')
        listitem.setProperty("hearing_imp", 'false')

        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=uri, listitem=listitem, isFolder=False)
    
    # item = {
    #     '2let_language': ['en', 'es'],
    #     'episode': '6',
    #     'temp': False,
    #     'title': 'The Fetal Kick Catalyst',
    #     'season': '10',
    #     'year': '',
    #     'rar': False,
    #     'tvshow': 'The Big Bang Theory',
    #     'file_original_path': u'smb://DLBOX/storage/TV Shows/The Big Bang Theory/Season 10/The Big Bang Theory - 10x06 The Fetal Kick Catalyst.mkv',  # nopep8
    #     '3let_language': ['eng', 'spa']
    # }


def download(url, params):
    fetcher = tusubtitulo.Fetcher()
    fetcher.set_state(params)

    resp = fetcher.fetch(url)

    subtitle_path = os.path.join(__temp__, 'sub.srt')

    if not xbmcvfs.exists(__temp__):
        xbmcvfs.mkdirs(__temp__)

    with open(subtitle_path, 'wb') as fh:
        fh.write(resp.content)

    return subtitle_path

# [
#     'plugin://service.subtitles.tusubtitulo/',
#     '11',
#     '?action=search&languages=English%2cSpanish&preferredlanguage=Spanish'
# ]

# Parse args
args = {k: v for (k, v) in urlparse.parse_qsl(sys.argv[2][1:])}
if args.get('languages', None):
    args['languages'] = args['languages'].split(',')

def debug(*args, **kwargs):
    print "================="
    print repr(args)
    print repr(kwargs)
    print "================="

debug(sys.argv)
debug(**args)

action = args.pop('action')
if action == 'search':
    search(**args)

elif action == 'download':
    args['params'] = json.loads(args['params'])
    subtitle_file = download(**args)

    listitem = xbmcgui.ListItem(label=subtitle_file)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=subtitle_file, listitem=listitem, isFolder=False)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
