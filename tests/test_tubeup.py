import unittest
import os
import shutil
import json
import time
import requests_mock
import glob

from tubeup.TubeUp import TubeUp, log, DOWNLOAD_DIR_NAME


current_path = os.path.dirname(os.path.realpath(__file__))


def get_testfile_path(name):
    return os.path.join(current_path, 'test_tubeup_files', name)


def mocked_ydl_progress_hook(d):
    pass


def mock_upload_response_by_videobasename(m, ia_id, videobasename):
    files_to_upload = glob.glob(videobasename + '*')

    for file_path in files_to_upload:
        filename = os.path.basename(file_path)
        m.put('https://s3.us.archive.org/%s/%s' % (ia_id, filename),
              content=b'',
              headers={'content-type': 'text/plain'})


def copy_testfiles_to_tubeup_rootdir_test():
    # Copy testfiles to rootdir path of TubeUp.
    # This method was created because after the uploading done by
    # internetarchive library, it deletes the files that has been uploaded.
    testfiles_dir = os.path.join(current_path, 'test_tubeup_files',
                                 'files_for_upload_and_download_tests')

    for filepath in os.listdir(testfiles_dir):
        shutil.copy(
            os.path.join(testfiles_dir, filepath),
            os.path.join(current_path, 'test_tubeup_rootdir', 'downloads',
                         filepath))


