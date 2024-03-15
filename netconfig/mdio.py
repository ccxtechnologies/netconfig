#!/usr/bin/python
# Copyright: 2017, CCX Technologies

import ctypes
import socket
import fcntl

# Generic MII registers.
MII_BMCR = 0x00  # Basic mode control register
MII_BMSR = 0x01  # Basic mode status register
MII_PHYSID1 = 0x02  # PHYS ID 1
MII_PHYSID2 = 0x03  # PHYS ID 2
MII_ADVERTISE = 0x04  # Advertisement control reg
MII_LPA = 0x05  # Link partner ability reg
MII_EXPANSION = 0x06  # Expansion register
MII_CTRL1000 = 0x09  # 1000BASE-T control
MII_STAT1000 = 0x0a  # 1000BASE-T status
MII_MMD_CTRL = 0x0d  # MMD Access Control Register
MII_MMD_DATA = 0x0e  # MMD Access Data Register
MII_ESTATUS = 0x0f  # Extended Status
MII_DCOUNTER = 0x12  # Disconnect counter
MII_FCSCOUNTER = 0x13  # False carrier counter
MII_NWAYTEST = 0x14  # N-way auto-neg test reg
MII_RERRCOUNTER = 0x15  # Receive error counter
MII_SREVISION = 0x16  # Silicon revision
MII_RESV1 = 0x17  # Reserved...
MII_LBRERROR = 0x18  # Loopback, rx, bypass error
MII_PHYADDR = 0x19  # PHY address
MII_RESV2 = 0x1a  # Reserved...
MII_TPISTATUS = 0x1b  # TPI status for 10Mbps
MII_NCONFIG = 0x1c  # Network interface config

# Basic mode control register.
BMCR_RESV = 0x003f  # Unused...
BMCR_SPEED1000 = 0x0040  # MSB of Speed (1000)
BMCR_CTST = 0x0080  # Collision test
BMCR_FULLDPLX = 0x0100  # Full duplex
BMCR_ANRESTART = 0x0200  # Auto negotiation restart
BMCR_ISOLATE = 0x0400  # Isolate data paths from MII
BMCR_PDOWN = 0x0800  # Enable low power state
BMCR_ANENABLE = 0x1000  # Enable auto negotiation
BMCR_SPEED100 = 0x2000  # Select 100Mbps
BMCR_LOOPBACK = 0x4000  # TXD loopback bits
BMCR_RESET = 0x8000  # Reset to default state

# Basic mode status register.
BMSR_ERCAP = 0x0001  # Ext-reg capability
BMSR_JCD = 0x0002  # Jabber detected
BMSR_LSTATUS = 0x0004  # Link status
BMSR_ANEGCAPABLE = 0x0008  # Able to do auto-negotiation
BMSR_RFAULT = 0x0010  # Remote fault detected
BMSR_ANEGCOMPLETE = 0x0020  # Auto-negotiation complete
BMSR_RESV = 0x00c0  # Unused...
BMSR_ESTATEN = 0x0100  # Extended Status in R15
BMSR_100HALF2 = 0x0200  # Can do 100BASE-T2 HDX
BMSR_100FULL2 = 0x0400  # Can do 100BASE-T2 FDX
BMSR_10HALF = 0x0800  # Can do 10Mbps, half-duplex
BMSR_10FULL = 0x1000  # Can do 10Mbps, full-duplex
BMSR_100HALF = 0x2000  # Can do 100Mbps, half-duplex
BMSR_100FULL = 0x4000  # Can do 100Mbps, full-duplex
BMSR_100BASE4 = 0x8000  # Can do 100Mbps, 4k packets

# Advertisement control register.
ADVERTISE_SLCT = 0x001f  # Selector bits
ADVERTISE_CSMA = 0x0001  # Only selector supported
ADVERTISE_10HALF = 0x0020  # Try for 10Mbps half-duplex
ADVERTISE_1000XFULL = 0x0020  # Try for 1000BASE-X full-duplex
ADVERTISE_10FULL = 0x0040  # Try for 10Mbps full-duplex
ADVERTISE_1000XHALF = 0x0040  # Try for 1000BASE-X half-duplex
ADVERTISE_100HALF = 0x0080  # Try for 100Mbps half-duplex
ADVERTISE_1000XPAUSE = 0x0080  # Try for 1000BASE-X pause
ADVERTISE_100FULL = 0x0100  # Try for 100Mbps full-duplex
ADVERTISE_1000XPSE_ASYM = 0x0100  # Try for 1000BASE-X asymmetric pause
ADVERTISE_100BASE4 = 0x0200  # Try for 100Mbps 4k packets
ADVERTISE_PAUSE_CAP = 0x0400  # Try for pause
ADVERTISE_PAUSE_ASYM = 0x0800  # Try for asymmetric pause
ADVERTISE_RESV = 0x1000  # Unused...
ADVERTISE_RFAULT = 0x2000  # Say we can detect faults
ADVERTISE_LPACK = 0x4000  # ACK link partners response
ADVERTISE_NPAGE = 0x8000  # Next page bit

