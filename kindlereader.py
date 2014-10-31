#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
main.py
Created by Jiedan<lxb429@gmail.com> on 2010-11-08.
"""

__author__ = "Jiedan<lxb429@gmail.com>"
__version__ = "0.3.3"

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import time
import hashlib
import re
import uuid
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import codecs
import ConfigParser
import getpass
import subprocess
import socket

import gflags
from gflags import FLAGS
from tornado import template
from tornado import escape
from BeautifulSoup import BeautifulSoup
from librssreader.inoreader import RssReader, ClientAuthMethod, Item

work_dir = os.path.dirname(sys.argv[0])
sys.path.append(os.path.join(work_dir, 'lib'))
from KVData import KVData
from RelatedServices import PocketService, AESService, FeedReadMarker
from ImageDownloader import ImageDownloadManager
from kindletemplate import TEMPLATES

# logging.basicConfig(level=logging.DEBUG)
socket.setdefaulttimeout(20)


def find_kindlegen_prog():
    kindlegen_prog = 'kindlegen'

    # search in current directory and PATH to find kinglegen
    sep = ':'
    dirs = ['.']
    dirs.extend(os.getenv('PATH').split(sep))
    for dir in dirs:
        if dir:
            fname = os.path.join(dir, kindlegen_prog)
            if os.path.exists(fname):
                # print fname
                return fname

kindlegen = find_kindlegen_prog()


class KindleReader(object):
    """docstring for KindleReader"""
    global q
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

    def get_config(self, section, name):
        try:
            return self.config.get(section, name).strip()
        except:
            return None

    def sendmail(self, data):
        """send html to kindle"""
        mail_host = self.get_config('mail', 'host')
        mail_port = self.get_config('mail', 'port')
        mail_ssl = self.config.getint('mail', 'ssl')
        mail_from = self.get_config('mail', 'from')
        mail_to = self.get_config('mail', 'to')
        mail_username = self.get_config('mail', 'username')
        mail_password = self.get_config('mail', 'password')
        if not mail_from:
            raise Exception("'mail from' is empty")
        if not mail_to:
            raise Exception("'mail to' is empty")
        if not mail_host:
            raise Exception("'mail host' is empty")
        if not mail_port:
            mail_port = 25
        logging.info("send mail to %s ... " % mail_to)
        msg = MIMEMultipart()
        msg['from'] = mail_from
        msg['to'] = mail_to
        msg['subject'] = 'Convert'

        htmlText = 'google reader delivery.'
        msg.preamble = htmlText

        msgText = MIMEText(htmlText, 'html', 'utf-8')
        msg.attach(msgText)

        att = MIMEText(data, 'base64', 'utf-8')
        att["Content-Type"] = 'application/octet-stream'
        att["Content-Disposition"] = 'attachment; filename="google-reader-%s.mobi"' % time.strftime('%H-%M-%S')
        msg.attach(att)

        try:
            mail = smtplib.SMTP(timeout=60)
            mail.connect(mail_host, int(mail_port))
            mail.ehlo()
            if mail_ssl:
                mail.starttls()
                mail.ehlo()
            if mail_username and mail_password:
                mail.login(mail_username, mail_password)

            mail.sendmail(msg['from'], msg['to'], msg.as_string())
            mail.close()
        except Exception, e:
            logging.error("fail:%s" % e)

    def make_mobi(self, user, feeds, format='book'):
        """docstring for make_mobi"""
        service_host = self.get_config('third_party', 'service_host')
        aes_secret = self.get_config('third_party', 'aes_service_secret')
        aes_service = None
        if aes_secret:
            aes_service = AESService(aes_secret)
        pocket_service = PocketService(service_host, aes_service)
        read_marker = FeedReadMarker(service_host)
        logging.info("generate .mobi file start... ")
        data_dir = os.path.join(self.work_dir, 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        for tpl in TEMPLATES:
            if tpl is 'book.html':
                continue

            t = template.Template(TEMPLATES[tpl])
            content = t.generate(
                user=user,
                feeds=feeds,
                uuid=uuid.uuid1(),
                pocket=pocket_service,
                read_marker=read_marker,
                format=format
            )

            fp = open(os.path.join(data_dir, tpl), 'wb')
            content = content.decode('utf-8', 'ignore').encode('utf-8')
            fp.write(escape.xhtml_unescape(content))
            # fp.write(content)
            fp.close()

        pre_mobi_file = "TheOldReader_%s" % time.strftime('%m-%dT%Hh%Mm')
        opf_file = os.path.join(data_dir, "content.opf")
        subprocess.call('%s %s -o "%s" > log.txt' %
                        (kindlegen, opf_file, pre_mobi_file), shell=True)
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
                try:
                    localimage, fullname = self.parse_image(img['src'], ref)
                    if os.path.isfile(fullname) is False:
                        images.append({
                            'url':img['src'],
                            'filename':fullname
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

    def parse_image(self, url, referer=None, filename=None):
        """download image"""
        url = escape.utf8(url)
        image_guid = hashlib.sha1(url).hexdigest()

        x = url.split('.')
        ext = 'jpg'
        if len(x) > 1:
            ext = x[-1]

            if len(ext) > 4:
                ext = ext[0:3]

            ext = re.sub('[^a-zA-Z]','', ext)
            ext = ext.lower()

            if ext not in ['jpg', 'jpeg', 'gif','png','bmp']:
                ext = 'jpg'

        y = url.split('/')
        h = hashlib.sha1(str(y[2])).hexdigest()

        hash_dir = os.path.join(h[0:1], h[1:2])
        filename = image_guid + '.' + ext

        img_dir = os.path.join(self.work_dir, 'data', 'images', hash_dir)
        fullname = os.path.join(img_dir, filename)

        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        localimage = 'images/%s/%s' % (hash_dir, filename)
        return localimage, fullname

    def main(self):
        username = self.get_config('reader', 'username')
        password = self.get_config('reader', 'password')

        if not password and self.password:
            password = self.password

        if not username or not password:
            raise Exception("google reader's username or password is empty!")

        auth = ClientAuthMethod(username, password)
        reader = RssReader(auth)
        user = reader.getUserInfo()
        reader.buildSubscriptionList()
        categoires = reader.getCategories()
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

        feed_idx, work_idx, updated_items = 0, 1, 0

        feed_num, current_feed = len(feeds), 0
        updated_feeds = []
        downing_images = []
        kv_data = KVData('data/kv')
        for feed_id in feeds:
            feed = feeds[feed_id]

            current_feed = current_feed + 1
            logging.info("[%s/%s]: %s" % (current_feed, feed_num, feed.id))
            try:
                feed_data = reader.getFeedContent(
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
                                item['content'], images = self.parse_summary(content, url)
                                item['idx'] = item_idx
                                item = Item(reader, item, feed)
                                item_idx += 1
                                downing_images += images
                            break
                feed.item_count = len(feed.items)
                updated_items += feed.item_count
                if mark_read:
                    if feed.item_count >= max_items_number:
                        for item in feed.items:
                            item.markRead()
                    elif feed.item_count > 0:
                        reader.markFeedAsRead(feed)

                if feed.item_count > 0:
                    feed_idx += 1
                    feed.idx = feed_idx
                    updated_feeds.append(feed)
                    logging.info("update %s items." % feed.item_count)
                else:
                    logging.info("no update.")
            except Exception, e:
                import traceback
                logging.error("fail: %s" % traceback.format_exc())
        kv_data.set('start_time', int(time.time()))
        kv_data.save()

        #download image by multithreading
        image_download_manager = ImageDownloadManager(downing_images)
        image_download_manager.run()

        if updated_items > 0:
            mail_enable = self.get_config('mail', 'mail_enable')
            kindle_format = self.get_config('general', 'kindle_format')
            if kindle_format not in ['book', 'periodical']:
                kindle_format = 'book'
            mobi_file = self.make_mobi(user, updated_feeds, kindle_format)

            if mobi_file and mail_enable == '1':
                fp = open(mobi_file, 'rb')
                self.sendmail(fp.read())
                fp.close()
        else:
            logging.info("no feed update.")

if __name__ == '__main__':
    gflags.DEFINE_boolean('debug', False,
                          'produces debugging output', short_name='d')
    gflags.DEFINE_string('send_mail', '',
                          '[mobi_path] just send a mobi already generated', short_name='m')
    try:
        FLAGS(sys.argv)  # parse flags
    except gflags.FlagsError, e:
        print '%s\nUsage: %s ARGS\n%s' % (e, sys.argv[0], FLAGS)
        sys.exit(1)

    if FLAGS.debug:
        log_lvl = logging.DEBUG
    else:
        log_lvl = logging.INFO
    logging.basicConfig(level=log_lvl,
                        format='%(asctime)s:%(msecs)03d %(filename)s  %(lineno)03d %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')

    conf_file = os.path.join(work_dir, "config.ini")

    if os.path.isfile(conf_file) is False:
        logging.error("config file '%s' not found" % conf_file)
        sys.exit(1)

    config = ConfigParser.ConfigParser()

    try:
        config.readfp(codecs.open(conf_file, "r", "utf-8-sig"))
    except Exception, e:
        config.readfp(codecs.open(conf_file, "r", "utf-8"))

    st = time.time()
    logging.info("welcome, start ...")
    try:
        kr = KindleReader(work_dir=work_dir, config=config)
        if FLAGS.send_mail:
            with open(FLAGS.send_mail, 'rb') as fp:
                kr.sendmail(fp.read())
                sys.exit(0)
        else:
            if not kindlegen:
                logging.error("Can't find kindlegen")
                sys.exit(1)
            kr.main()
    except Exception:
        import traceback
        logging.error(traceback.format_exc(e))
        sys.exit(-1)

    logging.info("used time %.2fs" % (time.time()-st))
    logging.info("done.")
