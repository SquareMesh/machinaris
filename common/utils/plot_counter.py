#
# On-disk plot file enumeration. Used to obtain a ground-truth plot count
# and size, independent of Chia's plot_cache (which can go stale when
# plot directories become empty between harvester scans).
#

import os


MINIMUM_PLOT_SIZE_BYTES = 100 * 1024 * 1024


def plot_dirs_from_env():
    """Parse the colon-separated ``plots_dir`` env var into a list of paths."""
    raw = os.environ.get('plots_dir', '')
    return [p for p in raw.split(':') if p.strip()]


def count_plot_files(plot_dirs):
    """Count readable plot files on disk across ``plot_dirs``.

    Returns ``(total_count, total_bytes, per_dir)`` where ``per_dir`` is
    ``{dir: {"count": int, "bytes": int}}``. A missing, empty, or
    unreadable directory contributes zero — that is the case the caller
    needs to detect, not an error.
    """
    total_count = 0
    total_bytes = 0
    per_dir = {}
    for d in plot_dirs:
        count = 0
        size_bytes = 0
        try:
            with os.scandir(d) as it:
                for entry in it:
                    try:
                        if not entry.is_file(follow_symlinks=True):
                            continue
                    except OSError:
                        continue
                    if not entry.name.endswith('.plot'):
                        continue
                    try:
                        entry_size = entry.stat().st_size
                    except OSError:
                        continue
                    if entry_size >= MINIMUM_PLOT_SIZE_BYTES:
                        count += 1
                        size_bytes += entry_size
        except (FileNotFoundError, NotADirectoryError, PermissionError, OSError):
            pass
        per_dir[d] = {"count": count, "bytes": size_bytes}
        total_count += count
        total_bytes += size_bytes
    return total_count, total_bytes, per_dir
