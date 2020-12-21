#!/usr/bin/python
# Copyright: 2020, CCX Technologies

import asyncio
import netaddr
from pyroute2 import IPRoute
from pyroute2.netlink.exceptions import NetlinkError
from functools import partial


class AIPRoute():
    def __init__(self, loop=None, executor=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.executor = executor

    def _get_id(self, device_name: str) -> None:
        with IPRoute() as ipr:
            device_ids = ipr.link_lookup(ifname=device_name)

            try:
                return device_ids[0]
            except IndexError:
                return 0

    def _get_name(self, device_id: int) -> str:
        with IPRoute() as ipr:
            links = ipr.get_links(device_id)
            try:
                return links[0].get_attr('IFLA_IFNAME')
            except (IndexError, KeyError):
                return None

    def _delete_device(self, device_name: str) -> None:
        with IPRoute() as ipr:
            try:
                ipr.link('del', ifname=device_name)
            except NetlinkError as exc:
                if exc.code == 19:
                    # if it doesn't exist that's okay
                    pass
                else:
                    raise

    def _set_master(self, device_id: int, master_id: int) -> None:
        with IPRoute() as ipr:
            try:
                ipr.link('set', index=device_id, master=master_id)

            except (OSError, NetlinkError):
                raise RuntimeError(
                        f"Failed to add {device_id} to bridge {master_id}"
                )

    def _add_device(self, device_name: str, device_type: str) -> None:
        with IPRoute() as ipr:
            ipr.link('add', ifname=device_name, kind=device_type)

    def _set_address(self, device_id: int, address: netaddr.IPNetwork) -> None:
        with IPRoute() as ipr:
            ipr.flush_addr(index=device_id)

            if bool(address.ip) and bool(address.prefixlen):
                ipr.addr(
                        'add',
                        index=device_id,
                        address=str(address.ip),
                        mask=address.prefixlen
                )

    def _set_mtu(self, device_id: int, mtu: int) -> None:
        with IPRoute() as ipr:
            ipr.link('set', index=device_id, mut=mtu)

    def _set_up(self, device_id: int, state: bool) -> None:
        with IPRoute() as ipr:
            ipr.link('set', index=device_id, state='up' if state else 'down')

    async def get_id(self, device_name: str) -> int:
        return await self.loop.run_in_executor(
                self.executor, partial(self._get_id, device_name)
        )

    async def get_name(self, device_id: int) -> str:
        if device_id <= 0:
            return None

        return await self.loop.run_in_executor(
                self.executor, partial(self._get_name, device_id)
        )

    async def delete_device(self, device_name: str) -> None:
        await self.loop.run_in_executor(
                self.executor, partial(self._delete_device, device_name)
        )

    async def add_device(self, device_name: str, device_type: str) -> None:
        await self.loop.run_in_executor(
                self.executor,
                partial(self._add_device, device_name, device_type)
        )

    async def set_master(self, device_id: int, master_id: int) -> None:
        await self.loop.run_in_executor(
                self.executor, partial(self._set_master, device_id, master_id)
        )

    async def set_address(
            self, device_id: int, address: netaddr.IPNetwork
    ) -> None:
        await self.loop.run_in_executor(
                self.executor, partial(self._set_address, device_id, address)
        )

    async def set_mtu(self, device_id: int, mtu: int) -> None:
        await self.loop.run_in_executor(
                self.executor, partial(self._set_mtu, device_id, mtu)
        )

    async def set_up(self, device_id: int, state: bool) -> None:
        await self.loop.run_in_executor(
                self.executor, partial(self._set_up, device_id, state)
        )
