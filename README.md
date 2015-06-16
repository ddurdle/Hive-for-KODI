A Hive (QVIVO) Video/Music add-on for XBMC / KODI

A video add-on that enables playback of video and music files stored in a Hive account.

This is a very early release. I need people to help test and help me improvement the plugin.

What is implemented?
- Playback of video
- Folders support
- Multiple account support (up to 10)
- Access friends' Hives [since 0.1.2]
- Search [since 0.1.3] -- requires Gotham or better
- Streaming support [since 0.1.3]
- Speed up by saving cookies/sessions between runs [since 0.1.4]
- support for Feeds, latest videos in your and your friend's hive (same feeds on website) [since 0.1.7]
- support up to 300 friends [since 0.1.7]
- Creation of STRM files for video and audio [since 0.1.6]
- fanart file support (include a fanart.jpg in your folder, and it will be loaded when viewing content in that folder)
- thumbnail support
- support for Music info [since 0.1.8]
- photo support [since 0.1.9]
- bookmarks [since 0.2.1]
- saved search [since 0.2.1]
- thumbnails added for friend's (thx to JoKeRzBoX)
- filter out unprocessed videos (useful for non-premium / free users) -- default for non-premium [since 0.2.2]
- default to 240p playback (useful for non-premium / free users) -- default for non-premium  [since 0.2.2]
- option to "Request Encoding" (right-click on video) for non-encoded videos [since 0.2.2]

What is being worked on?
- support for Music info (priority #1)
- support for TV info (priority #2)
- support for Movie info (priority #3)
- support for NFO file creation


Supports [Tested on daily]:
- XBMC 13-alpha, 13 13.2
- KODI 14

including Linux, Windows, OS X, Android, Pivos, iOS (including ATV2), Raspberry Pi

Note for Raspberry Pi users: Due to a bug in libcurl with HTTPS streams, playback of content on these devices may not work. I have tested on various Raspberry Pi distributions and have personally witnessed about a 90% failure rate for playback of videos over HTTPS. HTTP is unaffected. "Disk Cache", when implemented, will bypass this problem. It is not implemented at this time.

Getting Started:

Installing the repository (automatic updates):
1) download the repository.ddurdle (download from http://dmdsoftware.net/repository.ddurdle.zip or https://github.com/ddurdle/repository.dd...durdle.zip)
2) transfer the .zip file to XBMC
3) in Video Add-ons, select Install from .zip; repository should be installed
4) in Video Add-ons, select Get Add-ons, select ddurdle's XBMC Addons, select Video Add-ons, select Hive

Installing the plugin only (no automatic updates):
1) download the .zip file
2) transfer the .zip file to XBMC
3) in Video Add-on, select Install from .zip

BUILDS

Available in GitHub -> https://github.com/ddurdle/KODI-Hive

Report Issues to this thread or create an issue in GitHub -> https://github.com/ddurdle/KODI-Hive/issues

Before starting the add-on for the first time, either "Configure" or right click and select "Add-on Settings". Enter your fully-qualified Username and Password.

Contributions and Thanks
- several code contribution from JoKeRzBoX
- donation support from iorifly

FAQ:

1) Is there support for multiple accounts?
Yes, up to 10 accounts.

2) Does this add-on support Pictures or other filetypes?
Music and video files are supported; pictures/images will be added shortly.