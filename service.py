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
import unicodedata  # normalize
import tusubtitulo

import legacy

__me__ = 'misubtitulo'


#
# Utils
#

def log(name, msg):
    print("{id}.{name}: {msg}".format(id=__scriptid__, name=name, msg=msg))


#
# Plugin actions
#

def search(languages=[], preferredlanguage=None):
    item = legacy.get_file_info()
    # item = {
    #     'episode': '6',
    #     'temp': False,
    #     'title': 'The Fetal Kick Catalyst',
    #     'season': '10',
    #     'year': '',
    #     'rar': False,
    #     'tvshow': 'The Big Bang Theory',
    #     'file_original_path': u'/storage/TV Shows/The Big Bang Theory/Season 10/The Big Bang Theory - 10x06 The Fetal Kick Catalyst.mkv',  # nopep8
    # }

    # Determine if we have all required data for a concrete search
    by_filename = False
    for f in ['tvshow', 'season', 'episode']:
        if f not in item or not item[f]:
            by_filename = True
            break

    # Search for subtitles
    api = tusubtitulo.API()
    if by_filename:
        filename = os.path.basename(item['file_original_path'])
        log(__name__, "Search subtitles for filename: '{filename}'".format(
            filename=filename))
        subs = api.get_subtitles_from_filename(filename)
    else:
        log(__name__, "Search subtitles for show: {show}, season: {season}, "
                      "episode: {episode}".format(**item))
        subs = api.get_subtitles(
            item['tvshow'], item['season'], item['episode'])

    langs = {
        'es-es': {
            'full': 'Castellano',
            '2let': 'es',
            'index': 0
        },
        'es-lat': {
            'full': 'Latino',
            '2let': 'es',
            'index': 1
        }
    }

    log(__name__, "{n} subtitles found".format(n=len(subs)))

    subs = [x for x in subs if x.language in langs]
    subs = sorted(subs, key=lambda x: langs[x.language]['index'])
    log(__name__, "{n} subtitles in valid languages".format(n=len(subs)))

    for sub in subs:
        uri = "plugin://%s/?action=download&url=%s&params=%s" % (
            __scriptid__,
            sub.url,
            urllib.quote(json.dumps(sub.params))
        )
        log(__name__, "Reporting subtitle: {url} (params={params}".format(
            url=sub.url,
            params=repr(sub.params)
        ))

        listitem = xbmcgui.ListItem(
            label=langs[sub.language]['full'],
            label2=sub.title,
            thumbnailImage=langs[sub.language]['2let']
        )
        listitem.setProperty("sync",  'false')
        listitem.setProperty("hearing_imp", 'false')
        xbmcplugin.addDirectoryItem(
            handle=int(sys.argv[1]), url=uri, listitem=listitem,
            isFolder=False)




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
