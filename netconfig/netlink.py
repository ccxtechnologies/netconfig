#!/usr/bin/python
# Copyright: 2017-2022, CCX Technologies

import socket
import struct
import asyncio

from .iface import Iface

BUFFER_SIZE = 1048576
READ_SIZE = 65535

# == from linux headers

RTMGRP_LINK = 1

RTM_NEWLINK = 16

NLMSG_NOOP = 0x1  # Nothing
NLMSG_ERROR = 0x2  # Error

IFF_UP = (1 << 0)
IFF_LOWER_UP = (1 << 16)

IFLA_IFNAME = 3


async def monitor_state_change(queues):
    """Monitors for up / lower_up state changes on network interfaces.

    Loads a message dictionary into queues, with keys for different events.
    Currently support "up", "lower_up", and "start".

    Args:
        queues: a dictionary of queues, one queue for each interface
            to track, the keys are the interface names, ie.
            { "eth0": asyncio.Queue(), "eth1": asyncio.Queue() }
    """

    with socket.socket(
            socket.AF_NETLINK, socket.SOCK_RAW, socket.NETLINK_ROUTE
    ) as skt:

        skt.setblocking(0)
        skt.bind((0, RTMGRP_LINK))
        skt.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)

        start_sent = False

        # I would like to use something like asyncio.open_connection but
        # it doesn't understand socket.AF_NETLINK / socket.SOCK_RAW so have to
        # use the _create_connection_transport method
        loop = asyncio.get_event_loop()

        if isinstance(loop, asyncio.unix_events._UnixSelectorEventLoop):  # noqa pylint: disable=protected-access
            reader = asyncio.streams.StreamReader(loop=loop)
            protocol = asyncio.streams.StreamReaderProtocol(reader, loop=loop)
            await loop._create_connection_transport(  # noqa pylint: disable=protected-access
                    skt, lambda: protocol, None, ''
            )

        while True:
            # NOTE: There is a bug in the stock asyncio library and this
            # will this will only work with uvloop, refer to an older
            # version based on loop._create_connection_transport
            try:
                if isinstance(
                        loop
                ) == asyncio.unix_events._UnixSelectorEventLoop:  # noqa pylint: disable=protected-access
                    data = await reader.read(READ_SIZE)
                else:
                    data = await loop.sock_recv(skt, READ_SIZE)
            except OSError as exc:
                if exc.errno == 105:
                    # No buffer space so retry later
                    start_sent = False
                    await asyncio.sleep(3.2)
                    continue
                else:
                    raise

            msg_len, msg_type, flags, _, _ = struct.unpack("=LHHLL", data[:16])

            if msg_type == NLMSG_NOOP:
                continue
            elif msg_type == NLMSG_ERROR:
                raise RuntimeError("Netlink Message Error")

            if msg_type != RTM_NEWLINK:
                continue

            data = data[16:]
            _, _, _, _, flags, _ = struct.unpack("=BBHiII", data[:16])

            messages = {}
            if flags & IFF_LOWER_UP:
                messages["lower_up"] = True
            else:
                messages["lower_up"] = False

            if flags & IFF_UP:
                messages["up"] = True
            else:
                messages["up"] = False

            remaining = msg_len - 32
            data = data[16:]

            while remaining:
                rta_len, rta_type = struct.unpack("=HH", data[:4])

                # This check comes from RTA_OK
                if rta_len < 4:
                    break

                rta_data = data[4:rta_len - 1]

                increment = (rta_len + 4 - 1) & ~(4 - 1)
                data = data[increment:]
                remaining -= increment

                if rta_type == IFLA_IFNAME:
                    iface = rta_data.decode("utf-8")

            if iface in queues:
                await queues[iface].put(messages)

            # Once the first message is sent the monitor is ready,
            # so send start to all interfaces
            if not start_sent:
                for device in Iface.get_all():
                    if device not in queues:
                        continue

                    await queues[device].put({"start": True})

                start_sent = True
