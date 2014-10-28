#!/usr/bin/env python
# -*- coding: utf-8 -*- #
#// -*- mode:Python; tab-width:4; py-basic-offset:4; indent-tabs-mode:nil -*-
#/*************************************************************************
# * Copyright (c) 2014 Ganji.com, Inc. All Rights Reserved
# * $Id: KVData.py,v 0.0 2014/08/25 10:44:42 zhangzhiqiang Exp $
# *************************************************************************/
#/**
# * \file		KVData.py
# * \brief		save some data by json in a file
# *
# *
# *
# * \author		ZhangZhiqiang(zhangzhiqiang@ganji.com)
# * \bug		No known bugs.
# *
# * $Date: 2014/08/25 10:44:57 $
# * $Revision: 1.0 $
# */
import json
import os


class KVData:
    def __init__(self, data_file_path):
        self.df_path = data_file_path
        if os.path.exists(data_file_path):
            with open(data_file_path, 'r') as df:
                self.data = json.load(df)
        else:
            self.data = {}

    def save(self):
        if not self.data:
            return False
        with open(self.df_path, 'w') as df:
            json.dump(self.data, df)
            return True

    def set(self, key, value):
        if self.data is None:
            return None
        self.data[key] = value
        return self.data.get(key)

    def get(self, key):
        if self.data is None:
            return None
        return self.data.get(key)
