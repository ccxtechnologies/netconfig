#!/usr/bin/python
# Copyright: 2017, CCX Technologies

import ctypes
import socket
import fcntl

IFNAMSIZ = 16

# from linux/source/include/uapi/linux/sockios.h

SIOCETHTOOL = 0x8946

# from linux/source/include/uapi/linux/ethtool.h

# CMDs currently supported
ETHTOOL_GSET = 0x00000001  # Get settings.
ETHTOOL_SSET = 0x00000002  # Set settings.
ETHTOOL_GDRVINFO = 0x00000003  # Get driver info.
ETHTOOL_GREGS = 0x00000004  # Get NIC registers.
ETHTOOL_GWOL = 0x00000005  # Get wake-on-lan options.
ETHTOOL_SWOL = 0x00000006  # Set wake-on-lan options.
ETHTOOL_GMSGLVL = 0x00000007  # Get driver message level
ETHTOOL_SMSGLVL = 0x00000008  # Set driver msg level.
ETHTOOL_NWAY_RST = 0x00000009  # Restart autonegotiation.
# Get link status for host, ie whether the interface *and* the
# * physical port (if there is one) are up (ethtool_value).
ETHTOOL_GLINK = 0x0000000a
ETHTOOL_GEEPROM = 0x0000000b  # Get EEPROM data
ETHTOOL_SEEPROM = 0x0000000c  # Set EEPROM data.
ETHTOOL_GCOALESCE = 0x0000000e  # Get coalesce config
ETHTOOL_SCOALESCE = 0x0000000f  # Set coalesce config.
ETHTOOL_GRINGPARAM = 0x00000010  # Get ring parameters
ETHTOOL_SRINGPARAM = 0x00000011  # Set ring parameters.
ETHTOOL_GPAUSEPARAM = 0x00000012  # Get pause parameters
ETHTOOL_SPAUSEPARAM = 0x00000013  # Set pause parameters.
ETHTOOL_GRXCSUM = 0x00000014  # Get RX hw csum enable (ethtool_value)
ETHTOOL_SRXCSUM = 0x00000015  # Set RX hw csum enable (ethtool_value)
ETHTOOL_GTXCSUM = 0x00000016  # Get TX hw csum enable (ethtool_value)
ETHTOOL_STXCSUM = 0x00000017  # Set TX hw csum enable (ethtool_value)
ETHTOOL_GSG = 0x00000018  # Get scatter-gather enable (ethtool_value)
ETHTOOL_SSG = 0x00000019  # Set scatter-gather enable (ethtool_value)
ETHTOOL_TEST = 0x0000001a  # execute NIC self-test.
ETHTOOL_GSTRINGS = 0x0000001b  # get specified string set
ETHTOOL_PHYS_ID = 0x0000001c  # identify the NIC
ETHTOOL_GSTATS = 0x0000001d  # get NIC-specific statistics
ETHTOOL_GTSO = 0x0000001e  # Get TSO enable (ethtool_value)
ETHTOOL_STSO = 0x0000001f  # Set TSO enable (ethtool_value)
ETHTOOL_GPERMADDR = 0x00000020  # Get permanent hardware address
ETHTOOL_GUFO = 0x00000021  # Get UFO enable (ethtool_value)
ETHTOOL_SUFO = 0x00000022  # Set UFO enable (ethtool_value)
ETHTOOL_GGSO = 0x00000023  # Get GSO enable (ethtool_value)
ETHTOOL_SGSO = 0x00000024  # Set GSO enable (ethtool_value)
ETHTOOL_GFLAGS = 0x00000025  # Get flags bitmap(ethtool_value)
ETHTOOL_SFLAGS = 0x00000026  # Set flags bitmap(ethtool_value)
ETHTOOL_GPFLAGS = 0x00000027  # Get driver-private flags bitmap
ETHTOOL_SPFLAGS = 0x00000028  # Set driver-private flags bitmap
ETHTOOL_GRXFH = 0x00000029  # Get RX flow hash configuration
ETHTOOL_SRXFH = 0x0000002a  # Set RX flow hash configuration
ETHTOOL_GGRO = 0x0000002b  # Get GRO enable (ethtool_value)
ETHTOOL_SGRO = 0x0000002c  # Set GRO enable (ethtool_value)
ETHTOOL_GRXRINGS = 0x0000002d  # Get RX rings available for LB
ETHTOOL_GRXCLSRLCNT = 0x0000002e  # Get RX class rule count
ETHTOOL_GRXCLSRULE = 0x0000002f  # Get RX classification rule
ETHTOOL_GRXCLSRLALL = 0x00000030  # Get all RX classification rule
ETHTOOL_SRXCLSRLDEL = 0x00000031  # Delete RX classification rule
ETHTOOL_SRXCLSRLINS = 0x00000032  # Insert RX classification rule
ETHTOOL_FLASHDEV = 0x00000033  # Flash firmware to device
ETHTOOL_RESET = 0x00000034  # Reset hardware
ETHTOOL_SRXNTUPLE = 0x00000035  # Add an n-tuple filter to device
ETHTOOL_GRXNTUPLE = 0x00000036  # deprecated
ETHTOOL_GSSET_INFO = 0x00000037  # Get string set info
ETHTOOL_GRXFHINDIR = 0x00000038  # Get RX flow hash indir'n table
ETHTOOL_SRXFHINDIR = 0x00000039  # Set RX flow hash indir'n table
ETHTOOL_GFEATURES = 0x0000003a  # Get device offload settings
ETHTOOL_SFEATURES = 0x0000003b  # Change device offload settings
ETHTOOL_GCHANNELS = 0x0000003c  # Get no of channels
ETHTOOL_SCHANNELS = 0x0000003d  # Set no of channels
ETHTOOL_SET_DUMP = 0x0000003e  # Set dump settings
ETHTOOL_GET_DUMP_FLAG = 0x0000003f  # Get dump settings
ETHTOOL_GET_DUMP_DATA = 0x00000040  # Get dump data
ETHTOOL_GET_TS_INFO = 0x00000041  # Get time stamping and PHC info
ETHTOOL_GMODULEINFO = 0x00000042  # Get plug-in module information
ETHTOOL_GMODULEEEPROM = 0x00000043  # Get plug-in module EEPROM
ETHTOOL_GEEE = 0x00000044  # Get EEE settings
ETHTOOL_SEEE = 0x00000045  # Set EEE settings
ETHTOOL_GRSSH = 0x00000046  # Get RX flow hash configuration
ETHTOOL_SRSSH = 0x00000047  # Set RX flow hash configuration
ETHTOOL_GTUNABLE = 0x00000048  # Get tunable configuration
ETHTOOL_STUNABLE = 0x00000049  # Set tunable configuration

