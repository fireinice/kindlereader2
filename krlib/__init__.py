# -*- coding: utf-8 -*-

# kindlereader
# Copyright (C) 2014  Zigler Zhang <zigler.zhang@gmail.com>
# generate kindle magzine from rss reader

__author__ = "Zigler Zhang <zigler.zhang@gmail.com>"
__version__ = "0.0.1"
__copyright__ = "MIT License"

try:
    from tornado import escape
    from BeautifulSoup import BeautifulSoup
    from librssreader.inoreader import RssReader, ClientAuthMethod, Item
    import pytz
except ImportError:
    # Will occur during setup.py install
    pass
else:
    import imp
    from .Reader import Reader, Kindle
    from .KVData import KVData
    from .Tools import Tools
