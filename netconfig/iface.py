#!/usr/bin/python
# Copyright: 2017, CCX Technologies

import fcntl
import socket
import ctypes
import struct
import errno

# =================== from linux headers ========================

IFF_UP = (1 << 0)
IFF_BROADCAST = (1 << 1)
IFF_DEBUG = (1 << 2)
IFF_LOOPBACK = (1 << 3)
IFF_POINTOPOINT = (1 << 4)
IFF_NOTRAILERS = (1 << 5)
IFF_RUNNING = (1 << 6)
IFF_NOARP = (1 << 7)
IFF_PROMISC = (1 << 8)
IFF_ALLMULTI = (1 << 9)
IFF_MASTER = (1 << 10)
IFF_SLAVE = (1 << 11)
IFF_MULTICAST = (1 << 12)
IFF_PORTSEL = (1 << 13)
IFF_AUTOMEDIA = (1 << 14)
IFF_DYNAMIC = (1 << 15)
IFF_LOWER_UP = (1 << 16)
IFF_DORMANT = (1 << 17)
IFF_ECHO = (1 << 18)

# Routing table calls.
SIOCADDRT = 0x890B  # add routing table entry
SIOCDELRT = 0x890C  # delete routing table entry
SIOCRTMSG = 0x890D  # call to routing system

# Socket configuration controls.
SIOCGIFNAME = 0x8910  # get iface name
SIOCSIFLINK = 0x8911  # set iface channel
SIOCGIFCONF = 0x8912  # get iface list
SIOCGIFFLAGS = 0x8913  # get flags
SIOCSIFFLAGS = 0x8914  # set flags
SIOCGIFADDR = 0x8915  # get PA address
SIOCSIFADDR = 0x8916  # set PA address
SIOCGIFDSTADDR = 0x8917  # get remote PA address
SIOCSIFDSTADDR = 0x8918  # set remote PA address
SIOCGIFBRDADDR = 0x8919  # get broadcast PA address
SIOCSIFBRDADDR = 0x891a  # set broadcast PA address
SIOCGIFNETMASK = 0x891b  # get network PA mask
SIOCSIFNETMASK = 0x891c  # set network PA mask
SIOCGIFMETRIC = 0x891d  # get metric
SIOCSIFMETRIC = 0x891e  # set metric
SIOCGIFMEM = 0x891f  # get memory address (BSD)
SIOCSIFMEM = 0x8920  # set memory address (BSD)
SIOCGIFMTU = 0x8921  # get MTU size
SIOCSIFMTU = 0x8922  # set MTU size
SIOCSIFNAME = 0x8923  # set interface name
SIOCSIFHWADDR = 0x8924  # set hardware address
SIOCGIFENCAP = 0x8925  # get/set encapsulations
SIOCSIFENCAP = 0x8926
SIOCGIFHWADDR = 0x8927  # Get hardware address
SIOCGIFSLAVE = 0x8929  # Driver slaving support
SIOCSIFSLAVE = 0x8930
SIOCADDMULTI = 0x8931  # Multicast address lists
SIOCDELMULTI = 0x8932
SIOCGIFINDEX = 0x8933  # name -> if_index mapping
SIOGIFINDEX = SIOCGIFINDEX  # misprint compatibility :-)
SIOCSIFPFLAGS = 0x8934  # set/get extended flags set
SIOCGIFPFLAGS = 0x8935
SIOCDIFADDR = 0x8936  # delete PA address
SIOCSIFHWBROADCAST = 0x8937  # set hardware broadcast addr
SIOCGIFCOUNT = 0x8938  # get number of devices

SIOCGIFBR = 0x8940  # Bridging support
SIOCSIFBR = 0x8941  # Set bridging options

SIOCGIFTXQLEN = 0x8942  # Get the tx queue length
SIOCSIFTXQLEN = 0x8943  # Set the tx queue length

SIOCETHTOOL = 0x8946  # Ethtool interface

SIOCGMIIPHY = 0x8947  # Get address of MII PHY in use.
SIOCGMIIREG = 0x8948  # Read MII PHY register.
SIOCSMIIREG = 0x8949  # Write MII PHY register.

SIOCWANDEV = 0x894A  # get/set netdev parameters

SIOCOUTQNSD = 0x894B  # output queue size (not sent only)

# ARP cache control calls.
SIOCDARP = 0x8953  # delete ARP table entry
SIOCGARP = 0x8954  # get ARP table entry
SIOCSARP = 0x8955  # set ARP table entry

# RARP cache control calls.
SIOCDRARP = 0x8960  # delete RARP table entry
SIOCGRARP = 0x8961  # get RARP table entry
SIOCSRARP = 0x8962  # set RARP table entry

# Driver configuration calls

SIOCGIFMAP = 0x8970  # Get device parameters
SIOCSIFMAP = 0x8971  # Set device parameters

# DLCI configuration calls

SIOCADDDLCI = 0x8980  # Create new DLCI device
SIOCDELDLCI = 0x8981  # Delete DLCI device

