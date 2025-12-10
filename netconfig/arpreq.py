#!/usr/bin/python
# Copyright: 2022-2025, CCX Technologies

import socket
import time
import asyncio
from struct import pack, unpack

import netaddr
import async_timeout

READ_SIZE = 1024


async def arpreq(
        src_ipaddr: netaddr.IPAddress,
        dst_ipaddr: netaddr.IPAddress,
        if_name: str,
        timeout: int = 10
) -> bool:
    with socket.socket(
            socket.AF_PACKET, socket.SOCK_RAW, socket.SOCK_RAW
    ) as _socket:
        _socket.setblocking(False)
        _socket.bind((if_name, socket.SOCK_RAW))

        # I would like to use something like asyncio.open_connection but
        # it doesn't understand socket.AF_RAW / socket.SOCK_RAW
        loop = asyncio.get_event_loop()

        frame_list = [
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

        frame: bytes = b''.join(frame_list)

        _socket.send(frame)
        send_time = time.time()
        recv_time = send_time

        while True:
            async with async_timeout.timeout(
                    (timeout + 2) - (recv_time - send_time)
            ):
                frame = await loop.sock_recv(_socket, READ_SIZE)

            recv_time = time.time()

            proto_type = int.from_bytes(frame[12:14], "big")
            if proto_type != 0x0806:
                continue

            op = int.from_bytes(frame[20:22], "big")
            if op != 2:
                continue

            arp_headers = frame[18:20]
            hw_size, pt_size = [
                    int.from_bytes(h, "big")
                    for h in unpack('!1s1s', arp_headers)
            ]
            total_addresses_byte = hw_size * 2 + pt_size * 2
            arp_addrs = frame[22:22 + total_addresses_byte]
            src_hw, src_pt, _, _ = unpack(
                    '!%ss%ss%ss%ss' % (hw_size, pt_size, hw_size, pt_size),
                    arp_addrs
            )

            if src_pt == pack('!4B', *dst_ipaddr.words):
                return netaddr.EUI(int.from_bytes(src_hw, "big"))

            if (recv_time - send_time) > (timeout + 2):
                raise asyncio.TimeoutError(
                        f"No valid ARP response in {timeout} seconds"
                )
