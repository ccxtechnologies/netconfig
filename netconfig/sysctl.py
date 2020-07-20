# Copyright: 2020, CCX Technologies



def sysctl_read(key):
    try:
        with open(
                f'/proc/sys/{key.replace(".", "/")}', mode='r'
        ) as fi:
            return (await fi.read()).strip()
    except FileNotFoundError:
        return None


def sysctl_write(key, value):
    with open(
            f'/proc/sys/{key.replace(".", "/")}', mode='w'
    ) as fo:
        await fo.write(value)
