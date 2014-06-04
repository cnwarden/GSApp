#-*- coding: UTF-8 -*-

import os
import sys
import socket
import ctypes
import ConfigParser
import logging
from datetime import datetime

#110000000572
#135790

class GSAPI:

    F_CUSTID = ''
    CUSTID = ''
    FUNDID = ''
    ORGID = ''
    PASSWORD = ''
    SESSIONID = ''

    Msg_EstablishChannel = ('FUNCID','CUSTID')
    Msg_Subscribe = ('FUNCID', 'CUSTID', 'SUBJECTTYPE', 'SUBJECT', 'IDENTIFYCODE', 'PARAMETER', 'STRATEGY')
    Msg_Logon = ('SESSIONID','FUNCID','g_serverid','g_funcid','g_operid','g_operpwd','g_operway','g_stationaddr','g_checksno','fundid','tranpwd')
    Msg_Query_Money = ('SESSIONID','FUNCID','g_serverid','g_funcid','g_operid','g_operpwd','g_operway','g_stationaddr','g_checksno','custid','orgid','fundid','moneytype','mvflag')
    Msg_Query_ShareHolder = ('SESSIONID','FUNCID','g_serverid','g_funcid','g_operid','g_operpwd','g_operway','g_stationaddr','g_checksno','custid','orgid','fundid','market','secuid','count','posstr')
    Msg_Query_Cash = ('SESSIONID','FUNCID','g_serverid','g_funcid','g_operid','g_operpwd','g_operway','g_stationaddr','g_checksno','custid','orgid','strdate','enddate','fundid','count','posstr','moneytype','creditid','creditflag')
    Msg_Sep = chr(1)
    Msg_Header = 'GXFIXSTD'

    Msg_Response = ('FUNCID','RESULTSIZE','SESSIONID','RETCODE','RETMESSAGE')
    Msg_Query_Money_Response = []
    Msg_Query_ShareHolder_Response = ('posstr','custid','market','secuid','name','secuseq','regflag')
    
    
    Msg_RealTime_Response = ('STAMP','SEQNUM','QUOTETIME','IDENTIFYCODE','LEVEL2','TYPE','STATUS','MARKET','CODE','NAME','PRECLOSE','OPEN','SUM','AMOUNT','HIGH','LOW','NEW','IOPV','DIOPV','DIOPVS1','DIOPVB1','UPPERLIMITPRICE','LOWERLIMITPRICE','OPENINTEREST','PREOPENINTEREST','PRESETTLEPRICE','SETTLEPRICE','PREDELTA','DELTA','BP1','BA1','SP1','SA1','BP2','BA2','SP2','SA2','BP3','BA3','SP3','SA3','BP4','BA4','SP4','SA4','BP5','BA5','SP5','SA5','BP6','BA6','SP6','SA6','BP7','BA7','SP7','SA7','BP8','BA8','SP8','SA8','BP9','BA9','SP9','SA9','BP10','BA10','SP10','SA10')

    def __init__(self):
        self.LoadCfg('GSCfg.ini')
        self.dll = ctypes.cdll.LoadLibrary( 'KDEncodeCli.dll' )
        
    def LoadCfg(self, cfgFile):
        self.cf = ConfigParser.ConfigParser()
        self.cf.read(cfgFile)
        
        self.CUSTID = self.cf.get('GSAPI','CUSTID')
        self.FUNDID = self.cf.get('GSAPI','FUNDID')
        self.ORGID = self.cf.get('GSAPI','ORGID')
        self.F_CUSTID = self.cf.get('GSAPI','F_CUSTID')
        self.PASSWORD = self.cf.get('GSAPI','PASSWORD')
        
    def __create_raw_package(self, header, content):
        self.buff = str(len(header)) + self.Msg_Sep + str(1) + self.Msg_Sep
        self.buff = self.buff + self.Msg_Sep.join(header) + self.Msg_Sep
        self.buff = self.buff + self.Msg_Sep.join(content) + self.Msg_Sep
        self.buff = self.Msg_Header + '%08d' % (len(self.buff)) + self.buff
        return self.buff

    def EstablishChannel(self):
        Msg_EstablishChannel_Body = ('ESTABLISHCHANNEL', self.CUSTID)
        return self.__create_raw_package(self.Msg_EstablishChannel, Msg_EstablishChannel_Body)

    def Subscribe(self,asset,stocks):
        Msg_Subscribe_Body = ('SUBSCRIBE', self.CUSTID, asset, stocks, '' ,'', 'TERM=-1,TIMES=-1,INTERVAL=3')
        return self.__create_raw_package(self.Msg_Subscribe, Msg_Subscribe_Body)
        
    def UnSubscribeAll(self):
        Msg_Subscribe_Body = ('UNSUBSCRIBEALL', self.CUSTID, '', '', '' ,'', '')
        return self.__create_raw_package(self.Msg_Subscribe, Msg_Subscribe_Body)

    #short link
    def Logon(self):
        Msg_Logon_Body = ['','420301','','420301','','','','','',self.FUNDID,self.PASSWORD]

        #encode password
        encodedStr = ' ' * 32
        pPwd = ctypes.c_char_p()
        pPwd.value = Msg_Logon_Body[10]
        pKey = ctypes.c_char_p()
        pKey.value = Msg_Logon_Body[9]

        pStr = ctypes.c_char_p()
        pStr.value = encodedStr
        pVoid = ctypes.cast(pStr, ctypes.c_void_p).value
        self.dll.KDEncode(6, pPwd, len(Msg_Logon_Body[10]), pVoid, 32, pKey, len(Msg_Logon_Body[9]))
        Msg_Logon_Body[10] = encodedStr

        return self.__create_raw_package(self.Msg_Logon, Msg_Logon_Body)

    def QueryMoney(self):
        Msg_Query_Money_Body = (self.SESSIONID, '440206', '', '440206', '' ,'', '', '', '', self.CUSTID, self.ORGID, self.FUNDID, '', '')
        return self.__create_raw_package(self.Msg_Query_Money, Msg_Query_Money_Body)

    def QueryShareHolder(self):
        Msg_Query_ShareHolder_Body = (self.SESSIONID, '440207', '', '440207', '' ,'', '', '', '', self.CUSTID, self.ORGID, self.FUNDID, '', '', '10', '')
        return self.__create_raw_package(self.Msg_Query_ShareHolder, Msg_Query_ShareHolder_Body)
    
    def QueryCash(self):
        Msg_Query_Cash_Body = (self.SESSIONID, '440210', '', '440210', '' ,'', '', '', '', self.CUSTID, self.ORGID, '20130101', '20140530', self.FUNDID, '10', '', '', '', '')
        return self.__create_raw_package(self.Msg_Query_Cash, Msg_Query_Cash_Body)
        
    def GetResponseHeader(self, buffer):
        length = int(buffer[8:16])
        buff = buffer[16:16+length].split(chr(1))
        #5 col 1 row
        del buff[0]
        del buff[0]
        header = buff[5*1: 5*1+5]
        sessionId = header[2]
        errorCode = int(header[3])
        errorMsg = header[4]
        return sessionId, errorCode, errorMsg
        
    def GetResponseBody(self, buffer):
        length = int(buffer[8:16])
        buff = buffer[16:16+length].split(chr(1))
        #5 col 1 row
        del buff[0]
        del buff[0]
        body = buff[5*1+5:]
        return (int(body[0]),int(body[1]),body[2:])
        
    def GetResponseHeader_DataLine(self, buffer):
        length = int(buffer[8:16])
        buff = buffer[16:16+length].split(chr(1))
        #7 col 1 row
        del buff[0]
        del buff[0]
        body = buff[7*1: 7*1+7]
        errorCode = int(body[3])
        errorMsg = body[4]
        return errorCode,errorMsg

    def GetResponseBody_DataLine(self, buffer):
        length = int(buffer[8:16])
        buff = buffer[16:16+length].split(chr(1))
        #7 col 1 row
        del buff[0]
        del buff[0]
        body = buff[7*1+7:]
        col = int(body[0])
        row = int(body[1])

        records = []
        for i in range(1,row+1):
            record = body[2+col*i:2+col*(i+1)]
            records.append(record)
            
        return col,row,body[2:2+col],records
        
def main():
    pass
    

if __name__ == '__main__':
    main()