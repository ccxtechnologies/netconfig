#!/usr/bin/python
# Copyright: 2022, CCX Technologies

import asyncio
from functools import partial

from pr2modules.netlink.nl80211 import nl80211cmd
from pr2modules.netlink.nl80211 import NL80211_NAMES
from pr2modules.netlink import NLM_F_ACK
from pr2modules.netlink import NLM_F_REQUEST

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

    async def get_phy_device_ids(self, phy_id: int) -> list:
        if phy_id < 0:
            return None

        return await self.loop.run_in_executor(
                self.executor, partial(self._get_phy_device_ids, phy_id)
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
