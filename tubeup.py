#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# tubeup.py - Download a video using youtube-dl and upload to the Internet Archive with metadata

# Copyright (C) 2016 Bibliotheca Anonoma
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
import re
import os
import sys
import glob
import json
import time
import docopt
import youtube_dl
import internetarchive
import logging

__doc__ = """tubeup.py - Download a video with Youtube-dl, then upload to Internet Archive, passing all metadata.

Usage:
  tubeup.py <url>...
  tubeup.py [--proxy <prox>]
  tubeup.py -h | --help

Arguments:
  <url>           Youtube-dl compatible URL to download.
                  Check Youtube-dl documentation for a list
                  of compatible websites. 

Options:
  -h --help       Show this screen.
  --proxy <prox>  Use a proxy while uploading.
"""

def mkdirs(path):
	"""Make directory, if it doesn't exist."""
	if not os.path.exists(path):
		os.makedirs(path)

# log youtube-dl errors to stdout
class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

# equivalent of youtube-dl --title --continue --retries 4 --write-info-json --write-description --write-thumbnail --write-annotations --all-subs --ignore-errors URL 
# uses downloads/ folder and safe title in output template
def download(URLs, proxy_url):
    
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s-%(id)s.%(ext)s',
        'download_archive': 'downloads/.ytdlarchive', 
        'restrictfilenames': True,
        'verbose': True,
        'progress_with_newline': True,
        'forcetitle': True,
        'continuedl': True,
        'retries': 100,
        'forcejson': True,
        'writeinfojson': True,
        'writedescription': True,
        'writethumbnail': True,
        'writeannotations': True,
        'writesubtitles': True,
        'allsubtitles': True,
        'logger': MyLogger(),
        'progress_hooks': [my_hook]
    }
    
    if proxy_url is not None: # use proxy url as argument
        ydl_opts['proxy'] = proxy_url
    
    # format: We don't set a default format. Youtube-dl will choose the best option for us automatically.
    # Since the end of April 2015 and version 2015.04.26 youtube-dl uses -f bestvideo+bestaudio/best as default format selection (see #5447, #5456). 
    # If ffmpeg or avconv are installed this results in downloading bestvideo and bestaudio separately and muxing them together into a single file giving the best overall quality available. 
    # Otherwise it falls back to best and results in downloading best available quality served as a single file.
    # best is also needed for videos that don't come from YouTube because they don't provide the audio and video in two different files. 
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(URLs)

