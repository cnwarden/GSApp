#-*- coding: UTF-8 -*-

import os
import sys
import socket
import ctypes
import ConfigParser
import logging
import threading
from datetime import datetime

from GSClient import *
from GSDataClient import *
from MarketLogicEngine import *

logging.basicConfig(filename='log.txt',level=logging.DEBUG)

def StringCodec(buff):
    return buff.decode('utf-8').encode('GB2312')

class GSDataChannel(threading.Thread):
    def __init__(self):
        super(GSDataChannel, self).__init__(name='GSDataChannel')
        self.setDaemon(True)
        
    def run(self):
        logging.debug('GS DataChannel Starting...')
        self.engine = MarketLogicEngine()
        gsClient = GSDataClient()
        gsClient.SetMarketLogicEngine(self.engine)
        gsClient.Establish()
        
class GSCommandChannel(threading.Thread):
    def __init__(self):
        super(GSCommandChannel, self).__init__(name='GSCommandChannel')
        
    def run(self):
        logging.debug('GS CommandChannel Starting...')
        gsClient = GSClient()
        gsClient.UnSubscribeAll()
        
        sublist = []
        for i in range(600000,600101):
            sublist.append(str(i))
        sublistStr = ','.join(sublist)
        
        gsClient.Subscribe('STOCK', sublistStr)
 
        if not gsClient.Logon():
            exit(0)
        
        while(True):
            os.system('cls')
            print StringCodec("""
            ----------------------操作菜单------------------------
            | [1]订阅数据
            | [2]取消订阅
            | [3]取消所有订阅
            | [4]查询资金
            | [5]查询股东
            | [6]查询资金流水
            | [7]当前状态
            | [0]退出
            ------------------------------------------------------
            """)
            data = raw_input(StringCodec('输入操作内容:'))
            
            id = int(data)
            if id==1:
                asset = raw_input(StringCodec('资产类别[STOCK|INDEX|FUTURE]:'))
                stocks = ''
                if asset == 'STOCK':
                    stocks = raw_input(StringCodec('股票代码[600000,600001]:'))
                gsClient.Subscribe(asset,stocks)
            elif id==2:
                pass
            elif id==3:
                gsClient.UnSubscribeAll()
            elif id==4:
                records = gsClient.QueryMoney()
                for record in records:
                    print '%s:%s' % (StringCodec('资金余额'),record[4])
                    print '%s:%s' % (StringCodec('资金可用金额'),record[5])
                    print '%s:%s' % (StringCodec('资产总值'),record[6])
                    print '%s:%s' % (StringCodec('资产资产'),record[7])
                    print '%s:%s' % (StringCodec('市值'),record[8])
            elif id==0:
                exit(0)
            
            raw_input(StringCodec('继续操作？'))

def main():
    dataChannel = GSDataChannel()
    dataChannel.start()
    
    time.sleep(3)
    
    cmdChannel = GSCommandChannel()
    cmdChannel.start()
    
    cmdChannel.join()
    

if __name__ == '__main__':
    main()

    
    
    