SUPPORTED_10baseT_Half = (1 << 0)
SUPPORTED_10baseT_Full = (1 << 1)
SUPPORTED_100baseT_Half = (1 << 2)
SUPPORTED_100baseT_Full = (1 << 3)
SUPPORTED_1000baseT_Half = (1 << 4)
SUPPORTED_1000baseT_Full = (1 << 5)
SUPPORTED_Autoneg = (1 << 6)
SUPPORTED_TP = (1 << 7)
SUPPORTED_AUI = (1 << 8)
SUPPORTED_MII = (1 << 9)
SUPPORTED_FIBRE = (1 << 10)
SUPPORTED_BNC = (1 << 11)
SUPPORTED_10000baseT_Full = (1 << 12)
SUPPORTED_Pause = (1 << 13)
SUPPORTED_Asym_Pause = (1 << 14)
SUPPORTED_2500baseX_Full = (1 << 15)
SUPPORTED_Backplane = (1 << 16)
SUPPORTED_1000baseKX_Full = (1 << 17)
SUPPORTED_10000baseKX4_Full = (1 << 18)
SUPPORTED_10000baseKR_Full = (1 << 19)
SUPPORTED_10000baseR_FEC = (1 << 20)
SUPPORTED_20000baseMLD2_Full = (1 << 21)
SUPPORTED_20000baseKR2_Full = (1 << 22)
SUPPORTED_40000baseKR4_Full = (1 << 23)
SUPPORTED_40000baseCR4_Full = (1 << 24)
SUPPORTED_40000baseSR4_Full = (1 << 25)
SUPPORTED_40000baseLR4_Full = (1 << 26)
SUPPORTED_56000baseKR4_Full = (1 << 27)
SUPPORTED_56000baseCR4_Full = (1 << 28)
SUPPORTED_56000baseSR4_Full = (1 << 29)
SUPPORTED_56000baseLR4_Full = (1 << 30)
ADVERTISED_10baseT_Half = (1 << 0)
ADVERTISED_10baseT_Full = (1 << 1)
ADVERTISED_100baseT_Half = (1 << 2)
ADVERTISED_100baseT_Full = (1 << 3)
ADVERTISED_1000baseT_Half = (1 << 4)
ADVERTISED_1000baseT_Full = (1 << 5)
ADVERTISED_Autoneg = (1 << 6)
ADVERTISED_TP = (1 << 7)
ADVERTISED_AUI = (1 << 8)
ADVERTISED_MII = (1 << 9)
ADVERTISED_FIBRE = (1 << 10)
ADVERTISED_BNC = (1 << 11)
ADVERTISED_10000baseT_Full = (1 << 12)
ADVERTISED_Pause = (1 << 13)
ADVERTISED_Asym_Pause = (1 << 14)
ADVERTISED_2500baseX_Full = (1 << 15)
ADVERTISED_Backplane = (1 << 16)
ADVERTISED_1000baseKX_Full = (1 << 17)
ADVERTISED_10000baseKX4_Full = (1 << 18)
ADVERTISED_10000baseKR_Full = (1 << 19)
ADVERTISED_10000baseR_FEC = (1 << 20)
ADVERTISED_20000baseMLD2_Full = (1 << 21)
ADVERTISED_20000baseKR2_Full = (1 << 22)
ADVERTISED_40000baseKR4_Full = (1 << 23)
ADVERTISED_40000baseCR4_Full = (1 << 24)
ADVERTISED_40000baseSR4_Full = (1 << 25)
ADVERTISED_40000baseLR4_Full = (1 << 26)
ADVERTISED_56000baseKR4_Full = (1 << 27)
ADVERTISED_56000baseCR4_Full = (1 << 28)
ADVERTISED_56000baseSR4_Full = (1 << 29)
ADVERTISED_56000baseLR4_Full = (1 << 30)

