#-*- coding: UTF-8 -*-

import os
import sys
import socket
import ctypes
import logging
import codecs
import sqlite3
from datetime import datetime

from GSAPI import *

class PersistEngine:

    def __init__(self):
        self.cx = sqlite3.connect('data.db')
        self.cx.execute('create table if not exists InstrumentTrading(seq integer primary key autoincrement, id integer, quoteTime integer, lastPrc double, openPrc double, highPrc double, lowPrc double, acVol double, turnover double)')
        self.cx.commit()
        
    def Insert(self, record):
        try:
            self.cx.execute('insert into InstrumentTrading(id,quoteTime,lastPrc,openPrc,highPrc,lowPrc,acVol,turnover) values(%d,%d,%f,%f,%f,%f,%f,%f)' % (int(record[0]), int(record[2]), float(record[9]), float(record[4]), float(record[7]), float(record[8]), float(record[6]), float(record[5]) ))
            self.cx.commit()
        except Exception,e:
            print e

def main():
    pe = PersistEngine()
    record = ['600000', '99832321', '23.56']
    pe.Insert(record)
    
if __name__ == '__main__':
    main()
    