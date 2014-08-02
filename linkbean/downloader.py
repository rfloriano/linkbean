import sys
import os
import re
import urllib2
import logging
import threading
import shutil
from Queue import Queue

FILENAME_REGEX = re.compile('filename=(?P<filename>.*);?$')


class CriticalPart(object):
    """
    Downloader class.
    """

    def __init__(self, url, download_folder, start_part, end_part):
        self.url = url
        self.download_folder = download_folder
        self.start_part = start_part
        self.end_part = end_part
        self.length = end_part - start_part + 1
        self.request = urllib2.Request(url)
        self.request = self.__prepareHeader(self.request)

    def file_exist(self):
        return os.path.exists(self.get_filename())

    def is_complete(self):
        return self.length == self.get_partial_size()

    def get_partial_size(self):
        status = os.stat(self.get_filename())
        return status.st_size

    def get_filename(self):
        """
        Return the full path to file.
        """
        filename = "%d-%d.temp" % (self.start_part, self.end_part)  # build the name of file
        return os.path.join(self.download_folder, filename)  # return the full path to file

    def __prepareHeader(self, request):
        """
        Prepare the header to download the especified range of bytes.
        """
        request.add_header("Range", "bytes=%d-%d" % (self.start_part, self.end_part))
        return request

    def download(self):
        """
        Download the especific part.
        """
        try:
            self.file = urllib2.urlopen(self.request)
        except Exception, e:
            logging.info(e)
            sys.exit()

        filename = self.get_filename()
        if self.file_exist() and self.is_complete():
            logging.info("%s already finished!" % filename)
            return

        mode = 'wb'
        logging.info("Downloading(%s) %s..." % (mode, filename))
        temp_file = open(filename, mode)
        temp_file.write(self.file.read())
        temp_file.close()
        logging.info("%s finished!" % filename)


class FileDownloader(object):
    """
    My download manager class.
    """

    def __init__(self, link, connections=20, sections=100, download_folder="downloads", clear_tmp=False):
        self.link = link
        self.connections = connections
        self.sections = sections
        self.download_folder = download_folder
        self.clear_tmp = clear_tmp

        try:
            self.file = urllib2.urlopen(self.link)
        except Exception, e:
            logging.info(e)
            sys.exit()

        if not self.is_url_ok():
            logging.info("Incorrect URL!")
            sys.exit(-1)

        self.queue = Queue()
        self.threads = []
        for i in range(self.connections):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.threads.append(t)

    def is_url_ok(self):
        return self.file.code == 200

    def is_complete(self):
        return self.get_filesize() == self.get_partial_size()

    def get_partial_size(self):
        filename = os.path.join(self.download_folder, self.get_filename())
        status = os.stat(filename)
        return status.st_size

    def get_filesize(self):
        for header in self.file.headers.items():
            if header[0].lower() == "content-length":
                return long(header[1])
        raise Exception("Not found content-length in header")

    def get_filename(self):
        """
        Return the name of file.
        """
        info = self.file.headers.get('content-disposition', '')
        result = FILENAME_REGEX.search(info)
        if result:
            return result.group('filename').strip('"')

        filename = self.file.url
        if filename.rfind('/') == len(filename) - 1:  # check if the url ends with /
            filename = filename[:-1]  # remove the / at end of url

        start_at = filename.rfind('/') + 1  # get index of last / in url incressed by 1
        params_index = filename.find('?')  # get the index of first ? in url
        if params_index > 0:  # if found ? in url
            filename = filename[:params_index]  # remove the params from url

        return filename[start_at:]  # get only the file name

    def create_filefolder(self):
        """
        Create the file download folder.
        """
        if not os.path.exists(self.download_folder):
            os.mkdir(self.download_folder)
        os.mkdir(self.get_filefolder_name())

    def file_exist(self):
        file_path = os.path.join(self.download_folder, self.get_filename())
        return os.path.exists(file_path)

    def filefolder_exist(self):
        """
        Verify if the file download folder exists.
        """
        return os.path.exists(self.get_filefolder_name())

    def get_filefolder_name(self):
        filename = self.get_filename() + '.temp'
        return os.path.join(self.download_folder, filename)

    def get_part_size(self):
        total_size = self.get_filesize()
        return total_size / self.sections

    def worker(self):
        while True:
            part = self.queue.get()
            part.download()
            self.queue.task_done()

    def get_parts(self):
        logging.info('calculating size for %s' % self.link)
        part_size = self.get_part_size()
        total_size = self.get_filesize()
        start_part = 0
        parts = []
        while start_part < total_size:
            end_part = start_part + part_size
            if end_part >= total_size:
                end_part = total_size
            parts.append((start_part, end_part))
            start_part = end_part + 1

        return parts

    def download(self):
        if not self.filefolder_exist():
            self.create_filefolder()

        filename = self.get_filename()
        if self.file_exist() and self.is_complete():
            logging.info("%s already downloaded!" % filename)
            return

        logging.info('downloading file %s from url %s' % (filename, self.link))
        parts = self.get_parts()
        tmp_folder = self.get_filefolder_name()
        for start_part, end_part in parts:
            part = CriticalPart(self.file.url, tmp_folder, start_part, end_part)
            self.queue.put(part)

        self.queue.join()

        try:
            self.file_join(parts)
        except Exception, e:
            raise e
        else:
            self.clear_folder(tmp_folder)

    def file_join(self, parts):
        filename = os.path.join(self.download_folder, self.get_filename())
        output = open(filename, 'wb')

        logging.info('join file %s' % filename)
        for start_part, end_part in parts:
            filename = "%s-%s.temp" % (start_part, end_part)
            logging.debug('part file %s' % filename)
            filepath = os.path.join(self.get_filefolder_name(), filename)
            fin = open(filepath, 'rb')
            output.write(fin.read())
            fin.close()

        output.close()

    def clear_folder(self, folder):
        if self.clear_tmp:
            shutil.rmtree(folder)