# The forced speed, 10Mb, 100Mb, gigabit, [2.5|5|10|20|25|40|50|56|100]GbE.
SPEED_10 = 10
SPEED_100 = 100
SPEED_1000 = 1000
SPEED_2500 = 2500
SPEED_5000 = 5000
SPEED_10000 = 10000
SPEED_20000 = 20000
SPEED_25000 = 25000
SPEED_40000 = 40000
SPEED_50000 = 50000
SPEED_56000 = 56000
SPEED_100000 = 100000
SPEED_UNKNOWN = -1

# Duplex, half or full.
DUPLEX_HALF = 0x00
DUPLEX_FULL = 0x01
DUPLEX_UNKNOWN = 0xff

# Which connector port.
PORT_TP = 0x00
PORT_AUI = 0x01
PORT_MII = 0x02
PORT_FIBRE = 0x03
PORT_BNC = 0x04
PORT_DA = 0x05
PORT_NONE = 0xef
PORT_OTHER = 0xff

# Which transceiver to use.
XCVR_INTERNAL = 0x00  # PHY and MAC are in the same package
XCVR_EXTERNAL = 0x01  # PHY and MAC are in different packages
XCVR_DUMMY1 = 0x02
XCVR_DUMMY2 = 0x03
XCVR_DUMMY3 = 0x04

# Enable or disable autonegotiation.
AUTONEG_DISABLE = 0x00
AUTONEG_ENABLE = 0x01

# MDI or MDI-X status/control - if MDI/MDI_X/AUTO is set then
#  the driver is required to renegotiate link

ETH_TP_MDI_INVALID = 0x00  # status: unknown; control: unsupported
ETH_TP_MDI = 0x01  # status: MDI;     control: force MDI
ETH_TP_MDI_X = 0x02  # status: MDI-X;   control: force MDI-X
ETH_TP_MDI_AUTO = 0x03  # control: auto-select

# Wake-On-Lan options.
WAKE_PHY = (1 << 0)
WAKE_UCAST = (1 << 1)
WAKE_MCAST = (1 << 2)
WAKE_BCAST = (1 << 3)
WAKE_ARP = (1 << 4)
WAKE_MAGIC = (1 << 5)
WAKE_MAGICSECURE = (1 << 6)  # only meaningful if WAKE_MAGIC