ADVERTISE_FULL = (ADVERTISE_100FULL | ADVERTISE_10FULL | ADVERTISE_CSMA)
ADVERTISE_ALL = (
        ADVERTISE_10HALF | ADVERTISE_10FULL | ADVERTISE_100HALF
        | ADVERTISE_100FULL
)

# Link partner ability register.
LPA_SLCT = 0x001f  # Same as advertise selector
LPA_10HALF = 0x0020  # Can do 10Mbps half-duplex
LPA_1000XFULL = 0x0020  # Can do 1000BASE-X full-duplex
LPA_10FULL = 0x0040  # Can do 10Mbps full-duplex
LPA_1000XHALF = 0x0040  # Can do 1000BASE-X half-duplex
LPA_100HALF = 0x0080  # Can do 100Mbps half-duplex
LPA_1000XPAUSE = 0x0080  # Can do 1000BASE-X pause
LPA_100FULL = 0x0100  # Can do 100Mbps full-duplex
LPA_1000XPAUSE_ASYM = 0x0100  # Can do 1000BASE-X pause asymmetric
LPA_100BASE4 = 0x0200  # Can do 100Mbps 4k packets
LPA_PAUSE_CAP = 0x0400  # Can pause
LPA_PAUSE_ASYM = 0x0800  # Can pause asymmetrically
LPA_RESV = 0x1000  # Unused...
LPA_RFAULT = 0x2000  # Link partner faulted
LPA_LPACK = 0x4000  # Link partner ACKed us
LPA_NPAGE = 0x8000  # Next page bit

LPA_DUPLEX = (LPA_10FULL | LPA_100FULL)
LPA_100 = (LPA_100FULL | LPA_100HALF | LPA_100BASE4)

# Expansion register for auto-negotiation.
EXPANSION_NWAY = 0x0001  # Can do N-way auto-negotiation
EXPANSION_LCWP = 0x0002  # Got new RX page code word
EXPANSION_ENABLENPAGE = 0x0004  # This enables npage words
EXPANSION_NPCAPABLE = 0x0008  # Link partner supports npage
EXPANSION_MFAULTS = 0x0010  # Multiple faults detected
EXPANSION_RESV = 0xffe0  # Unused...

ESTATUS_1000_TFULL = 0x2000  # Can do 1000baseT Full
ESTATUS_1000_THALF = 0x1000  # Can do 1000baseT Half

# N-way test register.
NWAYTEST_RESV1 = 0x00ff  # Unused...
NWAYTEST_LOOPBACK = 0x0100  # Enable loopback for N-way
NWAYTEST_RESV2 = 0xfe00  # Unused...

# 1000BASE-T Control register
ADVERTISE_1000FULL = 0x0200  # Advertise 1000BASE-T full duplex
ADVERTISE_1000HALF = 0x0100  # Advertise 1000BASE-T half duplex
CTL1000_AS_MASTER = 0x0800
CTL1000_ENABLE_MASTER = 0x1000

# 1000BASE-T Status register
LPA_1000LOCALRXOK = 0x2000  # Link partner local receiver status
LPA_1000REMRXOK = 0x1000  # Link partner remote receiver status
LPA_1000FULL = 0x0800  # Link partner 1000BASE-T full duplex
LPA_1000HALF = 0x0400  # Link partner 1000BASE-T half duplex

# Flow control flags
FLOW_CTRL_TX = 0x01
FLOW_CTRL_RX = 0x02

# MMD Access Control register fields
MII_MMD_CTRL_DEVAD_MASK = 0x1f  # Mask MMD DEVAD
MII_MMD_CTRL_ADDR = 0x0000  # Address
MII_MMD_CTRL_NOINCR = 0x4000  # no post increment
MII_MMD_CTRL_INCR_RDWT = 0x8000  # post increment on reads & writes
MII_MMD_CTRL_INCR_ON_WT = 0xC000  # post increment on writes only

# MII SOIC Commands
SIOCGMIIPHY = 0x8947  # Get address of MII PHY in use.
SIOCGMIIREG = 0x8948  # Read MII PHY register.
SIOCSMIIREG = 0x8949  # Write MII PHY register.


class mii_ioctl_data(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
            ('phy_id', ctypes.c_uint16),
            ('reg_num', ctypes.c_uint16),
            ('val_in', ctypes.c_uint16),
            ('val_out', ctypes.c_uint16),
    ]


class ifreq(ctypes.Structure):
    _pack_ = 1
    _fields_ = [('ifr_name', (ctypes.c_ubyte * 16)), ('data', mii_ioctl_data)]

    def __init__(self, ifname):
        self.ifr_name = (ctypes.c_ubyte * 16)(*bytearray(ifname.encode()))


def mdio_read_reg(ifname, reg):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        ifr = ifreq()
        ifr.ifr_name = (ctypes.c_ubyte * 16)(*bytearray(ifname.encode()))
        fcntl.ioctl(sock, SIOCGMIIPHY, ifr)
        ifr.data.reg_num = reg
        fcntl.ioctl(sock, SIOCGMIIPHY, ifr)
        return ifr.data.val_out
