# Copyright: 2020, CCX Technologies

import aiofiles


async def sysctl_read(key):
    try:
        async with aiofiles.open(
                f'/proc/sys/{key.replace(".", "/")}', mode='r'
        ) as fi:
            return (await fi.read()).strip()
    except FileNotFoundError:
        return None


async def sysctl_write(key, value):
    async with aiofiles.open(
            f'/proc/sys/{key.replace(".", "/")}', mode='w'
    ) as fo:
        await fo.write(value)
