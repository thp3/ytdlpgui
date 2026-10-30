import os


def _walkable(path: str) -> bool:
    try:
        with os.scandir(path) as it:
            next(it, None)
        return True
    except OSError:
        return False


def sanitize_path(env: dict | None = None) -> list[str]:
    """Drop PATH entries that cannot be traversed (e.g. WinError 448 on untrusted junctions).

    Tool lookups by yt-dlp and shutil.which walk every PATH entry and abort on the first one that raises.
    Returns the entries that were dropped.
    """
    env = os.environ if env is None else env
    kept, dropped = [], []
    for p in env.get("PATH", "").split(os.pathsep):
        if not p:
            continue
        (kept if _walkable(p) else dropped).append(p)
    env["PATH"] = os.pathsep.join(kept)
    return dropped
