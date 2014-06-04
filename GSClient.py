#-*- coding: UTF-8 -*-

import os
import sys
import socket
import ctypes
import ConfigParser
import logging
from datetime import datetime

from GSAPI import *

class GSClient:

    gsApi = None

    def __init__(self):
        logging.basicConfig(filename='log.txt',level=logging.DEBUG)
        
        self.cf = ConfigParser.ConfigParser()
        self.cf.read('GSCfg.ini')
        
        self.serverIp = self.cf.get('GSCLIENT','IP')
        self.port = int(self.cf.get('GSCLIENT','PORT'))
      
        self.gsApi = GSAPI()
        
    def SendAndRecv(self, buff):
        chunk = None

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.settimeout(5)
            self.s.connect((self.serverIp, self.port))
            self.s.send(buff)
            logging.debug('[%s][SEND]:%s' % (datetime.now(), buff))

            chunk = self.s.recv(2048)
            if chunk:
                length = int(chunk[8:16])
                logging.debug('[%s][RECV]:MsgBodyLen=%d Len=%d Raw:%s' % (datetime.now(), length, len(chunk), chunk))
            else:
                logging.debug('None Response')
            self.s.close()
        except socket.timeout:
            print 'Socket Timeout'
            
        return chunk
        
    def Subscribe(self,asset,stocks):
        chunk = self.SendAndRecv(self.gsApi.Subscribe(asset,stocks))
        if not chunk:
            return
            
        sessionId, errorCode, errorMsg = self.gsApi.GetResponseHeader(chunk)
        
        print errorMsg
        
        if errorCode:
            print errorCode
            
    def UnSubscribeAll(self):
        chunk = self.SendAndRecv(self.gsApi.UnSubscribeAll())
        if not chunk:
            return
            
        sessionId, errorCode, errorMsg = self.gsApi.GetResponseHeader(chunk)
        
        print errorMsg
        
        if errorCode:
            print errorCode

    def Logon(self):
        chunk = self.SendAndRecv(self.gsApi.Logon())
        if not chunk:
            return
            
        sessionId, errorCode, errorMsg = self.gsApi.GetResponseHeader(chunk)
        
        if errorCode:
            print errorMsg
            return False
        else:
            self.gsApi.SESSIONID = sessionId
            return True

    def QueryMoney(self):
        chunk = self.SendAndRecv(self.gsApi.QueryMoney())
        if not chunk:
            return
        
        sessionId, errorCode, errorMsg = self.gsApi.GetResponseHeader(chunk)

        if errorCode:
            print errorMsg
        else:
            (cols, rows, body) = self.gsApi.GetResponseBody(chunk)
            records = []
            for idx in range(1, rows+1):
                record = body[cols*idx:cols*(idx+1)-1]
                #print '资金余额:%s' % (record[4])
                #print '资金可用金额:%s' % (record[5])
                #print '资产总值:%s' % (record[6])
                #print '资产资产:%s' % (record[7])
                #print '市值:%s' % (record[8])
                records.append(record)
            return records

    def QueryShareHolder(self):
        chunk = self.SendAndRecv(self.gsApi.QueryShareHolder())
        if not chunk:
            return
        
        sessionId, errorCode, errorMsg = self.gsApi.GetResponseHeader(chunk)

        if errorCode:
            print errorMsg
        else:
            (cols, rows, body) = self.gsApi.GetResponseBody(chunk)
            for idx in range(1, rows+1):
                record = body[cols*idx:cols*(idx+1)-1]
                print '客户代码:%s' % (record[self.gsApi.Msg_Query_ShareHolder_Response.index('custid')])

    def QueryCash(self):
        chunk = self.SendAndRecv(self.gsApi.QueryCash())
        if not chunk:
            return
        
        sessionId, errorCode, errorMsg = self.gsApi.GetResponseHeader(chunk)

        if errorCode:
            print errorMsg
        else:
            (cols, rows, body) = self.gsApi.GetResponseBody(chunk)
            for idx in range(1, rows+1):
                record = body[cols*idx:cols*(idx+1)-1]
                print record

def main():
    pass
    

if __name__ == '__main__':
    main()
    