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

import sys

sys.path.append(os.path.join( addon_dir, 'resources', 'lib' ) )

import authorization
#import cloudservice
import folder
import file
import package
import mediaurl
import crashreport
import gSpreadsheets

#global variables
PLUGIN_NAME = 'hive'
PLUGIN_URL = sys.argv[0]


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

        # hive specific ***
        self.isPremium = True
        try:
            if int(self.addon.getSetting(self.instanceName+'_type')) == 1:
                self.isPremium = True
            else:
                self.isPremium = False
        except:
            self.isPremium = True

        # hive specific ***
        self.loginType = 0
        try:
            self.loginType = int(self.addon.getSetting(self.instanceName+'_provider'))
        except:
            self.loginType = 0


        try:
            if self.isPremium:
                self.skipUnwatchable = self.addon.getSetting('hide_unwatchable')
            else:
                self.skipUnwatchable = self.addon.getSetting('free_hide_unwatchable')
        except:
            self.skipUnwatchable = False

        if self.skipUnwatchable == 'true':
            self.skipUnwatchable = True
        else:
            self.skipUnwatchable = False
        #***

        self.cookiejar = cookielib.CookieJar()

        self.user_agent = user_agent

        # hive specific ***
        #token?
        if (not self.authorization.loadToken(self.instanceName,addon, 'token')):
            if (self.loginType == 1):
                self.login_Google()
            else:
                self.login()

        self.isLibrary = False
        try:
            if self.addon.getSetting('gdrive_library') == 'true':
                self.isLibrary = True
            else:
                self.isLibrary = False
        except:
                self.isLibrary = False

        if self.isLibrary:
            self.library = gSpreadsheets.gSpreadsheets(self.addon,self.crashreport,self.user_agent)

            spreadsheets = self.library.getSpreadsheetList()

            worksheets = self.library.getSpreadsheetWorksheets(spreadsheets['Hive'])

            self.worksheet = ''
            try:
                self.worksheet = worksheets['content']
            except:
                self.worksheet = self.library.createWorksheet(spreadsheets['Hive'],'content',10,5)

            #self.buildSpreadsheet('','')
            #self.library.createRow(self.worksheet)
        #***

    ##
    # perform login
    ##
    def login(self):

        self.authorization.isUpdated = True

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar), MyHTTPErrorProcessor)
        opener.addheaders = [('User-Agent', self.user_agent)]

        url = 'https://api.hive.im/api/user/sign-in/'

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
    # perform login
    ##
    def login_Google(self):

        self.authorization.isUpdated = True

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar),MyHTTPErrorProcessor )
        opener.addheaders = [('User-Agent', self.user_agent)]

        url = 'https://accounts.google.com/o/oauth2/auth?scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fplus.login%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email&state=google&response_type=code&client_id=45190457022.apps.googleusercontent.com&access_type=offline&requestvisibleactions=https%3A%2F%2Fschemas.google.com%2FAddActivity&redirect_uri=http://login.hive.im/'

        request = urllib2.Request(url)
        self.cookiejar.add_cookie_header(request)

        # try login
        try:
            response = opener.open(request)

        except urllib2.URLError, e:
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
            return
        response_data = response.read()
        response.close()


        for cookie in self.cookiejar:
            for r in re.finditer(' ([^\=]+)\=([^\s]+)\s',
                        str(cookie), re.DOTALL):
                cookieType,cookieValue = r.groups()

        url = ''
        for r in re.finditer('The (document) has moved \<A HREF\=\"([^\"]+)\"' ,response_data, re.DOTALL):
                document,url = r.groups()
                url = re.sub('\&amp\;', '&',url)


        request = urllib2.Request(url)
        self.cookiejar.add_cookie_header(request)

        # try login
        try:
            response = opener.open(request)

        except urllib2.URLError, e:
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
            return
        response_data = response.read()
        response.close()

        GALX = ''
        for r in re.finditer('\<input name\=\"(GALX)\" type\=\"hidden\"\n?\s+value\=\"([^\"]+)\"\>' ,response_data, re.DOTALL):
                document,GALX = r.groups()

        continueURL = ''
        for r in re.finditer('\<input name\=\"(continue)\" type\=\"hidden\"\n?\s+value\=\"([^\"]+)\"\>' ,response_data, re.DOTALL):
                document,continueURL = r.groups()

        shdf = ''
        for r in re.finditer('\<input name\=\"(shdf)\" type\=\"hidden\"\n?\s+value\=\"([^\"]+)\"\>' ,response_data, re.DOTALL):
                document,shdf = r.groups()


        request = urllib2.Request(url)
        self.cookiejar.add_cookie_header(request)

        # try login
        try:
            response = opener.open(request,'GALX='+GALX+'&continue='+continueURL+'&service=lso&ltmpl=popup&shdf='+shdf+'&scc=1&sarp=1&checkedDomains=youtube&checkConnection=youtube%3A1877%3A1&pstMsg=1&_utf8=%E2%98%83&bgresponse=%21vr1CtoaYkYtX9QZEtJkO4_-eZbsCAAAAIlIAAAAGKgD8KIryUXbwbxMU9wdYZQgs0NFaQBH8Xh6M1pCC-ox8EpkBpUsMeH5SnSsKvf5z3div4gY9qxbt_ieE8xPTjyUz8_HcugCmSbTSD4-wku2IkbF7T_BtlxC1Gog3KcQT4kMkCytzi9V_NiL6KUhKOPAruSbcEIb56h6M3VQBFP9wqHcFomv-wHPcL8ywZ3UWSiw0LNJeCzkHwAGDtfRxFfYhG4nSMYsCVWTjemdszsEjjy_Pdv8QtAd3I2Z0d8Rh1G_0jix1FXcMegOd5iAMLjWg3ldwlvI4MDrKnUqSTH1E64Qo_K4plyZBhPUdtBbRBEF7tRwbJ9V40ZwRMvUb&pstMsg=1&dnConn=&checkConnection=youtube%3A62%3A1&checkedDomains=youtube&Email='+self.authorization.username+'&Passwd='+self.addon.getSetting(self.instanceName+'_password')+'&signIn=Sign+in&PersistentCookie=yes')

        except urllib2.URLError, e:
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
            return
        response_data = response.read()
        response.close()

        for r in re.finditer('(content)\=\"4\;url\=([^\"]+)\"\>' ,response_data, re.DOTALL):
                document,url = r.groups()
                url = re.sub('\&amp\;', '&',url)

        request = urllib2.Request(url)
        self.cookiejar.add_cookie_header(request)

        # try login
        try:
            response = opener.open(request)

        except urllib2.URLError, e:
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
            return
        response_data = response.read()
        response.close()

        for r in re.finditer('(The document has moved) \<A HREF\=\"([^\"]+)\"\>' ,response_data, re.DOTALL):
                document,url = r.groups()
                url = re.sub('\&amp\;', '&',url)

        request = urllib2.Request(url)
        self.cookiejar.add_cookie_header(request)

        # try login
        try:
            response = opener.open(request)

        except urllib2.URLError, e:
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
            return
        response_data = response.read()
        response.close()

        for r in re.finditer('(The document has moved) \<A HREF\=\"([^\"]+)\"\>' ,response_data, re.DOTALL):
                document,url = r.groups()
                url = re.sub('\&amp\;', '&',url)

        opener.addheaders = [('Cookie', 'redirect_uri=https%3A%2F%2Ftouch.hive.im')]

        request = urllib2.Request(url)
        self.cookiejar.add_cookie_header(request)


        # try login
        try:
            response = opener.open(request)

        except urllib2.URLError, e:
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
            return
        response_data = response.info().getheader('Location')
        response.close()

        googleToken = ''
        for r in re.finditer('(google_token)\/(.*)' ,response_data, re.DOTALL):
                document,googleToken = r.groups()

        url = 'https://api.hive.im/api/user/sign-in/'
        request = urllib2.Request(url)
        self.cookiejar.add_cookie_header(request)


        # try login
        try:
            response = opener.open(request,'provider=googleplus&accessToken='+googleToken)

        except urllib2.URLError, e:
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
            return
        response_data = response.read()
        response.close()

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

        #token not set?  try logging in; if still fail, report error
        if (tokenValue == ''):
            if (self.loginType == 1):
                self.login_Google()
            else:
                self.login()
            tokenValue = self.authorization.getToken('token')

            if (tokenValue == ''):
                xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050),+'tokenValue')
                self.crashreport.sendError('getMediaList:tokenValue',response_data)
                xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+'tokenValue', xbmc.LOGERROR)
                return


        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]

        media = {}
        if self.isLibrary and folderName != '':
            media = self.library.getMediaInformation(self.worksheet, folderName)


        if folderName=='' or userID != '':
            url = 'https://api.hive.im/api/hive/get/'
        elif folderName=='FRIENDS':
            url = 'https://api.hive.im/api/user/get-friends-list/'
        elif folderName=='FEED':
            url = 'https://api.hive.im/api/activity/get/'
        else:
            url = 'https://api.hive.im/api/hive/get-children/'

        request = urllib2.Request(url)


        offset=0
        loop = True
        mediaFiles = []
        limit = 300
        parentID = folderName
        while loop:
          loop = False
          itemCount=0
          # if action fails, validate login
          try:

            if parentID=='':
                response = opener.open(request)
                loop = False
            elif userID != '':
                response = opener.open(request, 'userId='+userID)
                loop = False
            elif parentID=='FEED':
                response = opener.open(request, 'offset=0&limit=100')
                loop = False
            elif parentID=='FRIENDS':
                response = opener.open(request, 'offset=0&limit=300')
                loop = False
            else:
                response = opener.open(request, 'parentId='+parentID+'&offset='+str(offset)+'&limit='+str(limit)+'&order=dateModified&sort=desc')

          #maybe authorization key expired?
          except urllib2.URLError, e:
                if (self.loginType == 1):
                    self.login_Google()
                else:
                    self.login()

                opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]
                request = urllib2.Request(url)
                try:
                    if parentID=='':
                        response = opener.open(request)
                        loop = False
                    elif userID != '':
                        response = opener.open(request, 'userId='+userID)
                        loop = False
                    elif parentID=='FEED':
                        response = opener.open(request, 'offset=0&limit=100')
                        loop = False
                    elif parentID=='FRIENDS':
                        response = opener.open(request, 'offset=0&limit=300')
                        loop = False
                    else:
                        response = opener.open(request, 'parentId='+parentID+'&offset='+str(offset)+'&limit='+str(limit)+'&order=dateModified&sort=desc')
                except urllib2.URLError, e:
                    xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                    self.crashreport.sendError('getMediaList',str(e))
                    return

          response_data = response.read()
          response.close()

          if parentID == 'FRIENDS':
            for r in re.finditer('\"thumbnail\"\:\"([^\"]+)\".*?\"userId\"\:\"([^\"]+)\"\,\"authName\"\:([^\,]+)\,\"authLastName\"\:([^\,]+)\,\"authFirstName\"\:([^\,]+)\,' ,response_data, re.DOTALL):
                thumb,userID,userName,userFirst,userLast = r.groups()
                thumbURL = re.sub('"', '', re.sub('\\\/', '/', thumb))
                userName = re.sub('"', '', userName)
                userFirst = re.sub('"', '', userFirst)
                userLast = re.sub('"', '', userLast)

                if userName != 'null':
                    media = package.package(None,folder.folder('u='+userID+'f=0',userName, thumbURL))
                else:
                    media = package.package(None,folder.folder('u='+userID+'f=0',userFirst + ' - '+userLast, thumbURL))

                mediaFiles.append(media)

            return mediaFiles
          elif parentID == 'FEED':
            for r in re.finditer('\{\"id\"\:.*?\d\"\}' ,response_data, re.DOTALL):
                entry = r.group()

                for q in re.finditer('\"hiveId\"\:\"([^\"]+)\".*?\"thumb\"\:\"([^\"]+)\".*\"title\"\:\"([^\"]+)\".*\"type\"\:\"video\".*?\,\"dateCreated\"\:\"(\d\d\d\d)\-(\d\d)\-(\d\d)' ,entry, re.DOTALL):
                    fileID,thumbnail,fileName,year,month,day = q.groups()
                    thumbnail = re.sub('\\\\', '', thumbnail)
                    fileName = urllib.quote(fileName)
                    media = package.package(file.file(fileID, fileName, fileName, self.VIDEO, '', thumbnail, date=str(day)+'.'+str(month)+'.'+str(year)),folder.folder('',''))
                    mediaFiles.append(media)

                for q in re.finditer('\"hiveId\"\:\"([^\"]+)\".*?\"thumb\"\:\"([^\"]+)\".*\"title\"\:\"([^\"]+)\".*\"type\"\:\"album\".*?\,\"dateCreated\"\:\"(\d\d\d\d)\-(\d\d)\-(\d\d)' ,entry, re.DOTALL):
                    fileID,thumbnail,fileName,year,month,day = q.groups()
                    thumbnail = re.sub('\\\\', '', thumbnail)
                    fileName = urllib.quote(fileName)
                    media = package.package(file.file(fileID, fileName, fileName, self.AUDIO, '', thumbnail, date=str(day)+'.'+str(month)+'.'+str(year)),folder.folder('',''))
                    mediaFiles.append(media)
            return mediaFiles

          # parsing page for files
