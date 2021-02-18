import os
import sys
import re
import glob
import time
import json
import logging
import internetarchive

from internetarchive.config import parse_config_file
from datetime import datetime
from youtube_dl import YoutubeDL
from .utils import (sanitize_identifier, check_is_file_empty,
                    EMPTY_ANNOTATION_FILE)
from logging import getLogger
from urllib.parse import urlparse

from tubeup import __version__


DOWNLOAD_DIR_NAME = 'downloads'


class TubeUp(object):

    def __init__(self,
                 verbose=False,
                 dir_path='~/.tubeup',
                 ia_config_path=None,
                 output_template=None):
        """
        `tubeup` is a tool to archive YouTube by downloading the videos and
        uploading it back to the archive.org.

        :param verbose:         A boolean, True means all loggings will be
                                printed out to stdout.
        :param dir_path:        A path to directory that will be used for
                                saving the downloaded resources. Default to
                               '~/.tubeup'.
        :param ia_config_path:  Path to an internetarchive config file, will
                                be used in uploading the file.
        """
        self.dir_path = dir_path
        self.verbose = verbose
        self.ia_config_path = ia_config_path
        self.logger = getLogger(__name__)
        if output_template is None:
            self.output_template = '%(id)s.%(ext)s'
        else:
            self.output_template = output_template

        # Just print errors in quiet mode
        if not self.verbose:
            self.logger.setLevel(logging.ERROR)

    @property
    def dir_path(self):
        return self._dir_path

    @dir_path.setter
    def dir_path(self, dir_path):
        """
        Set a directory to be the saving directory for resources that have
        been downloaded.

        :param dir_path:  Path to a directory that will be used to save the
                          videos, if it not created yet, the directory
                          will be created.
        """
        extended_usr_dir_path = os.path.expanduser(dir_path)

        # Create the directories.
        os.makedirs(
            os.path.join(extended_usr_dir_path, DOWNLOAD_DIR_NAME),
            exist_ok=True)

        self._dir_path = {
            'root': extended_usr_dir_path,
            'downloads': os.path.join(extended_usr_dir_path,
                                      DOWNLOAD_DIR_NAME)
        }

    def get_resource_basenames(self, urls, proxy_url=None, ydl_username=None,
                               ydl_password=None, use_download_archive=False):
        """
        Get resource basenames from an url.

        :param urls:                  A list of urls that will be downloaded with
                                      youtubedl.
        :param proxy_url:             A proxy url for YoutubeDL.
        :param ydl_username:          Username that will be used to download the
                                      resources with youtube_dl.
        :param ydl_password:          Password of the related username, will be used
                                      to download the resources with youtube_dl.
        :param use_download_archive:  Record the video url to the download archive.
                                      This will download only videos not listed in
                                      the archive file. Record the IDs of all
                                      downloaded videos in it.
        :return:                      Set of videos basename that has been downloaded.
        """
        downloaded_files_basename = set()

        def ydl_progress_hook(d):
            if d['status'] == 'downloading' and self.verbose:
                if d.get('_total_bytes_str') is not None:
                    msg_template = ('%(_percent_str)s of %(_total_bytes_str)s '
                                    'at %(_speed_str)s ETA %(_eta_str)s')
                elif d.get('_total_bytes_estimate_str') is not None:
                    msg_template = ('%(_percent_str)s of '
                                    '~%(_total_bytes_estimate_str)s at '
                                    '%(_speed_str)s ETA %(_eta_str)s')
                elif d.get('_downloaded_bytes_str') is not None:
                    if d.get('_elapsed_str'):
                        msg_template = ('%(_downloaded_bytes_str)s at '
                                        '%(_speed_str)s (%(_elapsed_str)s)')
                    else:
                        msg_template = ('%(_downloaded_bytes_str)s '
                                        'at %(_speed_str)s')
                else:
                    msg_template = ('%(_percent_str)s % at '
                                    '%(_speed_str)s ETA %(_eta_str)s')

                process_msg = '\r[download] ' + (msg_template % d) + '\033[K'
                sys.stdout.write(process_msg)
                sys.stdout.flush()

            if d['status'] == 'finished':
                msg = 'Downloaded %s' % d['filename']

                self.logger.debug(d)
                self.logger.info(msg)
                if self.verbose:
                    print('\n%s' % d)
                    print(msg)

            if d['status'] == 'error':
                # TODO: Complete the error message
                msg = 'Error when downloading the video'

                self.logger.error(msg)
                if self.verbose:
                    print(msg)

        ydl_opts = self.generate_ydl_options(ydl_progress_hook, proxy_url,
                                             ydl_username, ydl_password,
                                             use_download_archive)

        with YoutubeDL(ydl_opts) as ydl:
            for url in urls:
                # Get the info dict of the url, it also download the resources
                # if necessary.
                info_dict = ydl.extract_info(url)

                downloaded_files_basename.update(
                    self.create_basenames_from_ydl_info_dict(ydl, info_dict)
                )

        self.logger.debug(
            'Basenames obtained from url (%s): %s'
            % (url, downloaded_files_basename))

        return downloaded_files_basename

    def create_basenames_from_ydl_info_dict(self, ydl, info_dict):
        """
        Create basenames from YoutubeDL info_dict.

        :param ydl:        A `youtube_dl.YoutubeDL` instance.
        :param info_dict:  A ydl info_dict that will be used to create
                           the basenames.
        :return:           A set that contains basenames that created from
                           the `info_dict`.
        """
        info_type = info_dict.get('_type', 'video')
        self.logger.debug('Creating basenames from ydl info dict with type %s'
                          % info_type)

        filenames = set()

        if info_type == 'playlist':
            # Iterate and get the filenames through the playlist
            for video in info_dict['entries']:
                filenames.add(ydl.prepare_filename(video))
        else:
            filenames.add(ydl.prepare_filename(info_dict))

        basenames = set()

        for filename in filenames:
            filename_without_ext = os.path.splitext(filename)[0]
            file_basename = re.sub(r'(\.f\d+)', '', filename_without_ext)
            basenames.add(file_basename)

        return basenames

    def generate_ydl_options(self,
                             ydl_progress_hook,
                             proxy_url=None,
                             ydl_username=None,
                             ydl_password=None,
                             use_download_archive=False,
                             ydl_output_template=None):
        """
        Generate a dictionary that contains options that will be used
        by youtube_dl.

        :param ydl_progress_hook:     A function that will be called during the
                                      download process by youtube_dl.
        :param proxy_url:             A proxy url for YoutubeDL.
        :param ydl_username:          Username that will be used to download the
                                      resources with youtube_dl.
        :param ydl_password:          Password of the related username, will be
                                      used to download the resources with
                                      youtube_dl.
        :param use_download_archive:  Record the video url to the download archive.
                                      This will download only videos not listed in
                                      the archive file. Record the IDs of all
                                      downloaded videos in it.
        :return:                      A dictionary that contains options that will
                                      be used by youtube_dl.
        """
        ydl_opts = {
            'outtmpl': os.path.join(self.dir_path['downloads'],
                                    self.output_template),
            'restrictfilenames': True,
            'quiet': not self.verbose,
            'verbose': self.verbose,
            'progress_with_newline': True,
            'forcetitle': True,
            'continuedl': True,
            'retries': 9001,
            'fragment_retries': 9001,
            'forcejson': True,
            'writeinfojson': True,
            'writedescription': True,
            'writethumbnail': True,
            'writeannotations': True,
            'writesubtitles': True,
            'allsubtitles': True,
            'ignoreerrors': True,  # Geo-blocked,
                                   # copyrighted/private/deleted
                                   # will be printed to STDOUT and channel
                                   # ripping will  continue uninterupted,
                                   # use with verbose off
            'fixup': 'warn',  # Slightly more verbosity for debugging
                              # problems
            'nooverwrites': True,  # Don't touch what's already been
                                   # downloaded speeds things
            'consoletitle': True,   # Download percentage in console title
            'prefer_ffmpeg': True,  # `ffmpeg` is better than `avconv`,
                                    # let's prefer it's use
            # Warns on out of date youtube-dl script, helps debugging for
            # youtube-dl devs
            'call_home': False,
            'logger': self.logger,
            'progress_hooks': [ydl_progress_hook]
        }

        if proxy_url is not None:
            ydl_opts['proxy'] = proxy_url

        if ydl_username is not None:
            ydl_opts['username'] = ydl_username

        if ydl_password is not None:
            ydl_opts['password'] = ydl_password

        if use_download_archive:
            ydl_opts['download_archive'] = os.path.join(self.dir_path['root'],
                                                        '.ytdlarchive')

        return ydl_opts

    def upload_ia(self, videobasename, custom_meta=None):
        """
        Upload video to archive.org.

        :param videobasename:  A video base name.
        :param custom_meta:    A custom meta, will be used by internetarchive
                               library when uploading to archive.org.
        :return:               A tuple containing item name and metadata used
                               when uploading to archive.org.
        """
        json_metadata_filepath = videobasename + '.info.json'
        with open(json_metadata_filepath) as f:
            vid_meta = json.load(f)

        itemname = ('%s-%s' % (vid_meta['extractor'],
                               vid_meta['display_id']))

        # Replace illegal characters within identifer
        itemname = sanitize_identifier(itemname)

        metadata = self.create_archive_org_metadata_from_youtubedl_meta(
            vid_meta)

        # Delete empty description file
        description_file_path = videobasename + '.description'
        if (os.path.exists(description_file_path) and
            (('description' in vid_meta and
             vid_meta['description'] == '') or
                check_is_file_empty(description_file_path))):
            os.remove(description_file_path)

        # Delete empty annotations.xml file so it isn't uploaded
        annotations_file_path = videobasename + '.annotations.xml'
        if (os.path.exists(annotations_file_path) and
            (('annotations' in vid_meta and
             vid_meta['annotations'] in {'', EMPTY_ANNOTATION_FILE}) or
                check_is_file_empty(annotations_file_path))):
            os.remove(annotations_file_path)

        # Upload all files with videobase name: e.g. video.mp4,
        # video.info.json, video.srt, etc.
        files_to_upload = glob.glob(videobasename + '*')

        # Upload the item to the Internet Archive
        item = internetarchive.get_item(itemname)

        if custom_meta:
            metadata.update(custom_meta)

        # Parse internetarchive configuration file.
        parsed_ia_s3_config = parse_config_file(self.ia_config_path)[1]['s3']
        s3_access_key = parsed_ia_s3_config['access']
        s3_secret_key = parsed_ia_s3_config['secret']

        if None in {s3_access_key, s3_secret_key}:
            msg = ('`internetarchive` configuration file is not configured'
                   ' properly.')

            self.logger.error(msg)
            if self.verbose:
                print(msg)
            raise Exception(msg)

        item.upload(files_to_upload, metadata=metadata, retries=9001,
                    request_kwargs=dict(timeout=9001), delete=True,
                    verbose=self.verbose, access_key=s3_access_key,
                    secret_key=s3_secret_key)

        return itemname, metadata

    def archive_urls(self, urls, custom_meta=None, proxy=None,
                     ydl_username=None, ydl_password=None,
                     use_download_archive=False):
        """
        Download and upload videos from youtube_dl supported sites to
        archive.org

        :param urls:                  List of url that will be downloaded and uploaded
                                      to archive.org
        :param custom_meta:           A custom metadata that will be used when
                                      uploading the file with archive.org.
        :param proxy_url:             A proxy url for YoutubeDL.
        :param ydl_username:          Username that will be used to download the
                                      resources with youtube_dl.
        :param ydl_password:          Password of the related username, will be used
                                      to download the resources with youtube_dl.
        :param use_download_archive:  Record the video url to the download archive.
                                      This will download only videos not listed in
                                      the archive file. Record the IDs of all
                                      downloaded videos in it.
        :return:                      Tuple containing identifier and metadata of the
                                      file that has been uploaded to archive.org.
        """
        downloaded_file_basenames = self.get_resource_basenames(
            urls, proxy, ydl_username, ydl_password, use_download_archive)

        for basename in downloaded_file_basenames:
            identifier, meta = self.upload_ia(basename, custom_meta)
            yield identifier, meta

    @staticmethod
    def determine_collection_type(url):
        """
        Determine collection type for an url.

        :param url:  URL that the collection type will be determined.
        :return:     String, name of a collection.
        """
        if urlparse(url).netloc == 'soundcloud.com':
            return 'opensource_audio'
        return 'opensource_movies'

    @staticmethod
    def determine_licenseurl(vid_meta):
        """
        Determine licenseurl for an url

        :param vid_meta:
        :return:
        """
        licenseurl = ''
        licenses = {
            "Creative Commons Attribution license (reuse allowed)": "https://creativecommons.org/licenses/by/3.0/",
            "Attribution-NonCommercial-ShareAlike": "https://creativecommons.org/licenses/by-nc-sa/2.0/",
            "Attribution-NonCommercial": "https://creativecommons.org/licenses/by-nc/2.0/",
            "Attribution-NonCommercial-NoDerivs": "https://creativecommons.org/licenses/by-nc-nd/2.0/",
            "Attribution": "https://creativecommons.org/licenses/by/2.0/",
            "Attribution-ShareAlike": "https://creativecommons.org/licenses/by-sa/2.0/",
            "Attribution-NoDerivs": "https://creativecommons.org/licenses/by-nd/2.0/"
        }

        if 'license' in vid_meta and vid_meta['license']:
            licenseurl = licenses.get(vid_meta['license'])

        return licenseurl

    @staticmethod
    def create_archive_org_metadata_from_youtubedl_meta(vid_meta):
        """
        Create an archive.org from youtubedl-generated metadata.

        :param vid_meta: A dict containing youtubedl-generated metadata.
        :return:         A dict containing metadata to be used by
                         internetarchive library.
        """
        title = '%s' % (vid_meta['title'])
        videourl = vid_meta['webpage_url']

        collection = TubeUp.determine_collection_type(videourl)

        # Some video services don't tell you the uploader,
        # use our program's name in that case.
        try:
            if vid_meta['extractor_key'] == 'TwitchClips' and 'creator' in vid_meta and vid_meta['creator']:
                uploader = vid_meta['creator']
            elif 'uploader' in vid_meta and vid_meta['uploader']:
                uploader = vid_meta['uploader']
            elif 'uploader_url' in vid_meta and vid_meta['uploader_url']:
                uploader = vid_meta['uploader_url']
            else:
                uploader = 'tubeup.py'
        except TypeError:  # apparently uploader is null as well
            uploader = 'tubeup.py'

        uploader_url = vid_meta.get('uploader_url', videourl)

        try:  # some videos don't give an upload date
            d = datetime.strptime(vid_meta['upload_date'], '%Y%m%d')
            upload_date = d.isoformat().split('T')[0]
            upload_year = upload_date[:4]  # 20150614 -> 2015
        except (KeyError, TypeError):
            # Use current date and time as default values
            upload_date = time.strftime("%Y-%m-%d")
            upload_year = time.strftime("%Y")

        # load up tags into an IA compatible semicolon-separated string
        # example: Youtube;video;
        tags_string = '%s;video;' % vid_meta['extractor_key']

        if 'categories' in vid_meta:
            # add categories as tags as well, if they exist
            try:
                for category in vid_meta['categories']:
                    tags_string += '%s;' % category
            except Exception:
                print("No categories found.")

        if 'tags' in vid_meta:  # some video services don't have tags
            try:
                if 'tags' in vid_meta is None:
                    tags_string += '%s;' % vid_meta['id']
                    tags_string += '%s;' % 'video'
                else:
                    for tag in vid_meta['tags']:
                        tags_string += '%s;' % tag
            except Exception:
                print("Unable to process tags successfully.")

        # license
        licenseurl = TubeUp.determine_licenseurl(vid_meta)

        # if there is no description don't upload the empty .description file
        description_text = vid_meta.get('description', '')
        if description_text is None:
            description_text = ''
        # archive.org does not display raw newlines
        description_text = re.sub('\r?\n', '<br>', description_text)

        description = ('{0} <br/><br/>Source: <a href="{1}">{2}</a>'
                       '<br/>Uploader: <a href="{3}">{4}</a>').format(
            description_text, videourl, videourl, uploader_url, uploader)

        metadata = dict(
            mediatype=('audio' if collection == 'opensource_audio'
                       else 'movies'),
            creator=uploader,
            collection=collection,
            title=title,
            description=description,
            date=upload_date,
            year=upload_year,
            subject=tags_string,
            originalurl=videourl,
            licenseurl=licenseurl,

            # Set 'scanner' metadata pair to allow tracking of TubeUp
            # powered uploads, per request from archive.org
            scanner='TubeUp Video Stream Mirroring Application {}'.format(__version__))

        return metadata