class TubeUpTests(unittest.TestCase):

    def setUp(self):
        self.tu = TubeUp()
        self.maxDiff = 999999999

    def test_set_dir_path(self):
        root_path = os.path.join(
            current_path, '.directory_for_tubeup_set_dir_path_test')
        dir_paths_dict = dict(root=root_path,
                              downloads=os.path.join(root_path,
                                                     DOWNLOAD_DIR_NAME))

        self.tu.dir_path = root_path
        self.assertEqual(self.tu.dir_path, dir_paths_dict)

        # Make sure that other directories are created as well
        self.assertTrue(os.path.exists(dir_paths_dict['downloads']))

        # Clean the test directory
        shutil.rmtree(root_path, ignore_errors=True)

    def test_determine_collection_type(self):
        soundcloud_colltype = self.tu.determine_collection_type(
            'https://soundcloud.com/testurl')
        another_colltype = self.tu.determine_collection_type(
            'https://www.youtube.com/watch?v=testVideo'
        )

        self.assertEqual(soundcloud_colltype, 'opensource_audio')
        self.assertEqual(another_colltype, 'opensource_movies')

    def test_generate_ydl_options(self):
        result = self.tu.generate_ydl_options(mocked_ydl_progress_hook)

        download_path = os.path.join(
            os.path.expanduser('~/.tubeup'), DOWNLOAD_DIR_NAME)

        expected_result = {
            'outtmpl': os.path.join(
                download_path, '%(title)s-%(id)s.%(ext)s'),
            'restrictfilenames': True,
            'verbose': False,
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
            'ignoreerrors': True,
            'fixup': 'warn',
            'nooverwrites': True,
            'consoletitle': True,
            'prefer_ffmpeg': True,
            'call_home': False,
            'logger': log,
            'progress_hooks': [mocked_ydl_progress_hook]}

        self.assertEqual(result, expected_result)

    def test_generate_ydl_options_with_proxy(self):
        result = self.tu.generate_ydl_options(
            mocked_ydl_progress_hook, proxy_url='http://proxytest.com:8080')

        download_path = os.path.join(
            os.path.expanduser('~/.tubeup'), DOWNLOAD_DIR_NAME)

        expected_result = {
            'outtmpl': os.path.join(
                download_path, '%(title)s-%(id)s.%(ext)s'),
            'restrictfilenames': True,
            'verbose': False,
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
            'ignoreerrors': True,
            'fixup': 'warn',
            'nooverwrites': True,
            'consoletitle': True,
            'prefer_ffmpeg': True,
            'call_home': False,
            'logger': log,
            'progress_hooks': [mocked_ydl_progress_hook],
            'proxy': 'http://proxytest.com:8080'}

        self.assertEqual(result, expected_result)

    def test_generate_ydl_options_with_ydl_account(self):
        result = self.tu.generate_ydl_options(
            mocked_ydl_progress_hook, ydl_username='testUsername',
            ydl_password='testPassword')

        download_path = os.path.join(
            os.path.expanduser('~/.tubeup'), DOWNLOAD_DIR_NAME)

        expected_result = {
            'outtmpl': os.path.join(
                download_path, '%(title)s-%(id)s.%(ext)s'),
            'restrictfilenames': True,
            'verbose': False,
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
            'ignoreerrors': True,
            'fixup': 'warn',
            'nooverwrites': True,
            'consoletitle': True,
            'prefer_ffmpeg': True,
            'call_home': False,
            'logger': log,
            'progress_hooks': [mocked_ydl_progress_hook],
            'username': 'testUsername',
            'password': 'testPassword'}

        self.assertEqual(result, expected_result)

    def test_create_archive_org_metadata_from_youtubedl_meta(self):
        with open(get_testfile_path(
                'Mountain_3_-_Video_Background_HD_1080p-6iRV8liah8A.info.json')
                ) as f:
            vid_meta = json.load(f)

        result = TubeUp.create_archive_org_metadata_from_youtubedl_meta(
            vid_meta
        )

        expected_result = {
            'mediatype': 'movies',
            'creator': 'Video Background',
            'collection': 'opensource_movies',
            'title': 'Mountain 3 - Video Background HD 1080p',
            'description': ('Mountain 3 - Video Background HD 1080p\n'
                            'If you use this video please put credits to my '
                            'channel in description:\nhttps://www.youtube.com'
                            '/channel/UCWpsozCMdAnfI16rZHQ9XDg\n© Don\'t '
                            'forget to SUBSCRIBE, LIKE, COMMENT and RATE. '
                            'Hope you all enjoy! <br/><br/>Source: '
                            '<a href="https://www.youtube.com/watch?v='
                            '6iRV8liah8A">https://www.youtube.com/watch?v='
                            '6iRV8liah8A</a><br/>Uploader: <a href="http://ww'
                            'w.youtube.com/channel/UCWpsozCMdAnfI16rZHQ9XDg">'
                            'Video Background</a>'),
            'date': '2015-01-05',
            'year': '2015',
            'subject': ('Youtube;video;Entertainment;Video Background;Footage;'
                        'Animation;Cinema;stock video footage;Royalty '
                        'free videos;Creative Commons videos;free movies '
                        'online;youtube;HD;1080p;Amazing Nature;Mountain;'),
            'originalurl': 'https://www.youtube.com/watch?v=6iRV8liah8A',
            'licenseurl': ''}

        self.assertEqual(expected_result, result)

    def test_create_archive_org_metadata_from_youtubedl_meta_no_uploader(self):
        with open(get_testfile_path(
                'Mountain_3_-_Video_Background_HD_1080p-6iRV8liah8A.info_no_'
                'uploader.json')
        ) as f:
            vid_meta = json.load(f)

        result = TubeUp.create_archive_org_metadata_from_youtubedl_meta(
            vid_meta
        )

        expected_result = {
            'mediatype': 'movies',
            'creator': 'tubeup.py',
            'collection': 'opensource_movies',
            'title': 'Mountain 3 - Video Background HD 1080p',
            'description': ('Mountain 3 - Video Background HD 1080p\n'
                            'If you use this video please put credits to my '
                            'channel in description:\nhttps://www.youtube.com'
                            '/channel/UCWpsozCMdAnfI16rZHQ9XDg\n© Don\'t '
                            'forget to SUBSCRIBE, LIKE, COMMENT and RATE. '
                            'Hope you all enjoy! <br/><br/>Source: '
                            '<a href="https://www.youtube.com/watch?v='
                            '6iRV8liah8A">https://www.youtube.com/watch?v='
                            '6iRV8liah8A</a><br/>Uploader: <a href="http://ww'
                            'w.youtube.com/channel/UCWpsozCMdAnfI16rZHQ9XDg">'
                            'tubeup.py</a>'),
            'date': '2015-01-05',
            'year': '2015',
            'subject': ('Youtube;video;Entertainment;Video Background;Footage;'
                        'Animation;Cinema;stock video footage;Royalty '
                        'free videos;Creative Commons videos;free movies '
                        'online;youtube;HD;1080p;Amazing Nature;Mountain;'),
            'originalurl': 'https://www.youtube.com/watch?v=6iRV8liah8A',
            'licenseurl': ''}

        self.assertEqual(expected_result, result)

    def test_create_archive_org_metadata_from_youtubedl_meta_no_date(self):
        with open(get_testfile_path(
                'Mountain_3_-_Video_Background_HD_1080p-6iRV8liah8A.'
                'info_no_date.json')
        ) as f:
            vid_meta = json.load(f)

        result = TubeUp.create_archive_org_metadata_from_youtubedl_meta(
            vid_meta
        )

        upload_date = time.strftime("%Y-%m-%d")
        upload_year = time.strftime("%Y")

        expected_result = {
            'mediatype': 'movies',
            'creator': 'Video Background',
            'collection': 'opensource_movies',
            'title': 'Mountain 3 - Video Background HD 1080p',
            'description': ('Mountain 3 - Video Background HD 1080p\n'
                            'If you use this video please put credits to my '
                            'channel in description:\nhttps://www.youtube.com'
                            '/channel/UCWpsozCMdAnfI16rZHQ9XDg\n© Don\'t '
                            'forget to SUBSCRIBE, LIKE, COMMENT and RATE. '
                            'Hope you all enjoy! <br/><br/>Source: '
                            '<a href="https://www.youtube.com/watch?v='
                            '6iRV8liah8A">https://www.youtube.com/watch?v='
                            '6iRV8liah8A</a><br/>Uploader: <a href="http://ww'
                            'w.youtube.com/channel/UCWpsozCMdAnfI16rZHQ9XDg">'
                            'Video Background</a>'),
            'date': upload_date,
            'year': upload_year,
            'subject': ('Youtube;video;Entertainment;Video Background;Footage;'
                        'Animation;Cinema;stock video footage;Royalty '
                        'free videos;Creative Commons videos;free movies '
                        'online;youtube;HD;1080p;Amazing Nature;Mountain;'),
            'originalurl': 'https://www.youtube.com/watch?v=6iRV8liah8A',
            'licenseurl': ''}

        self.assertEqual(expected_result, result)

    def test_get_resource_basenames(self):
        tu = TubeUp(dir_path=os.path.join(current_path,
                                          'test_tubeup_rootdir'))

        copy_testfiles_to_tubeup_rootdir_test()

        result = tu.get_resource_basenames(
            ['https://www.youtube.com/watch?v=6iRV8liah8A'])

        expected_result = {os.path.join(
            current_path, 'test_tubeup_rootdir', 'downloads',
            'Mountain_3_-_Video_Background_HD_1080p-6iRV8liah8A')}

        self.assertEqual(expected_result, result)

    def test_upload_ia(self):
        tu = TubeUp(dir_path=os.path.join(current_path,
                                          'test_tubeup_rootdir'),
                    # Use custom ia configuration file so we don't need
                    # to login with username and password.
                    ia_config_path=get_testfile_path('ia_config_for_test.ini'))

        videobasename = os.path.join(
            current_path, 'test_tubeup_rootdir', 'downloads',
            'Mountain_3_-_Video_Background_HD_1080p-6iRV8liah8A')

        copy_testfiles_to_tubeup_rootdir_test()

        with requests_mock.Mocker() as m:
            # Mock the request to s3.us.archive.org, so it will responds
            # a custom json. `internetarchive` library sends GET request to
            # that url to check that we don't violate the upload limit.
            m.get('https://s3.us.archive.org',
                  content=b'{"over_limit": 0}',
                  headers={'content-type': 'application/json'})

            m.get('https://archive.org/metadata/youtube-6iRV8liah8A',
                  content=b'{}',
                  headers={'content-type': 'application/json'})

            # Mock the PUT requests for internetarchive urls that defined
            # in mock_upload_response_by_videobasename(), so this test
            # doesn't perform upload to the real archive.org server.
            mock_upload_response_by_videobasename(
                m, 'youtube-6iRV8liah8A', videobasename)

            result = tu.upload_ia(videobasename)

            expected_result = (
                'youtube-6iRV8liah8A',
                {'mediatype': 'movies',
                 'creator': 'Video Background',
                 'collection': 'opensource_movies',
                 'title': 'Mountain 3 - Video Background HD 1080p',
                 'description': ('Mountain 3 - Video Background HD 1080p\nIf '
                                 'you use this video please put credits to my'
                                 ' channel in description:\nhttps://www.youtub'
                                 'e.com/channel/UCWpsozCMdAnfI16rZHQ9XDg\n© D'
                                 'on\'t forget to SUBSCRIBE, LIKE, COMMENT an'
                                 'd RATE. Hope you all enjoy! <br/><br/>Sourc'
                                 'e: <a href="https://www.youtube.com/watch?v'
                                 '=6iRV8liah8A">https://www.youtube.com/watch'
                                 '?v=6iRV8liah8A</a><br/>Uploader: <a href="h'
                                 'ttp://www.youtube.com/channel/UCWpsozCMdAnf'
                                 'I16rZHQ9XDg">Video Background</a>'),
                 'date': '2015-01-05',
                 'year': '2015',
                 'subject': ('Youtube;video;Entertainment;Video Background;'
                             'Footage;Animation;Cinema;stock video footage;'
                             'Royalty free videos;Creative Commons videos;'
                             'free movies online;youtube;HD;1080p;Amazing '
                             'Nature;Mountain;'),
                 'originalurl': 'https://www.youtube.com/watch?v=6iRV8liah8A',
                 'licenseurl': '',
                 'scanner': 'Internet Archive Python library 1.7.3'})

            self.assertEqual(expected_result, result)

    def test_archive_urls(self):
        tu = TubeUp(dir_path=os.path.join(current_path,
                                          'test_tubeup_rootdir'),
                    ia_config_path=get_testfile_path('ia_config_for_test.ini'))

        videobasename = os.path.join(
            current_path, 'test_tubeup_rootdir', 'downloads',
            'Mountain_3_-_Video_Background_HD_1080p-6iRV8liah8A')

        copy_testfiles_to_tubeup_rootdir_test()

        with requests_mock.Mocker() as m:
            # Mock the request to s3.us.archive.org, so it will responds
            # a custom json. `internetarchive` library sends GET request to
            # that url to check that we don't violate the upload limit.
            m.get('https://s3.us.archive.org',
                  content=b'{"over_limit": 0}',
                  headers={'content-type': 'application/json'})

            m.get('https://archive.org/metadata/youtube-6iRV8liah8A',
                  content=b'{}',
                  headers={'content-type': 'application/json'})

            # Mock the PUT requests for internetarchive urls that defined
            # in mock_upload_response_by_videobasename(), so this test
            # doesn't perform upload to the real archive.org server.
            mock_upload_response_by_videobasename(
                m, 'youtube-6iRV8liah8A', videobasename)

            result = list(tu.archive_urls(
                ['https://www.youtube.com/watch?v=6iRV8liah8A']))

            expected_result = [(
                'youtube-6iRV8liah8A',
                {'mediatype': 'movies',
                 'creator': 'Video Background',
                 'collection': 'opensource_movies',
                 'title': 'Mountain 3 - Video Background HD 1080p',
                 'description': ('Mountain 3 - Video Background HD 1080p\nIf '
                                 'you use this video please put credits to my'
                                 ' channel in description:\nhttps://www.youtub'
                                 'e.com/channel/UCWpsozCMdAnfI16rZHQ9XDg\n© D'
                                 'on\'t forget to SUBSCRIBE, LIKE, COMMENT an'
                                 'd RATE. Hope you all enjoy! <br/><br/>Sourc'
                                 'e: <a href="https://www.youtube.com/watch?v'
                                 '=6iRV8liah8A">https://www.youtube.com/watch'
                                 '?v=6iRV8liah8A</a><br/>Uploader: <a href="h'
                                 'ttp://www.youtube.com/channel/UCWpsozCMdAnf'
                                 'I16rZHQ9XDg">Video Background</a>'),
                 'date': '2015-01-05',
                 'year': '2015',
                 'subject': ('Youtube;video;Entertainment;Video Background;'
                             'Footage;Animation;Cinema;stock video footage;'
                             'Royalty free videos;Creative Commons videos;'
                             'free movies online;youtube;HD;1080p;Amazing '
                             'Nature;Mountain;'),
                 'originalurl': 'https://www.youtube.com/watch?v=6iRV8liah8A',
                 'licenseurl': '',
                 'scanner': 'Internet Archive Python library 1.7.3'})]

            self.assertEqual(expected_result, result)
