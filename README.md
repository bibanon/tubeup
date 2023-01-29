Tubeup - a multi-VOD service to Archive.org uploader
==========================================

![Unit Tests](https://github.com/bibanon/tubeup/workflows/Unit%20Tests/badge.svg)
![Lint](https://github.com/bibanon/tubeup/workflows/Lint/badge.svg)

`tubeup` uses yt-dlp to download a Youtube video (or [any other provider supported by yt-dlp](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)), and then uploads it with all metadata to the Internet Archive using the python module internetarchive.

It was designed by the [Bibliotheca Anonoma](https://github.com/bibanon/bibanon/wiki) to archive single videos, playlists (see warning below about more than video uploads) or accounts to the Internet Archive.

## Prerequisites

This script strongly recommends Linux or some sort of POSIX system (such as macOS), preferably from a rented VPS and not your personal machine or phone.

Reccomended system specifications:
- Linux VPS with Python 3.8 or higher and `pip` installed
- 2GB of RAM, 100GB of storage or much more for anything other than single short video mirroring. If your OS drive is too small, `symlink` it to something larger.

## Setup and Installation

1. Install `ffmpeg`, pip3 (typically `python3-pip`), and git.  
   To install ffmpeg in Ubuntu, enable the Universe repository.

For Debian/Ubuntu:

```
   sudo apt install ffmpeg python3-pip git
```

2. Use pip3 to install the required python3 packages.
   At a minimum Python 3.7.13 and up is required (latest Python preferred).

```
   python3 -m pip install -U pip tubeup
```

3. If you don't already have an Internet Archive account, [register for one](https://archive.org/account/login.createaccount.php) to give the script upload privileges.

4. Configure `internetarchive` with your Internet Archive account.

```
   ia configure
```

You will be prompted for your login credentials for the Internet Archive account you use.

Once configured to upload, you're ready to go.

5. Start archiving a video by running the script on a URL (or multiple URLs) [supported by yt-dlp.](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md). For YouTube, this includes account URLs and playlist URLs.

```
   tubeup <url>
```

6. Each archived video gets its own Archive.org item. Check out what you've uploaded at

   `http://archive.org/details/@yourusername`.


Perodically *before* running, upgrade `tubeup` and its dependencies by running:

```
   python3 -m pip install -U tubeup pip
```


## Docker

Dockerized tubeup is provided by [etnguyen03/docker-tubeup](https://github.com/etnguyen03/docker-tubeup). Instructions are provided.
   
## Windows Setup

1. Install WSL2, pick a distribution of your choice. Ubuntu is popular and well-supported.
2. Use Windows Terminal by Microsoft to interact with the WSL2 instance.
3. Fully update the Linux installation with your package manager of choice.
   ```sudo apt update ; sudo apt upgrade```
4. Install python `pip` and `ffmpeg`.
5. Install Tubeup using steps 4-6 in the Linux configuration guide above and configuring `internetarchive` for your Archive.org account.
6. Periodically update your Linux packages and pip packages.

## Usage

```
Usage:
  tubeup <url>... [--username <user>] [--password <pass>]
                  [--metadata=<key:value>...]
                  [--cookies=<filename>]
                  [--proxy <prox>]
                  [--quiet] [--debug]
                  [--use-download-archive]
                  [--output <output>]
                  [--ignore-existing-item]
  tubeup -h | --help
  tubeup --version
```
```
Arguments:
  <url>                         yt-dlp compatible URL to download.
                                Check yt-dlp documentation for a list
                                of compatible websites.
  --metadata=<key:value>        Custom metadata to add to the archive.org
                                item.
Options:
  -h --help                    Show this screen.
  -p --proxy <prox>            Use a proxy while uploading.
  -u --username <user>         Provide a username, for sites like Nico Nico Douga.
  -p --password <pass>         Provide a password, for sites like Nico Nico Douga.
  -a --use-download-archive    Record the video url to the download archive.
                               This will download only videos not listed in
                               the archive file. Record the IDs of all
                               downloaded videos in it.
  -q --quiet                   Just print errors.
  -d --debug                   Print all logs to stdout.
  -o --output <output>         yt-dlp output template.
  -i --ignore-existing-item    Don't check if an item already exists on archive.org
```

## Metadata

You can specify custom metadata with the `--metadata` flag.
For example, this script will upload your video to the [Community Video collection](https://archive.org/details/opensource_movies) by default.
You can specify a different collection with the `--metadata` flag:

```
   tubeup --metadata=collection:opensource_audio <url>
```

Any arbitrary metadata can be added to the item, with a few exceptions.
You can learn more about archive.org metadata [here](https://archive.org/services/docs/api/metadata-schema/).

### Collections

Archive.org users can upload to four open collections:

* [Community Audio](https://archive.org/details/opensource_audio) where the identifier is `opensource_audio`.
* [Community Software](https://archive.org/details/open_source_software)  where the identifier is `opensource_software`.
* [Community Texts](https://archive.org/details/opensource) where the identifier is `opensource`.
* [Community Video](https://archive.org/details/opensource_movies) where the identifier is `opensource_movies`.

Note that care should be taken when uploading entire channels.
Read the appropriate section [in this guide](https://archive.org/about/faqs.php#Collections) for creating collections, and contact the [collections staff](mailto:collections-service@archive.org) if you're uploading a channel or multiple channels on one subject (gaming or horticulture for example). Internet Archive collections staff will either create a collection for you or merge any uploaded items based on the YouTube uploader name that are already up into a new collection.

**Dumping entire channels into Community Video is abusive and may get your account locked.** _Talk to the Internet Archive admins first before doing large uploads; it's better to ask for guidence or help first than run afoul of the rules._

**If you do not own a collection you will need to be added as an admin for that collection if you want to upload to it.** Talk to the collection owner or staff if you need assistance with this.

## Troubleshooting

* Some videos are copyright blocked in certain countries. Use the proxy or torrenting/privacy VPN option to use a proxy to bypass this. Sweden and Germany are good countries to bypass geo-restrictions.
* Upload taking forever? Getting s3 throttling on upload? Tubeup has specifically been tailored to wait the longest possible time before failing, and we've never seen a S3 outage that outlasted the insane wait times set in Tubeup.

## Major Credits (in no particular order)

- [emijrp](https://github.com/emijrp/) who wrote the original [youtube2internetarchive.py](https://code.google.com/p/emijrp/source/browse/trunk/scrapers/youtube2internetarchive.py) in 2012
- [Matt Hazinski](https://github.com/matthazinski) who forked emijrp's work in 2015 with numerous improvements of his own.
- Antonizoon for switching the script to library calls rather than functioning as an external script, and many small improvements.
- Small PRs from various people, both in and out of BibAnon.
- vxbinaca for stabilizing downloads/uploads in `yt-dlp`/`internetarchive` library calls, cleansing item output, subtitles collection, and numerous small improvements over time.
- mrpapersonic for adding logic to check if an item already exists in the Internet Archive and if so skips ingestion.
- [Jake Johnson](https://github.com/jjjake) of the Internet Archive for adding variable collections ability as a flag, switching Tubeup from a script to PyPi repository, ISO-compliant item dates, fixing what others couldn't, and many improvements.
- [Refeed](https://github.com/refeed) for re-basing the code to OOP, turning Tubeup itself into a library. and adding download and upload bar graphs, and squashing bugs.

## License (GPLv3)

Copyright (C) 2020 Bibliotheca Anonoma

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
