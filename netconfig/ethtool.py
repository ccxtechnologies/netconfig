# Copyright: 2017-2026, CCX Technologies

import ctypes
import socket
import fcntl

IFNAMSIZ = 16

# from linux/source/include/uapi/linux/sockios.h
SIOCETHTOOL = 0x8946

# CMDs currently supported
ETHTOOL_GDRVINFO = 0x00000003  # Get driver info.
ETHTOOL_GREGS = 0x00000004  # Get NIC registers.
ETHTOOL_GWOL = 0x00000005  # Get wake-on-lan options.
ETHTOOL_SWOL = 0x00000006  # Set wake-on-lan options.
ETHTOOL_GMSGLVL = 0x00000007  # Get driver message level
ETHTOOL_SMSGLVL = 0x00000008  # Set driver msg level.
ETHTOOL_NWAY_RST = 0x00000009  # Restart autonegotiation.
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

# New Link Settings ioctls
ETHTOOL_GLINKSETTINGS = 0x0000004c
ETHTOOL_SLINKSETTINGS = 0x0000004d

ETHTOOL_PHY_GTUNABLE = 0x0000004e
ETHTOOL_PHY_STUNABLE = 0x0000004f

# PHY Tunables
ETHTOOL_PHY_DOWNSHIFT = 1
ETHTOOL_PHY_FAST_LINK_DOWN = 2
ETHTOOL_PHY_EDPD = 3

ETHTOOL_TUNABLE_U8 = 1
ETHTOOL_TUNABLE_U16 = 2


class ethtool_eee(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
            ('cmd', ctypes.c_uint32),
            ('supported', ctypes.c_uint32),
            ('advertised', ctypes.c_uint32),
            ('lp_advertised', ctypes.c_uint32),
            ('eee_active', ctypes.c_uint32),
            ('eee_enabled', ctypes.c_uint32),
            ('tx_lpi_enabled', ctypes.c_uint32),
            ('tx_lpi_timer', ctypes.c_uint32),
            ('reserved1', ctypes.c_uint32),
            ('reserved2', ctypes.c_uint32),
    ]


class ethtool_value(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
            ('cmd', ctypes.c_uint32),
            ('data', ctypes.c_uint32),
    ]


class ethtool_tunable_downshift(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
            ('cmd', ctypes.c_uint32),
            ('id', ctypes.c_uint32),
            ('type_id', ctypes.c_uint32),
            ('len', ctypes.c_uint32),
            ('count', ctypes.c_uint8),
    ]


class ethtool_tunable_edpd(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
            ('cmd', ctypes.c_uint32),
            ('id', ctypes.c_uint32),
            ('type_id', ctypes.c_uint32),
            ('len', ctypes.c_uint32),
            ('tx_msecs', ctypes.c_uint16),
    ]


class ethtool_link_settings(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
            ('cmd', ctypes.c_uint32),
            ('speed', ctypes.c_uint32),
            ('duplex', ctypes.c_uint8),
            ('port', ctypes.c_uint8),
            ('phy_address', ctypes.c_uint8),
            ('autoneg', ctypes.c_uint8),
            ('mdio_support', ctypes.c_uint8),
            ('eth_tp_mdix', ctypes.c_uint8),
            ('eth_tp_mdix_ctrl', ctypes.c_uint8),
            ('link_mode_masks_nwords', ctypes.c_int8),
            ('transceiver', ctypes.c_uint8),
            ('reserved1', ctypes.c_uint8 * 3),
            ('reserved', ctypes.c_uint32 * 7),
            ('link_mode_masks', ctypes.c_uint32 * (127 * 3)),
    ]


class ifr_data(ctypes.Union):
    _pack_ = 1
    _fields_ = [
            ('ethtool_value_ptr', ctypes.POINTER(ethtool_value)),
            ('ethtool_eee_ptr', ctypes.POINTER(ethtool_eee)),
            (
                    'ethtool_downshift_ptr',
                    ctypes.POINTER(ethtool_tunable_downshift)
            ),
            ('ethtool_edpd_ptr', ctypes.POINTER(ethtool_tunable_edpd)),
            (
                    'ethtool_link_settings_ptr',
                    ctypes.POINTER(ethtool_link_settings)
            ),
    ]


