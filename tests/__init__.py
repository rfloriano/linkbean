#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of linkbean.
# https://github.com/rfloriano/linkbean

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Rafael Floriano da Silva rflorianobr@gmail.com

import unittest
import logging
import sys


class LinkbeanTestCase(unittest.TestCase):
    def setUp(self):
        logger = logging.getLogger()
        logger.level = logging.INFO
        stream_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(stream_handler)
