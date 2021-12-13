# Copyright: 2017, CCX Technologies
# based on: https://gist.github.com/artizirk/3a8efeee33fce34baf6047aed7205a2e

import struct
import base64
import asyncio
from socket import AF_INET, AF_INET6
from socket import inet_ntop
from functools import partial

from pyroute2.netlink import NLM_F_REQUEST, NLM_F_DUMP, NLM_F_ACK
from pyroute2.netlink import nla, nla_base
from pyroute2.netlink import genlmsg
from pyroute2.netlink.generic import GenericNetlinkSocket

WG_GENL_NAME = "wireguard"
WG_GENL_VERSION = 1

WG_KEY_LEN = 32
WG_KEY_LEN_BASE64 = 44

WG_CMD_GET_DEVICE = 0
WG_CMD_SET_DEVICE = 1

WGDEVICE_F_REPLACE_PEERS = 1
WGPEER_F_REMOVE_ME = 1
WGPEER_F_REPLACE_ALLOWEDIPS = 2


class wireguardcmd(genlmsg):
    prefix = 'WGDEVICE_A_'
    nla_map = (
            ('WGDEVICE_A_UNSPEC', 'none'), ('WGDEVICE_A_IFINDEX', 'uint32'),
            ('WGDEVICE_A_IFNAME',
             'asciiz'), ('WGDEVICE_A_PRIVATE_KEY', 'cdata'),
            ('WGDEVICE_A_PUBLIC_KEY', 'cdata'), ('WGDEVICE_A_FLAGS', 'uint32'),
            ('WGDEVICE_A_LISTEN_PORT', 'uint16'),
            ('WGDEVICE_A_FWMARK', 'uint32'), ('WGDEVICE_A_PEERS', '*wgpeer')
    )

    class wgpeer(nla):
        prefix = 'WGPEER_A_'
        nla_map = (
                ('WGPEER_A_UNSPEC', 'none'), ('WGPEER_A_PUBLIC_KEY', 'cdata'),
                ('WGPEER_A_PRESHARED_KEY',
                 'cdata'), ('WGPEER_A_FLAGS',
                            'uint32'), ('WGPEER_A_ENDPOINT', 'sockaddr'),
                ('WGPEER_A_PERSISTENT_KEEPALIVE_INTERVAL',
                 'uint16'), ('WGPEER_A_LAST_HANDSHAKE_TIME',
                             'timespec64'), ('WGPEER_A_RX_BYTES', 'uint64'),
                ('WGPEER_A_TX_BYTES',
                 'uint64'), ('WGPEER_A_ALLOWEDIPS', '*wgallowedip')
        )

        class sockaddr(nla_base):
            """
            # IPv4
            struct sockaddr_in {
               uint16_t      sin_family; /* address family: AF_INET */
               uint16_t      sin_port;   /* port in network byte order */
               uint32_t      sin_addr;   /* internet address */
            };

            # IPv6
            struct sockaddr_in6 {
               uint16_t        sin6_family;   /* AF_INET6 */
               uint16_t        sin6_port;     /* port number */
               uint32_t        sin6_flowinfo; /* IPv6 flow information */
               uint8_t         sin6_addr[16]; /* IPv6 address */
               uint32_t        sin6_scope_id; /* Scope ID (new in 2.4) */
            };
            """

            fields = [('value', 's')]
            value: tuple = None

            def encode(self):
                nla_base.encode(self)

            def decode(self):
                nla_base.decode(self)
                family = struct.unpack('H', self['value'][:2])[0]

                if family == AF_INET:
                    port, host = struct.unpack('!H4s', self['value'][2:8])
                    self.value = (inet_ntop(family, host), port)

                elif family == AF_INET6:
                    port, flowinfo, host, scopeid = struct.unpack(
                            '!HI16sI', self['value'][2:28]
                    )
                    self.value = (
                            inet_ntop(family, host), port, flowinfo, scopeid
                    )

        class timespec64(nla):
            fields = [('value', 's')]
            value = None

            def decode(self):
                nla_base.decode(self)

                if len(self['value']) == 16:
                    sec, _ = struct.unpack('qq', self['value'])
                elif len(self['value']) == 12:
                    sec, _ = struct.unpack('ql', self['value'])
                elif len(self['value']) == 8:
                    sec, _ = struct.unpack('ll', self['value'])

                self.value = sec

        class wgallowedip(nla):
            prefix = 'WGALLOWEDIP_A_'
            nla_map = (
                    ('WGALLOWEDIP_A_UNSPEC',
                     'none'), ('WGALLOWEDIP_A_FAMILY',
                               'uint16'), ('WGALLOWEDIP_A_IPADDR', 'ipaddr'),
                    ('WGALLOWEDIP_A_CIDR_MASK', 'uint8')
            )


