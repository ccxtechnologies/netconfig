#!/usr/bin/python
# Copyright: 2020, CCX Technologies

import asyncio
import netaddr
import time
from pyroute2 import IPRoute
from pyroute2 import IPLinkRequest
from pyroute2.netlink.exceptions import NetlinkError
from functools import partial


class AIPRoute():
    def __init__(self, loop=None, executor=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.executor = executor
        self.ipr = IPRoute()

    def close(self):
        if not self.ipr.closed:
            self.ipr.close()

    def _get_id(self, device_name: str) -> None:
        try:
            device_ids = self.ipr.link_lookup(ifname=device_name)

        except OSError as exc:
            # sometimes calling this will lose the link for some reason
            if exc.errno == 9:
                self.ipr.close()
                self.ipr = IPRoute()
                device_ids = self.ipr.link_lookup(ifname=device_name)

        try:
            return device_ids[0]
        except IndexError:
            return 0

    def _get_name(self, device_id: int) -> str:
        try:
            links = self.ipr.get_links(device_id)
        except NetlinkError:
            return None
        try:
            return links[0].get_attr('IFLA_IFNAME')
        except (IndexError, KeyError):
            return None

    def _delete_device(self, device_name: str) -> None:
        try:
            self.ipr.link('del', ifname=device_name)
        except NetlinkError as exc:
            if exc.code == 19:
                # if it doesn't exist that's okay
                pass
            else:
                raise

    def _set_master(self, device_id: int, master_id: int) -> None:
        try:
            self.ipr.link('set', index=device_id, master=master_id)

        except (OSError, NetlinkError):
            raise RuntimeError(
                    f"Failed to add {device_id} to bridge {master_id}"
            )

    def _set_stp(self, device_id: int, stp: int) -> None:
        try:
            self.ipr.link(
                    'set',
                    **IPLinkRequest(
                            {
                                    'index': device_id,
                                    'kind': 'bridge',
                                    'br_stp_state': stp
                            }
                    )
            )

        except (OSError, NetlinkError):
            raise RuntimeError(f"Failed to set {device_id} stp to {stp}")

    def _add_device(
            self, device_name: str, device_type: str, **kwargs
    ) -> None:
        try:
            self.ipr.link(
                    'add', ifname=device_name, kind=device_type, **kwargs
            )
        except NetlinkError as exc:
            if exc.code == 17:
                raise FileExistsError(
                        f"Device {device_name} already exists"
                ) from exc
            else:
                raise

    def _set_address(self, device_id: int, address: netaddr.IPNetwork) -> None:
        self.ipr.flush_addr(index=device_id)

        if bool(address.ip) and bool(address.prefixlen):
            self.ipr.addr(
                    'add',
                    index=device_id,
                    address=str(address.ip),
                    mask=address.prefixlen
            )

    def _set_mac(self, device_id: int, mac: netaddr.EUI) -> None:
        if mac:
            info = self.ipr.get_links(device_id)[0]
            existing_mac = netaddr.EUI(info.get_attr("IFLA_ADDRESS"))
            if existing_mac != mac:
                self.ipr.link('set', index=device_id, address=str(mac))

    def _set_device_name(self, device_id: int, device_name: str) -> None:
        if not device_name:
            return

        try:
            self.ipr.link("set", index=device_id, ifname=device_name)
        except NetlinkError as exc:
            if exc.code == 16:
                time.sleep(2)
                self.ipr.link("set", index=device_id, ifname=device_name)
            else:
                raise

    def _set_mtu(self, device_id: int, mtu: int) -> None:
        self.ipr.link('set', index=device_id, mtu=mtu)

    def _set_up(self, device_id: int, state: bool) -> None:
        self.ipr.link('set', index=device_id, state='up' if state else 'down')

    def _flush_rules(self, **kwargs) -> None:
        try:
            self.ipr.flush_rules(**kwargs)
        except (OSError, NetlinkError):
            pass

    def _delete_rule(self, **kwargs) -> None:
        try:
            self.ipr.rule('delete', **kwargs)
        except NetlinkError:
            pass

    def _add_rule(self, **kwargs) -> None:
        try:
            self.ipr.rule('add', **kwargs)
        except NetlinkError as exc:
            if exc.code == 17:
                pass
            else:
                raise RuntimeError(f"Failed to add rule {kwargs}: {exc}")

    def _flush_routes(self, **kwargs) -> None:
        try:
            self.ipr.flush_routes(**kwargs)
        except (OSError, NetlinkError):
            pass

    def _delete_route(self, **kwargs) -> None:
        try:
            self.ipr.route('delete', **kwargs)
        except NetlinkError:
            pass

    def _add_route(self, **kwargs) -> None:
        try:
            self.ipr.route('add', **kwargs)
        except NetlinkError as exc:
            if exc.code == 17:
                time.sleep(0.250)
                try:
                    self.ipr.route('add', **kwargs)
                except NetlinkError as exc:
                    raise RuntimeError(f"Failed to add route {kwargs}: {exc}")
            else:
                raise RuntimeError(f"Failed to add route {kwargs}: {exc}")

    def _replace_tc(
            self, kind: str, device_id: int, handle: int, **kwargs
    ) -> None:
        self.ipr.tc("replace", kind, device_id, handle, **kwargs)

    def _delete_tc(
            self, kind: str, device_id: int, handle: int, **kwargs
    ) -> None:
        try:
            self.ipr.tc("del", kind, device_id, handle, **kwargs)
        except NetlinkError:
            pass

    def _add_filter_tc(self, kind: str, device_id: int, **kwargs) -> None:
        self.ipr.tc("add-filter", kind, device_id, **kwargs)

    def _run_routine(self, routine):
        try:
            routine(self.ipr)
        except NetlinkError as exc:
            raise RuntimeError(f"Netlink error in {routine}: {exc}")

    async def get_id(self, device_name: str) -> int:
        if not device_name:
            return 0

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
        if not device_name:
            return

        await self.loop.run_in_executor(
                self.executor, partial(self._delete_device, device_name)
        )

    async def add_device(
            self, device_name: str, device_type: str, **kwargs
    ) -> None:
        if not device_name or not device_type:
            return

        await self.loop.run_in_executor(
                self.executor,
                partial(self._add_device, device_name, device_type, **kwargs)
        )

    async def set_master(self, device_id: int, master_id: int) -> None:
        if device_id <= 0 or master_id < 0:
            return

        await self.loop.run_in_executor(
                self.executor, partial(self._set_master, device_id, master_id)
        )

    async def set_stp(self, device_id: int, stp: bool) -> None:
        if device_id <= 0:
            return

        await self.loop.run_in_executor(
                self.executor,
                partial(self._set_stp, device_id, 1 if stp else 0)
        )

    async def set_address(
            self, device_id: int, address: netaddr.IPNetwork
    ) -> None:
        if device_id <= 0:
            return

        await self.loop.run_in_executor(
                self.executor, partial(self._set_address, device_id, address)
        )

    async def set_mtu(self, device_id: int, mtu: int) -> None:
        if device_id <= 0 or mtu <= 0:
            return

        await self.loop.run_in_executor(
                self.executor, partial(self._set_mtu, device_id, mtu)
        )

    async def set_mac(self, device_id: int, mac: netaddr.EUI) -> None:
        if device_id <= 0:
            return

        await self.loop.run_in_executor(
                self.executor, partial(self._set_mac, device_id, mac)
        )

    async def set_device_name(self, device_id: int, device_name: str) -> None:
        if device_id <= 0:
            return

        await self.loop.run_in_executor(
                self.executor,
                partial(self._set_device_name, device_id, device_name)
        )

    async def set_up(self, device_id: int, state: bool) -> None:
        if device_id <= 0:
            return

        await self.loop.run_in_executor(
                self.executor, partial(self._set_up, device_id, state)
        )

    async def flush_rules(self, **kwargs) -> None:
        await self.loop.run_in_executor(
                self.executor, partial(self._flush_rules, **kwargs)
        )

    async def delete_rule(self, **kwargs) -> None:
        await self.loop.run_in_executor(
                self.executor, partial(self._delete_rule, **kwargs)
        )

    async def add_rule(self, **kwargs) -> None:
        await self.loop.run_in_executor(
                self.executor, partial(self._add_rule, **kwargs)
        )

    async def flush_routes(self, **kwargs) -> None:
        await self.loop.run_in_executor(
                self.executor, partial(self._flush_routes, **kwargs)
        )

    async def delete_route(self, **kwargs) -> None:
        await self.loop.run_in_executor(
                self.executor, partial(self._delete_route, **kwargs)
        )

    async def add_route(self, **kwargs) -> None:
        await self.loop.run_in_executor(
                self.executor, partial(self._add_route, **kwargs)
        )

    async def replace_tc(
            self,
            kind: str,
            device_id: int,
            handle: int = None,
            **kwargs
    ) -> None:
        await self.loop.run_in_executor(
                self.executor,
                partial(self._replace_tc, kind, device_id, handle, **kwargs)
        )

    async def delete_tc(
            self, kind: str, device_id: int, handle: int, **kwargs
    ) -> None:
        await self.loop.run_in_executor(
                self.executor,
                partial(self._delete_tc, kind, device_id, handle, **kwargs)
        )

    async def add_filter_tc(self, kind: str, device_id: int, **kwargs) -> None:
        await self.loop.run_in_executor(
                self.executor,
                partial(self._add_filter_tc, kind, device_id, **kwargs)
        )

    async def run_routine(self, routine):
        return await self.loop.run_in_executor(
                self.executor, partial(self._run_routine, routine)
        )
