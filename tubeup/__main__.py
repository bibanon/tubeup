#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# tubeup.py - Download a video using youtube-dl and upload to the Internet Archive with metadata

# Copyright (C) 2017 Bibliotheca Anonoma
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
"""tubeup - Download a video with Youtube-dl, then upload to Internet Archive, passing all metadata.

Usage:
  tubeup <url>... [--username <user>] [--password <pass>]
                  [--metadata=<key:value>...]
                  [--proxy <prox>]
                  [--quiet] [--debug]
                  [--use-download-archive]
  tubeup -h | --help

Arguments:
  <url>                         Youtube-dl compatible URL to download.
                                Check Youtube-dl documentation for a list
                                of compatible websites.
  --metadata=<key:value>        Custom metadata to add to the archive.org
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
  --quiet                   Just print errors.
  --debug                   Print all logs to stdout.
"""

import sys
import docopt
import logging
import internetarchive
import internetarchive.cli

from tubeup.TubeUp import TubeUp


def main():
    # Parse arguments from file docstring
    args = docopt.docopt(__doc__)

    URLs = args['<url>']
    proxy_url = args['--proxy']
    username = args['--username']
    password = args['--password']
    quiet_mode = args['--quiet']
    debug_mode = args['--debug']
    use_download_archive = args['--use-download-archive']

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

    tu = TubeUp(verbose=not quiet_mode)

    try:
        for identifier, meta in tu.archive_urls(URLs, metadata, proxy_url,
                                                username, password,
                                                use_download_archive):
            print('\n:: Upload Finished. Item information:')
            print('Title: %s' % meta['title'])
            print('Upload URL: https://archive.org/details/%s\n' % identifier)
    except Exception:
        sys.exit(1)


if __name__ == '__main__':
    main()
