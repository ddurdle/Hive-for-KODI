'''
    Copyright (C) 2014 ddurdle

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
import urllib

#
#
#
class file:
    # CloudService v0.2.1

    AUDIO = 1
    VIDEO = 2
    PICTURE = 3


    ##
    ##
    def __init__(self, id, title, plot, type, fanart,thumbnail, date='', size=0):
        self.id = id
        self.title = title
        self.plot = plot
        self.type = type
        self.fanart = fanart
        self.thumbnail = thumbnail
        self.hasMeta = False
        self.isEncoded = False
        self.date = date
        self.size = size

    def setAlbumMeta(self,album,artist,releaseDate,trackNumber,genre):
        self.album = album
        self.artist = artist
        self.trackNumber = trackNumber
        self.genre = genre
        self.releaseDate = releaseDate
        self.hasMeta = True

    def displayTitle(self):
        return urllib.unquote(self.title)

    def __repr__(self):
        return '{}: {} {}'.format(self.__class__.__name__,
                                  self.title)

    def __cmp__(self, other):
        if hasattr(other, 'title'):
            return self.title.__cmp__(other.title)

    def getKey(self):
        return self.title
