#-*- coding: UTF-8 -*-

import os
import sys
import socket
import ctypes
import ConfigParser
import logging
import time
from datetime import datetime

from GSAPI import *

class GSDataClient:

    gsApi = None

    def __init__(self):
        logging.basicConfig(filename='log.txt',level=logging.DEBUG)
        
        self.cf = ConfigParser.ConfigParser()
        self.cf.read('GSCfg.ini')
        
        self.serverIp = self.cf.get('GSCLIENT','DATA_IP')
        self.port = int(self.cf.get('GSCLIENT','DATA_PORT'))
      
        self.gsApi = GSAPI()
        self.isEstablished = False
        
        self.MarketLogicHandler = None
        
        self.journal = open('journal.dat','a')
        
    def SetMarketLogicEngine(self, handler):
        self.MarketLogicHandler = handler
        
    def Establish(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(10000)
        self.s.connect((self.serverIp, self.port))
        
        self.s.send(self.gsApi.EstablishChannel())
        
        chunk = self.s.recv(2048)
        if chunk:
            length = int(chunk[8:16])
            errorCode,errorMsg = self.gsApi.GetResponseHeader_DataLine(chunk)
            if errorCode == 0:
                self.isEstablished = True
            print errorMsg
            logging.debug('[%s][RECV]:MsgBodyLen=%d Len=%d Raw:%s' % (datetime.now(), length, len(chunk), chunk))
        else:
            logging.debug('None Response')
        
        remainBuff = ''
        self.s.setblocking(0)
        while(True):
            try:
                chunk = self.s.recv(9999)
                remainBuff = remainBuff + chunk
                if remainBuff:
                    packages = remainBuff.split('GXFIXSTD')
                    length = len(packages)
                    
                    for i in range(length):
                        if packages[i] != '':
                            current = 'GXFIXSTD' + packages[i]
                            if len(current) > 16:
                                length = int(current[8:16]) + 16 #add header
                                if length > len(current):
                                    remainBuff = current
                                    break
                                else:
                                    # should be equal
                                    logging.debug('[%s][RECV]:LenInMsg:%d Len:%d Raw:%s' % (datetime.now(), length, len(current), current))
                                    col,row,header,records = self.gsApi.GetResponseBody_DataLine(current)
                                    for record in records:
                                        self.MarketLogicHandler.ProcessRealTimeMsg(record)
                                        self.journal.write(','.join(record))
                                        self.journal.write('\n')
                                    remainBuff = ''
                                    
                                    # dump header for API
                                    #formatted = ''
                                    #for field in header:
                                    #    formatted = formatted + "\'%s\'," % (field)
                                    #logging.debug('[%s]' % (formatted))
                            else:
                                remainBuff = packages[i]
                                break
            except socket.error:
                pass
            except Exception,e:
                print e
            time.sleep(0.1)

def main():
    pass
    

if __name__ == '__main__':
    main()
    