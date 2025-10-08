#!/usr/bin/python
# Copyright: 2020-2025, CCX Technologies

import asyncio

from pyroute2 import AsyncWireGuard


class WGRoute:

    def __init__(self, loop=None, executor=None):
        self.wg = AsyncWireGuard()
        self.lock = asyncio.Lock()

    async def _set(
            self, ifname, ifindex, listen_port, fwmark, private_key, peer
    ):
        await self.wg.setup_endpoint()
        return await self.wg.set(
                ifname, ifindex, listen_port, fwmark, private_key, peer
        )

    async def _info(self, ifname, ifindex):
        await self.wg.setup_endpoint()
        return await self.wg.info(ifname, ifindex)

    async def set(
            self,
            ifname=None,
            ifindex=None,
            listen_port=None,
            fwmark=None,
            private_key=None,
            peer=None,
    ):
        async with self.lock:
            return await self._set(
                    ifname, ifindex, listen_port, fwmark, private_key, peer
            )

    async def info(self, ifname=None, ifindex=None):
        async with self.lock:
            return await self._info(ifname, ifindex)

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

    def get_nested(
            self, attr_names: tuple, attrs: list | dict | tuple
    ) -> object:
        _attrs: object = attrs

        for attr_name in attr_names:
            _attrs = self.get_attr(attr_name, _attrs)
        return _attrs

    async def get_peer_stats(self, ifname=None, ifindex=None):
        messages = await self.info(ifname=ifname, ifindex=ifindex)
        if messages is None:
            return {}

        peers = {}
        for msg in messages:
            if msg.get_attr('WGDEVICE_A_PEERS') is None:
                continue

            for peer in msg.get_attr('WGDEVICE_A_PEERS'):
                key = peer.get_attr('WGPEER_A_PUBLIC_KEY')
                last_handshake = peer.get_attr('WGPEER_A_LAST_HANDSHAKE_TIME')
                rx_bytes = peer.get_attr('WGPEER_A_RX_BYTES')
                tx_bytes = peer.get_attr('WGPEER_A_TX_BYTES')
                endpoint = peer.get_attr('WGPEER_A_ENDPOINT')

                peers[key] = (last_handshake, rx_bytes, tx_bytes, endpoint)

        return peers

    def close(self):
        self.wg.close()