# upload a video to the Internet Archive
def upload_ia(videobasename):
    # obtain metadata from JSON
    json_fname = videobasename + '.info.json'
    with open(json_fname) as f:    
        vid_meta = json.load(f)
    
    itemname = '%s-%s' % (vid_meta['extractor'], vid_meta['display_id'])
    language = 'en' # I doubt we usually archive spanish videos, but maybe this should be a cmd argument?
    collection = 'opensource_movies'
    title = '%s: %s - %s' % (vid_meta['extractor_key'], vid_meta['display_id'], vid_meta['title']) # Youtube: LE2v3sUzTH4 - THIS IS A BUTTERFLY!
    videourl = vid_meta['webpage_url']
    cc = False # let's not misapply creative commons
    
    # some video services don't tell you the uploader, use our program's name in that case
    if 'uploader' in vid_meta:
        uploader = vid_meta['uploader']
    else:
        uploader = 'tubeup.py'
    
    if 'uploader_url' in vid_meta:
        uploader_url = vid_meta['uploader_url']
    else:
        uploader_url = videourl

    if 'upload_date' in vid_meta: # some videos don't give an upload date
        if vid_meta['upload_date'] != "":
            upload_date = vid_meta['upload_date']
            upload_year = upload_date[:4] # 20150614 -> 2015
    else: # use current date and time as default values
        upload_date = time.strftime("%Y%m%d")
        upload_year = time.strftime("%Y")
    
    # load up tags into an IA compatible semicolon-separated string
    tags_string = '%s;video;' % vid_meta['extractor_key'] # Youtube;video;
    
    if 'categories' in vid_meta: # add categories as tags as well, if they exist
        categories = vid_meta['categories']
        for category in categories:
            tags_string += '%s;' % category
    
    if 'tags' in vid_meta: # some video services don't have tags
        tags = vid_meta['tags']
        for tag in tags:
            tags_string += '%s;' % tag
    
    # if there is no description don't upload the empty .description file
    description = ""
    no_description = True
    if 'description' in vid_meta:
        if vid_meta['description'] != "":
            description = vid_meta['description']
            no_description = False
    
    # delete empty description file so it isn't uploaded
    try:
        if no_description or os.stat(videobasename + '.description').st_size == 0:
            os.remove(videobasename + '.description')
    except OSError:
        print(":: Description not saved, so not removed.")
    
    # if there is no annotations file (or annotations are not in XML) don't upload the empty .annotation.xml file
    no_annotations = True
    if 'annotations' in vid_meta:
        if vid_meta['annotations'] != "" and vid_meta['annotations'] != """<?xml version="1.0" encoding="UTF-8" ?><document><annotations></annotations></document>""":
            no_annotations = False

    # delete empty annotations.xml file so it isn't uploaded
    try:
        if no_annotations or os.stat(videobasename + '.annotations.xml').st_size == 0:
            os.remove(videobasename + '.annotations.xml')
    except OSError:
        print(":: annotations.xml not saved, so not removed.")
    
    # upload all files with videobase name: e.g. video.mp4, video.info.json, video.srt, etc.
    vid_files = glob.glob(videobasename + '*')

    # upload the item to the Internet Archive
    item = internetarchive.get_item(itemname)
    meta = dict(mediatype='movies', creator=uploader, language=language, collection=collection, title=title, description=u'{0} <br/><br/>Source: <a href="{1}">{2}</a><br/>Uploader: <a href="{3}">{4}</a><br/>Upload date: {5}'.format(description, videourl, videourl, uploader_url, uploader, upload_date), date=upload_date, year=upload_year, subject=tags_string, originalurl=videourl, licenseurl=(cc and 'http://creativecommons.org/licenses/by/3.0/' or ''))
    
    item.upload(vid_files, metadata=meta)
    
    # return item identifier and metadata as output
    return itemname, meta

# array of basenames to upload (not ideal, maybe we should transform all this into an OOP library)
to_upload = []

# monitor download status
def my_hook(d):
    filename, file_extension = os.path.splitext(d['filename'])
    if d['status'] == 'finished': # only upload if download was a success
        print(d)    # display download stats
        print(':: Downloaded: %s...' % d['filename'])
        
        global to_upload
        videobasename = re.sub(r'(\.f\d+)', '', filename) # remove .fxxx from filename (e.g. .f141.mp4)
        if videobasename not in to_upload: # don't add if it's already in the list
            to_upload.append(videobasename)

    if d['status'] == 'error':
        print(':: Error occurred while downloading: %s.' % d['filename'])

def main():
    # display log output from internetarchive libraries: http://stackoverflow.com/a/14058475
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
    
    # parse arguments from file docstring
    args = docopt.docopt(__doc__)
    
    # test url: https://www.youtube.com/watch?v=LE2v3sUzTH4
    URLs = args['<url>']
    proxy_url = args['--proxy']

    # download all URLs with youtube-dl
    download(URLs, proxy_url)
    
    # while downloading, if the download hook returns status "finished", myhook() will append the basename to the `to_upload` array.
    
    # upload all URLs with metadata to the Internet Archive
    global to_upload
    for video in to_upload:
        print(":: Uploading %s..." % video)
        identifier, meta = upload_ia(video)
        
        print("\n:: Upload Finished. Item information:")
        print("Title: %s" % meta['title'])
        print("Upload URL: http://archive.org/details/%s" % identifier)

if __name__ == '__main__':
    main()