# L2-L4 network traffic flow types
TCP_V4_FLOW = 0x01  # hash or spec (tcp_ip4_spec)
UDP_V4_FLOW = 0x02  # hash or spec (udp_ip4_spec)
SCTP_V4_FLOW = 0x03  # hash or spec (sctp_ip4_spec)
AH_ESP_V4_FLOW = 0x04  # hash only
TCP_V6_FLOW = 0x05  # hash only
UDP_V6_FLOW = 0x06  # hash only
SCTP_V6_FLOW = 0x07  # hash only
AH_ESP_V6_FLOW = 0x08  # hash only
AH_V4_FLOW = 0x09  # hash or spec (ah_ip4_spec)
ESP_V4_FLOW = 0x0a  # hash or spec (esp_ip4_spec)
AH_V6_FLOW = 0x0b  # hash only
ESP_V6_FLOW = 0x0c  # hash only
IP_USER_FLOW = 0x0d  # spec only (usr_ip4_spec)
IPV4_FLOW = 0x10  # hash only
IPV6_FLOW = 0x11  # hash only
ETHER_FLOW = 0x12  # spec only (ether_spec)
# Flag to enable additional fields in struct ethtool_rx_flow_spec
FLOW_EXT = 0x80000000
FLOW_MAC_EXT = 0x40000000

# L3-L4 network traffic flow hash options
RXH_L2DA = (1 << 1)
RXH_VLAN = (1 << 2)
RXH_L3_PROTO = (1 << 3)
RXH_IP_SRC = (1 << 4)
RXH_IP_DST = (1 << 5)
RXH_L4_B_0_1 = (1 << 6)  # src port in case of TCP/UDP/SCTP
RXH_L4_B_2_3 = (1 << 7)  # dst port in case of TCP/UDP/SCTP
RXH_DISCARD = (1 << 31)

RX_CLS_FLOW_DISC = 0xffffffffffffffff

# Special RX classification rule insert location values
RX_CLS_LOC_SPECIAL = 0x80000000  # flag
RX_CLS_LOC_ANY = 0xffffffff
RX_CLS_LOC_FIRST = 0xfffffffe
RX_CLS_LOC_LAST = 0xfffffffd

# EEPROM Standards for plug in modules
ETH_MODULE_SFF_8079 = 0x1
ETH_MODULE_SFF_8079_LEN = 256
ETH_MODULE_SFF_8472 = 0x2
ETH_MODULE_SFF_8472_LEN = 512
ETH_MODULE_SFF_8636 = 0x3
ETH_MODULE_SFF_8636_LEN = 256
ETH_MODULE_SFF_8436 = 0x4
ETH_MODULE_SFF_8436_LEN = 256


class ethtool_cmd(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
            ('cmd', ctypes.c_uint32),
            ('supported', ctypes.c_uint32),
            ('advertising', ctypes.c_uint32),
            ('speed', ctypes.c_uint16),
            ('duplex', ctypes.c_uint8),
            ('port', ctypes.c_uint8),
            ('phy_address', ctypes.c_uint8),
            ('transceiver', ctypes.c_uint8),
            ('autoneg', ctypes.c_uint8),
            ('mdio_support', ctypes.c_uint8),
            ('maxtxpkt', ctypes.c_uint32),
            ('maxrxpkt', ctypes.c_uint32),
            ('speed_hi', ctypes.c_uint16),
            ('eth_tp_mdix', ctypes.c_uint8),
            ('eth_tp_mdix_ctrl', ctypes.c_uint8),
            ('lp_advertising', ctypes.c_uint32),
            ('reserved1', ctypes.c_uint32),
            ('reserved2', ctypes.c_uint32),
    ]


class ethtool_value(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
            ('cmd', ctypes.c_uint32),
            ('data', ctypes.c_uint32),
    ]


class ifr_data(ctypes.Union):
    _pack_ = 1
    _fields_ = [
            ('ethtool_cmd_ptr', ctypes.POINTER(ethtool_cmd)),
            ('ethtool_value_ptr', ctypes.POINTER(ethtool_value)),
    ]


class ifreq(ctypes.Structure):
    _pack_ = 1
    _fields_ = [('ifr_name', (ctypes.c_ubyte * 16)), ('ifr_data', ifr_data)]


# ============================================================================

def _dump_supported(mask):
    supported = []

    if mask & SUPPORTED_Autoneg:
        supported.append("Auto-Negotiate")

    if mask & SUPPORTED_10baseT_Half:
        supported.append("10baseT/Half")

    if mask & SUPPORTED_10baseT_Full:
        supported.append("10baseT/Full")

    if mask & SUPPORTED_100baseT_Half:
        supported.append("100baseT/Half")

    if mask & SUPPORTED_100baseT_Full:
        supported.append("100baseT/Full")

    if mask & SUPPORTED_1000baseT_Half:
        supported.append("1000baseT/Half")

    if mask & SUPPORTED_1000baseT_Full:
        supported.append("1000baseT/Full")

    if mask & SUPPORTED_2500baseX_Full:
        supported.append("2500baseX/Full")

    return supported


