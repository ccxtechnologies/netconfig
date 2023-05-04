#!/usr/bin/python
# Copyright: 2020-2023, CCX Technologies

import asyncio
import netaddr
import time
from pyroute2 import IPRoute
try:
    from pyroute2 import IPLinkRequest
except ImportError:
    IPLinkRequest = dict
from pyroute2.netlink.exceptions import NetlinkError
from functools import partial

# =================== from linux headers ========================

IFF_UP = (1 << 0)
IFF_LOWER_UP = (1 << 16)


class AIPRoute():

    def __init__(self, loop=None, executor=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.executor = executor
        self.ipr = IPRoute()
        self.lock = asyncio.Lock()

    def close(self):
        if not self.ipr.closed:
            self.ipr.close()

    def _get_id(self, device_name: str) -> int:
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

    def _get_up(self, device_id: int) -> bool:
        try:
            links = self.ipr.get_links(device_id)
        except NetlinkError:
            return False

        try:
            ifi_flags = links[0]['flags']
        except (IndexError, KeyError):
            return False

        return (ifi_flags & (IFF_UP | IFF_LOWER_UP)) == (IFF_UP | IFF_LOWER_UP)

    def _get_stats(self, device_id: int) -> bool:
        try:
            links = self.ipr.get_links(device_id)
        except NetlinkError:
            return None

        try:
            return links[0].get_attr('IFLA_STATS64')
        except (IndexError, KeyError):
            return None

    def _get_arp_cache(self, device_id: int, stale_timeout: int = 60) -> dict:
        try:
            response = self.ipr.get_neighbours(ifindex=device_id)
        except NetlinkError:
            return False

        cache = {}
        for r in response:
            mac = None
            address = None
            for name, value in r['attrs']:
                if name == "NDA_DST":
                    address = value
                elif name == "NDA_LLADDR":
                    mac = value
                elif name == "NDA_CACHEINFO":
                    confirmed_secs = value["ndm_confirmed"] / 100
            if mac and address and (confirmed_secs < stale_timeout):
                cache[mac] = address

        return cache

    def _delete_device(self, device_name: str) -> None:
        try:
            self.ipr.link('del', ifname=device_name)
        except NetlinkError as exc:
            if exc.code == 19:
                # if it doesn't exist that's okay
                pass
            elif exc.code == 95:
                # newer kernels can return operation not
                # supported instead of no such device
                pass
            else:
                raise
        else:
            for _ in range(0, 10):
                _id = self._get_id(device_name)
                if not _id:
                    break
            else:
                raise RuntimeError(f"Failed to remove {device_name}")

    def _set_master(self, device_id: int, master_id: int) -> None:
        try:
            self.ipr.link('set', index=device_id, master=master_id)

        except NetlinkError as exc:
            if exc.code == 16:
                # device busy
                time.sleep(2)
                self.ipr.link('set', index=device_id, master=master_id)
            else:
                raise RuntimeError(
                        f"Failed to add {device_id}"
                        f" to bridge {master_id}: {exc}"
                )

        except OSError as exc:
            raise RuntimeError(
                    f"Failed to add {device_id} to bridge {master_id}: {exc}"
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
            elif exc.code == 16:
                # device busy
                time.sleep(2)
                self.ipr.link(
                        'add', ifname=device_name, kind=device_type, **kwargs
                )
            else:
                raise

        for _ in range(0, 10):
            _id = self._get_id(device_name)
            if _id:
                break
        else:
            raise RuntimeError(f"Failed to add {device_name}")

        return _id

    def _flush_address(self, device_id) -> None:
        self.ipr.flush_addr(index=device_id)

    def _set_address(self, device_id: int, address: netaddr.IPNetwork) -> None:
        self.ipr.flush_addr(index=device_id)

        if bool(address.ip) and bool(address.prefixlen):
            self.ipr.addr(
                    'add',
                    index=device_id,
                    address=str(address.ip),
                    mask=address.prefixlen
            )

    def _replace_address(
            self, device_id: int, old_address: netaddr.IPNetwork,
            new_address: netaddr.IPNetwork
    ) -> None:
        if bool(old_address.ip) and bool(old_address.prefixlen):
            try:
                self.ipr.addr(
                        'del',
                        index=device_id,
                        address=str(old_address.ip),
                        mask=old_address.prefixlen
                )
            except NetlinkError:
                # delete can fail if the ip address doesn't exist,
                # but we still want to set it
                pass

        if bool(new_address.ip) and bool(new_address.prefixlen):
            self.ipr.addr(
                    'add',
                    index=device_id,
                    address=str(new_address.ip),
                    mask=new_address.prefixlen
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
                # device busy
                time.sleep(2)
                self.ipr.link("set", index=device_id, ifname=device_name)
            else:
                raise

    def _set_mtu(self, device_id: int, mtu: int) -> None:
        self.ipr.link('set', index=device_id, mtu=mtu)

    def _set_up(self, device_id: int, state: bool) -> None:
        if state:
            self.ipr.link('set', index=device_id, state='up')
        else:
            try:
                self.ipr.link('set', index=device_id, state='down')

            except NetlinkError as exc:
                if exc.code == 19:
                    # if device doesn't exist ignore
                    pass
                else:
                    raise

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
                except NetlinkError as exce:
                    if exce.code == 17:
                        raise FileExistsError(
                                f"Route {kwargs} already exists"
                        ) from exce

                    raise RuntimeError(f"Failed to add route {kwargs}: {exce}")
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

    def get_attr(self, attr_name: str, attrs) -> object:
        if attrs is None:
            return None

        def _nested_values(attr_name, _attrs):
            values = []

            if isinstance(_attrs, list) or isinstance(_attrs, tuple):
                for _attr in _attrs:
                    value = _nested_values(attr_name, _attr)
                    if value:
                        values.append(value)

            else:
                for name, value in _attrs['attrs']:
                    if name == attr_name:
                        values.append(value)

            if not values:
                return None
            elif len(values) == 1:
                return values[0]
            else:
                return values

        return _nested_values(attr_name, attrs)

    def get_nested(self, attr_names: tuple, attrs: dict) -> object:
        _attrs = attrs

        for attr_name in attr_names:
            _attrs = self.get_attr(attr_name, _attrs)
        return _attrs

    async def get_id(self, device_name: str) -> int:
        if not device_name:
            return 0

        async with self.lock:
            return await self.loop.run_in_executor(
                    self.executor, partial(self._get_id, device_name)
            )

    async def get_name(self, device_id: int) -> str:
        if device_id <= 0:
            return None

        async with self.lock:
            return await self.loop.run_in_executor(
                    self.executor, partial(self._get_name, device_id)
            )

    async def get_up(self, device_id: int) -> str:
        if device_id <= 0:
            return None

        async with self.lock:
            return await self.loop.run_in_executor(
                    self.executor, partial(self._get_up, device_id)
            )

    async def get_stats(self, device_id: int) -> str:
        if device_id <= 0:
            return None

        async with self.lock:
            return await self.loop.run_in_executor(
                    self.executor, partial(self._get_stats, device_id)
            )

    async def delete_device(self, device_name: str) -> None:
        if not device_name:
            return

        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor, partial(self._delete_device, device_name)
            )

    async def add_device(
            self, device_name: str, device_type: str, **kwargs
    ) -> int:
        if not device_name or not device_type:
            return

        async with self.lock:
            return await self.loop.run_in_executor(
                    self.executor,
                    partial(
                            self._add_device, device_name, device_type,
                            **kwargs
                    )
            )

    async def set_master(self, device_id: int, master_id: int) -> None:
        if device_id <= 0 or master_id < 0:
            return

        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor,
                    partial(self._set_master, device_id, master_id)
            )

    async def set_stp(self, device_id: int, stp: bool) -> None:
        if device_id <= 0:
            return

        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor,
                    partial(self._set_stp, device_id, 1 if stp else 0)
            )

    async def set_address(
            self, device_id: int, address: netaddr.IPNetwork
    ) -> None:
        if device_id <= 0:
            return

        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor,
                    partial(self._set_address, device_id, address)
            )

    async def flush_address(self, device_id: int) -> None:
        if device_id <= 0:
            return

        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor, partial(self._flush_address, device_id)
            )

    async def replace_address(
            self, device_id: int, old_address: netaddr.IPNetwork,
            new_address: netaddr.IPNetwork
    ) -> netaddr.IPNetwork:
        if device_id <= 0:
            return netaddr.IPNetwork('0.0.0.0/0')

        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor,
                    partial(
                            self._replace_address, device_id, old_address,
                            new_address
                    )
            )
        return new_address

    async def set_mtu(self, device_id: int, mtu: int) -> None:
        if device_id <= 0 or mtu <= 0:
            return

        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor, partial(self._set_mtu, device_id, mtu)
            )

    async def set_mac(self, device_id: int, mac: netaddr.EUI) -> None:
        if device_id <= 0:
            return

        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor, partial(self._set_mac, device_id, mac)
            )

    async def set_device_name(self, device_id: int, device_name: str) -> None:
        if device_id <= 0:
            return

        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor,
                    partial(self._set_device_name, device_id, device_name)
            )

    async def set_up(self, device_id: int, state: bool) -> None:
        if device_id <= 0:
            return

        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor, partial(self._set_up, device_id, state)
            )

    async def get_arp_cache(
            self, device_id: int, stale_timeout: int = 60
    ) -> dict:
        if device_id <= 0:
            return None

        async with self.lock:
            return await self.loop.run_in_executor(
                    self.executor,
                    partial(self._get_arp_cache, device_id, stale_timeout)
            )

    async def flush_rules(self, **kwargs) -> None:
        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor, partial(self._flush_rules, **kwargs)
            )

    async def delete_rule(self, **kwargs) -> None:
        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor, partial(self._delete_rule, **kwargs)
            )

    async def add_rule(self, **kwargs) -> None:
        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor, partial(self._add_rule, **kwargs)
            )

    async def flush_routes(self, **kwargs) -> None:
        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor, partial(self._flush_routes, **kwargs)
            )

    async def delete_route(self, **kwargs) -> None:
        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor, partial(self._delete_route, **kwargs)
            )

    async def add_route(self, **kwargs) -> None:
        async with self.lock:
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
        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor,
                    partial(
                            self._replace_tc, kind, device_id, handle, **kwargs
                    )
            )

    async def delete_tc(
            self, kind: str, device_id: int, handle: int, **kwargs
    ) -> None:
        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor,
                    partial(
                            self._delete_tc, kind, device_id, handle, **kwargs
                    )
            )

    async def add_filter_tc(self, kind: str, device_id: int, **kwargs) -> None:
        async with self.lock:
            await self.loop.run_in_executor(
                    self.executor,
                    partial(self._add_filter_tc, kind, device_id, **kwargs)
            )

    async def run_routine(self, routine):
        async with self.lock:
            return await self.loop.run_in_executor(
                    self.executor, partial(self._run_routine, routine)
            )
