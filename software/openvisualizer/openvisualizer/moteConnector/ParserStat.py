# Copyright (c) 2015, CNRS.
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

from DataBase import DataBase
from Graphs import Graphs

class ParserStat(Parser.Parser):

    HEADER_LENGTH  = 2
    MSPERSLOT      = 15 #ms per slot.

    # STATS
    SERTYPE_DATA_GENERATION    = 1
    SERTYPE_DATA_RX            = 2
    SERTYPE_PKT_TX             = 3
    SERTYPE_PKT_RX             = 4
    SERTYPE_CELL_ADD           = 5
    SERTYPE_CELL_REMOVE        = 6
    SERTYPE_ACK_TX             = 7
    SERTYPE_ACK_RX             = 8
    SERTYPE_PKT_TIMEOUT        = 9
    SERTYPE_PKT_ERROR          = 10
    SERTYPE_PKT_BUFFEROVERFLOW = 11
    SERTYPE_DIOTX              = 12
    SERTYPE_DAOTX              = 13
    SERTYPE_NODESTATE          = 14
    SERTYPE_6PSTATE            = 15

    def __init__(self, expid):

        self.expid = expid

        # log
        log.debug('create ParserStat instance')

        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)

        self._asn= ['asn_4',           # B
          'asn_2_3',                   # H
          'asn_0_1',                   # H
         ]

        # def db
        self.dbo = DataBase(self.expid)
        self.dbo.reinit()

        # def graphs
        self.gr = Graphs(self.expid)

    #======================== public ==========================================

    #======================== conversion ==========================================


 #returns a string with the decimal value of a uint16_t
    def BytesToInt(self, bytes):
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

    def ByteToBool(self, bytes):
        if (int(bytes) == 1):
            return 'true'
        else:
            return 'false'


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

    def ByteToCompType(self, byte):
        COMP_TYPE = {
        'COMPONENT_NULL'                      : 0x00,
        'COMPONENT_OPENWSN'                   : 0x01,
        #cross-layers
        'COMPONENT_IDMANAGER'                 : 0x02,
        'COMPONENT_OPENQUEUE'                 : 0x03,
        'COMPONENT_OPENSERIAL'                : 0x04,
        'COMPONENT_PACKETFUNCTIONS'           : 0x05,
        'COMPONENT_RANDOM'                    : 0x06,
        #PHY
        'COMPONENT_RADIO'                     : 0x07,
        #MAClow
        'COMPONENT_IEEE802154'                : 0x08,
        'COMPONENT_IEEE802154E'               : 0x09,

        #MAClow<->MAChigh ("virtual components")
        'COMPONENT_SIXTOP_TO_IEEE802154E'     : 0x0a,
        'COMPONENT_IEEE802154E_TO_SIXTOP'     : 0x0b,
        #MAChigh
        'COMPONENT_SIXTOP'                    : 0x0c,
        'COMPONENT_NEIGHBORS'                 : 0x0d,
        'COMPONENT_SCHEDULE'                  : 0x0e,
        'COMPONENT_SIXTOP_RES'                : 0x0f,
        #IPHC
        'COMPONENT_OPENBRIDGE'                : 0x10,
        'COMPONENT_IPHC'                      : 0x11,
        #IPv6
        'COMPONENT_FORWARDING'                : 0x12,
        'COMPONENT_ICMPv6'                    : 0x13,
        'COMPONENT_ICMPv6ECHO'                : 0x14,
        'COMPONENT_ICMPv6ROUTER'              : 0x15,
        'COMPONENT_ICMPv6RPL'                 : 0x16,
        #TRAN
        'COMPONENT_OPENTCP'                   : 0x17,
        'COMPONENT_OPENUDP'                   : 0x18,
        'COMPONENT_OPENCOAP'                  : 0x19,
        #applications
        'COMPONENT_C6T'                       : 0x1a,
        'COMPONENT_CEXAMPLE'                  : 0x1b,
        'COMPONENT_CINFO'                     : 0x1c,
        'COMPONENT_CLEDS'                     : 0x1d,
        'COMPONENT_CSENSORS'                  : 0x1e,
        'COMPONENT_CSTORM'                    : 0x1f,
        'COMPONENT_CWELLKNOWN'                : 0x20,
        'COMPONENT_TECHO'                     : 0x21,
        'COMPONENT_TOHLONE'                   : 0x22,
        'COMPONENT_UECHO'                     : 0x23,
        'COMPONENT_UINJECT'                   : 0x24,
        'COMPONENT_RRT'                       : 0x25,
        'COMPONENT_SECURITY'                  : 0x26
        }

        for key, value in COMP_TYPE.iteritems():
            if value == byte:
                return(key)
        return("CMPYPE_UNKNOWN")


    def ByteToUDPPort(self, bytes):

        result = eval(self.BytesToInt(bytes))

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



    #======================== write logs (factroized) ==========================================

       #info to write when a packet is transmitted
    def LogPktTx(self, addr, mycomponent, asnbytes, statType, input, code):
        log.info('{14}|addr={0}|comp={1}|asn={2}|statType={3}|trackinstance={4}|trackowner={5}|length={6}|frameType={7}|slotOffset={8}|frequency={9}|l2Dest={10}|txpower={11}|numTxAttempts={12}|queuePos={13}'.format(
            self.BytesToAddr(addr),
            self.ByteToCompType(mycomponent),
            self.BytesToInt(asnbytes),
            statType,
            self.BytesToInt(input[9:11]),
            self.BytesToAddr(input[11:19]),
            input[19],
            self.ByteToFrameType(input[20]),
            self.BytesToInt(input[21:23]),
            input[23],
            self.BytesToAddr(input[24:32]),
            input[32],
            input[33],
            input[34],
            code
            ));

    #info to write when a packet is received
    def LogPktRx(self, addr, mycomponent, asnbytes, statType, input, code):
      log.info('{15}|addr={0}|comp={1}|asn={2}|statType={3}|trackinstance={4}|trackowner={5}|length={6}|frameType={7}|slotOffset={8}|frequency={9}|l2Src={10}|rssi={11}|lqi={12}|crc={13}|queuePos={14}'.format(
            self.BytesToAddr(addr),
            self.ByteToCompType(mycomponent),
            self.BytesToInt(asnbytes),
            statType,
            self.BytesToInt(input[9:11]),
            self.BytesToAddr(input[11:19]),
            input[19],
            self.ByteToFrameType(input[20]),
            self.BytesToInt(input[21:23]),
            input[23],
            self.BytesToAddr(input[24:32]),
            input[32],
            input[33],
            input[34],
            input[35],
            code
            ));



   #======================== parses and writes the logs  ==========================================

    def parseInput(self,input):

        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug('received stat {0}'.format(input))



        #headers
        addr = input[0:2]
        mycomponent = input[2]
        asnbytes = input[3:8]
        (self._asn) = struct.unpack('<BHH',''.join([chr(c) for c in asnbytes]))
        statType = input[8]

        #depends on the stat-type
        if (statType == self.SERTYPE_DATA_GENERATION):
            log.info('STAT_DATAGEN|addr={0}|comp={1}|asn={2}|statType={3}|trackinstance={4}|trackowner={5}|seqnum={6}|l2Src={7}|l2Dest={8}|queuePos={9}'.format(
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                self.BytesToInt(asnbytes),
                statType,
                self.BytesToInt(input[9:11]),
                self.BytesToAddr(input[11:19]),
                self.BytesToInt(input[19:23]),
                self.BytesToAddr(input[23:31]),
                self.BytesToAddr(input[31:39]),
                input[39]
                ))

            self.dbo.Store(self.SERTYPE_DATA_GENERATION,[
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                int(self.BytesToInt(asnbytes)),
                int(self.BytesToInt(input[9:11])),
                self.BytesToAddr(input[11:19]),
                int(self.BytesToInt(input[19:23])),
                self.BytesToAddr(input[23:31]),
                self.BytesToAddr(input[31:39])
            ])

        elif (statType == self.SERTYPE_DATA_RX):
            log.info('STAT_DATARX|addr={0}|comp={1}|asn={2}|statType={3}|trackinstance={4}|trackowner={5}|seqnum={6}|l2Src={7}|l2Dest={8}'.format(
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                self.BytesToInt(asnbytes),
                statType,
                self.BytesToInt(input[9:11]),
                self.BytesToAddr(input[11:19]),
                self.BytesToInt(input[19:23]),
                self.BytesToAddr(input[23:31]),
                self.BytesToAddr(input[31:39])
                ))


            self.dbo.Store(self.SERTYPE_DATA_RX,[
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                int(self.BytesToInt(asnbytes)),
                int(self.BytesToInt(input[9:11])),
                self.BytesToAddr(input[11:19]),
                int(self.BytesToInt(input[19:23])),
                self.BytesToAddr(input[23:31]),
                self.BytesToAddr(input[31:39])
            ])

            print("OK")
            self.dbo.update_pdr()
            self.gr.pdr()

        elif (statType == self.SERTYPE_PKT_TX):
            self.LogPktTx(addr, self.ByteToCompType(mycomponent), asnbytes, statType, input, "STAT_PK_TX");

            self.dbo.Store(self.SERTYPE_PKT_TX,[
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                self.BytesToInt(asnbytes),
                int(self.BytesToInt(input[9:11])), # trackinstance
                self.BytesToAddr(input[11:19]), # trackowner
                int(input[19]), # length
                self.ByteToFrameType(input[20]), # type
                int(self.BytesToInt(input[21:23])), # SlotOffset
                int(input[23]), # frequency
                self.BytesToAddr(input[24:32]), # l2Dest
                int(input[32]), # txPower
                int(input[33]) # numTxAttempts
            ])

        elif (statType == self.SERTYPE_PKT_RX):
            self.LogPktRx(addr, self.ByteToCompType(mycomponent), asnbytes, statType, input, "STAT_PK_RX");

            self.dbo.Store(self.SERTYPE_PKT_RX,[
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                self.BytesToInt(asnbytes),
                int(self.BytesToInt(input[9:11])), # trackinstance
                self.BytesToAddr(input[11:19]), # trackowner
                int(input[19]), # length
                self.ByteToFrameType(input[20]), # type
                int(self.BytesToInt(input[21:23])), # SlotOffset
                int(input[23]), # frequency
                self.BytesToAddr(input[24:32]), # l2Src
                int(input[32]), # rssi
                int(input[33]), # lqi
                self.ByteToBool(input[34]) # crc
            ])

        elif (statType == self.SERTYPE_CELL_ADD):
            log.info('STAT_CELL_ADD|addr={0}|comp={1}|asn={2}|statType={3}|trackinstance={4}|trackowner={5}|slotOffset={6}|type={7}|shared={8}|channelOffset={9}|neighbor={10}'.format(
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                self.BytesToInt(asnbytes),
                statType,
                self.BytesToInt(input[9:11]),
                self.BytesToAddr(input[11:19]),
                input[19],
                input[20],
                input[21],
                input[22],
                self.BytesToAddr(input[23:31])
                ))

            self.dbo.Store(self.SERTYPE_CELL_ADD,[
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                int(self.BytesToInt(asnbytes)),
                int(self.BytesToInt(input[9:11])),
                self.BytesToAddr(input[11:19]),
                int(input[19]),
                int(input[20]),
                int(input[21]),
                int(input[22]),
                self.BytesToAddr(input[23:31])
            ])

        elif (statType == self.SERTYPE_CELL_REMOVE):
            log.info('STAT_CELL_REMOVE|addr={0}|comp={1}|asn={2}|statType={3}|trackinstance={4}|trackowner={5}|slotOffset={6}|type={7}|shared={8}|channelOffset={9}|neighbor={10}'.format(
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                self.BytesToInt(asnbytes),
                statType,
                self.BytesToInt(input[9:11]),
                self.BytesToAddr(input[11:19]),
                input[19],
                input[20],
                input[21],
                input[22],
                self.BytesToAddr(input[23:31])
            	))

            self.dbo.Store(self.SERTYPE_CELL_REMOVE,[
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                int(self.BytesToInt(asnbytes)),
                int(self.BytesToInt(input[9:11])),
                self.BytesToAddr(input[11:19]),
                int(input[19]),
                int(input[20]),
                int(input[21]),
                int(input[22]),
                self.BytesToAddr(input[23:31])
            ])

        elif (statType == self.SERTYPE_ACK_TX):
            log.info('STAT_ACK_TX|addr={0}|comp={1}|asn={2}|statType={3}'.format(
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                self.BytesToInt(asnbytes),
                statType
                ))

            self.dbo.Store(self.SERTYPE_ACK_TX,[
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                int(self.BytesToInt(asnbytes))
            ])

        elif (statType == self.SERTYPE_ACK_RX):
            log.info('STAT_ACK_RX|addr={0}|comp={1}|asn={2}|statType={3}'.format(
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                int(self.BytesToInt(asnbytes)),
                int(statType)
                ))

            self.dbo.Store(self.SERTYPE_ACK_RX,[
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                int(self.BytesToInt(asnbytes))
            ])

        elif (statType == self.SERTYPE_PKT_TIMEOUT):
           self.LogPktTx(addr, self.ByteToCompType(mycomponent), asnbytes, statType, input, "STAT_PK_TIMEOUT");

           self.dbo.Store(self.SERTYPE_PKT_TIMEOUT,[
               self.BytesToAddr(addr),
               self.ByteToCompType(mycomponent),
               self.BytesToInt(asnbytes),
               int(self.BytesToInt(input[9:11])), # trackinstance
               self.BytesToAddr(input[11:19]), # trackowner
               int(input[19]), # length
               self.ByteToFrameType(input[20]), # type
               int(self.BytesToInt(input[21:23])), # SlotOffset
               int(input[23]), # frequency
               self.BytesToAddr(input[24:32]), # l2Dest
               int(input[32]), # txPower
               int(input[33]) # numTxAttempts
           ])

        elif (statType == self.SERTYPE_PKT_ERROR):
            self.LogPktTx(addr, self.ByteToCompType(mycomponent), asnbytes, statType, input, "STAT_PK_ERROR");

            self.dbo.Store(self.SERTYPE_PKT_ERROR,[
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                self.BytesToInt(asnbytes),
                int(self.BytesToInt(input[9:11])), # trackinstance
                self.BytesToAddr(input[11:19]), # trackowner
                int(input[19]), # length
                self.ByteToFrameType(input[20]), # type
                int(self.BytesToInt(input[21:23])), # SlotOffset
                int(input[23]), # frequency
                self.BytesToAddr(input[24:32]), # l2Dest
                int(input[32]), # txPower
                int(input[33]) # numTxAttempts
            ])

        elif (statType == self.SERTYPE_PKT_BUFFEROVERFLOW):
            self.LogPktRx(addr, self.ByteToCompType(mycomponent), asnbytes, statType, input, "STAT_PK_BUFFEROVERFLOW");

            self.dbo.Store(self.SERTYPE_PKT_BUFFEROVERFLOW,[
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                self.BytesToInt(asnbytes),
                int(self.BytesToInt(input[9:11])), # trackinstance
                self.BytesToAddr(input[11:19]), # trackowner
                int(input[19]), # length
                self.ByteToFrameType(input[20]), # type
                int(self.BytesToInt(input[21:23])), # SlotOffset
                int(input[23]), # frequency
                self.BytesToAddr(input[24:32]), # l2Src
                int(input[32]), # rssi
                int(input[33]), # lqi
                self.ByteToBool(input[34]) # crc
            ])

        elif (statType == self.SERTYPE_DIOTX):
            log.info('STAT_DIOTX|addr={0}|comp={1}|asn={2}|statType={3}|'.format(
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                self.BytesToInt(asnbytes),
                statType
                ))

            self.dbo.Store(self.SERTYPE_DIOTX,[
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                int(self.BytesToInt(asnbytes))
            ])

        elif (statType == self.SERTYPE_DAOTX):
            log.info('STAT_DAOTX|addr={0}|comp={1}|asn={2}|statType={3}|parent={4}'.format(
                self.BytesToAddr(addr),
				self.ByteToCompType(mycomponent),
                self.BytesToInt(asnbytes),
                statType,
                self.BytesToAddr(input[9:17])
                ));

            self.dbo.Store(self.SERTYPE_DAOTX,[
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                int(self.BytesToInt(asnbytes)),
                self.BytesToAddr(input[9:17])
            ])

        elif (statType == self.SERTYPE_NODESTATE):

            TicsOn = struct.unpack('<I',''.join([chr(c) for c in input[9:13]]))[0]
            TicsTotal = struct.unpack('<I',''.join([chr(c) for c in input[13:17]]))[0]
            if (TicsTotal > 0):
                dcr = float(TicsOn) / float(TicsTotal) * 100
            else:
                dcr = 100


            log.info('STAT_NODESTATE|addr={0}|comp={1}|asn={2}|statType={3}|DutyCycleRatio={4}|NumDeSync={5}'.format(
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                self.BytesToInt(asnbytes),
                statType,
                dcr,
                input[17]
                ))

            self.dbo.Store(self.SERTYPE_NODESTATE,[
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                int(self.BytesToInt(asnbytes)),
                double(dcr),
                int(input[17])
            ])

        elif (statType == self.SERTYPE_6PSTATE):
            self.dbo.Store(self.SERTYPE_6PSTATE,[
                self.BytesToAddr(addr),
                self.ByteToCompType(mycomponent),
                int(self.BytesToInt(asnbytes)),
                int(self.BytesToInt(input[9:11])), # trackinstance
                self.BytesToAddr(input[11:19]), # trackowner
                self.BytesToAddr(input[19:27]), # addr
                int(input[27]), # numCells
                # Cell 1
                int(self.BytesToInt(input[28:30])), # slot
                int(self.BytesToInt(input[30:32])), # offset
                int(input[32]), # linkoptions
                # Cell 2
                int(self.BytesToInt(input[33:35])), # slot
                int(self.BytesToInt(input[35:37])), # offset
                int(input[37]), # linkoptions
                # Cell 3
                int(self.BytesToInt(input[38:40])), # slot
                int(self.BytesToInt(input[40:42])), # offset
                int(input[42]) # linkoptions
            ])

        else:
            print('Unknown stat type - component {0}, addr {1} type {2} asn {3}'.format(self.ByteToCompType(mycomponent), self.BytesToAddr(addr), statType, self.BytesToInt(asnbytes)))


        return ('error', input)



 #======================== private =========================================
