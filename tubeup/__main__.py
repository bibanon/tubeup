#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# tubeup.py - Download a video using youtube-dl and upload to the Internet Archive with metadata

# Copyright (C) 2018 Bibliotheca Anonoma
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
"""tubeup - Download a video with Youtube-dlc, then upload to Internet Archive, passing all metadata.

Usage:
  tubeup <url>... [--username <user>] [--password <pass>]
                  [--metadata=<key:value>...]
                  [--cookies=<filename>]
                  [--proxy <prox>]
                  [--quiet] [--debug]
                  [--use-download-archive]
                  [--use-upload-archive]
                  [--output <output>]
                  [--ignore-existing-item]
                  [--abort-on-error]
                  [--yt X...]
  tubeup -h | --help
  tubeup --version

Arguments:
  <url>                         Youtube-dlc compatible URL to download.
                                Check Youtube-dlc documentation for a list
                                of compatible websites.
  --metadata=<key:value>        Custom metadata to add to the archive.org
                                item.

Options:
  -h --help                    Show this screen.
  -p --proxy <prox>            Deprecated. Shortcut for the corresponding yt-dlp option.
  -u --username <user>         Deprecated. Shortcut for the corresponding yt-dlp option.
  -p --password <pass>         Deprecated. Shortcut for the corresponding yt-dlp option.
  -a --use-download-archive    Shortcut for --yt=--download-archive=%s
  -U --use-upload-archive      Record the video url to the upload archive at %s
                               This will upload only videos not listed in
                               the archive file. Record the IDs of all
                               uploaded videos in it.
  -q --quiet                   Just print errors.
  -d --debug                   Print all logs to stdout.
     --abort-on-error          Abort after the first failed upload.
  -o --output <output>         Youtube-dlc output template.
  -i --ignore-existing-item    Don't check if an item already exists on archive.org
  --yt X...                    Any option to be passed to underlying yt-dlp.

Example:
  Assuming that *.info.json files are consistent and
  that yt-dlp output template led to uniform/predictible file names,
  then a way to upload existing files based without triggering new downloads
  is to use a combination of the following:
  * --output='<same as yt-dlp output>'
  * --use-upload-archive
  * --use-download-archive
  * --ignore-existing-item
  * --yt=--no-playlist
  * --yt=--match-filter=!playlist
  * --yt=--no-overwrites

"""

import os
import sys
import docopt
import logging
import traceback

from yt_dlp import parse_options

import internetarchive
import internetarchive.cli

from tubeup.TubeUp import TubeUp
from tubeup import __version__

DEFAULT_DOWNLOAD_ARCHIVE = os.path.join(os.path.expanduser('~/.tubeup'), '.ytdlarchive')
DEFAULT_UPLOAD_ARCHIVE = os.path.join(os.path.expanduser('~/.tubeup'), '.iauparchive')

def main():
    # Parse arguments from file docstring
    args = docopt.docopt(__doc__ % (DEFAULT_DOWNLOAD_ARCHIVE, DEFAULT_UPLOAD_ARCHIVE),
                         version=__version__)

    URLs = args['<url>']
    for v in ['--cookies', '--proxy', '--username', '--password']:
        if v in args and args[v]:
            args['--yt'].append('%s=%s' % (v, args[v]))

    if args['--use-download-archive']:
        args['--yt'].append('--download-archive=' + DEFAULT_DOWNLOAD_ARCHIVE)

    quiet_mode = args['--quiet']
    debug_mode = args['--debug']
    use_upload_archive = args['--use-upload-archive']
    ignore_existing_item = args['--ignore-existing-item']
    abort_on_error = args['--abort-on-error']
    parser, opts, all_urls, yt_args = parse_options(args['--yt'])

    if debug_mode:
        # Display log messages.
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '\033[92m[DEBUG]\033[0m %(asctime)s - %(name)s - %(levelname)s - '
            '%(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    metadata = internetarchive.cli.argparser.get_args_dict(args['--metadata'])

    tu = TubeUp(verbose=not quiet_mode,
                output_template=args['--output'])

    downloaded_file_basenames = tu.download_urls(URLs, ignore_existing_item, yt_args)

    failures = []
    for basename in downloaded_file_basenames:
        try:
            identifier, meta = tu.upload_ia(basename, use_upload_archive, metadata)
            if identifier:
                print('\n:: Upload Finished. Item information:')
                print('Title: %s' % meta['title'])
                print('Item URL: https://archive.org/details/%s\n' % identifier)
            else:
                print('\n:: Upload skipped. Item information:')
                print('Title: %s' % meta['title'])
        except Exception:
            failures.append(basename)
            print('\n\033[91m'  # Start red color text
                  'An exception just occured, if you found this '
                  "exception isn't related with any of your connection problem, "
                  'please report this issue to '
                  'https://github.com/bibanon/tubeup/issues')
            traceback.print_exc()
            print('\033[0m')  # End the red color text
            if abort_on_error:
                break

    if len(failures) > 0:
        print("Failed uploads:\n" + "\n".join(failures))

if __name__ == '__main__':
    main()