class WGNetlinkSocket(GenericNetlinkSocket):
    def __init__(self, *args, **kwargs):
        GenericNetlinkSocket.__init__(self, *args, **kwargs)
        GenericNetlinkSocket.bind(
                self, WG_GENL_NAME, wireguardcmd, *args, **kwargs
        )

    def get_device_dump(self, ifname=None, ifindex=None):
        msg = wireguardcmd()
        msg['cmd'] = WG_CMD_GET_DEVICE
        msg['version'] = WG_GENL_VERSION

        if ifname is not None:
            msg['attrs'].append(['WGDEVICE_A_IFNAME', ifname])

        elif ifindex is not None:
            msg['attrs'].append(['WGDEVICE_A_IFINDEX', ifindex])
        else:
            raise ValueError("ifname or ifindex are unset")

        return self.nlm_request(
                msg,
                msg_type=self.prid,
                msg_flags=NLM_F_REQUEST | NLM_F_ACK | NLM_F_DUMP
        )

    def get_peer_stats(self, ifname=None, ifindex=None):
        msg = self.get_device_dump(ifname=ifname, ifindex=ifindex)
        if msg is None:
            return {}

        if msg[0].get_attr('WGDEVICE_A_PEERS') is None:
            return {}

        peers = {}
        for peer in msg[0].get_attr('WGDEVICE_A_PEERS'):
            key = peer.get_attr('WGPEER_A_PUBLIC_KEY')
            last_handshake = peer.get_attr('WGPEER_A_LAST_HANDSHAKE_TIME')
            rx_bytes = peer.get_attr('WGPEER_A_RX_BYTES')
            tx_bytes = peer.get_attr('WGPEER_A_TX_BYTES')
            endpoint = peer.get_attr('WGPEER_A_ENDPOINT')

            peers[key] = (last_handshake, rx_bytes, tx_bytes, endpoint)

        return peers

    def get_device_dict(self, ifname=None, ifindex=None):
        msg = self.get_device_dump(ifname=ifname, ifindex=ifindex)

        ret = {}
        for x in msg:
            dev = ret[x.get_attr('WGDEVICE_A_IFNAME')] = {}

            for key, val in x['attrs']:
                key = key.replace(x.prefix, '', 1).lower()

                if key == 'peers':
                    peers = []
                    for peer in val:
                        p = {}
                        peers.append(p)

                        for peer_key, peer_val in peer['attrs']:
                            peer_key = peer_key.replace(peer.prefix, '',
                                                        1).lower()
                            if peer_key == 'allowedips':
                                allowedips = []

                                for ips in peer_val:
                                    ip = ips.get_attr("WGALLOWEDIP_A_IPADDR")
                                    mask = ips.get_attr(
                                            "WGALLOWEDIP_A_CIDR_MASK"
                                    )
                                    allowedips.append("{}/{}".format(ip, mask))

                                peer_val = allowedips
                            p[peer_key] = peer_val
                    val = peers
                dev[key] = val
        return ret

    def set_device(
            self,
            ifname=None,
            ifindex=None,
            listen_port=None,
            fwmark=None,
            private_key=None
    ):
        msg = wireguardcmd()
        msg['cmd'] = WG_CMD_SET_DEVICE
        msg['version'] = WG_GENL_VERSION

        if ifname is not None:
            msg['attrs'].append(['WGDEVICE_A_IFNAME', ifname])

        elif ifindex is not None:
            msg['attrs'].append(['WGDEVICE_A_IFINDEX', ifindex])

        else:
            raise ValueError("ifname or ifindex are unset")

        if listen_port is not None:
            msg['attrs'].append(['WGDEVICE_A_LISTEN_PORT', listen_port])

        if fwmark is not None:
            msg['attrs'].append(['WGDEVICE_A_FWMARK', fwmark])

        if private_key is not None:
            if type(private_key) != bytes:
                raise ValueError("private_key has to be bytes")
            elif len(private_key) != WG_KEY_LEN_BASE64:
                raise ValueError(
                        f"private_key length has to be {WG_KEY_LEN_BASE64}"
                )
            msg['attrs'].append(
                    ['WGDEVICE_A_PRIVATE_KEY',
                     base64.b64decode(private_key)]
            )

        return self.put(msg, msg_type=self.prid, msg_flags=NLM_F_REQUEST)


class WGRoute:
    def __init__(self, loop=None, executor=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.executor = executor
        self.wg = WGNetlinkSocket()

    async def get_device_dump(self, ifname=None, ifindex=None):
        return await self.loop.run_in_executor(
                self.executor,
                partial(self.wg.get_device_dump, ifname, ifindex)
        )

    async def get_peer_stats(self, ifname=None, ifindex=None):
        return await self.loop.run_in_executor(
                self.executor,
                partial(self.wg.get_peer_stats, ifname, ifindex)
        )

    async def get_device_dict(self, ifname=None, ifindex=None):
        return await self.loop.run_in_executor(
                self.executor,
                partial(self.wg.get_device_dict, ifname, ifindex)
        )

    async def set_device(
            self,
            ifname=None,
            ifindex=None,
            listen_port=None,
            fwmark=None,
            private_key=None
    ):
        return await self.loop.run_in_executor(
                self.executor,
                partial(
                        self.wg.set_device, ifname, ifindex, listen_port,
                        fwmark, private_key
                )
        )

    def close(self):
        self.wg.close()
