# Copyright: 2022-2023, CCX Technologies

rt_files: dict = {}


def get_rt_value(name: str, rt_file: str, rt_files_dict: dict) -> int:
    rt_data = get_rt_file(rt_file, rt_files_dict)

    try:
        return rt_data[name]
    except KeyError:
        raise RuntimeError(f"Unable to find {name} in {rt_file}")


def get_rt_file(rt_file: str, rt_files_dict: dict):
    if not rt_files_dict.setdefault(rt_file, []):
        with open(f"/etc/iproute2/{rt_file}", "r") as fi:
            data = fi.read()

        rt_files[rt_file] = {
                line.split(' ', 1)[-1].split('\t')[-1].strip():
                int(line.split()[0])
                for line in data.splitlines()
                if line and line[0] != '#'
        }

    return rt_files[rt_file]


async def get_rt_table_id(name: str) -> int:
    return get_rt_value(name, 'rt_tables', rt_files)


async def get_rt_protocol_id(name: str) -> int:
    return get_rt_value(name, 'rt_protos', rt_files)
