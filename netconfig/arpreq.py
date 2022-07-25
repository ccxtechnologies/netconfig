#!/usr/bin/python
# Copyright: 2022, CCX Technologies

import socket
import netaddr

from struct import pack, unpack


def _val2int(val):
    return int(''.join([f"{ord(c):02d}" for c in val]), 16)


def arpreq(
        src_ipaddr: netaddr.IPAddress, dst_ipaddr: netaddr.IPAddress,
        if_name: str
) -> bool:
    _socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.SOCK_RAW)
    _socket.bind((if_name, socket.SOCK_RAW))

    frame = [
            pack('!6B',
                 *(0xFF, ) * 6),
            _socket.getsockname()[4],
            pack('!H', 0x0806),
            pack('!HHBB', 0x0001, 0x0800, 0x0006, 0x0004),
            pack('!H', 0x0001),
            _socket.getsockname()[4],
            pack('!4B', *src_ipaddr.words),
            pack('!6B',
                 *(0, ) * 6),
            pack('!4B', *dst_ipaddr.words)
    ]

    _socket.send(b''.join(frame))

    while 0xBeef:
        frame = _socket.recv(1024)

        proto_type = int.from_bytes(frame[12:14], "big")
        if proto_type != 0x0806:
            continue

        op = int.from_bytes(frame[20:22], "big")
        if op != 2:
            continue

        arp_headers = frame[18:20]
        hw_size, pt_size = [
                int.from_bytes(h, "big") for h in unpack('!1s1s', arp_headers)
        ]
        total_addresses_byte = hw_size * 2 + pt_size * 2
        arp_addrs = frame[22:22 + total_addresses_byte]
        src_hw, src_pt, _, _ = unpack(
                '!%ss%ss%ss%ss' % (hw_size, pt_size, hw_size, pt_size),
                arp_addrs
        )

        if src_pt == pack('!4B', *dst_ipaddr.words):
            return netaddr.EUI(int.from_bytes(src_hw, "big"))