#        for r in re.finditer('\{\"id\"\:.*?\"dateModified\"\:\"[^\"]+\"\}' ,response_data, re.DOTALL):
          fanart = ''
          for r in re.finditer('\{\"id\"\:.*?\d\"\}' ,response_data, re.DOTALL):
                entry = r.group()

                #fanart
                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"type\"\:\"photo\"\,\"title\"\:\"fanart\"\,\"folder\"\:false.*?\"thumb\"\:\"([^\"]+)\".*?\"download\"\:\"([^\"]+)\"' ,entry, re.DOTALL):
                    fileID,thumbnail,fanart = q.groups()
                    fanart = re.sub('\\\\', '', fanart)


          for r in re.finditer('\{\"id\"\:.*?\d\"\}' ,response_data, re.DOTALL):
                entry = r.group()

                processed = 0
                for q in re.finditer('\"id\"\:\"[^\"]+\".*?\"title\"\:\"SAVED-FOLDER\|([^\|]+)\|([^\"]+)\"\,\"folder\"\:true' ,entry, re.DOTALL):
                    folderID,folderName = q.groups()
                    folderName = urllib.quote(folderName)
                    folderName = '*'+str(folderName)
                    media = package.package(None,folder.folder(folderID,folderName))
                    mediaFiles.append(media)
                    processed = 1
                    itemCount = itemCount + 1

                for q in re.finditer('\"id\"\:\"[^\"]+\".*?\"title\"\:\"(SAVED-SEARCH)\|([^\"]+)\"\,\"folder\"\:true' ,entry, re.DOTALL):
                    search,searchCriteria = q.groups()
                    searchCriteria = urllib.quote(searchCriteria)
                    media = package.package(None,folder.folder('SAVED-SEARCH',searchCriteria))
                    mediaFiles.append(media)
                    processed = 1
                    itemCount = itemCount + 1

                if processed == 0:
                    for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"title\"\:\"([^\"]+)\"\,\"folder\"\:true' ,entry, re.DOTALL):
                        folderID,folderName = q.groups()
                        folderName = urllib.quote(folderName)
                        media = package.package(None,folder.folder(folderID,folderName))
                        mediaFiles.append(media)
                        itemCount = itemCount + 1

                # to separate media that has thumbnails from the ones that do not (e.g. unknown audio file)
                has_thumb = re.search(',\"thumb\"\:\"',entry)
                if has_thumb:

                    for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"type\"\:\"video\"\,\"title\"\:\"([^\"]+)\"\,\"folder\"\:false.*?\"thumb\"\:\"([^\"]+)\".*?\"download\"\:\"([^\"]+)\"\,\"dateCreated\"\:\"(\d\d\d\d)\-(\d\d)\-(\d\d).*?\"encoded\"\:([^\,]+)\,.*?\"size\"\:\"(\d+)\"' ,entry, re.DOTALL):
                        fileID,fileName,thumbnail,downloadURL,year,month,day,isEncoded,filesize = q.groups()

                        if isEncoded.lower() == 'false' and self.skipUnwatchable == True:
                            break

                        fileName = urllib.quote(fileName)
                        downloadURL = re.sub('\\\\', '', downloadURL)
                        thumbnail = re.sub('\\\\', '', thumbnail)

                        mediaFile = file.file(fileID, fileName, fileName, self.VIDEO, fanart, thumbnail, date=str(day)+'.'+str(month)+'.'+str(year), size=filesize)
                        if isEncoded.lower() == 'true':
                            mediaFile.isEncoded = True

                        media = package.package(mediaFile,folder.folder('',''))
                        media.setMediaURL(mediaurl.mediaurl(downloadURL, '','',''))
                        mediaFiles.append(media)
                        itemCount = itemCount + 1

                    for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"type\"\:\"photo\"\,\"title\"\:\"([^\"]+)\"\,\"folder\"\:false.*?\"thumb\"\:\"([^\"]+)\".*?\"download\"\:\"([^\"]+)\"\,.*?\"dateCreated\"\:\"(\d\d\d\d)\-(\d\d)\-(\d\d).*?\"size\"\:\"(\d+)\"' ,entry, re.DOTALL):
                        fileID,fileName,thumbnail,downloadURL,year,month,day,filesize = q.groups()
                        fileName = urllib.quote(fileName)
                        downloadURL = re.sub('\\\\', '', downloadURL)
                        thumbnail = re.sub('\\\\', '', thumbnail)

                        media = package.package(file.file(fileID, fileName, fileName, self.PICTURE, fanart, thumbnail, date=str(day)+'.'+str(month)+'.'+str(year), size=filesize),folder.folder('',''))
                        media.setMediaURL(mediaurl.mediaurl(downloadURL, '','',''))
                        mediaFiles.append(media)
                        itemCount = itemCount + 1


                    for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"type\"\:\"album\"\,\"title\"\:\"([^\"]+)\"\,\"folder\"\:false.*?\"hd\"\:\"([^\"]+)\"\,\"thumb\"\:\"([^\"]+)\".*?\"download\"\:\"([^\"]+)\"\,.*?\"dateCreated\"\:\"(\d\d\d\d)\-(\d\d)\-(\d\d).*?\"size\"\:\"(\d+)\"' ,entry, re.DOTALL):
                        fileID,fileName,hdImage,thumbnail,downloadURL,year,month,day,filesize = q.groups()

                        fileName = urllib.quote(fileName)
                        downloadURL = re.sub('\\\\', '', downloadURL)
                        thumbnail = re.sub('\\\\', '', thumbnail)
                        hdImage = re.sub('\\\\', '', hdImage)

                        musicFile = file.file(fileID, fileName, fileName, self.AUDIO, hdImage, thumbnail, date=str(day)+'.'+str(month)+'.'+str(year), size=filesize)

                        for s in re.finditer('\"meta\"\:\{\"artist\"\:"([^\"]+)\"\,\"title\"\:\"[^\"]+\"\,\"album\"\:\"([^\"]+)\"\,\"releaseDate\"\:\"([^\"]+)\"\,\"trackNo\"\:(\d+)\,\"totalTracks\"\:\d+\,\"genre\"\:\"([^\"]+)\"\}' ,entry, re.DOTALL):
                            artist,album,releaseDate,trackNumber,genre = s.groups()
                            musicFile.setAlbumMeta(album,artist,releaseDate,trackNumber,genre)

                        media = package.package(musicFile,folder.folder('',''))
                        media.setMediaURL(mediaurl.mediaurl(downloadURL, '','',''))
                        mediaFiles.append(media)
                        itemCount = itemCount + 1
                else:

                    for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"type\"\:\"album\"\,\"title\"\:\"([^\"]+)\"\,\"folder\"\:false.*?\"download\"\:\"([^\"]+)\"\,.*?\"dateCreated\"\:\"(\d\d\d\d)\-(\d\d)\-(\d\d).*?\"size\"\:\"(\d+)\"' ,entry, re.DOTALL):
                        fileID,fileName,downloadURL,year,month,day,filesize = q.groups()
                        fileName = urllib.quote(fileName)
                        downloadURL = re.sub('\\\\', '', downloadURL)

                        musicFile = file.file(fileID, fileName, fileName, self.AUDIO, '', '',date=str(day)+'.'+str(month)+'.'+str(year), size=filesize)

                        for s in re.finditer('\"meta\"\:\{\"artist\"\:"([^\"]+)\"\,\"title\"\:\"[^\"]+\"\,\"album\"\:\"([^\"]+)\"\,\"releaseDate\"\:\"([^\"]+)\"\,\"trackNo\"\:(\d+)\,\"totalTracks\"\:\d+\,\"genre\"\:\"([^\"]+)\"\}' ,entry, re.DOTALL):
                            artist,album,releaseDate,trackNumber,genre = s.groups()
                            musicFile.setAlbumMeta(album,artist,releaseDate,trackNumber,genre)

                        media = package.package(musicFile,folder.folder('',''))
                        media.setMediaURL(mediaurl.mediaurl(downloadURL, '','',''))
                        mediaFiles.append(media)
                        itemCount = itemCount + 1
          offset = offset + limit
          if itemCount == limit:
            loop = True
        return mediaFiles


    ##
    # retrieve a list of videos, using playback type stream
    #   parameters: prompt for video quality (optional), cache type (optional)
    #   returns: list of videos
    ##
    def getCollections(self):

        tokenValue = self.authorization.getToken('token')


        #token not set?  try logging in; if still fail, report error
        if (tokenValue == ''):
            if (self.loginType == 1):
                self.login_Google()
            else:
                self.login()

            tokenValue = self.authorization.getToken('token')

            if (tokenValue == ''):
                  xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050),+'tokenValue')
                  self.crashreport.sendError('getMediaList:tokenValue',response_data)
                  xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+'tokenValue', xbmc.LOGERROR)
                  return


        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]

        url = 'https://api.hive.im/api/collection/list/'

        request = urllib2.Request(url)

        # if action fails, validate login

        try:
                response = opener.open(request,  'offset=0&limit=20&sort=desc&order=dateModified')

        except urllib2.URLError, e:
                if (self.loginType == 1):
                    self.login_Google()
                else:
                    self.login()

                opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]
                request = urllib2.Request(url)
                try:
                    response = opener.open(request, 'offset=0&limit=20&sort=desc&order=dateModified')
                except urllib2.URLError, e:
                    xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                    self.crashreport.sendError('getCollections',str(e))
                    return

        response_data = response.read()
        response.close()


        mediaFiles = []

        # parsing page for files
