import subprocess


class Mount:
    def __init__(self, mount_point: str, device: str, used: int,
                 size: int):
        self._size = size
        self._used = used
        self._device = device
        self._mount_point = mount_point

    @property
    def device(self) -> str:
        return self._device

    @property
    def mount_point(self) -> str:
        return self._mount_point

    @property
    def size(self) -> int:
        return self._size

    @property
    def used(self) -> int:
        return self._used

    def get_used_percent(self):
        return (self.used / self.size) * 100

    def is_local(self):
        return not self.mount_point.startswith(("/mnt", "/media", "/run/media"))

    def get_dict(self):
        return {
            "mount": self.mount_point,
            "device": self.device,
            "percent_usage": self.get_used_percent(),
            "size": self.size,
            "used": self.used,
            "is_local": self.is_local()
        }


def get_mounts():
    list = subprocess.check_output(['df']).decode("utf-8").split("\n")
    out = []
    junk = ["tmpfs", "run", "dev", "Filesystem"]
    for mount in list:
        parts = mount.split()
        if parts and parts[0] not in junk:
            out.append(
                Mount(" ".join(parts[5:]), parts[0], int(parts[2]),
                      int(parts[1])))
    return out


def get_mount(mount_location: str):
    for mount in get_mounts():
        if mount.mount_point == mount_location:
            return mount
    raise Exception("mount not found")
