#!/usr/bin/python
# Copyright: 2020, CCX Technologies

import asyncio

from functools import partial
from pyroute2 import WireGuard


class WGRoute:
    def __init__(self, loop=None, executor=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.executor = executor
        self.wg = WireGuard()

    async def set(
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
                        self.wg.set, ifname, ifindex, listen_port, fwmark,
                        private_key
                )
        )

    async def info(self, ifname=None, ifindex=None):
        return await self.loop.run_in_executor(
                self.executor, partial(self.wg.info, ifname, ifindex)
        )

    def close(self):
        self.wg.close()
