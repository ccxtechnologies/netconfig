# Copyright: 2022, CCX Technologies

import aiofiles


async def _get_rt_value(name: str, rt_file: str) -> int:
    async with aiofiles.open(f"/etc/iproute2/{rt_file}", "r") as fi:
        async for line in fi:
            if line[0] == '#':
                continue
            label = line.split(' ', 1)[-1].strip()
            if label == name:
                return int(line.split()[0])
    raise RuntimeError(f"Unable to fine {name} in {rt_file}")


async def get_rt_protocol_id(name: str) -> int:
    return await _get_rt_value(name, 'rt_tables')


async def get_rt_table_id(name: str) -> int:
    return await _get_rt_value(name, 'rt_protos')
