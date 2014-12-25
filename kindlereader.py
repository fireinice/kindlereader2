#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
main.py
Created by Jiedan<lxb429@gmail.com> on 2010-11-08.
Modified by ZiglerZhang<zigler.zhang@gmail.com> on 2014-11-19
"""

__author__ = "zigler.zhang@gmail.com"
__version__ = "0.0.1"

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import time
import socket
import logging
import ConfigParser
import pytz

import gflags
from gflags import FLAGS

from krlib import Tools, Reader, Kindle, KVData


if __name__ == '__main__':
    work_dir = os.path.dirname(sys.argv[0])

    gflags.DEFINE_boolean('debug', False,
                          'produces debugging output', short_name='d')
    gflags.DEFINE_boolean('generate_config', False,
                          'generate the config template')
    gflags.DEFINE_boolean('mail', True,
                          'send mail after generate mobi file')
    gflags.DEFINE_boolean('since_time', True,
                          'only update items after this time')
    gflags.DEFINE_boolean('make_mobi', True,
                          'generate mobi magzine')
    gflags.DEFINE_string('only_mail', '',
                         '[mobi_path] just send a mobi already generated',
                         short_name='m')
    gflags.DEFINE_string('config', '',
                         'specific the config file',
                         short_name='c')
    try:
        FLAGS(sys.argv)  # parse flags
    except gflags.FlagsError, e:
        print '%s\nUsage: %s ARGS\n%s' % (e, sys.argv[0], FLAGS)
        sys.exit(1)

    if FLAGS.generate_config:
        Tools.generate_config()
        print 'config generated, please fill it by your option'
        sys.exit(0)

    if FLAGS.debug:
        log_lvl = logging.DEBUG
    else:
        log_lvl = logging.INFO
    logging.basicConfig(level=log_lvl,
                        format='%(asctime)s:%(msecs)03d %(filename)s  %(lineno)03d %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')
    socket.setdefaulttimeout(20)

    conf_file = FLAGS.config
    if not conf_file:
        conf_file = os.path.join(work_dir, "config.ini")
    if not os.path.isfile(conf_file):
        print 'conf file does not exist\nUsage: %s ARGS\n%s' % (sys.argv[0], FLAGS)
        sys.exit(1)

    config = ConfigParser.SafeConfigParser()

    config.read(conf_file)
    mail_enable = config.getboolean('general', 'mail_enable')
    magzine_format = config.get('general', 'kindle_format')
    tz = pytz.timezone(config.get('general', 'timezone'))

    reorder = config.getboolean('reader', 'time_order')

    data_dir = os.path.join(work_dir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    if 0 != Kindle.check_kindle_gen():
        logging.error("do not find kindle book generator, exit...")
        sys.exit(1)

    st = time.time()
    since_time = None
    kv_data = KVData(os.path.join(data_dir, 'kv'))
    if FLAGS.since_time:
        since_time = kv_data.get('start_time')
    logging.info("welcome, start ...")
    try:
        if FLAGS.only_mail:
            Tools.mail_magzine(FLAGS.only_mail, **dict(config.items('mail')))
            sys.exit(0)

        reader = Reader(data_dir, **dict(config.items('reader')))

        updated_feeds = reader.check_feeds_update(since_time, reorder)

        if FLAGS.make_mobi:
            mobi_file = Kindle.make_mobi(reader.user_info,
                                         updated_feeds,
                                         data_dir,
                                         magzine_format,
                                         timezone=tz,
                                         )

            if mobi_file and mail_enable and FLAGS.mail:
                Tools.mail_magzine(mobi_file, **dict(config.items('mail')))

    except Exception:
        import traceback
        logging.error(traceback.format_exc())
        sys.exit(-1)

    kv_data.set('start_time', int(time.time()))
    kv_data.save()
    logging.info("used time %.2fs" % (time.time()-st))
    logging.info("done.")
