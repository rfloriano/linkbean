#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
import logging

from linkbean.downloader import FileDownloader


def main():
    parser = OptionParser()
    parser.add_option('-u', '--url', dest='url', default='',
                      help='URL to download.')
    parser.add_option('-c', '--connections', type=int, dest='connections', default=20,
                      help='Parallel connections to download file.')
    parser.add_option('-o', '--output', dest='output', default='./downloads',
                      help='Parallel connections to download file.')
    parser.add_option('-s', '--sections', type=int, dest='sections', default=100,
                      help='Sections to split download file.')
    log_level_msg = 'The log level to be used. Possible values are: ' + \
        'debug, info, warning, error, critical or notset. [default: info].'
    parser.add_option('-l', '--log-level', dest='log_level', default="warning", help=log_level_msg)

    (opt, args) = parser.parse_args()

    logging.basicConfig(
        format='[linkbean][%(asctime)s] %(levelname)s:%(filename)s:%(funcName)s: %(message)s',
        level=getattr(logging, opt.log_level.upper())
    )

    downloader = FileDownloader(opt.url, opt.connections, opt.sections, opt.output)
    try:
        downloader.download()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