def _dump_advertised(mask):
    advertising = []

    if mask & ADVERTISED_Autoneg:
        advertising.append("Auto-Negotiate")

    if mask & ADVERTISED_10baseT_Half:
        advertising.append("10baseT/Half")

    if mask & ADVERTISED_10baseT_Full:
        advertising.append("10baseT/Full")

    if mask & ADVERTISED_100baseT_Half:
        advertising.append("100baseT/Half")

    if mask & ADVERTISED_100baseT_Full:
        advertising.append("100baseT/Full")

    if mask & ADVERTISED_1000baseT_Half:
        advertising.append("1000baseT/Half")

    if mask & ADVERTISED_1000baseT_Full:
        advertising.append("1000baseT/Full")

    if mask & ADVERTISED_2500baseX_Full:
        advertising.append("2500baseX/Full")

    if mask & ADVERTISED_10000baseT_Full:
        advertising.append("10000baseT/Full")

    return advertising


def _dump_ecmd(ep):
    settings = {}
    settings["supported"] = _dump_supported(ep.supported)
    settings["advertised"] = _dump_advertised(ep.advertising)
    settings["link_partner"] = _dump_advertised(ep.lp_advertising)

    if ep.speed == SPEED_10:
        settings['speed'] = "10Mb/s"
    elif ep.speed == SPEED_100:
        settings['speed'] = "100Mb/s"
    elif ep.speed == SPEED_1000:
        settings['speed'] = "1000Mb/s"
    elif ep.speed == SPEED_2500:
        settings['speed'] = "2500Mb/s"
    elif ep.speed == SPEED_10000:
        settings['speed'] = "10000Mb/s"
    else:
        settings['speed'] = f"Unknown! ({ep.speed})"

    if ep.duplex == DUPLEX_HALF:
        settings['duplex'] = "Half"
    elif ep.duplex == DUPLEX_FULL:
        settings['duplex'] = "Full"
    else:
        settings['duplex'] = f"Unknown! ({ep.duplex})"

    if ep.autoneg == AUTONEG_DISABLE:
        settings['autoneg'] = False
    else:
        settings['autoneg'] = True

    return settings


class EthTool:
    def __init__(self, ifname):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._name = (ctypes.c_ubyte *
                      IFNAMSIZ)(*bytearray(str(ifname).encode()))

    def _ifreq_ecmd(self):
        ifr = ifreq()
        ecmd = ethtool_cmd()
        ifr.ifr_data.ethtool_cmd_ptr = ctypes.pointer(ecmd)
        ifr.ifr_name = self._name
        return ifr, ecmd

    def _ifreq_value(self):
        ifr = ifreq()
        evalue = ethtool_value()
        ifr.ifr_data.ethtool_value_ptr = ctypes.pointer(evalue)
        ifr.ifr_name = self._name
        return ifr, evalue

    def get_settings(self):
        ifr, ecmd = self._ifreq_ecmd()

        ecmd.cmd = ETHTOOL_GSET
        try:
            fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)
        except OSError as exc:
            if exc.errno == 95:
                return None
            else:
                raise

        return _dump_ecmd(ecmd)

    def link_detected(self):
        ifr, evalue = self._ifreq_value()

        evalue.cmd = ETHTOOL_GLINK
        try:
            fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)
            return bool(evalue.data)
        except OSError as exc:
            if exc.errno == 45:
                return False
            else:
                raise

    def enable_autoneg(self):
        ifr, ecmd = self._ifreq_ecmd()

        ecmd.cmd = ETHTOOL_GSET
        fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)

        ecmd.cmd = ETHTOOL_SSET
        ecmd.autoneg = AUTONEG_ENABLE
        fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)

    def force_speed(self, speed, duplex):
        ifr, ecmd = self._ifreq_ecmd()

        ecmd.cmd = ETHTOOL_GSET
        fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)

        ecmd.cmd = ETHTOOL_SSET
        ecmd.autoneg = AUTONEG_DISABLE
        ecmd.speed = speed
        ecmd.duplex = duplex
        fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)

    def set_advertised(self, advertise):
        ifr, ecmd = self._ifreq_ecmd()

        ecmd.cmd = ETHTOOL_GSET
        fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)

        ecmd.cmd = ETHTOOL_SSET
        ecmd.advertising = ecmd.supported & advertise
        fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)