#        for r in re.finditer('\{\"id\"\:.*?\"dateModified\"\:\"[^\"]+\"\}' ,response_data, re.DOTALL):
        for r in re.finditer('\{\"collectionId\"\:.*?\d\}' ,response_data, re.DOTALL):
            entry = r.group()

            for q in re.finditer('\"collectionId\"\:\"([^\"]+)\".*?\"title\"\:\"([^\"]+)\"\,' ,entry, re.DOTALL):
                    collectionID,collectionName = q.groups()
                    collectionName = urllib.quote(collectionName)
                    media = package.package(None,folder.folder(collectionID,'['+collectionName+']'))
                    mediaFiles.append(media)

        return mediaFiles


    ##
    # retrieve a list of videos, using playback type stream
    #   parameters: prompt for video quality (optional), cache type (optional)
    #   returns: list of videos
    ##
    def getSearchResults(self, searchText):

        tokenValue = self.authorization.getToken('token')


        #token not set?  try logging in; if still fail, report error
        if (tokenValue == ''):
            if (self.loginType == 1):
                self.login_Google()
            else:
                self.login()

            tokenValue = self.authorization.getToken('token')

            if (tokenValue == ''):
                  xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050),+'tokenValue')
                  self.crashreport.sendError('getMediaList:tokenValue',response_data)
                  xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+'tokenValue', xbmc.LOGERROR)
                  return


        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]

        url = 'https://api.hive.im/api/search/hive/ '

        request = urllib2.Request(url)

        # if action fails, validate login

        try:
                response = opener.open(request,  'limit=50&term='+searchText)

        except urllib2.URLError, e:
                if (self.loginType == 1):
                    self.login_Google()
                else:
                    self.login()

                opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]
                request = urllib2.Request(url)
                try:
                    response = opener.open(request)
                except urllib2.URLError, e:
                    xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                    self.crashreport.sendError('getSearchResults',str(e))
                    return

        response_data = response.read()
        response.close()


        mediaFiles = []

        # parsing page for files
