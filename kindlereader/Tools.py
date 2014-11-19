#!/usr/bin/env python
# -*- coding: utf-8 -*- #
# // -*- mode:Python; tab-width:4; py-basic-offset:4; indent-tabs-mode:nil -*-
# /*************************************************************************
# * $Id: Tools.py,v 0.0 2014/11/08 18:59:57 Zigler Zhang Exp $
# *************************************************************************/
# /**
# * \file		Tools.py
# * \brief		some tools for kindlereader
# *
# *
# *
# * \author		Zigler Zhang(zigler.zhang.com)
# * \bug		No known bugs.
# *
# * $Date: 2014/11/08 19:00:21 $
# * $Revision: 1.0 $
# */

import os
import time
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from tornado import template


class Tools(object):
    @staticmethod
    def generate_config(work_dir):
        from configtemplate import TEMPLATES
        t = template.Template(TEMPLATES['config.ini'])
        content = t.generate()
        fp = open(os.path.join(work_dir, 'config.ini'), 'wb')
        content = content.decode('utf-8', 'ignore').encode('utf-8')
        fp.write(content)
        fp.close()

    @staticmethod
    def mail_magzine(filename,  config):
        """send html to kindle"""
        mail_host = config.get('mail', 'host')
        mail_port = config.getint('mail', 'port')
        mail_ssl = config.get('mail', 'ssl')
        mail_from = config.get('mail', 'from')
        mail_to = config.get('mail', 'to')
        mail_username = config.get('mail', 'username')
        mail_password = config.get('mail', 'password')
        if not mail_from:
            raise Exception("'mail from' is empty")
        if not mail_to:
            raise Exception("'mail to' is empty")
        if not mail_host:
            raise Exception("'mail host' is empty")
        if not mail_port:
            mail_port = 25
        with open(filename, 'rb') as fp:
            data = fp.read()
        logging.info("send mail to %s ... " % mail_to)
        msg = MIMEMultipart()
        msg['from'] = mail_from
        msg['to'] = mail_to
        msg['subject'] = 'Convert'

        htmlText = 'reader delivery.'
        msg.preamble = htmlText

        msgText = MIMEText(htmlText, 'html', 'utf-8')
        msg.attach(msgText)

        att = MIMEText(data, 'base64', 'utf-8')
        att["Content-Type"] = 'application/octet-stream'
        att["Content-Disposition"] = 'attachment; filename="reader-%s.mobi"' % time.strftime('%H-%M-%S')
        msg.attach(att)

        try:
            mail = smtplib.SMTP(timeout=60)
            mail.connect(mail_host, mail_port)
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
