#!/usr/bin/env python
# -*- coding: utf-8 -*- #
# // -*- mode:Python; tab-width:4; py-basic-offset:4; indent-tabs-mode:nil -*-
# /*************************************************************************
# * $Id: Reader.py,v 0.0 2014/11/09 08:40:35 zhangzhiqiang Exp $
# *************************************************************************/
# /**
# * \file		Reader.py
# * \brief		reader services
# *
# *
# *
# * \author		Zigler Zhang(zigler.zhang@ganji.com)
# * \bug		No known bugs.
# *
# * $Date: 2014/11/09 08:40:46 $
# * $Revision: 1.0 $
# */
import os
import sys
import time
import uuid
import getpass
import subprocess
import commands
import logging
from tornado import template
from tornado import escape
from BeautifulSoup import BeautifulSoup
from librssreader.inoreader import RssReader, ClientAuthMethod, Item

from KVData import KVData
from ImageDownloader import ImageDownloadManager
from kindletemplate import TEMPLATES


class Reader(object):
    """docstring for KindleReader"""
    work_dir = None
    config = None
    template_dir = None
    password = None
    remove_tags = ['script', 'object','video','embed','iframe','noscript', 'style']
    remove_attributes = ['class','id','title','style','width','height','onclick']
    max_image_number = 0
    user_agent = "kindlereader"

    def __init__(self, work_dir=None, config=None, template_dir=None):
        if work_dir:
            self.work_dir = work_dir
        else:
            self.work_dir = os.path.dirname(sys.argv[0])

        self.config = config

        if template_dir is not None and os.path.isdir(template_dir) is False:
            raise Exception("template dir '%s' not found" % template_dir)
        else:
            self.template_dir = template_dir

        self.password = self.get_config('reader', 'password')
        if not self.password:
            self.password = getpass.getpass(
                "please input your google reader's password:")
        username = self.get_config('reader', 'username')
        password = self.get_config('reader', 'password')

        if not password and self.password:
            password = self.password

        if not username or not password:
            raise Exception("google reader's username or password is empty!")

        auth = ClientAuthMethod(username, password)
        self.reader = RssReader(auth)
        self.user_info = self.reader.getUserInfo()

    def get_config(self, section, name):
        try:
            return self.config.get(section, name).strip()
        except:
            return None

    def is_url_blocked(self, url):
        if(url.find("feedsportal.com") >= 0 or
           url.find("feedsky.com") >= 0 or
           url.startswith("http://union.vancl.com/")):
            return True
        else:
            return False

    def parse_summary(self, summary, ref):
        """处理文章"""

        soup = BeautifulSoup(summary)

        for span in list(soup.findAll(attrs={"style": "display: none;"})):
            span.extract()

        for attr in self.remove_attributes:
            for x in soup.findAll(attrs={attr: True}):
                del x[attr]

        for tag in soup.findAll(self.remove_tags):
            tag.extract()

        img_count = 0
        images = []
        for img in list(soup.findAll('img')):
            if ((self.max_image_number >= 0 and
                 img_count >= self.max_image_number) or
                img.has_key('src') is False or
                self.is_url_blocked(img['src'])):
                img.extract()
            else:
                if len(img['src']) > 2048:
                    logging.warning("img src is too long")
                    img.extract()
                else:
                    try:
                        output_dir = os.path.join(self.work_dir, 'data')
                        localimage, fullname = ImageDownloadManager.parse_image(
                            img['src'], ref, output_dir)
                        if os.path.isfile(fullname) is False:
                            images.append({
                                'url': img['src'],
                                'filename': fullname
                            })

                        if localimage:
                            img['src'] = localimage
                            img_count = img_count + 1
                        else:
                            img.extract()
                    except Exception, e:
                        logging.info("error: %s" % e)
                        img.extract()

        return soup.renderContents('utf-8'), images

    def check_feeds_update(self):
        self.reader.buildSubscriptionList()
        categoires = self.reader.getCategories()
        select_categories = self.get_config('reader', 'select_categories')
        skip_categories = self.get_config('reader', 'skip_categories')

        selects = []
        if select_categories:
            select_categories = select_categories.split(',')

            for c in select_categories:
                if c:
                    selects.append(c.encode('utf-8').strip())
            select_categories = None

        skips = []
        if not selects and skip_categories:
            skip_categories = skip_categories.split(',')

            for c in skip_categories:
                if c:
                    skips.append(c.encode('utf-8').strip())
            skip_categories = None

        feeds = {}
        for category in categoires:
            skiped = False
            if selects:
                if category.label.encode("utf-8") in selects:
                    fd = category.getFeeds()
                    for f in fd:
                        if f.id not in feeds:
                            feeds[f.id] = f
                    fd = None
                else:
                    skiped = True

            else:
                if category.label.encode("utf-8") not in skips:
                    fd = category.getFeeds()
                    for f in fd:
                        if f.id not in feeds:
                            feeds[f.id] = f
                    fd = None
                else:
                    skiped = True
            if skiped:
                logging.info('skip category: %s' % category.label)

        max_items_number = self.config.getint('reader', 'max_items_number')
        mark_read = self.config.getint('reader', 'mark_read')
        exclude_read = self.config.getint('reader', 'exclude_read')
        max_image_per_article = self.config.getint(
            'reader', 'max_image_per_article')

        try:
            max_image_per_article = int(max_image_per_article)
            self.max_image_number = max_image_per_article
        except:
            pass

        if not max_items_number:
            max_items_number = 50

        feed_idx = 0

        feed_num, current_feed = len(feeds), 0
        updated_feeds = []
        downing_images = []
        kv_data = KVData('data/kv')
        for feed_id in feeds:
            feed = feeds[feed_id]

            current_feed = current_feed + 1
            logging.info("[%s/%s]: %s" % (current_feed, feed_num, feed.id))
            try:
                feed_data = self.reader.getFeedContent(
                    feed, exclude_read, loadLimit=max_items_number,
                    since=kv_data.get('start_time'))

                if not feed_data:
                    continue

                item_idx = 1
                for item in feed_data['items']:
                    for category in item.get('categories', []):
                        if category.endswith('/state/com.google/reading-list'):
                            content = item.get('content',
                                               item.get(
                                                   'summary', {})).get(
                                                       'content', '')
                            url = None
                            for alternate in item.get('alternate', []):
                                if alternate.get('type', '') == 'text/html':
                                    url = alternate['href']
                                    break
                            if content:
                                item['content'], images = self.parse_summary(
                                    content, url)
                                item['idx'] = item_idx
                                item = Item(self.reader, item, feed)
                                item_idx += 1
                                downing_images += images
                            break
                feed.item_count = len(feed.items)
                if mark_read:
                    if feed.item_count >= max_items_number:
                        for item in feed.items:
                            item.markRead()
                    elif feed.item_count > 0:
                        self.reader.markFeedAsRead(feed)

                if feed.item_count > 0:
                    feed_idx += 1
                    feed.idx = feed_idx
                    updated_feeds.append(feed)
                    logging.info("update %s items." % feed.item_count)
                else:
                    logging.info("no update.")
            except Exception:
                import traceback
                logging.error("fail: %s" % traceback.format_exc())
        kv_data.set('start_time', int(time.time()))
        kv_data.save()

        # download image by multithreading
        image_download_manager = ImageDownloadManager(downing_images)
        image_download_manager.run()
        return updated_feeds