#        for r in re.finditer('\{\"id\"\:.*?\"dateModified\"\:\"[^\"]+\"\}' ,response_data, re.DOTALL):
        for r in re.finditer('\{\"id\"\:.*?\d\}' ,response_data, re.DOTALL):
            entry = r.group()

            # to separate media that has thumbnails from the ones that do not (e.g. unknown audio file)
            has_thumb = re.search(',\"thumb\"\:\"',entry)
            if has_thumb:

                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"title\"\:\"([^\"]+)\"\,\"folder\"\:true' ,entry, re.DOTALL):
                    folderID,folderName = q.groups()
                    folderName = urllib.quote(folderName)
                    media = package.package(None,folder.folder(folderID,folderName))
                    mediaFiles.append(media)

                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"type\"\:\"video\"\,\"title\"\:\"([^\"]+)\"\,\"folder\"\:false.*?\"size\"\:\"(\d+)\".*?\"thumb\"\:\"([^\"]+)\".*?\,\"dateCreated\"\:\"(\d\d\d\d)\-(\d\d)\-(\d\d)' ,entry, re.DOTALL):
                    fileID,fileName,filesize,thumbnail,year,month,day = q.groups()

                    thumbnail = re.sub('\\\\', '', thumbnail)
                    fileName = urllib.quote(fileName)
                    media = package.package(file.file(fileID, fileName, fileName, self.VIDEO, '', thumbnail, date=str(day)+'.'+str(month)+'.'+str(year), size=filesize),folder.folder('',''))
                    mediaFiles.append(media)

                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"type\"\:\"album\"\,\"title\"\:\"([^\"]+)\"\,\"folder\"\:false.*?\"size\"\:\"(\d+)\".*?\"thumb\"\:\"([^\"]+)\".*?\,\"dateCreated\"\:\"(\d\d\d\d)\-(\d\d)\-(\d\d)' ,entry, re.DOTALL):
                    fileID,fileName,filesize,thumbnail,year,month,day = q.groups()

                    thumbnail = re.sub('\\\\', '', thumbnail)
                    fileName = urllib.quote(fileName)
                    media = package.package(file.file(fileID, fileName, fileName, self.AUDIO, '', thumbnail, date=str(day)+'.'+str(month)+'.'+str(year), size=filesize),folder.folder('',''))
                    mediaFiles.append(media)
            else:
                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"title\"\:\"([^\"]+)\"\,\"folder\"\:true' ,entry, re.DOTALL):
                    folderID,folderName = q.groups()
                    folderName = urllib.quote(folderName)
                    media = package.package(None,folder.folder(folderID,folderName))
                    mediaFiles.append(media)

                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"type\"\:\"video\"\,\"title\"\:\"([^\"]+)\"\,\"folder\"\:false.*?\"size\"\:\"(\d+)\".*?\,\"dateCreated\"\:\"(\d\d\d\d)\-(\d\d)\-(\d\d)' ,entry, re.DOTALL):
                    fileID,fileName,filesize,year,month,day = q.groups()
                    fileName = urllib.quote(fileName)
                    media = package.package(file.file(fileID, fileName, fileName, self.VIDEO, '', '', date=str(day)+'.'+str(month)+'.'+str(year), size=filesize),folder.folder('',''))
                    mediaFiles.append(media)

                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"type\"\:\"album\"\,\"title\"\:\"([^\"]+)\"\,\"folder\"\:false.*?\"size\"\:\"(\d+)\".*?\,\"dateCreated\"\:\"(\d\d\d\d)\-(\d\d)\-(\d\d)' ,entry, re.DOTALL):
                    fileID,fileName,filesize,year,month,day = q.groups()
                    fileName = urllib.quote(fileName)
                    media = package.package(file.file(fileID, fileName, fileName, self.AUDIO, '', '', date=str(day)+'.'+str(month)+'.'+str(year), size=filesize),folder.folder('',''))
                    mediaFiles.append(media)


        return mediaFiles


    ##
    # retrieve a playback url
    #   returns: url
    ##
    def getPlaybackCall(self, playbackType, package):

        tokenValue = self.authorization.getToken('token')


        #token not set?  try logging in; if still fail, report error
        if (tokenValue == ''):
            if (self.loginType == 1):
                self.login_Google()
            else:
                self.login()
            tokenValue = self.authorization.getToken('token')

            if (tokenValue == ''):
                  xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050),+'tokenValue')
                  self.crashreport.sendError('getMediaList:tokenValue',response_data)
                  xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+'tokenValue', xbmc.LOGERROR)
                  return


        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]


        url = 'https://api.hive.im/api/hive/get-streams/'


        request = urllib2.Request(url)

        # if action fails, validate login

        try:
            response = opener.open(request, 'hiveId='+package.file.id)

        except urllib2.URLError, e:
                if (self.loginType == 1):
                    self.login_Google()
                else:
                    self.login()

                opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]
                request = urllib2.Request(url)
                try:
                    response = opener.open(request, 'hiveId='+package.file.id)
                except urllib2.URLError, e:
                    xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                    self.crashreport.sendError('getPlaybackCall',str(e))
                    return

        response_data = response.read()
        response.close()

