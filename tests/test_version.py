#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of linkbean.
# https://github.com/rfloriano/linkbean

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Rafael Floriano da Silva rflorianobr@gmail.com

from preggy import expect

from linkbean import __version__
from tests.base import TestCase


class VersionTestCase(TestCase):
    def test_has_proper_version(self):
        expect(__version__).to_equal("0.0.1")