class Kindle(object):
    kindle_gen_prog = 'kindlegen'

    @staticmethod
    def check_kindle_gen():
        os.environ["PATH"] = os.environ["PATH"] + ":./"
        status, result = commands.getstatusoutput(
            'which %s' % Kindle.kindle_gen_prog)
        return status

    @staticmethod
    def make_mobi(user, feeds, data_dir, kindle_format='book',
                  **other_services):
        """docstring for make_mobi"""
        is_updated = False
        for feed in feeds:
            if len(feed.items) > 0:
                is_updated = True
        if not is_updated:
            logging.info("no feed update.")
            return None

        if kindle_format not in ['book', 'periodical']:
            kindle_format = 'book'
        logging.info("generate .mobi file start... ")

        for tpl in TEMPLATES:
            if tpl is 'book.html':
                continue

            t = template.Template(TEMPLATES[tpl])
            content = t.generate(
                user=user,
                feeds=feeds,
                uuid=uuid.uuid1(),
                pocket=other_services['pocket_service'],
                read_marker=other_services['read_marker'],
                format=kindle_format
            )

            fp = open(os.path.join(data_dir, tpl), 'wb')
            content = content.decode('utf-8', 'ignore').encode('utf-8')
            fp.write(escape.xhtml_unescape(content))
            # fp.write(content)
            fp.close()

        pre_mobi_file = "TheOldReader_%s" % time.strftime('%m-%dT%Hh%Mm')
        opf_file = os.path.join(data_dir, "content.opf")
        os.environ["PATH"] = os.environ["PATH"] + ":./"
        subprocess.call('%s %s -o "%s" > log.txt' %
                        (Kindle.kindle_gen_prog, opf_file, pre_mobi_file),
                        shell=True)
        pre_mobi_file = os.path.join(data_dir, pre_mobi_file)
        mobi_file = pre_mobi_file+".mobi"
        subprocess.call('python kindlestrip_v136.py "%s" "%s" >> log.txt' %
                        (pre_mobi_file, mobi_file), shell=True)

        if os.path.isfile(mobi_file) is False:
            logging.error("failed!")
            return None
        else:
            fsize = os.path.getsize(mobi_file)
            logging.info(".mobi save as: %s(%.2fMB)" %
                         (mobi_file, float(fsize)/(1024*1024)))
            return mobi_file