#{"status":"success","data":[{"profile":"240p","progress":"100","status":"Encoded","position":null,"url":"https:\/\/dfiv2g75s7q7p.cloudfront.net\/api\/stream\/?token=TTgrSEh6SVJzL2ozT3RBbVdvbStCaUhGa1hVd3FqbG5GaFpwckxFc2VKYz0=&accessKey=4qu2p9aNpvKJ5QPu&file=Vy9ZQ2F5RWhOZk93dG84VUxvU3RxUzViRk1WL1NiY3RPQkxkaFpRSEgvdGMySXdKenpyTHFvc1dPWHRNakgxZE9nUmpGbVh6WENTT3prb2R1bXh6dGc9PQ==","lastPlayPosition":null},{"profile":"360p","progress":"100","status":"Encoded","position":null,"url":"https:\/\/dfiv2g75s7q7p.cloudfront.net\/api\/stream\/?token=TTgrSEh6SVJzL2ozT3RBbVdvbStCaUhGa1hVd3FqbG5GaFpwckxFc2VKYz0=&accessKey=4qu2p9aNpvKJ5QPu&file=ZjBmQ3lSQThMd2ZEdHBWcFIyTmRMYlhlNzhPbUZ0U3hDcENQRy8xcmgzeGNxVTl1amYzbDR5eDh1VUU5T0ZmQzBBNXpXZmpweDA3UUk5dzFvZ0dRWEE9PQ==","lastPlayPosition":null}],"date":1416459748,"_elapsed":14}

        mediaURLs = []

        for r in re.finditer('\{\"profile\"\:[^\}]+\}' ,response_data, re.DOTALL):
            entry = r.group()

            for r in re.finditer('\"profile\"\:\"([^\"]+)\"\,\"progress\"\:\"(\d+)\".*?\"url\"\:"([^\"]+)\"' ,entry, re.DOTALL):
                quality,progress,url = r.groups()
                if progress == "100":
                    url = re.sub('\\\\', '', url)
                    mediaURLs.append(mediaurl.mediaurl(url, quality, 0, 3))


        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]


        url = 'https://api.hive.im/api/hive/get-child/'


        request = urllib2.Request(url)

        # if action fails, validate login

        try:
            response = opener.open(request, 'hiveId='+package.file.id)

        except urllib2.URLError, e:
                if (self.loginType == 1):
                    self.login_Google()
                else:
                    self.login()

                opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]
                request = urllib2.Request(url)
                try:
                    response = opener.open(request, 'hiveId='+package.file.id)
                except urllib2.URLError, e:
                    xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                    self.crashreport.sendError('getPlaybackCall',str(e))
                    return

        response_data = response.read()
        response.close()

        for r in re.finditer('\{\"id\"\:.*?\d\"\}' ,response_data, re.DOTALL):
                entry = r.group()

                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"type\"\:\"video\"\,\"title\"\:\"([^\"]+)\"\,\"folder\"\:false.*?\"download\"\:\"([^\"]+)\"' ,entry, re.DOTALL):
                    fileID,fileName,downloadURL = q.groups()
                    downloadURL = re.sub('\\\\', '', downloadURL)
                    mediaURLs.append(mediaurl.mediaurl(downloadURL, 'original', 0, 3))

                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"type\"\:\"photo\"\,\"title\"\:\"([^\"]+)\"\,\"folder\"\:false.*?\"download\"\:\"([^\"]+)\"' ,entry, re.DOTALL):
                    fileID,fileName,downloadURL = q.groups()
                    downloadURL = re.sub('\\\\', '', downloadURL)
                    mediaURLs.append(mediaurl.mediaurl(downloadURL, 'original', 0, 3))

                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"type\"\:\"album\"\,\"title\"\:\"([^\"]+)\"\,\"folder\"\:false.*?\"download\"\:\"([^\"]+)\"' ,entry, re.DOTALL):
                    fileID,fileName,downloadURL = q.groups()
                    downloadURL = re.sub('\\\\', '', downloadURL)
                    mediaURLs.append(mediaurl.mediaurl(downloadURL, 'original', 0, 3))

        return mediaURLs

    ##
    # retrieve a media url
    #   returns: url
    ##
    def getMediaCall(self, package):
        return #not implemented


    def buildSpreadsheet(self, folderID='', folderName=''):


        mediaItems = self.getMediaList(folderID,0)

        if mediaItems:
            for item in mediaItems:

                url = 0
                try:
                    if item.file == 0:
