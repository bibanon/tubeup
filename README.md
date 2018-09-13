Tubeup - a multi-site video to Archive.org uploader
==========================================

[![Build Status](https://travis-ci.org/bibanon/tubeup.svg?branch=master)](https://travis-ci.org/bibanon/tubeup)

`tubeup` uses youtube-dl to download a Youtube video (or [any other provider supported by youtube-dl](https://github.com/rg3/youtube-dl/blob/master/docs/supportedsites.md)), and then uploads it with all metadata to the Internet Archive.

It was designed by the [Bibliotheca Anonoma](https://github.com/bibanon/bibanon/wiki) to archive entire Youtube accounts and playlists to the Internet Archive.

## Prerequisites

This script strongly recommends Linux or some sort of POSIX system (such as Mac OS X).

If you are using Windows, we recommend that you run this script in `c9.io`, which gives you a full Linux development environment with 5GBs of space, on the cloud. It may be possible to run this script on Windows + Python3 with great difficulty, but we don't recommend it.

* **Python 3** - This script requires python3, which has better integration with Unicode strings.
* **docopt** - The usage documentation can specify command line arguments and options.
* **youtube-dl** - Used to download the videos.
* **internetarchive** - A Python library used to upload videos with their metadata to the Internet Archive.
* **jsonpatch** - For JSON things.

## Installation

1. Install `avconv` or `ffmpeg`, depending on what your distro prefers. Also install pip3 and git. 
   The script prefers ffmpeg if found but will work with just libav. To install ffmpeg in ubuntu have
   the Universe repository enabled.

For Debian/Ubuntu:

```
   sudo apt-get install libav-tools ffmpeg python3-pip git
```

2. Use pip3 to install the required python3 packages. 
   At the minimum Python 3.4.2 and up is required, as 3.2 will not work.

```
   sudo -H pip3 install -U pip tubeup
```

Perodically upgrade tubeup and it's dependencies by running:

```
   sudo -H pip3 install -U tubeup 
```

3. If you don't already have an Internet Archive account, [register for one](https://archive.org/account/login.createaccount.php) to give the script upload privileges.

4. Configure internetarchive with your Internet Archive account.

```
   ia configure
```

You will be prompted for your login credentials for the Internet Archive account you use.


5. Start archiving a video by running the script on a URL. Or multiple URLs at once. Youtube, Dailymotion, [anything supported by youtube-dl.](https://github.com/rg3/youtube-dl/blob/master/docs/supportedsites.md) For YouTube, this includes account URLs and playlist URLs.

```
   tubeup <url>
```

6. Each archived video gets it's own Archive.org item. Check out what you've uploaded at

   `http://archive.org/details/@yourusername`.

## Usage

```
tubeup - Download a video with Youtube-dl, then upload to Internet Archive, passing all metadata.

Usage:
  tubeup <url>... [--metadata=<key:value>...]
  tubeup <url> [--username <user>] [--password <pass>]
  tubeup <url> [--proxy <prox>]
  tubeup <url> --use-download-archive
  tubeup <url> -q | --quiet
  tubeup <url> -d | --debug
  tubeup -h | --help

Arguments:
  <url>                         Youtube-dl compatible URL to download.
                                Check Youtube-dl documentation for a list
                                of compatible websites.
  -m, --metadata=<key:value>    Custom metadata to add to the archive.org
                                item.

Options:
  -h --help                 Show this screen.
  --proxy <prox>            Use a proxy while uploading.
  --username <user>         Provide a username, for sites like Nico Nico Douga.
  --password <pass>         Provide a password, for sites like Nico Nico Douga.
  --use-download-archive    Record the video url to the download archive.
                            This will download only videos not listed in
                            the archive file. Record the IDs of all
                            downloaded videos in it.
  -q --quiet                Just print errors.
  -d --debug                Print all logs to stdout.
```

## Metadata

You can specify custom metadata with the `--metadata` flag.
For example, this script will upload your video to the [Community Video collection](https://archive.org/details/opensource_movies) by default.
You can specify a different collection with the `--metadata` flag:

```
   tubeup --metadata=collection:opensource_audio <url>
```

Any arbitrary metadta can be added to the item, with a few exceptions.
You can learn more about archive.org metadata [here](http://internetarchive.readthedocs.io/en/latest/metadata.html).

### Collections

Archive.org users can upload to to four open collections:

* [Community Audio](https://archive.org/details/opensource_audio) where the identifier is `opensource_audio`.
* [Community Software](https://archive.org/details/open_source_software)  where the identifier is `opensource_software`.
* [Community Texts](https://archive.org/details/opensource) where the identifier is `opensource`.
* [Community Video](https://archive.org/details/opensource_movies) where the identifier is `opensource_movies`.

Note that care should be taken when uploading entire channels.
Read the appropraite section [in this guide](https://archive.org/about/faqs.php#Collections) for creating collections, and contact the [collections staff](mailto:collections-service@archive.org) if you're uploading a channel or multiple channels on one subject (gaming or horticulture for example), they'll create a collection for you or merge any uploaded items based on the Youtube uploader name that are already up into a new collection.

**Dumping entire channels into Community Video is abusive and may get your account locked.** _Talk to the admins first before doing large uploads it's better to ask for guidence or help first than run afowl with the rules._

**If you do not own a collection you will need to be added as an admin for that collection if you want to upload to it** Talk to the collection owner or staff if you need assistance with this.

## Troubleshooting

* Obviously, if someone else uploaded the video to the Internet Archive, you will get a permissions error. We don't want duplicates, do we?
* Some videos are copyright blocked in certain countries. Use the proxy or torrenting/privacy VPN option to use a proxy to bypass this. Sweden and Germany are good countries to bypass geo-restrrictions.
* Upload taking forever? Getting s3 throttling on upload? Tubeup has specifically been tailored to wait the longest possible time before failing, and we've never seen a S3 outage that outlasted the insane wait times set in Tubeup.

## Major Credits

- [emijrp](https://github.com/emijrp/) who wrote the original [youtube2internetarchive.py](https://code.google.com/p/emijrp/source/browse/trunk/scrapers/youtube2internetarchive.py) in 2012
- [Matt Hazinski](https://github.com/matthazinski) who forked emijrps work in 2015 with numerous improvements of his own.
- Antonizoon for switching the script to library calls rather than functioning as an external script, and many small improvements.
- Small PRs from various people, both in and out of BibAnon.
- vxbinaca for stabilizing downloads/uploads in `youtube-dl`/`internetarchive` library calls, cleansing item output, subtitles collection, and numerous small improvements over time.
- [Jake Johnson](https://github.com/jjjake) of the Internet Archive for adding variable collections ability as a flag, switching Tubeup from a script to PyPi repository, ISO-compliant item dates, fixing what others couldn't, and many improvements.
- [Refeed](https://github.com/refeed) for re-basing the code to OOP, turning Tubeup it's self into a library. and adding download and upload bar graphs, and squashing bugs.

## License (GPLv3)

Copyright (C) 2016 Bibliotheca Anonoma

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