SIOCGIFVLAN = 0x8982  # 802.1Q VLAN support
SIOCSIFVLAN = 0x8983  # Set 802.1Q VLAN options

# bonding calls

SIOCBONDENSLAVE = 0x8990  # enslave a device to the bond
SIOCBONDRELEASE = 0x8991  # release a slave from the bond
SIOCBONDSETHWADDR = 0x8992  # set the addr of the bond
SIOCBONDSLAVEINFOQUERY = 0x8993  # return info about slave state
SIOCBONDINFOQUERY = 0x8994  # return info about bond state
SIOCBONDCHANGEACTIVE = 0x8995  # update to a new active slave

# bridge calls
SIOCBRADDBR = 0x89a0  # create new bridge device
SIOCBRDELBR = 0x89a1  # remove bridge device
SIOCBRADDIF = 0x89a2  # add interface to bridge
SIOCBRDELIF = 0x89a3  # remove interface from bridge

# hardware time stamping: parameters in linux/net_tstamp.h
SIOCSHWTSTAMP = 0x89b0  # set and get config
SIOCGHWTSTAMP = 0x89b1  # get config


class sockaddr_gen(ctypes.Structure):
    _fields_ = [
            ("sa_family", ctypes.c_uint16),
            ("sa_data", (ctypes.c_uint8 * 22)),
    ]


class in_addr(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
            ("s_addr", ctypes.c_uint32),
    ]


class sockaddr_in(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
            ("sin_family", ctypes.c_ushort),
            ("sin_port", ctypes.c_ushort),
            ("sin_addr", in_addr),
            ("sin_zero", (ctypes.c_uint8 * 16)),
    ]


class in6_u(ctypes.Union):
    _pack_ = 1
    _fields_ = [
            ("u6_addr8", (ctypes.c_uint8 * 16)),
            ("u6_addr16", (ctypes.c_uint16 * 8)),
            ("u6_addr32", (ctypes.c_uint32 * 4)),
    ]


class in6_addr(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
            ("in6_u", in6_u),
    ]


class sockaddr_in6(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
            ("sin6_family", ctypes.c_short),
            ("sin6_port", ctypes.c_ushort),
            ("sin6_flowinfo", ctypes.c_uint32),
            ("sin6_addr", in6_addr),
            ("sin6_scope_id", ctypes.c_uint32),
    ]


class sockaddr_dl(ctypes.Structure):
    _fields_ = [
            ("sdl_len", ctypes.c_uint8), ("sdl_family", ctypes.c_uint8),
            ("sdl_index", ctypes.c_uint16), ("sdl_type", ctypes.c_uint8),
            ("sdl_nlen", ctypes.c_uint8), ("sdl_alen", ctypes.c_uint8),
            ("sdl_slen", ctypes.c_uint8)
    ]


class sockaddr(ctypes.Union):
    _pack_ = 1
    _fields_ = [
            ('gen', sockaddr_gen), ('in4', sockaddr_in), ('in6', sockaddr_in6)
    ]


class ifmap(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
            ('mem_start', ctypes.c_ulong), ('mem_end', ctypes.c_ulong),
            ('base_addr', ctypes.c_ushort), ('irq', ctypes.c_ubyte),
            ('dma', ctypes.c_ubyte), ('port', ctypes.c_ubyte)
    ]


IFNAMSIZ = 16
IFHWADDRLEN = 6


class ifr_data(ctypes.Union):
    _pack_ = 1
    _fields_ = [
            ('ifr_addr', sockaddr), ('ifr_dstaddr', sockaddr),
            ('ifr_broadaddr', sockaddr), ('ifr_netmask', sockaddr),
            ('ifr_hwaddr', sockaddr), ('ifr_flags', ctypes.c_short),
            ('ifr_ifindex', ctypes.c_int), ('ifr_ifqlen', ctypes.c_int),
            ('ifr_metric', ctypes.c_int), ('ifr_mtu', ctypes.c_int),
            ('ifr_map', ifmap), ('ifr_slave', (ctypes.c_ubyte * IFNAMSIZ)),
            ('ifr_newname', (ctypes.c_ubyte * IFNAMSIZ)),
            ('ifr_data', ctypes.c_void_p)
    ]


class ifreq(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
            ('ifr_name', (ctypes.c_ubyte * IFNAMSIZ)),
            ('data', ifr_data),
    ]


# ===============================================================


def _get_sin_addr(sockaddr):
    if sockaddr.gen.sa_family == socket.AF_INET:
        return sockaddr.in4.sin_addr.s_addr
    if sockaddr.gen.sa_family == socket.AF_INET6:
        return sockaddr.in6.sin6_addr.in6_u
    return 0


def _sockaddr_from_string(addr):
    sin4 = sockaddr()

    sin4.in4.sin_family = socket.AF_INET
    sin4.in4.sin_addr.s_addr = struct.unpack(
            '<L', socket.inet_pton(socket.AF_INET, addr)
    )[0]
    return sin4


