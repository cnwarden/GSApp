#-*- coding: UTF-8 -*-

#import sys
#reload(sys)
#sys.setdefaultencoding('utf8')

import os
import sys
import socket
import ctypes
import ConfigParser
import logging
import codecs
from datetime import datetime

from PersistEngine import *
from GSAPI import *

class MarketLogicEngine:

    def __init__(self):
        self.gsApi = GSAPI()
        if not os.path.exists('Data'):
            os.mkdir('Data')
            
        self.cx = PersistEngine()
        
        self.fp = codecs.open('Data/data.csv','a','utf-8')
        header = unicode('股票代码,股票名称,时间戳,前收盘价,今开盘价,总成交金额,总成交量,最高价,最低价,最新价\n','utf-8')
        self.fp.write(header)
        
        self.idxs = [
                self.gsApi.Msg_RealTime_Response.index('CODE'),
                self.gsApi.Msg_RealTime_Response.index('NAME'),
                self.gsApi.Msg_RealTime_Response.index('QUOTETIME'),
                self.gsApi.Msg_RealTime_Response.index('PRECLOSE'),
                self.gsApi.Msg_RealTime_Response.index('OPEN'),
                self.gsApi.Msg_RealTime_Response.index('SUM'),
                self.gsApi.Msg_RealTime_Response.index('AMOUNT'),
                self.gsApi.Msg_RealTime_Response.index('HIGH'),
                self.gsApi.Msg_RealTime_Response.index('LOW'),
                self.gsApi.Msg_RealTime_Response.index('NEW')
               ]
        
    def ProcessRealTimeMsg(self, record):
        data = []
        for i in self.idxs:
            data.append(record[i].decode('GB2312'))
        self.cx.Insert(data)
        newstr = u','.join(data)
        self.fp.write(newstr)
        self.fp.write('\n')
        self.fp.flush()

def main():
    pass
    
if __name__ == '__main__':
    main()
    