#!/usr/bin/python
# Copyright: 2022, CCX Technologies

import asyncio
from functools import partial

from pr2modules.netlink.nl80211 import nl80211cmd
from pr2modules.netlink.nl80211 import NL80211_NAMES
from pr2modules.netlink import NLM_F_ACK
from pr2modules.netlink import NLM_F_REQUEST
from pyroute2.netlink.exceptions import NetlinkError

from pyroute2 import IW


class IWRoute:

    def __init__(self, loop=None, executor=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.executor = executor
        self.iw = IW()

    def _set_tx_power_limit(self, phy_id, tx_power_dbm):

        msg = nl80211cmd()
        msg['cmd'] = NL80211_NAMES['NL80211_CMD_SET_WIPHY']
        msg['attrs'] = [
                ['NL80211_ATTR_WIPHY', phy_id],
                ['NL80211_ATTR_WIPHY_TX_POWER_SETTING', 1],
        ]
        msg['attrs'].append(
                ['NL80211_ATTR_WIPHY_TX_POWER_LEVEL', 100 * tx_power_dbm]
        )

        self.iw.nlm_request(
                msg,
                msg_type=self.iw.prid,
                msg_flags=NLM_F_REQUEST | NLM_F_ACK
        )

    def _get_phy_device_ids(self, phy_id):
        return [
                intf.get_attr('NL80211_ATTR_IFINDEX')
                for intf in self.iw.get_interface_by_phy(phy_id)
        ]

    def _get_id(self, phy_id, device_name):
        for _id, _name in [
                (
                        intf.get_attr('NL80211_ATTR_IFINDEX'),
                        intf.get_attr('NL80211_ATTR_IFNAME')
                ) for intf in self.iw.get_interface_by_phy(phy_id)
        ]:
            if _name == device_name:
                return _id

        return None

    def _add_device(
            self, phy_id: int, device_name: str, device_type: str
    ) -> None:
        try:
            self.iw.add_interface(
                    ifname=device_name, iftype=device_type, phy=phy_id
            )
        except NetlinkError as exc:
            if exc.code == 17:
                raise FileExistsError(
                        f"Device {device_name} already exists"
                ) from exc
            else:
                raise

        for _ in range(0, 10):
            _id = self._get_id(phy_id, device_name)
            if _id:
                break
        else:
            raise RuntimeError(f"Failed to add {device_name}")

        return _id

    async def get_phy_device_ids(self, phy_id: int) -> list:
        if phy_id < 0:
            return None

        return await self.loop.run_in_executor(
                self.executor, partial(self._get_phy_device_ids, phy_id)
        )

    async def get_id(self, phy_id: int, device_name: str) -> int:
        if phy_id < 0 or not device_name:
            return None

        return await self.loop.run_in_executor(
                self.executor, partial(self._get_id, phy_id, device_name)
        )

    async def add_device(
            self, phy_id: int, device_name: str, device_type
    ) -> int:
        """
        device_type can be:
            1. adhoc
            2. station
            3. ap
            4. ap_vlan
            5. wds
            6. monitor
            7. mesh_point
            8. p2p_client
            9. p2p_go
            10. p2p_device
            11. ocb
        """

        if not device_name or not device_type:
            return

        return await self.loop.run_in_executor(
                self.executor,
                partial(self._add_device, phy_id, device_name, device_type)
        )

    async def delete_device(self, device_id: int) -> None:
        if device_id <= 0:
            return

        await self.loop.run_in_executor(
                self.executor, partial(self.iw.del_interface, device_id)
        )

    async def set_tx_power_limit(self, phy_id: int, tx_power_dbm: int) -> None:
        if phy_id < 0:
            return

        await self.loop.run_in_executor(
                self.executor,
                partial(self._set_tx_power_limit, phy_id, tx_power_dbm)
        )

    def close(self):
        self.iw.close()