def _sockaddr_to_string(sockaddr):
    if sockaddr.gen.sa_family == 0:
        return 'None'

    p = struct.pack('<L', _get_sin_addr(sockaddr))
    return socket.inet_ntop(sockaddr.gen.sa_family, p)


# ===============================================================


class Iface:
    """A simplified linux network device configuration and control interface.

        It can be used in situations where pyroute2 is over-kill.
    """
    @staticmethod
    def get_all():
        ifr = ifreq()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0) as skt:
            ifaces = []
            for i in range(1, 64):
                ifr.data.ifr_ifindex = i
                try:
                    fcntl.ioctl(skt, SIOCGIFNAME, ifr)
                except OSError as exc:
                    if exc.errno == errno.ENODEV:
                        break
                    else:
                        raise
                ifaces.append(ctypes.string_at(ifr.ifr_name).decode("utf-8"))
        return ifaces

    def __init__(self, ifname):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._name = (ctypes.c_ubyte * IFNAMSIZ)(*bytearray(ifname.encode()))

    def _ifreq(self):
        ifr = ifreq()
        ifr.ifr_name = (ctypes.c_ubyte * IFNAMSIZ)(*bytearray(self._name))
        return ifr

    def get_index(self):
        ifr = self._ifreq()
        fcntl.ioctl(self.sock, SIOCGIFINDEX, ifr)
        return ifr.data.ifr_ifindex

    def get_up(self):
        ifr = self._ifreq()
        fcntl.ioctl(self.sock, SIOCGIFFLAGS, ifr)
        return (ifr.data.ifr_flags & IFF_UP) == IFF_UP

    def set_up(self, value):
        ifr = self._ifreq()
        fcntl.ioctl(self.sock, SIOCGIFFLAGS, ifr)
        if value and not (ifr.data.ifr_flags & IFF_UP):
            ifr.data.ifr_flags |= IFF_UP
            fcntl.ioctl(self.sock, SIOCSIFFLAGS, ifr)
        elif not value and (ifr.data.ifr_flags & IFF_UP):
            ifr.data.ifr_flags &= ~IFF_UP
            fcntl.ioctl(self.sock, SIOCSIFFLAGS, ifr)

    def get_mtu(self):
        ifr = self._ifreq()
        fcntl.ioctl(self.sock, SIOCGIFMTU, ifr)
        return int(ifr.data.ifr_mtu)

    def set_mtu(self, value):
        ifr = self._ifreq()
        ifr.data.ifr_mtu = int(value)
        fcntl.ioctl(self.sock, SIOCSIFMTU, ifr)

    def get_mac_addr(self):
        ifr = self._ifreq()
        fcntl.ioctl(self.sock, SIOCGIFHWADDR, ifr)
        addy = ifr.data.ifr_hwaddr.gen.sa_data

        mac = []
        for i in addy[:IFHWADDRLEN]:
            mac.append(f'{i:02x}')

        return '-'.join(mac)

    def set_mac_addr(self, value):
        ifr = self._ifreq()
        for i, a in enumerate(value.replace('-', ':').split(':')):
            ifr.data.ifr_hwaddr.sin_addr.s_addr[i] = int(a, 16)
        fcntl.ioctl(self.sock, SIOCSIFHWADDR, ifr)

    def get_ip_addr(self):
        ifr = self._ifreq()
        try:
            fcntl.ioctl(self.sock, SIOCGIFADDR, ifr)
        except OSError as exc:
            if exc.errno == errno.EADDRNOTAVAIL:
                return '0.0.0.0'
            else:
                raise
        return _sockaddr_to_string(ifr.data.ifr_addr)

    def set_ip_addr(self, value):
        ifr = self._ifreq()
        ifr.data.ifr_addr = _sockaddr_from_string(value)
        fcntl.ioctl(self.sock, SIOCSIFADDR, ifr)

    def get_broadcast_addr(self):
        ifr = self._ifreq()
        try:
            fcntl.ioctl(self.sock, SIOCGIFBRDADDR, ifr)
        except OSError as exc:
            if exc.errno == errno.EADDRNOTAVAIL:
                return '0.0.0.0'
            else:
                raise
        return _sockaddr_to_string(ifr.data.ifr_broadaddr)

    def set_broadcast_addr(self, value):
        ifr = self._ifreq()
        ifr.data.ifr_broadaddr = _sockaddr_from_string(value)
        fcntl.ioctl(self.sock, SIOCSIFBRDADDR, ifr)

    def get_netmask_addr(self):
        ifr = self._ifreq()
        try:
            fcntl.ioctl(self.sock, SIOCGIFNETMASK, ifr)
        except OSError as exc:
            if exc.errno == errno.EADDRNOTAVAIL:
                return '0.0.0.0'
            else:
                raise
        return _sockaddr_to_string(ifr.data.ifr_netmask)

    def set_netmask_addr(self, value):
        ifr = self._ifreq()
        ifr.data.ifr_netmask = _sockaddr_from_string(value)
        fcntl.ioctl(self.sock, SIOCSIFNETMASK, ifr)