class ifreq(ctypes.Structure):
    _pack_ = 1
    _fields_ = [('ifr_name', (ctypes.c_ubyte * 16)), ('ifr_data', ifr_data)]


# ============================================================================


class EthTool:
    SUPPORTED_10baseT_Half = 1 << 0
    SUPPORTED_10baseT_Full = 1 << 1
    SUPPORTED_100baseT_Half = 1 << 2
    SUPPORTED_100baseT_Full = 1 << 3
    SUPPORTED_1000baseT_Half = 1 << 4
    SUPPORTED_1000baseT_Full = 1 << 5
    SUPPORTED_Autoneg = 1 << 6
    SUPPORTED_TP = 1 << 7
    SUPPORTED_AUI = 1 << 8
    SUPPORTED_MII = 1 << 9
    SUPPORTED_FIBRE = 1 << 10
    SUPPORTED_BNC = 1 << 11
    SUPPORTED_10000baseT_Full = 1 << 12
    SUPPORTED_Pause = 1 << 13
    SUPPORTED_Asym_Pause = 1 << 14
    SUPPORTED_2500baseX_Full = 1 << 15
    SUPPORTED_Backplane = 1 << 16
    SUPPORTED_1000baseKX_Full = 1 << 17
    SUPPORTED_10000baseKX4_Full = 1 << 18
    SUPPORTED_10000baseKR_Full = 1 << 19
    SUPPORTED_10000baseR_FEC = 1 << 20
    SUPPORTED_20000baseMLD2_Full = 1 << 21
    SUPPORTED_20000baseKR2_Full = 1 << 22
    SUPPORTED_40000baseKR4_Full = 1 << 23
    SUPPORTED_40000baseCR4_Full = 1 << 24
    SUPPORTED_40000baseSR4_Full = 1 << 25
    SUPPORTED_40000baseLR4_Full = 1 << 26
    SUPPORTED_56000baseKR4_Full = 1 << 27
    SUPPORTED_56000baseCR4_Full = 1 << 28
    SUPPORTED_56000baseSR4_Full = 1 << 29
    SUPPORTED_56000baseLR4_Full = 1 << 30

    # Extended Bits for ETHTOOL_GLINKSETTINGS
    SUPPORTED_2500baseT_Full = 1 << 47

    ADVERTISED_10baseT_Half = 1 << 0
    ADVERTISED_10baseT_Full = 1 << 1
    ADVERTISED_100baseT_Half = 1 << 2
    ADVERTISED_100baseT_Full = 1 << 3
    ADVERTISED_1000baseT_Half = 1 << 4
    ADVERTISED_1000baseT_Full = 1 << 5
    ADVERTISED_Autoneg = 1 << 6
    ADVERTISED_TP = 1 << 7
    ADVERTISED_AUI = 1 << 8
    ADVERTISED_MII = 1 << 9
    ADVERTISED_FIBRE = 1 << 10
    ADVERTISED_BNC = 1 << 11
    ADVERTISED_10000baseT_Full = 1 << 12
    ADVERTISED_Pause = 1 << 13
    ADVERTISED_Asym_Pause = 1 << 14
    ADVERTISED_2500baseX_Full = 1 << 15
    ADVERTISED_Backplane = 1 << 16
    ADVERTISED_1000baseKX_Full = 1 << 17
    ADVERTISED_10000baseKX4_Full = 1 << 18
    ADVERTISED_10000baseKR_Full = 1 << 19
    ADVERTISED_10000baseR_FEC = 1 << 20
    ADVERTISED_20000baseMLD2_Full = 1 << 21
    ADVERTISED_20000baseKR2_Full = 1 << 22
    ADVERTISED_40000baseKR4_Full = 1 << 23
    ADVERTISED_40000baseCR4_Full = 1 << 24
    ADVERTISED_40000baseSR4_Full = 1 << 25
    ADVERTISED_40000baseLR4_Full = 1 << 26
    ADVERTISED_56000baseKR4_Full = 1 << 27
    ADVERTISED_56000baseCR4_Full = 1 << 28
    ADVERTISED_56000baseSR4_Full = 1 << 29
    ADVERTISED_56000baseLR4_Full = 1 << 30

    # Extended Bits for ETHTOOL_GLINKSETTINGS
    ADVERTISED_2500baseT_Full = 1 << 47

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

    DUPLEX_HALF = 0x00
    DUPLEX_FULL = 0x01
    DUPLEX_UNKNOWN = 0xff

    PORT_TP = 0x00
    PORT_AUI = 0x01
    PORT_MII = 0x02
    PORT_FIBRE = 0x03
    PORT_BNC = 0x04
    PORT_DA = 0x05
    PORT_NONE = 0xef
    PORT_OTHER = 0xff

    XCVR_INTERNAL = 0x00
    XCVR_EXTERNAL = 0x01
    XCVR_DUMMY1 = 0x02
    XCVR_DUMMY2 = 0x03
    XCVR_DUMMY3 = 0x04

    AUTONEG_DISABLE = 0x00
    AUTONEG_ENABLE = 0x01

    EEE_DISABLE = 0x00
    EEE_ENABLE = 0x01

    ETH_TP_MDI_INVALID = 0x00
    ETH_TP_MDI = 0x01
    ETH_TP_MDI_X = 0x02
    ETH_TP_MDI_AUTO = 0x03

    # EEPROM Standards for plug in modules
    ETH_MODULE_SFF_8079 = 0x1
    ETH_MODULE_SFF_8079_LEN = 256
    ETH_MODULE_SFF_8472 = 0x2
    ETH_MODULE_SFF_8472_LEN = 512
    ETH_MODULE_SFF_8636 = 0x3
    ETH_MODULE_SFF_8636_LEN = 256
    ETH_MODULE_SFF_8436 = 0x4
    ETH_MODULE_SFF_8436_LEN = 256

    PHY_EDPD_DFLT_TX_MSECS = 0xffff
    PHY_EDPD_DISABLE = 0

    class _LegacyEcmdWrapper:
        pass

    def __init__(self, ifname):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._name = (ctypes.c_ubyte *
                      IFNAMSIZ)(*bytearray(str(ifname).encode()))

    def _ifreq_link_settings(self, ecmd=None):
        ifr = ifreq()
        if ecmd is None:
            ecmd = ethtool_link_settings()
        ifr.ifr_data.ethtool_link_settings_ptr = ctypes.pointer(ecmd)
        ifr.ifr_name = self._name  # noqa pylint: disable=attribute-defined-outside-init
        return ifr, ecmd

    def _ifreq_downshift(self):
        ifr = ifreq()
        ecmd = ethtool_tunable_downshift()
        ifr.ifr_data.ethtool_downshift_ptr = ctypes.pointer(ecmd)
        ifr.ifr_name = self._name  # noqa pylint: disable=attribute-defined-outside-init
        return ifr, ecmd

    def _ifreq_edpd(self):
        ifr = ifreq()
        ecmd = ethtool_tunable_edpd()
        ifr.ifr_data.ethtool_edpd_ptr = ctypes.pointer(ecmd)
        ifr.ifr_name = self._name  # noqa pylint: disable=attribute-defined-outside-init
        return ifr, ecmd

    def _ifreq_eee(self):
        ifr = ifreq()
        ecmd = ethtool_eee()
        ifr.ifr_data.ethtool_eee_ptr = ctypes.pointer(ecmd)
        ifr.ifr_name = self._name  # noqa pylint: disable=attribute-defined-outside-init
        return ifr, ecmd

    def _ifreq_value(self):
        ifr = ifreq()
        evalue = ethtool_value()
        ifr.ifr_data.ethtool_value_ptr = ctypes.pointer(evalue)
        ifr.ifr_name = self._name  # noqa pylint: disable=attribute-defined-outside-init
        return ifr, evalue

    def _mask_to_int(self, masks, offset, nwords):
        res = 0
        for i in range(nwords):
            res |= (masks[offset + i] << (32 * i))
        return res

    def _int_to_mask(self, val, masks, offset, nwords):
        for i in range(nwords):
            masks[offset + i] = (val >> (32 * i)) & 0xffffffff

    def _get_link_settings(self):
        ifr, ecmd = self._ifreq_link_settings()
        ecmd.cmd = ETHTOOL_GLINKSETTINGS  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.link_mode_masks_nwords = 0  # noqa pylint: disable=attribute-defined-outside-init
        try:
            fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)
        except OSError as exc:
            if exc.errno == 95:
                return None
            raise

        if ecmd.link_mode_masks_nwords < 0:
            ecmd.link_mode_masks_nwords = -ecmd.link_mode_masks_nwords  # noqa pylint: disable=attribute-defined-outside-init
            fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)

        return ecmd

    def get_settings(self):
        ecmd = self._get_link_settings()
        if ecmd is None:
            return None

        ep = self._LegacyEcmdWrapper()
        nwords = ecmd.link_mode_masks_nwords
        ep.supported = self._mask_to_int(ecmd.link_mode_masks, 0, nwords)  # noqa pylint: disable=attribute-defined-outside-init
        ep.advertising = self._mask_to_int( # noqa pylint: disable=attribute-defined-outside-init
                ecmd.link_mode_masks, nwords, nwords
        )
        ep.lp_advertising = self._mask_to_int( # noqa pylint: disable=attribute-defined-outside-init
                ecmd.link_mode_masks, 2 * nwords, nwords
        )
        ep.speed = ecmd.speed  # noqa pylint: disable=attribute-defined-outside-init
        ep.duplex = ecmd.duplex  # noqa pylint: disable=attribute-defined-outside-init
        ep.autoneg = ecmd.autoneg  # noqa pylint: disable=attribute-defined-outside-init
        return self._dump_ecmd(ep)

    def get_eee(self):
        ifr, ecmd = self._ifreq_eee()

        ecmd.cmd = ETHTOOL_GEEE  # noqa pylint: disable=attribute-defined-outside-init
        try:
            fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)
        except OSError as exc:
            if exc.errno == 95:
                return None
            raise

        return self._dump_eee(ecmd)

    def get_downshift(self):
        ifr, ecmd = self._ifreq_downshift()

        ecmd.cmd = ETHTOOL_PHY_GTUNABLE  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.id = ETHTOOL_PHY_DOWNSHIFT  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.type_id = ETHTOOL_TUNABLE_U8  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.len = 1  # noqa pylint: disable=attribute-defined-outside-init

        try:
            fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)
        except OSError as exc:
            if exc.errno == 95:
                return None
            raise

        return self._dump_downshift(ecmd)

    def get_edpd(self):
        ifr, ecmd = self._ifreq_edpd()

        ecmd.cmd = ETHTOOL_PHY_GTUNABLE  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.id = ETHTOOL_PHY_EDPD  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.type_id = ETHTOOL_TUNABLE_U16  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.len = 2  # noqa pylint: disable=attribute-defined-outside-init

        try:
            fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)
        except OSError as exc:
            if exc.errno == 95:
                return None
            raise

        return self._dump_edpd(ecmd)

    def link_detected(self):
        ifr, evalue = self._ifreq_value()

        evalue.cmd = ETHTOOL_GLINK  # noqa pylint: disable=attribute-defined-outside-init
        try:
            fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)
            return bool(evalue.data)
        except OSError as exc:
            if exc.errno == 45:
                return False
            raise

    def update_downshift(self, count):
        ifr, ecmd = self._ifreq_downshift()

        ecmd.cmd = ETHTOOL_PHY_GTUNABLE  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.id = ETHTOOL_PHY_DOWNSHIFT  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.type_id = ETHTOOL_TUNABLE_U8  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.len = 1  # noqa pylint: disable=attribute-defined-outside-init

        try:
            fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)
        except OSError as exc:
            if exc.errno == 95:
                # operation not supported
                return
            raise

        ecmd.cmd = ETHTOOL_PHY_STUNABLE  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.count = count  # noqa pylint: disable=attribute-defined-outside-init
        fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)

    def enable_edpd(self):

        ifr, ecmd = self._ifreq_edpd()

        ecmd.cmd = ETHTOOL_PHY_GTUNABLE  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.id = ETHTOOL_PHY_EDPD  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.type_id = ETHTOOL_TUNABLE_U16  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.len = 2  # noqa pylint: disable=attribute-defined-outside-init

        try:
            fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)
        except OSError as exc:
            # operation not supported
            if exc.errno == 95:
                return
            raise

        ecmd.cmd = ETHTOOL_PHY_STUNABLE  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.tx_msecs = self.PHY_EDPD_DFLT_TX_MSECS  # noqa pylint: disable=attribute-defined-outside-init
        fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)

    def disable_edpd(self):

        ifr, ecmd = self._ifreq_edpd()

        ecmd.cmd = ETHTOOL_PHY_GTUNABLE  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.id = ETHTOOL_PHY_EDPD  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.type_id = ETHTOOL_TUNABLE_U16  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.len = 2  # noqa pylint: disable=attribute-defined-outside-init

        try:
            fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)
        except OSError as exc:
            # operation not supported
            if exc.errno == 95:
                return
            raise

        ecmd.cmd = ETHTOOL_PHY_STUNABLE  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.tx_msecs = self.PHY_EDPD_DISABLE  # noqa pylint: disable=attribute-defined-outside-init
        fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)

    def enable_eee(self):
        ifr, ecmd = self._ifreq_eee()

        ecmd.cmd = ETHTOOL_GEEE  # noqa pylint: disable=attribute-defined-outside-init
        try:
            fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)
        except OSError as exc:
            if exc.errno == 95:
                # operation not supported
                return
            raise

        ecmd.cmd = ETHTOOL_SEEE  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.eee_enabled = self.EEE_ENABLE  # noqa pylint: disable=attribute-defined-outside-init
        fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)

    def disable_eee(self):
        ifr, ecmd = self._ifreq_eee()

        ecmd.cmd = ETHTOOL_GEEE  # noqa pylint: disable=attribute-defined-outside-init
        try:
            fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)
        except OSError as exc:
            if exc.errno == 95:
                # operation not supported
                return
            raise

        ecmd.cmd = ETHTOOL_SEEE  # noqa pylint: disable=attribute-defined-outside-init
        ecmd.eee_enabled = self.EEE_DISABLE  # noqa pylint: disable=attribute-defined-outside-init
        fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)

    def enable_autoneg(self):
        ecmd = self._get_link_settings()
        if ecmd is not None:
            ecmd.cmd = ETHTOOL_SLINKSETTINGS  # noqa pylint: disable=attribute-defined-outside-init
            ecmd.autoneg = self.AUTONEG_ENABLE  # noqa pylint: disable=attribute-defined-outside-init
            ifr, _ = self._ifreq_link_settings(ecmd)
            fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)

    def force_speed(self, speed, duplex):
        ecmd = self._get_link_settings()
        if ecmd is not None:
            ecmd.cmd = ETHTOOL_SLINKSETTINGS  # noqa pylint: disable=attribute-defined-outside-init
            ecmd.autoneg = self.AUTONEG_DISABLE  # noqa pylint: disable=attribute-defined-outside-init
            ecmd.speed = speed  # noqa pylint: disable=attribute-defined-outside-init
            ecmd.duplex = duplex  # noqa pylint: disable=attribute-defined-outside-init
            ifr, _ = self._ifreq_link_settings(ecmd)
            fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)

    def set_advertised(self, advertise):
        ecmd = self._get_link_settings()
        if ecmd is not None:
            nwords = ecmd.link_mode_masks_nwords
            supported = self._mask_to_int(ecmd.link_mode_masks, 0, nwords)
            new_adv = supported & advertise
            self._int_to_mask(new_adv, ecmd.link_mode_masks, nwords, nwords)
            ecmd.cmd = ETHTOOL_SLINKSETTINGS  # noqa pylint: disable=attribute-defined-outside-init
            ifr, _ = self._ifreq_link_settings(ecmd)
            fcntl.ioctl(self.sock, SIOCETHTOOL, ifr)

    def _dump_supported(self, mask):
        supported = []

        if mask & self.SUPPORTED_Autoneg:
            supported.append("Auto-Negotiate")

        if mask & self.SUPPORTED_10baseT_Half:
            supported.append("10baseT/Half")

        if mask & self.SUPPORTED_10baseT_Full:
            supported.append("10baseT/Full")

        if mask & self.SUPPORTED_100baseT_Half:
            supported.append("100baseT/Half")

        if mask & self.SUPPORTED_100baseT_Full:
            supported.append("100baseT/Full")

        if mask & self.SUPPORTED_1000baseT_Half:
            supported.append("1000baseT/Half")

        if mask & self.SUPPORTED_1000baseT_Full:
            supported.append("1000baseT/Full")

        if mask & self.SUPPORTED_2500baseT_Full:
            supported.append("2500baseT/Full")

        if mask & self.SUPPORTED_2500baseX_Full:
            supported.append("2500baseX/Full")

        return supported

    def _dump_advertised(self, mask):
        advertising = []

        if mask & self.ADVERTISED_Autoneg:
            advertising.append("Auto-Negotiate")

        if mask & self.ADVERTISED_10baseT_Half:
            advertising.append("10baseT/Half")

        if mask & self.ADVERTISED_10baseT_Full:
            advertising.append("10baseT/Full")

        if mask & self.ADVERTISED_100baseT_Half:
            advertising.append("100baseT/Half")

        if mask & self.ADVERTISED_100baseT_Full:
            advertising.append("100baseT/Full")

        if mask & self.ADVERTISED_1000baseT_Half:
            advertising.append("1000baseT/Half")

        if mask & self.ADVERTISED_1000baseT_Full:
            advertising.append("1000baseT/Full")

        if mask & self.ADVERTISED_2500baseT_Full:
            advertising.append("2500baseT/Full")

        if mask & self.ADVERTISED_2500baseX_Full:
            advertising.append("2500baseX/Full")

        if mask & self.ADVERTISED_10000baseT_Full:
            advertising.append("10000baseT/Full")

        return advertising

    def _dump_ecmd(self, ep):
        settings = {}
        settings["supported"] = self._dump_supported(ep.supported)
        settings["advertised"] = self._dump_advertised(ep.advertising)
        settings["link_partner"] = self._dump_advertised(ep.lp_advertising)

        if ep.speed == self.SPEED_10:
            settings['speed'] = "10Mb/s"
        elif ep.speed == self.SPEED_100:
            settings['speed'] = "100Mb/s"
        elif ep.speed == self.SPEED_1000:
            settings['speed'] = "1000Mb/s"
        elif ep.speed == self.SPEED_2500:
            settings['speed'] = "2500Mb/s"
        elif ep.speed == self.SPEED_10000:
            settings['speed'] = "10000Mb/s"
        else:
            settings['speed'] = f"Unknown! ({ep.speed})"

        if ep.duplex == self.DUPLEX_HALF:
            settings['duplex'] = "Half"
        elif ep.duplex == self.DUPLEX_FULL:
            settings['duplex'] = "Full"
        else:
            settings['duplex'] = f"Unknown! ({ep.duplex})"

        if ep.autoneg == self.AUTONEG_DISABLE:
            settings['autoneg'] = False
        else:
            settings['autoneg'] = True

        return settings

    def _dump_eee(self, ep):
        settings = {}
        settings["supported"] = self._dump_supported(ep.supported)
        settings["advertised"] = self._dump_advertised(ep.advertised)
        settings["link_partner"] = self._dump_advertised(ep.lp_advertised)
        settings["enabled"] = bool(ep.eee_enabled)
        settings["active"] = bool(ep.eee_active)

        return settings

    def _dump_downshift(self, ep):
        settings = {}
        settings["enabled"] = bool(ep.count)
        settings["count"] = ep.count

        return settings

    def _dump_edpd(self, ep):
        settings = {}
        settings["enabled"] = bool(ep.tx_msecs)
        settings["tx_msecs"] = ep.tx_msecs

        return settings
