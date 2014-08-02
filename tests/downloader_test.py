# -*- coding: utf-8 -*-
import os
import shutil
import mock

from tests import LinkbeanTestCase
from linkbean.downloader import FileDownloader, CriticalPart


class FileDownloaderTest(LinkbeanTestCase):
    @mock.patch('urllib2.urlopen')
    def setUp(self, urlopen_mock):
        self.url = 'http://test.com/file.tst'
        self.file = mock.Mock(headers={'Accept-Ranges': 'bytes', 'Content-Length': '1000'}, read=mock.Mock(return_value='1'), code=200, url=self.url)
        urlopen_mock.return_value = self.file

        self.downloader = FileDownloader(self.url, download_folder="tests/downloads")

    def tearDown(self):
        try:
            shutil.rmtree('./tests/downloads')
        except OSError:
            pass

    def test_init(self):
        self.assertEqual(self.downloader.link, 'http://test.com/file.tst')
        self.assertEqual(self.downloader.sections, 15)
        self.assertEqual(self.downloader.download_folder, 'tests/downloads')
        self.assertEqual(self.downloader.file, self.file)

    @mock.patch('linkbean.downloader.Section')
    def test_download(self, SectionMock):
        instance = SectionMock.return_value
        self.downloader.download()
        self.assertEqual(SectionMock.call_count, 15)
        self.assertEqual(instance.start.call_count, 15)
        self.assertEqual(instance.join.call_count, 15)


class CriticalPartTest(LinkbeanTestCase):
    @mock.patch('urllib2.urlopen')
    def setUp(self, urlopen_mock):
        self.url = 'http://test.com/file.tst'
        self.file = mock.Mock(headers={'Accept-Ranges': 'bytes', 'Content-Length': '1000'}, read=mock.Mock(return_value='1'), code=200, url=self.url)
        urlopen_mock.return_value = self.file

        try:
            os.mkdir("tests/downloads")
        except OSError:
            pass

        self.cpart = CriticalPart("tests/downloads", "http://test.com/file.tst", 1000)

    def tearDown(self):
        try:
            shutil.rmtree('./tests/downloads')
        except OSError:
            pass

    def test_init(self):
        self.assertEqual(self.cpart.url, "http://test.com/file.tst")
        self.assertEqual(self.cpart.download_folder, "tests/downloads")
        self.assertEqual(self.cpart.start_at, 0)
        self.assertEqual(self.cpart.length, 1000)
        self.assertEqual(self.cpart.file_size, 1000)
        self.assertEqual(self.cpart.file, self.file)

    def test_download(self):
        self.cpart.download()
        fl = file(self.cpart.get_filename(), 'r')
        content = fl.read()
        fl.close()
        self.assertEqual(content, '1')
