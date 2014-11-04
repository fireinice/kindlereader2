#!/usr/bin/env python
import os
import threading
import Queue
import urllib
import hashlib
import re
import logging
from tornado import escape

try:
    from PIL import Image
except ImportError:
    Image = None


class ImageDownloadManager():
    def __init__(self, images, threads_num=5):
        self.image_queue = Queue.Queue(0)
        if not images:
            return
        self.threads_num = threads_num
        for i in images:
            self.image_queue.put(i)

    def run(self,):
        if self.image_queue.empty():
            return
        threads = []
        for i in range(self.threads_num):
            t = ImageDownloader('ImageDownloader Thread %s' %
                                (i+1), self.image_queue)
            threads.append(t)
        for t in threads:
            t.setDaemon(True)
            t.start()
        self.image_queue.join()

    @staticmethod
    def parse_image(url, referer, output_dir):
        """download image"""
        url = escape.utf8(url)
        image_guid = hashlib.sha1(url).hexdigest()

        x = url.split('.')
        ext = 'jpg'
        if len(x) > 1:
            ext = x[-1]

            if len(ext) > 4:
                ext = ext[0:3]
            ext = re.sub('[^a-zA-Z]', '',  ext)
            ext = ext.lower()
            if ext not in ['jpg', 'jpeg', 'gif', 'png', 'bmp']:
                ext = 'jpg'

        y = url.split('/')
        h = hashlib.sha1(str(y[2])).hexdigest()

        hash_dir = os.path.join(h[0:1], h[1:2])
        filename = image_guid + '.' + ext

        img_dir = os.path.join(output_dir, 'images', hash_dir)
        fullname = os.path.join(img_dir, filename)

        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        localimage = 'images/%s/%s' % (hash_dir, filename)
        return localimage, fullname


class ImageDownloader(threading.Thread):
    def __init__(self, threadname, image_queue):
        threading.Thread.__init__(self, name=threadname)
        self.images = image_queue

    def run(self):
        while True:
            i = self.images.get()
            try:
                urllib.urlretrieve(i['url'], i['filename'])
                if Image:
                    try:
                        img = Image.open(i['filename'])
                        new_img = img.convert("L")
                        new_img.save(i['filename'])
                    except:
                        pass
                logging.info("download: %s" % i['url'])
            except Exception, e:
                logging.error("Failed: %s" % e)
                # q.put(i)
            self.images.task_done()
