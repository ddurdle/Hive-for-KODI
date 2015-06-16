'''
    Hive for XBMC Plugin
    Copyright (C) 2013-2014 ddurdle

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''



import xbmc, xbmcgui, xbmcplugin, xbmcaddon


import sys
import urllib
import cgi
import re
import xbmcvfs

# global variables
PLUGIN_NAME = 'hive'



#helper methods
def log(msg, err=False):
    if err:
        xbmc.log(addon.getAddonInfo('name') + ': ' + msg, xbmc.LOGERROR)
    else:
        xbmc.log(addon.getAddonInfo('name') + ': ' + msg, xbmc.LOGDEBUG)

def parse_query(query):
    queries = cgi.parse_qs(query)
    q = {}
    for key, value in queries.items():
        q[key] = value[0]
    q['mode'] = q.get('mode', 'main')
    return q

def addMediaFile(service, package):

    listitem = xbmcgui.ListItem(package.file.displayTitle(), iconImage=package.file.thumbnail,
                                thumbnailImage=package.file.thumbnail)

    if package.file.type == package.file.AUDIO:
        if package.file.hasMeta:
            infolabels = decode_dict({ 'title' : package.file.displayTitle(), 'tracknumber' : package.file.trackNumber, 'artist': package.file.artist, 'album': package.file.album,'genre': package.file.genre,'premiered': package.file.releaseDate, 'date' : package.file.date, 'size' : package.file.size})
        else:
            infolabels = decode_dict({ 'title' : package.file.displayTitle(), 'date' : package.file.date, 'size' : package.file.size })
        listitem.setInfo('Music', infolabels)
        playbackURL = '?mode=audio'
    elif package.file.type == package.file.VIDEO:
        infolabels = decode_dict({ 'title' : package.file.displayTitle() , 'plot' : package.file.plot, 'date' : package.file.date, 'size' : package.file.size })
        listitem.setInfo('Video', infolabels)
        playbackURL = '?mode=video'
    elif package.file.type == package.file.PICTURE:
        infolabels = decode_dict({ 'title' : package.file.displayTitle() , 'plot' : package.file.plot, 'date' : package.file.date, 'size' : package.file.size })
        listitem.setInfo('Pictures', infolabels)
        playbackURL = '?mode=photo'
    else:
        infolabels = decode_dict({ 'title' : package.file.displayTitle() , 'plot' : package.file.plot })
        listitem.setInfo('Video', infolabels)
        playbackURL = '?mode=video'

    listitem.setProperty('IsPlayable', 'true')
    listitem.setProperty('fanart_image', package.file.fanart)
    cm=[]

    try:
        url = package.getMediaURL()
        cleanURL = re.sub('---', '', url)
        cleanURL = re.sub('&', '---', cleanURL)
    except:
        cleanURL = ''

#    url = PLUGIN_URL+'?mode=streamurl&title='+package.file.title+'&url='+cleanURL
    url = PLUGIN_URL+playbackURL+'&instance='+str(service.instanceName)+'&title='+package.file.title+'&filename='+package.file.id

    if package.file.isEncoded == False:
        cm.append(( addon.getLocalizedString(30086), 'XBMC.RunPlugin('+PLUGIN_URL+'?mode=requestencoding&instance='+str(service.instanceName)+'&title='+package.file.title+'&filename='+package.file.id+')', ))

    cm.append(( addon.getLocalizedString(30042), 'XBMC.RunPlugin('+PLUGIN_URL+'?mode=buildstrm&username='+str(service.authorization.username)+'&title='+package.file.title+'&filename='+package.file.id+')', ))
#    cm.append(( addon.getLocalizedString(30046), 'XBMC.PlayMedia('+playbackURL+'&title='+ package.file.title + '&directory='+ package.folder.id + '&filename='+ package.file.id +'&playback=0)', ))
#    cm.append(( addon.getLocalizedString(30047), 'XBMC.PlayMedia('+playbackURL+'&title='+ package.file.title + '&directory='+ package.folder.id + '&filename='+ package.file.id +'&playback=1)', ))
#    cm.append(( addon.getLocalizedString(30048), 'XBMC.PlayMedia('+playbackURL+'&title='+ package.file.title + '&directory='+ package.folder.id + '&filename='+ package.file.id +'&playback=2)', ))
    #cm.append(( addon.getLocalizedString(30032), 'XBMC.RunPlugin('+PLUGIN_URL+'?mode=download&title='+package.file.title+'&filename='+package.file.id+')', ))

#    listitem.addContextMenuItems( commands )
#    if cm:
    listitem.addContextMenuItems(cm, False)
    xbmcplugin.addDirectoryItem(plugin_handle, url, listitem,
                                isFolder=False, totalItems=0)

def addDirectory(service, folder):

    if folder.id == 'SAVED-SEARCH':
        listitem = xbmcgui.ListItem('Search - ' + decode(folder.displayTitle()), iconImage='', thumbnailImage='')
    else:
        listitem = xbmcgui.ListItem(decode(folder.displayTitle()), iconImage=decode(folder.thumb), thumbnailImage=decode(folder.thumb))
    fanart = addon.getAddonInfo('path') + '/fanart.jpg'


    if folder.id != '':
        cm=[]
        cm.append(( addon.getLocalizedString(30042), 'XBMC.RunPlugin('+PLUGIN_URL+'?mode=buildstrm&title='+folder.title+'&username='+str(service.authorization.username)+'&folderID='+str(folder.id)+')', ))
        cm.append(( addon.getLocalizedString(30081), 'XBMC.RunPlugin('+PLUGIN_URL+'?mode=createbookmark&title='+folder.title+'&instance='+str(service.instanceName)+'&folderID='+str(folder.id)+')', ))

        listitem.addContextMenuItems(cm, False)
    listitem.setProperty('fanart_image', fanart)

    if folder.id == 'SAVED-SEARCH':
        xbmcplugin.addDirectoryItem(plugin_handle, PLUGIN_URL+'?mode=search&instance='+str(service.instanceName)+'&criteria='+folder.title, listitem,
                                isFolder=True, totalItems=0)
    else:
        xbmcplugin.addDirectoryItem(plugin_handle, service.getDirectoryCall(folder), listitem,
                                isFolder=True, totalItems=0)

def addMenu(url,title):
    listitem = xbmcgui.ListItem(decode(title), iconImage='', thumbnailImage='')
    fanart = addon.getAddonInfo('path') + '/fanart.jpg'

    listitem.setProperty('fanart_image', fanart)
    xbmcplugin.addDirectoryItem(plugin_handle, url, listitem,
                                isFolder=True, totalItems=0)


#http://stackoverflow.com/questions/1208916/decoding-html-entities-with-python/1208931#1208931
def _callback(matches):
    id = matches.group(1)
    try:
        return unichr(int(id))
    except:
        return id

def decode(data):
    return re.sub("&#(\d+)(;|(?=\s))", _callback, data).strip()

def decode_dict(data):
    for k, v in data.items():
        if type(v) is str or type(v) is unicode:
            data[k] = decode(v)
    return data


def numberOfAccounts(accountType):

    count = 1
    max_count = int(addon.getSetting(accountType+'_numaccounts'))
    actualCount = 0
    while True:
        try:
            if addon.getSetting(accountType+str(count)+'_username') != '':
                actualCount = actualCount + 1
        except:
            break
        if count == max_count:
            break
        count = count + 1
    return actualCount


#global variables
PLUGIN_URL = sys.argv[0]
plugin_handle = int(sys.argv[1])
plugin_queries = parse_query(sys.argv[2][1:])

addon = xbmcaddon.Addon(id='plugin.video.hive')

addon_dir = xbmc.translatePath( addon.getAddonInfo('path') )

import os
sys.path.append(os.path.join( addon_dir, 'resources', 'lib' ) )

import hive
import cloudservice
import folder
import file
import package
import mediaurl
import authorization


#from resources.lib import gPlayer
#from resources.lib import tvWindow


#debugging
try:

    remote_debugger = addon.getSetting('remote_debugger')
    remote_debugger_host = addon.getSetting('remote_debugger_host')

    # append pydev remote debugger
    if remote_debugger == 'true':
        # Make pydev debugger works for auto reload.
        # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
        import pysrc.pydevd as pydevd
        # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
        pydevd.settrace(remote_debugger_host, stdoutToServer=True, stderrToServer=True)
except ImportError:
    log(addon.getLocalizedString(30016), True)
    sys.exit(1)
except :
    pass


# retrieve settings
user_agent = addon.getSetting('user_agent')


mode = plugin_queries['mode']

# make mode case-insensitive
mode = mode.lower()


log('plugin url: ' + PLUGIN_URL)
log('plugin queries: ' + str(plugin_queries))
log('plugin handle: ' + str(plugin_handle))


instanceName = ''
try:
    instanceName = (plugin_queries['instance']).lower()
except:
    pass

xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_SIZE)


#* utilities *
#clear the authorization token(s) from the identified instanceName or all instances
if mode == 'clearauth':

    if instanceName != '':

        try:
            addon.setSetting(instanceName + '_token', '')
            xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30023))
        except:
            #error: instance doesn't exist
            pass

    # clear all accounts
    else:
        count = 1
        max_count = int(addon.getSetting(PLUGIN_NAME+'_numaccounts'))
        while True:
            instanceName = PLUGIN_NAME+str(count)
            try:
                addon.setSetting(instanceName + '_token', '')
            except:
                break
            if count == max_count:
                break
            count = count + 1
        xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30023))
    xbmcplugin.endOfDirectory(plugin_handle)


#create strm files
elif mode == 'buildstrm':

    silent = 0
    try:
        silent = int(addon.getSetting('strm_silent'))
    except:
        silent = 0

    try:
        silent = int(plugin_queries['silent'])
    except:
        pass

    path = ''
    try:
        path = int(plugin_queries['path'])
    except:
        pass

    try:
        path = str(addon.getSetting('strm_path'))
    except:
        pass

    if path == '':
        path = xbmcgui.Dialog().browse(0,addon.getLocalizedString(30026), 'files','',False,False,'')
        addon.setSetting('strm_path', path)

    if path != '':
        if silent == 0:
            returnPrompt = xbmcgui.Dialog().yesno(addon.getLocalizedString(30000), addon.getLocalizedString(30027) + '\n'+path +  '?')
        else:
            returnPrompt = True

    if path != '' and returnPrompt:

        if silent != 2:
            try:
                pDialog = xbmcgui.DialogProgressBG()
                pDialog.create(addon.getLocalizedString(30000), 'Building STRMs...')
            except:
                pass

        try:
            url = plugin_queries['streamurl']
            title = plugin_queries['title']
            url = re.sub('---', '&', url)
        except:
            url=''

        if url != '':

                filename = path + '/' + title+'.strm'
                strmFile = xbmcvfs.File(filename, "w")


                strmFile.write(url+'\n')
                strmFile.close()
        else:

            try:
                folderID = plugin_queries['folderID']
                title = plugin_queries['title']
            except:
                folderID = ''

            try:
                filename = plugin_queries['filename']
                title = plugin_queries['title']
            except:
                filename = ''


            try:
                    invokedUsername = plugin_queries['username']
            except:
                    invokedUsername = ''

            if folderID != '':

                count = 1
                max_count = int(addon.getSetting(PLUGIN_NAME+'_numaccounts'))
                loop = True
                while loop:
                    instanceName = PLUGIN_NAME+str(count)
                    try:
                        username = addon.getSetting(instanceName+'_username')
                        if username == invokedUsername:

                            #let's log in
                            service = hive.hive(PLUGIN_URL,addon,instanceName, user_agent)
                            loop = False
                    except:
                        break

                    if count == max_count:
                        #fallback on first defined account
                        service = hive.hive(PLUGIN_URL,addon,PLUGIN_NAME+'1', user_agent)
                        break
                    count = count + 1

                service.buildSTRM(path + '/'+title,folderID)



            elif filename != '':
                            url = PLUGIN_URL+'?mode=video&title='+title+'&filename='+filename + '&username='+invokedUsername
#                            filename = xbmc.translatePath(os.path.join(path, title+'.strm'))
                            filename = path + '/' + title+'.strm'
                            strmFile = xbmcvfs.File(filename, "w")

                            strmFile.write(url+'\n')
                            strmFile.close()

            else:

                count = 1
                max_count = int(addon.getSetting(PLUGIN_NAME+'_numaccounts'))
                while True:
                    instanceName = PLUGIN_NAME+str(count)
                    try:
                        username = addon.getSetting(instanceName+'_username')
                    except:
                        username = ''

                    if username != '':
                        service = hive.hive(PLUGIN_URL,addon,instanceName, user_agent)
                        service.buildSTRM(path + '/'+username)

                    if count == max_count:
                        #fallback on first defined account
                        service = hive.hive(PLUGIN_URL,addon,PLUGIN_NAME+'1', user_agent)
                        break
                    count = count + 1

        if silent != 2:
            try:
                pDialog.update(100)
            except:
                pass
        if silent == 0:
            xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30028))
    xbmcplugin.endOfDirectory(plugin_handle)


#create strm files
elif mode == 'createbookmark':

        try:
                folderID = plugin_queries['folderID']
                title = plugin_queries['title']
                instanceName = plugin_queries['instance']
        except:
                folderID = ''

        if folderID != '':

                try:
                    username = addon.getSetting(instanceName+'_username')
                except:
                    username = ''

                if username != '':
                    service = hive.hive(PLUGIN_URL,addon,instanceName, user_agent)

                    newTitle = ''
                    try:
                        dialog = xbmcgui.Dialog()
                        newTitle = dialog.input('Enter a name for the bookmark', title, type=xbmcgui.INPUT_ALPHANUM)
                    except:
                        newTitle = title

                    if newTitle == '':
                        newTitle = title

                    service.createBookmark(folderID,newTitle)
        xbmcplugin.endOfDirectory(plugin_handle)


#create strm files
elif mode == 'createsearch':

        searchText = ''
        try:
            searchText = addon.getSetting('criteria')
        except:
            searchText = ''

        if searchText == '':

            try:
                dialog = xbmcgui.Dialog()
                searchText = dialog.input('Enter search string', type=xbmcgui.INPUT_ALPHANUM)
            except:
                xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30100))
                searchText = 'life'

        if searchText != '':

            instanceName = ''
            try:
                instanceName = (plugin_queries['instance']).lower()
            except:
                pass

            numberOfAccounts = numberOfAccounts(PLUGIN_NAME)

            # show list of services
            if numberOfAccounts > 1 and instanceName == '':
                count = 1
                max_count = int(addon.getSetting(PLUGIN_NAME+'_numaccounts'))
                while True:
                    instanceName = PLUGIN_NAME+str(count)
                    try:
                        username = addon.getSetting(instanceName+'_username')
                        if username != '':
                            addMenu(PLUGIN_URL+'?mode=main&instance='+instanceName,username)
                    except:
                        break
                    if count == max_count:
                        #fallback on first defined account
                        service = hive.hive(PLUGIN_URL,addon,PLUGIN_NAME+'1', user_agent)
                        break
                    count = count + 1

            else:
                # show index of accounts
                if instanceName == '' and numberOfAccounts == 1:

                    count = 1
                    max_count = int(addon.getSetting(PLUGIN_NAME+'_numaccounts'))
                    loop = True
                    while loop:
                        instanceName = PLUGIN_NAME+str(count)
                        try:
                            username = addon.getSetting(instanceName+'_username')
                            if username != '':

                                #let's log in
                                service = hive.hive(PLUGIN_URL,addon,instanceName, user_agent)
                                loop = False
                        except:
                            break

                        if count == max_count:
                            #fallback on first defined account
                            service = hive.hive(PLUGIN_URL,addon,PLUGIN_NAME+'1', user_agent)

                            break
                        count = count + 1

                        # no accounts defined
                elif numberOfAccounts == 0:

                    #legacy account conversion
                    try:
                        username = addon.getSetting('username')

                        if username != '':
                            addon.setSetting(PLUGIN_NAME+'1_username', username)
                            addon.setSetting(PLUGIN_NAME+'1_password', addon.getSetting('password'))
                            addon.setSetting(PLUGIN_NAME+'1_auth_token', addon.getSetting('auth_token'))
                            addon.setSetting(PLUGIN_NAME+'1_auth_session', addon.getSetting('auth_session'))
                            addon.setSetting('username', '')
                            addon.setSetting('password', '')
                            addon.setSetting('auth_token', '')
                            addon.setSetting('auth_session', '')
                        else:
                            xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30015))
                            log(addon.getLocalizedString(30015), True)
                            xbmcplugin.endOfDirectory(plugin_handle)
                    except :
                            xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30015))
                            log(addon.getLocalizedString(30015), True)
                            xbmcplugin.endOfDirectory(plugin_handle)

                    #let's log in
                    service = hive.hive(PLUGIN_URL,addon,instanceName, user_agent)


                # show entries of a single account (such as folder)
                elif instanceName != '':

                    service = hive.hive(PLUGIN_URL,addon,instanceName, user_agent)

            try:
                service
            except NameError:
                xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30051), addon.getLocalizedString(30052), addon.getLocalizedString(30053))
                log(addon.getLocalizedString(30050)+ 'hive-login', True)
                xbmcplugin.endOfDirectory(plugin_handle)

            service.createSearch(searchText)

            mediaItems = service.getSearchResults(searchText)

            if mediaItems:
                    for item in mediaItems:

                        try:
                            if item.file is None:
                                addDirectory(service, item.folder)
                            else:
                                addMediaFile(service, item)
                        except:
                            addMediaFile(service, item)

            service.updateAuthorization(addon)
            xbmcplugin.endOfDirectory(plugin_handle)

numberOfAccounts = numberOfAccounts(PLUGIN_NAME)

try:
    invokedUsername = plugin_queries['username']
except:
    invokedUsername = ''


# show list of services
if numberOfAccounts > 1 and instanceName == '' and invokedUsername == '':
    if mode == 'main':
        mode = ''
    count = 1
    max_count = int(addon.getSetting(PLUGIN_NAME+'_numaccounts'))
    while True:
        instanceName = PLUGIN_NAME+str(count)
        try:
            username = addon.getSetting(instanceName+'_username')
            if username != '':
                addMenu(PLUGIN_URL+'?mode=main&instance='+instanceName,username)
                try:
                    service
                except:
                    service = hive.hive(PLUGIN_URL,addon,instanceName, user_agent)
        except:
            break
        if count == max_count:
            #fallback on first defined account
            service = hive.hive(PLUGIN_URL,addon,PLUGIN_NAME+'1', user_agent)
            break
        count = count + 1

else:
    # show index of accounts
    if instanceName == '' and invokedUsername == '' and numberOfAccounts == 1:

        count = 1
        max_count = int(addon.getSetting(PLUGIN_NAME+'_numaccounts'))
        loop = True
        while loop:
            instanceName = PLUGIN_NAME+str(count)
            try:
                username = addon.getSetting(instanceName+'_username')
                if username != '':

                    #let's log in
                    service = hive.hive(PLUGIN_URL,addon,instanceName, user_agent)
                    loop = False
            except:
                break

            if count == max_count:
                #fallback on first defined account
                service = hive.hive(PLUGIN_URL,addon,PLUGIN_NAME+'1', user_agent)
                break
            count = count + 1

    # no accounts defined
    elif numberOfAccounts == 0:

        #legacy account conversion
        try:
            username = addon.getSetting('username')

            if username != '':
                addon.setSetting(PLUGIN_NAME+'1_username', username)
                addon.setSetting(PLUGIN_NAME+'1_password', addon.getSetting('password'))
                addon.setSetting(PLUGIN_NAME+'1_auth_token', addon.getSetting('auth_token'))
                addon.setSetting(PLUGIN_NAME+'1_auth_session', addon.getSetting('auth_session'))
                addon.setSetting('username', '')
                addon.setSetting('password', '')
                addon.setSetting('auth_token', '')
                addon.setSetting('auth_session', '')
            else:
                xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30015))
                log(addon.getLocalizedString(30015), True)
                xbmcplugin.endOfDirectory(plugin_handle)
        except :
            xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30015))
            log(addon.getLocalizedString(30015), True)
            xbmcplugin.endOfDirectory(plugin_handle)

        #let's log in
        service = hive.hive(PLUGIN_URL,addon,instanceName, user_agent)


    # show entries of a single account (such as folder)
    elif instanceName != '':

        service = hive.hive(PLUGIN_URL,addon,instanceName, user_agent)

    elif invokedUsername != '':

        count = 1
        max_count = int(addon.getSetting(PLUGIN_NAME+'_numaccounts'))
        loop = True
        while loop:
            instanceName = PLUGIN_NAME+str(count)
            try:
                username = addon.getSetting(instanceName+'_username')
                if username == invokedUsername:

                    #let's log in
                    service = hive.hive(PLUGIN_URL,addon,instanceName, user_agent)
                    loop = False
            except:
                break

            if count == max_count:
                #fallback on first defined account
                service = hive.hive(PLUGIN_URL,addon,PLUGIN_NAME+'1', user_agent)
                break
            count = count + 1


if mode == 'main':
    addMenu(PLUGIN_URL+'?mode=options','<< '+addon.getLocalizedString(30043)+' >>')
    addMenu(PLUGIN_URL+'?mode=search','<<SEARCH>>')

#dump a list of videos available to play
if mode == 'main' or mode == 'folder':

    folderName=''

    if (mode == 'folder'):
        folderName = plugin_queries['directory']
    else:
        pass

    try:
        service
    except NameError:
        xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30051), addon.getLocalizedString(30052), addon.getLocalizedString(30053))
        log(addon.getLocalizedString(30050)+ 'hive-login', True)
        xbmcplugin.endOfDirectory(plugin_handle)

    if folderName == '':
        addMenu(PLUGIN_URL+'?mode=folder&instance='+instanceName+'&directory=FRIENDS','['+addon.getLocalizedString(30091)+']')
        addMenu(PLUGIN_URL+'?mode=folder&instance='+instanceName+'&directory=FEED','['+addon.getLocalizedString(30092)+']')
        mediaItems = service.getCollections()
        if mediaItems:
            for item in mediaItems:

                try:
                    if item.file is None:
                        addDirectory(service, item.folder)
                    else:
                        addMediaFile(service, item)
                except:
                    addMediaFile(service, item)

    mediaItems = service.getMediaList(folderName,0)

    if mediaItems:
            for item in mediaItems:

                try:
                    if item.file is None:
                        addDirectory(service, item.folder)
                    else:
                        addMediaFile(service, item)
                except:
                    addMediaFile(service, item)

    service.updateAuthorization(addon)

#dump a list of videos available to play
elif mode == 'search':

    searchText = ''
    try:
        searchText = plugin_queries['criteria']
    except:
        searchText = ''

    if searchText == '':

            try:
                dialog = xbmcgui.Dialog()
                searchText = dialog.input('Enter search string', type=xbmcgui.INPUT_ALPHANUM)
            except:
                xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30100))
                searchText = 'life'

    try:
        service
    except NameError:
        xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30051), addon.getLocalizedString(30052), addon.getLocalizedString(30053))
        log(addon.getLocalizedString(30050)+ 'hive-login', True)
        xbmcplugin.endOfDirectory(plugin_handle)


    mediaItems = service.getSearchResults(searchText)


    if mediaItems:
            for item in mediaItems:

                try:
                    if item.file is None:
                        addDirectory(service, item.folder)
                    else:
                        addMediaFile(service, item)
                except:
                    addMediaFile(service, item)

    service.updateAuthorization(addon)
#    xbmcplugin.setContent(int(sys.argv[1]), 'videos')
#    xbmcplugin.setProperty(int(sys.argv[1]),'IsPlayable', 'false')
#    xbmc.executebuiltin("ActivateWindow(Videos)")

#play a video given its exact-title
elif mode == 'video' or mode == 'audio':

    filename = plugin_queries['filename']
    try:
        directory = plugin_queries['directory']
    except:
        directory = ''

    try:
        title = plugin_queries['title']
    except:
        title = ''

    try:
        service
    except NameError:
        xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30051), addon.getLocalizedString(30052), addon.getLocalizedString(30053))
        log(aaddon.getLocalizedString(30050)+ 'hive-login', True)
        xbmcplugin.endOfDirectory(plugin_handle)

    playbackType = 0
    try:
        playbackType = plugin_queries['playback']
    except:
        playbackType = ''
        if service.isPremium:
            try:
                if mode == 'audio':
                    playbackType = int(addon.getSetting('playback_type_audio'))
                else:
                    playbackType = int(addon.getSetting('playback_type_video'))
            except:
                playbackType = 0
        else:
            try:
                if mode == 'audio':
                    playbackType = int(addon.getSetting('free_playback_type_audio'))
                else:
                    playbackType = int(addon.getSetting('free_playback_type_video'))
            except:
                if mode == 'audio':
                    playbackType = 0
                else:
                    playbackType = 1

    mediaFile = file.file(filename, title, '', 0, '','')
    mediaFolder = folder.folder(directory,directory)
    mediaURLs = service.getPlaybackCall(playbackType,package.package(mediaFile,mediaFolder ))

    playbackURL = ''

    # BEGIN JoKeRzBoX
    # - Get list of possible resolutions (quality), pre-ordered from best to lower res, from a String constant
    # - Create associative array (a.k.a. hash list) availableQualities with each available resolution (key) and media URL (value)
    # - Simple algorithm to go through possible resolutions and find the best available one based on user's choice
    # FIX: list of qualities shown to user are now ordered from highest to low resolution
    if mode == 'audio':
        possibleQualities = addon.getLocalizedString(30058)
    else:
        possibleQualities = addon.getLocalizedString(30057)
    listPossibleQualities = possibleQualities.split("|")
    availableQualities = {}
    for mediaURL in mediaURLs:
        availableQualities[mediaURL.qualityDesc] = mediaURL.url

    ## User has chosen: "Always original quality"
    #if playbackType == 0:
    #    playbackURL = availableQualities['original']

    # User has chosen a max quality other than "original". Let's decide on the best stream option available
    #else:
    userChosenQuality = listPossibleQualities[playbackType]
    reachedThreshold = 0
    for quality in listPossibleQualities:
        if quality == userChosenQuality:
            reachedThreshold  = 1
        if reachedThreshold and quality in availableQualities:
            playbackURL = availableQualities[quality]
            chosenRes = str(quality)
            reachedThreshold = 0
    if reachedThreshold and playbackType != len(listPossibleQualities)-1 and len(availableQualities) == 3:
        # Means that the exact encoding requested by user was not found.
        # Also, there are the only available: original, 360p and  240p (because cont = 3).
        # Therefore if user did not choose "always ask" it is safe to assume "original" is the one closest to the quality selected by user
        playbackURL = availableQualities['original']

    # Desired quality still not found. Lets bring list of available options and let user select
    if  playbackURL == '':
        options = []
        for quality in listPossibleQualities:
            if quality in availableQualities:
                options.append(quality)
        ret = xbmcgui.Dialog().select(addon.getLocalizedString(30033), options)
        if ret >= 0:
            playbackURL = availableQualities[str(options[ret])]
            chosenRes = str(options[ret])

    # END JoKeRzBoX

    # JoKeRzBox: FIX: when user does not choose from list, addon was still playing a stream
    if playbackURL != '':
        item = xbmcgui.ListItem(path=playbackURL)
#       item.setInfo( type="Video", infoLabels={ "Title": title , "Plot" : title } )
#       item.setInfo( type="Video")
        # Add resolution to beginning of title while playing media. Format "<RES> | <TITLE>"
        if mode == 'audio':
            item.setInfo( type="music", infoLabels={ "Title": title + " @ " + chosenRes} )
        else:
            item.setInfo( type="video", infoLabels={ "Title": title + " @ " + chosenRes, "Plot" : title } )
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

#play a video given its exact-title
elif mode == 'requestencoding':

    filename = plugin_queries['filename']
    try:
        directory = plugin_queries['directory']
    except:
        directory = ''

    try:
        title = plugin_queries['title']
    except:
        title = ''

    try:
            service
    except NameError:
            xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30051), addon.getLocalizedString(30052), addon.getLocalizedString(30053))
            log(aaddon.getLocalizedString(30050)+ 'hive-login', True)
            xbmcplugin.endOfDirectory(plugin_handle)

    mediaFile = file.file(filename, title, '', 0, '','')
    mediaFolder = folder.folder(directory,directory)
    mediaURLs = service.getPlaybackCall(0,package.package(mediaFile,mediaFolder ))

    xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30087), title)


elif mode == 'photo':

    filename = plugin_queries['filename']
    try:
        directory = plugin_queries['directory']
    except:
        directory = ''

    try:
        title = plugin_queries['title']
    except:
        title = ''

    try:
            service
    except NameError:
            xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30051), addon.getLocalizedString(30052), addon.getLocalizedString(30053))
            log(aaddon.getLocalizedString(30050)+ 'hive-login', True)
            xbmcplugin.endOfDirectory(plugin_handle)


    path = ''
    try:
        path = addon.getSetting('photo_folder')
    except:
        pass

    import os.path

    if not os.path.exists(path):
        path = ''

    while path == '':
        path = xbmcgui.Dialog().browse(0,addon.getLocalizedString(30038), 'files','',False,False,'')
        if not os.path.exists(path):
            path = ''
        else:
            addon.setSetting('photo_folder', path)



    mediaFile = file.file(filename, title, '', 0, '','')
    mediaFolder = folder.folder(directory,directory)
    mediaURLs = service.getPlaybackCall(0,package.package(mediaFile,mediaFolder ))

    playbackURL = ''
    for mediaURL in mediaURLs:
            if mediaURL.qualityDesc == 'original':
                playbackURL = mediaURL.url

    import xbmcvfs
    xbmcvfs.mkdir(path + '/'+str(directory))
    try:
        xbmcvfs.rmdir(path + '/'+str(directory)+'/'+str(title))
    except:
        pass

    service.downloadPicture(playbackURL, path + '/'+str(directory) + '/'+str(title))
    xbmc.executebuiltin("XBMC.ShowPicture("+path + '/'+str(directory) + '/'+str(title)+")")


#play a video given its exact-title
elif mode == 'streamurl':

    url = plugin_queries['url']

    try:
        title = plugin_queries['title']
    except:
        title = ''

    try:
            service
    except NameError:
            xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30051), addon.getLocalizedString(30052), addon.getLocalizedString(30053))
            log(aaddon.getLocalizedString(30050)+ 'hive-login', True)
            xbmcplugin.endOfDirectory(plugin_handle)

    url = re.sub('---', '&', url)

    item = xbmcgui.ListItem(path=url)
    item.setInfo( type="Video", infoLabels={ "Title": title , "Plot" : title } )
#    item.setInfo( type="Music", infoLabels={ "Title": title , "Plot" : title } )

    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)


if mode == 'options' or mode == 'buildstrm' or mode == 'clearauth':
    addMenu(PLUGIN_URL+'?mode=clearauth','<<'+addon.getLocalizedString(30018)+'>>')
    addMenu(PLUGIN_URL+'?mode=buildstrm','<<'+addon.getLocalizedString(30025)+'>>')
    addMenu(PLUGIN_URL+'?mode=createsearch','<<Save Search>>')



xbmcplugin.endOfDirectory(plugin_handle)
