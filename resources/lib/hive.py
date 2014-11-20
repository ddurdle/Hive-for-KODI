'''
    Hive XBMC Plugin
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

import os
import re
import urllib, urllib2
import cookielib
#from resources.lib import authorization
from cloudservice import cloudservice
#from resources.lib import folder
#from resources.lib import file
#from resources.lib import package
#from resources.lib import mediaurl
import unicodedata


import xbmc, xbmcaddon, xbmcgui, xbmcplugin

addon = xbmcaddon.Addon(id='plugin.video.hive')
addon_dir = xbmc.translatePath( addon.getAddonInfo('path') )

import os
import sys

sys.path.append(os.path.join( addon_dir, 'resources', 'lib' ) )

import authorization
#import cloudservice
import folder
import file
import package
import mediaurl
import crashreport

#
#
#
class hive(cloudservice):


    AUDIO = 1
    VIDEO = 2
    PICTURE = 3

    MEDIA_TYPE_MUSIC = 1
    MEDIA_TYPE_VIDEO = 2
    MEDIA_TYPE_PICTURE = 3

    MEDIA_TYPE_FOLDER = 0

    CACHE_TYPE_MEMORY = 0
    CACHE_TYPE_DISK = 1
    CACHE_TYPE_AJAX = 2

    ##
    # initialize (save addon, instance name, user agent)
    ##
    def __init__(self, PLUGIN_URL, addon, instanceName, user_agent):
        self.PLUGIN_URL = PLUGIN_URL
        self.addon = addon
        self.instanceName = instanceName

        self.crashreport = crashreport.crashreport(self.addon)
#        self.crashreport.sendError('test','test')

        try:
            username = self.addon.getSetting(self.instanceName+'_username')
        except:
            username = ''
        self.authorization = authorization.authorization(username)


        self.cookiejar = cookielib.CookieJar()

        self.user_agent = user_agent


        self.login();



    ##
    # perform login
    ##
    def login(self):

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar), MyHTTPErrorProcessor)
        opener.addheaders = [('User-Agent', self.user_agent)]

        url = 'https://api-beta.hive.im/api/user/sign-in/'

        request = urllib2.Request(url)
        self.cookiejar.add_cookie_header(request)

        # try login
        try:
            response = opener.open(request,'email='+self.authorization.username+'&password='+self.addon.getSetting(self.instanceName+'_password')+'&ip=MTkyLjE3MS40MC4xNg==')

        except urllib2.URLError, e:
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
            return
        response_data = response.read()
        response.close()

        for cookie in self.cookiejar:
            for r in re.finditer(' ([^\=]+)\=([^\s]+)\s',
                        str(cookie), re.DOTALL):
                cookieType,cookieValue = r.groups()

        for r in re.finditer('\"(token)\"\:\"([^\"]+)\"',
                             response_data, re.DOTALL):
            tokenName,tokenValue = r.groups()
            self.authorization.setToken(tokenName,tokenValue)

        if (tokenValue == ''):
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050),'tokenValue')
            self.crashreport.sendError('login:tokenValue',response_data)
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+ 'tokenValue', xbmc.LOGERROR)
            return


        return


    ##
    # return the appropriate "headers" for onedrive requests that include 1) user agent, 2) authorization cookie
    #   returns: list containing the header
    ##
    def getHeadersList(self):
        auth = self.authorization.getToken('auth_token')
        session = self.authorization.getToken('auth_session')
        if (auth != '' or session != ''):
            return [('User-Agent', self.user_agent), ('Cookie', session+'; oc_username='+self.authorization.username+'; oc_token='+auth+'; oc_remember_login=1')]
        else:
            return [('User-Agent', self.user_agent )]



    ##
    # return the appropriate "headers" for onedrive requests that include 1) user agent, 2) authorization cookie
    #   returns: URL-encoded header string
    ##
    def getHeadersEncoded(self):
        auth = self.authorization.getToken('auth_token')
        session = self.authorization.getToken('auth_session')

        if (auth != '' or session != ''):
            return urllib.urlencode({ 'User-Agent' : self.user_agent, 'Cookie' : session+'; oc_username='+self.authorization.username+'; oc_token='+auth+'; oc_remember_login=1' })
        else:
            return urllib.urlencode({ 'User-Agent' : self.user_agent })

    ##
    # retrieve a list of videos, using playback type stream
    #   parameters: prompt for video quality (optional), cache type (optional)
    #   returns: list of videos
    ##
    def getMediaList(self, folderName='', cacheType=CACHE_TYPE_MEMORY):

        tokenValue = self.authorization.getToken('token')

        userID = ''
        for r in re.finditer('u\=(\d+)f\=(\d+)' ,folderName, re.DOTALL):
            userID,userFolderID = r.groups()


        if (tokenValue == ''):
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050),+'tokenValue')
            self.crashreport.sendError('getMediaList:tokenValue',response_data)
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+'tokenValue', xbmc.LOGERROR)
            return


        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]


        if folderName=='' or userID != '':
            url = 'https://api-beta.hive.im/api/hive/get/'
        elif folderName=='FRIENDS':
            url = 'https://api-beta.hive.im/api/user/get-friends-list/'
        else:
            url = 'https://api-beta.hive.im/api/hive/get-children/'

        request = urllib2.Request(url)

        # if action fails, validate login

        try:

            if folderName=='':
                response = opener.open(request)
            elif userID != '':
                response = opener.open(request, 'userId='+userID)
            else:
                response = opener.open(request, 'parentId='+folderName+'&offset=0&order=dateModified&sort=desc')


        except urllib2.URLError, e:
                xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                self.crashreport.sendError('getMediaList',str(e))
                return

        response_data = response.read()
        response.close()

        mediaFiles = []

        if folderName == '':
            media = package.package(0,folder.folder('FRIENDS','<<Friends>>'))
            mediaFiles.append(media)



        if folderName == 'FRIENDS':
            for r in re.finditer('\"userId\"\:\"([^\"]+)\"\,\"authName\"\:([^\,]+)\,\"authLastName\"\:([^\,]+)\,\"authFirstName\"\:([^\,]+)\,' ,response_data, re.DOTALL):
                userID,userName,userFirst,userLast = r.groups()
                userName = re.sub('"', '', userName)
                userFirst = re.sub('"', '', userFirst)
                userLast = re.sub('"', '', userLast)

                if userName != 'null':
                    media = package.package(0,folder.folder('u='+userID+'f=0',userName))
                else:
                    media = package.package(0,folder.folder('u='+userID+'f=0',userFirst + ' - '+userLast))

                mediaFiles.append(media)

            return mediaFiles

        # parsing page for files
#        for r in re.finditer('\{\"id\"\:.*?\"dateModified\"\:\"[^\"]+\"\}' ,response_data, re.DOTALL):
        for r in re.finditer('\{\"id\"\:.*?\d\"\}' ,response_data, re.DOTALL):
                entry = r.group()

                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"title\"\:\"([^\"]+)\"\,\"folder\"\:true' ,entry, re.DOTALL):
                    folderID,folderName = q.groups()
                    media = package.package(0,folder.folder(folderID,folderName))
                    mediaFiles.append(media)

                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"type\"\:\"video\"\,\"title\"\:\"([^\"]+)\"\,\"folder\"\:false.*?\"download\"\:\"([^\"]+)\"' ,entry, re.DOTALL):
                    fileID,fileName,downloadURL = q.groups()
                    downloadURL = re.sub('\\\\', '', downloadURL)

                    media = package.package(file.file(fileID, fileName, fileName, self.VIDEO, '', ''),folder.folder('',''))
                    media.setMediaURL(mediaurl.mediaurl(downloadURL, '','',''))
                    mediaFiles.append(media)

                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"type\"\:\"album\"\,\"title\"\:\"([^\"]+)\"\,\"folder\"\:false.*?\"download\"\:\"([^\"]+)\"' ,entry, re.DOTALL):
                    fileID,fileName,downloadURL = q.groups()
                    downloadURL = re.sub('\\\\', '', downloadURL)

                    media = package.package(file.file(fileID, fileName, fileName, self.AUDIO, '', ''),folder.folder('',''))
                    media.setMediaURL(mediaurl.mediaurl(downloadURL, '','',''))
                    mediaFiles.append(media)

        return mediaFiles



    ##
    # retrieve a list of videos, using playback type stream
    #   parameters: prompt for video quality (optional), cache type (optional)
    #   returns: list of videos
    ##
    def getSearchResults(self):

        tokenValue = self.authorization.getToken('token')


        if (tokenValue == ''):
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050),+'tokenValue')
            self.crashreport.sendError('getMediaList:tokenValue',response_data)
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+'tokenValue', xbmc.LOGERROR)
            return


        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]

        url = 'https://api-beta.hive.im/api/user/get/'

        request = urllib2.Request(url)

        # if action fails, validate login

        try:
                response = opener.open(request)

        except urllib2.URLError, e:
                xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                self.crashreport.sendError('getSearchResults',str(e))
                return

        response_data = response.read()
        response.close()

        userID = ''
        searchAPIKey = ''
        for r in re.finditer('\"userId\"\:\"(\d+)\".*?\"searchApiKey\"\:\"([^\"]+)\"' ,response_data, re.DOTALL):
                userID,searchAPIKey = r.groups()

        searchText = ''
        try:
            dialog = xbmcgui.Dialog()
            searchText = dialog.input('Enter search string', type=xbmcgui.INPUT_ALPHANUM)
        except:
            searchText = 'life'

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', self.user_agent),('X-Algolia-Application-Id', 'W59TAFXI29'),('X-Algolia-API-Key', searchAPIKey), ('Content-type', 'application/json')]

        url = 'https://w59tafxi29-1.algolia.io/1/indexes/HiveBeta/query'

        request = urllib2.Request(url)

        # if action fails, validate login

        try:
                response = opener.open(request, '{"params":"query='+searchText+'","apiKey":"'+searchAPIKey+'","appID":"W59TAFXI29","X-Algolia-TagFilters":"('+userID+')"}')

        except urllib2.URLError, e:
                xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                self.crashreport.sendError('getSearchResults',str(e))
                return

        response_data = response.read()
        response.close()

        for r in re.finditer('\"userId\"\:\"(\d+)\".*?\"searchApiKey\"\:\"([^\"]+)\"' ,response_data, re.DOTALL):
                userID,searchAPIKey = r.groups()



        mediaFiles = []

        # parsing page for files
#        for r in re.finditer('\{\"id\"\:.*?\"dateModified\"\:\"[^\"]+\"\}' ,response_data, re.DOTALL):
        for r in re.finditer('\"id\"\:.*?\d\"\]' ,response_data, re.DOTALL):
                entry = r.group()

                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"title\"\:\"([^\"]+)\"\,\"folder\"\:true' ,entry, re.DOTALL):
                    folderID,folderName = q.groups()
                    media = package.package(0,folder.folder(folderID,folderName))
                    mediaFiles.append(media)

                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"type\"\:\"video\"\,\"title\"\:\"([^\"]+)\"\,\"folder\"\:false.*?' ,entry, re.DOTALL):
                    fileID,fileName = q.groups()

                    media = package.package(file.file(fileID, fileName, fileName, self.VIDEO, '', ''),folder.folder('',''))
                    mediaFiles.append(media)

                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"type\"\:\"album\"\,\"title\"\:\"([^\"]+)\"\,\"folder\"\:false.*?' ,entry, re.DOTALL):
                    fileID,fileName = q.groups()

                    media = package.package(file.file(fileID, fileName, fileName, self.AUDIO, '', ''),folder.folder('',''))
                    mediaFiles.append(media)

        return mediaFiles


    ##
    # retrieve a playback url
    #   returns: url
    ##
    def getPlaybackCall(self, playbackType, package):

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar), MyHTTPErrorProcessor)
        opener.addheaders = [('User-Agent', self.user_agent)]

        zValue = self.authorization.getToken('z')

        if (zValue == ''):
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050),'z')
            self.crashreport.sendError('getPlaybackCall:z','not set')
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+'z', xbmc.LOGERROR)
            return

        url = 'https://app.box.com/files'

        opener.addheaders = [('User-Agent', self.user_agent),('Cookie', 'z='+zValue+';')]
        request = urllib2.Request(url)

        # if action fails, validate login

        try:
            response = opener.open(request)

        except urllib2.URLError, e:
                xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                return

        response_data = response.read()
        response.close()


        requestTokenValue=''
        for r in re.finditer('(request_token) \= \'([^\']+)\'' ,response_data, re.DOTALL):
            requestTokenName,requestTokenValue = r.groups()

        subIDValue=''
        for r in re.finditer('(realtime_subscriber_id) \=\'([^\']+)\'' ,response_data, re.DOTALL):
            subIDName,subIDValue = r.groups()

        if (requestTokenValue == ''):
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050), 'requestTokenValue')
            self.crashreport.sendError('getPlaybackCall:requestTokenValue',response_data)
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+ 'requestTokenValue', xbmc.LOGERROR)
            return

        if (subIDValue == ''):
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050), 'subIDValue')
            self.crashreport.sendError('getPlaybackCall:subIDValue',response_data)
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+ 'subIDValue', xbmc.LOGERROR)
            return

        url = 'https://app.box.com/index.php?rm=box_download_file_via_post'


        request = urllib2.Request(url)

                # if action fails, validate login

        try:
            response = opener.open(request,'file_id='+package.file.id+'&request_token='+requestTokenValue)

        except urllib2.URLError, e:
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
            return

        downloadURL=''
        try:
            downloadURL = response.info().getheader('Location')
        except:
            pass
        response.close()

        if (downloadURL == ''):
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050), 'downloadURL')
            self.crashreport.sendError('getPlaybackCall:downloadURL','not set')
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+ 'downloadURL', xbmc.LOGERROR)
            return

        return downloadURL


    ##
    # retrieve a media url
    #   returns: url
    ##
    def getMediaCall(self, package):
        return #not implemented

    ##
    # retrieve a directory url
    #   returns: url
    ##
    def getDirectoryCall(self, folder):
        return self.PLUGIN_URL+'?mode=folder&instance='+self.instanceName+'&directory='+folder.id



class MyHTTPErrorProcessor(urllib2.HTTPErrorProcessor):

    def http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()

        # only add this line to stop 302 redirection.
        if code == 302: return response
        if code == 303: return response

        if not (200 <= code < 300):
            response = self.parent.error(
                'http', request, response, code, msg, hdrs)
        return response

    https_response = http_response