#                        self.library.createRow(self.worksheet, item.folder.id,item.folder.title,'','')
                        self.buildSpreadsheet(item.folder.id,item.folder.title)
                    else:
                        self.library.createRow(self.worksheet, folderID,folderName,item.file.id,item.file.title)
                except:
                    self.library.createRow(self.worksheet, folderID,folderName,item.file.id,item.file.title)

    def downloadPicture(self, url, file):

        tokenValue = self.authorization.getToken('token')


        #token not set?  try logging in; if still fail, report error
        if (tokenValue == ''):
            if (self.loginType == 1):
                self.login_Google()
            else:
                self.login()

            tokenValue = self.authorization.getToken('token')

            if (tokenValue == ''):
                  xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050),+'tokenValue')
                  self.crashreport.sendError('getMediaList:tokenValue',response_data)
                  xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+'tokenValue', xbmc.LOGERROR)
                  return

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]

        req = urllib2.Request(url)

        # if action fails, validate login
        try:
            open(file,'wb').write(urllib2.urlopen(req).read())

        except urllib2.URLError, e:
            if (self.loginType == 1):
                self.login_Google()
            else:
                self.login()

            tokenValue = self.authorization.getToken('token')

            if (tokenValue == ''):
                  xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050),+'tokenValue')
                  self.crashreport.sendError('getMediaList:tokenValue',response_data)
                  xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+'tokenValue', xbmc.LOGERROR)
                  return

            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
            opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]

            req = urllib2.Request(url)
            try:
                open(file,'wb').write(urllib2.urlopen(req).read())
            except urllib2.URLError, e:
                log(str(e), True)
                return



    def createBookmark(self, folderID, folderName):

        tokenValue = self.authorization.getToken('token')


        #token not set?  try logging in; if still fail, report error
        if (tokenValue == ''):
            if (self.loginType == 1):
                self.login_Google()
            else:
                self.login()
            tokenValue = self.authorization.getToken('token')

            if (tokenValue == ''):
                  xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050),+'tokenValue')
                  self.crashreport.sendError('getMediaList:tokenValue',response_data)
                  xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+'tokenValue', xbmc.LOGERROR)
                  return

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]

        url = 'https://api.hive.im/api/hive/get/'

        request = urllib2.Request(url)

        # if action fails, validate login

        try:
            response = opener.open(request)

        except urllib2.URLError, e:
                if (self.loginType == 1):
                    self.login_Google()
                else:
                    self.login()
                opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]
                request = urllib2.Request(url)
                try:
                    response = opener.open(request, 'hiveId='+package.file.id)
                except urllib2.URLError, e:
                    xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                    self.crashreport.sendError('createBookmark',str(e))
                    return

        response_data = response.read()
        response.close()

        saveFolderID = 0
        for r in re.finditer('\{\"id\"\:.*?\d\"\}' ,response_data, re.DOTALL):
                entry = r.group()

                processed = 0
                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"title\"\:\"(Documents)\"\,\"folder\"\:true' ,entry, re.DOTALL):
                    saveFolderID,saveFolderName = q.groups()

        if saveFolderID != 0:
            url = 'https://api.hive.im/api/hive/create/'

            request = urllib2.Request(url)

            # if action fails, validate login

            try:
                response = opener.open(request, 'filename=SAVED-FOLDER|'+str(folderID)+'|'+str(folderName)+'&parent='+str(saveFolderID)+'&locked=false&friends=')

            except urllib2.URLError, e:
                if (self.loginType == 1):
                    self.login_Google()
                else:
                    self.login()
                opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]
                request = urllib2.Request(url)
                try:
                    response = opener.open(request, 'hiveId='+package.file.id)
                except urllib2.URLError, e:
                    xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                    self.crashreport.sendError('createBookmark',str(e))
                    return

            response.close()


    def createSearch(self, searchCriteria):

        tokenValue = self.authorization.getToken('token')


        #token not set?  try logging in; if still fail, report error
        if (tokenValue == ''):
            if (self.loginType == 1):
                self.login_Google()
            else:
                self.login()
            tokenValue = self.authorization.getToken('token')

            if (tokenValue == ''):
                  xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050),+'tokenValue')
                  self.crashreport.sendError('getMediaList:tokenValue',response_data)
                  xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+'tokenValue', xbmc.LOGERROR)
                  return

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]

        url = 'https://api.hive.im/api/hive/get/'

        request = urllib2.Request(url)

        # if action fails, validate login

        try:
            response = opener.open(request)

        except urllib2.URLError, e:
            if (self.loginType == 1):
                self.login_Google()
            else:
                self.login()

            opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]
            request = urllib2.Request(url)
            try:
                response = opener.open(request, 'hiveId='+package.file.id)
            except urllib2.URLError, e:
                xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                self.crashreport.sendError('createBookmark',str(e))
                return

        response_data = response.read()
        response.close()

        saveFolderID = 0
        for r in re.finditer('\{\"id\"\:.*?\d\"\}' ,response_data, re.DOTALL):
                entry = r.group()

                processed = 0
                for q in re.finditer('\"id\"\:\"([^\"]+)\".*?\"title\"\:\"(Documents)\"\,\"folder\"\:true' ,entry, re.DOTALL):
                    saveFolderID,saveFolderName = q.groups()

        if saveFolderID != 0:
            url = 'https://api.hive.im/api/hive/create/'

            request = urllib2.Request(url)

            # if action fails, validate login

            try:
                response = opener.open(request, 'filename=SAVED-SEARCH|'+str(searchCriteria)+'&parent='+str(saveFolderID)+'&locked=false&friends=')

            except urllib2.URLError, e:
                if (self.loginType == 1):
                    self.login_Google()
                else:
                    self.login()
                opener.addheaders = [('User-Agent', self.user_agent),('Client-Version','0.1'),('Authorization', tokenValue), ('Client-Type', 'Browser'), ('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')]
                request = urllib2.Request(url)
                try:
                    response = opener.open(request, 'hiveId='+package.file.id)
                except urllib2.URLError, e:
                    xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                    self.crashreport.sendError('createBookmark',str(e))
                    return

            response.close()


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
