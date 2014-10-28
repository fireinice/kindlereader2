#!/usr/bin/env python
import threading
import Queue
import urllib
import logging
try:
    from PIL import Image
except ImportError:
    Image = None

        # if downing_images:
        #     for i in downing_images:
        #         q.put(i)
        #     threads = []
        #     for i in range(self.thread_numbers):
        #         t = ImageDownloader('Thread %s' % (i+1))
        #         threads.append(t)
        #     for t in threads:
        #         t.setDaemon(True)
        #         t.start()
        #     q.join()


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
