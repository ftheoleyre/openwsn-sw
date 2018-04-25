# Copyright (c) 2018, CNRS.
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License

import logging
log = logging.getLogger('ParserStat')
log.setLevel(logging.INFO)
log.addHandler(logging.NullHandler())

import struct

from pydispatch import dispatcher

from ParserException import ParserException
import Parser

from array import array

class ParserStat(Parser.Parser):
    
    HEADER_LENGTH  = 2
    MSPERSLOT      = 15 #ms per slot.
   
    #type of stat message 
    SERTYPE_PKT_TX             = 1
    SERTYPE_PKT_RX             = 2
    SERTYPE_CELL               = 3
    SERTYPE_ACK                = 4
    SERTYPE_DIO                = 5
    SERTYPE_DAO                = 6
    SERTYPE_NODESTATE          = 7
    SERTYPE_6PCMD              = 8


 
    def __init__(self):
        
        # log
        log.debug('create ParserStat instance')

        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)
        
        self._asn= ['asn_4',           # B
          'asn_2_3',                   # H
          'asn_0_1',                   # H
         ]


       

    
    #======================== public ==========================================
    
    #======================== conversion ==========================================
    
 
 #returns a string with the decimal value of a uint16_t
    def BytesToString(self, bytes):
        str = ''
        i = 0

        #print bytes

        for byte in bytes:
            str = format(eval('{0} + {1} * 256 ** {2}'.format(str, byte, i)))
            #print ('{0}:{1}'.format(i, str)) 
            i = i + 1      

        return(str)

    def BytesToAddr(self, bytes):
        str = ''
        i = 0

        for byte in bytes:
            str = str + '{:02x}'.format(byte) 
            #if (i < len(bytes)-1):
            #    str = str + '-'
            i += 1

        return(str)

    def ByteToCellMode(self, byte):
        CELLMODE = {
            'ADD' : 1,
            'DEL' : 2
        }
        for key, value in CELLMODE.iteritems():
            if value == byte:
                return(key)
        return("UNKNOWN")
    
    
    def ByteToCellType(self, byte):
        CELLTYPE = {
            'OFF'              : 0,
            'TX'               : 1,
            'RX'               : 2,
            'TXRX'             : 3,
            'SERIALRX'         : 4,
            'MORESERIALRX'     : 5
        }
        for key, value in CELLTYPE.iteritems():
            if value == byte:
                return(key)
        return("UNKNOWN")




    def ByteToSixtopCode(self, byte):
        SIXTOPCODE = {
            'CELLADD_REQ'   : 1,
            'CELLADD_REP'   : 2,
            'CELLDEL_REQ'   : 3,
            'CELLDEL_REP'   : 4,
            'CELLLIST_REP'  : 5,
            'CELLLIST_REQ'  : 6,
            'CELLCLEAR_REP' : 7,
            'CELLCLEAR_REQ' : 8,
            'CELLCOUNT_REP' : 9,
            'CELLCOUNT_REQ' : 10
        } 

        for key, value in SIXTOPCODE.iteritems():
            if value == byte:
                return(key)
        return("UNKNOWN")


    def ByteToStatus(self, byte):
        CODE = {
             'ENQUEUED'  : 1,
             'TXED'      : 2,
             'RCVD'      : 3,
             'FAILED'    : 4
        } 

        for key, value in CODE.iteritems():
            if value == byte:
                return(key)
        return("UNKNOWN")


    def ByteToL4protocol(self, byte):
       
        IANA = {
        'IANA_IPv6HOPOPT'                     : 0x00,
        'IANA_TCP'                            : 0x06,
        'IANA_UDP'                            : 0x11,
        'IANA_IPv6ROUTE'                      : 0x2b,
        'IANA_ICMPv6'                         : 0x3a,
        'IANA_ICMPv6_ECHO_REQUEST'            :  128,
        'IANA_ICMPv6_ECHO_REPLY'              :  129,
        'IANA_ICMPv6_RS'                      :  133,
        'IANA_ICMPv6_RA'                      :  134,
        'IANA_ICMPv6_RA_PREFIX_INFORMATION'   :    3,
        'IANA_ICMPv6_RPL'                     :  155,
        'IANA_ICMPv6_RPL_DIO'                 : 0x01,
        'IANA_ICMPv6_RPL_DAO'                 : 0x02,
        'IANA_RSVP'                           :   46,
        'IANA_UNDEFINED'                      :  250
        } 

        for key, value in IANA.iteritems():
            if value == byte:
                return(key)
        return("IANA_UNKNOWN")

    def ByteToFrameType(self, byte):
        IEEE154_TYPE = {
        'IEEE154_TYPE_BEACON'                 : 0,
        'IEEE154_TYPE_DATA'                   : 1,
        'IEEE154_TYPE_ACK'                    : 2,
        'IEEE154_TYPE_CMD'                    : 3,
        'IEEE154_TYPE_UNDEFINED'              : 5
        }
 
        for key, value in IEEE154_TYPE.iteritems():
            if value == byte:
                return(key)
        return("FTYPE_UNKNOWN")


    def ByteToUDPPort(self, bytes):
        
        result = eval(self.BytesToString(bytes))        

        WKP = {
        'WKP_TCP_HTTP'                        :    80,
        'WKP_TCP_ECHO'                        :     7,
        'WKP_UDP_COAP'                        :  5683,
        'WKP_UDP_ECHO'                        :     7,
        'WKP_UDP_RINGMASTER'                  : 15000
        }

        for key, value in WKP.iteritems():
            if value == result:
                return(key)
        return("WKP_UNKNOWN")

    def BytesToCells(selfself, bytes):
        result = ''
        num = 0
        
        for i in range(0, len(bytes) / 5) :
            if (bytes[5*i] == 1):                
                result = result + format('choffset[{0}]={1}|slotoffset[{0}]={2}|'.format(
                    num,
                    bytes[5*i+1],
                    bytes[5*i+3]
                    ))
                num = num + 1
        return(result)

    #======================== write logs (factroized) ==========================================
 
       #info to write when a packet is transmitted
    def LogPktTx(self, addr, asnbytes, input, message):
        log.info('{0}|addr={1}|asn={2}|length={3}|frameType={4}|slotOffset={5}|frequency={6}|txpower={7}|numTxAttempts={8}|l2Dest={9}|L3Src={10}|L3Dest={11}|'.format(
            message,
            self.BytesToAddr(addr),
            self.BytesToString(asnbytes),
            input[8],
            self.ByteToFrameType(input[9]),
            self.BytesToString(input[10:12]),
            input[12],
            input[13],
            input[14],
            self.BytesToAddr(input[15:23]),
            self.BytesToAddr(input[23:39]),
            self.BytesToAddr(input[39:55]),
            ));


    #info to write when a packet is received
    def LogPktRx(self, addr, asnbytes, input, message):
        log.info('{0}|addr={1}|asn={2}|length={3}|frameType={4}|slotOffset={5}|frequency={5}|l2Src={6}|rssi={7}|lqi={8}|crc={9}'.format(
            message,
            self.BytesToAddr(addr),
            self.BytesToString(asnbytes),
            input[8],
            self.ByteToFrameType(input[9]),
            self.BytesToString(input[10:12]),
            input[12],
            self.BytesToAddr(input[13:21]),
            input[21],
            input[22],
            input[23],
            ));



   #======================== parses and writes the logs  ==========================================
 
    def parseInput(self,input):
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug('received stat {0}'.format(input))
                  
        #headers
        addr = input[0:2]
        asnbytes = input[2:7]  
        (self._asn) = struct.unpack('<BHH',''.join([chr(c) for c in asnbytes])) 
        statType = input[7]
        
        #depends on the stat-type
        if (statType == self.SERTYPE_PKT_TX):
            self.LogPktTx(addr, asnbytes, input, "STAT_PK_TX");

        elif (statType == self.SERTYPE_PKT_RX):
            self.LogPktRx(addr, asnbytes, input, "STAT_PK_RX");


        elif (statType == self.SERTYPE_CELL):
            log.info('STAT_CELL|addr={0}|asn={1}|command={2}|celltype={3}|shared={4}|slotOffset={5}|channelOffset={6}|neighbor={7}'.format(
                self.BytesToAddr(addr),
                self.BytesToString(asnbytes),
                self.ByteToCellMode(input[8]),
                self.ByteToCellType(input[9]),
                input[10],
                input[11],
                input[12],
                self.BytesToAddr(input[13:21])
                ));       
        elif (statType == self.SERTYPE_ACK):
            log.info('STAT_ACK|addr={0}|asn={1}|status={2}|l2addr={3}'.format(
                self.BytesToAddr(addr),
                self.BytesToString(asnbytes),
                self.ByteToStatus(input[8]),
                self.BytesToAddr(input[9:17])
                ));

        elif (statType == self.SERTYPE_DIO):
            log.info('STAT_DIO|addr={0}|asn={1}|status={2}|rplinstanceId={3}|rank={4}|DODAGID={5}'.format(
                self.BytesToAddr(addr),
                 self.BytesToString(asnbytes),
                self.ByteToStatus(input[8]),
                input[9],
                self.BytesToString(input[10:12]),
                self.BytesToAddr(input[12:28])               
                ));

        elif (statType == self.SERTYPE_DAO):
            log.info('STAT_DAO|addr={0}|asn={1}|status={2}|parent={3}|DODAGID={4}'.format(
                self.BytesToAddr(addr),
                self.BytesToString(asnbytes),
                self.ByteToStatus(input[8]),
                self.BytesToAddr(input[9:17]),
                self.BytesToAddr(input[17:33])               
                ));
                
        elif (statType == self.SERTYPE_NODESTATE):
            
            TicsOn = struct.unpack('<I',''.join([chr(c) for c in input[8:12]]))[0]
            TicsTotal = struct.unpack('<I',''.join([chr(c) for c in input[12:16]]))[0]
            if (TicsTotal > 0):
                dcr = float(TicsOn) / float(TicsTotal) * 100
            else:
                dcr = 100                
                
            log.info('STAT_NODESTATE|addr={0}|asn={1}|DutyCycleRatio={2}|NumDeSync={3}'.format(
                self.BytesToAddr(addr),
                self.BytesToString(asnbytes),
                dcr,
                input[16]
                ));

        elif (statType == self.SERTYPE_6PCMD):
            log.info('STAT_6PCMD|addr={0}|asn={1}|command={2}|status={3}|neigh={4}|{5}'.format(
                self.BytesToAddr(addr),
                self.BytesToString(asnbytes),
                self.ByteToSixtopCode(input[8]),
                self.ByteToStatus(input[9]),
                self.BytesToAddr(input[10:18]),
                self.BytesToCells(input[18:])       
                ));
        

        else:
            print('Unknown stat type: type {0} addr {1} asn {2}'.format(
                statType, 
                self.BytesToAddr(addr), 
                self.BytesToString(asnbytes)))
 
       
        return ('error', input)



 #======================== private =========================================
 
  
