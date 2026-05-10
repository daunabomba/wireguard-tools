import subprocess
import os
import multiprocessing
from pathlib import Path
from mods import colors
from mods.build import get_build_env, SubprocessRunner


# Module-level runner, initialized when needed
_runner = None

def _get_runner(trace_file=None):
    """Get or create the subprocess runner."""
    global _runner
    if _runner is None:
        _runner = SubprocessRunner(trace_file)
    return _runner

def set_trace_file(trace_file):
    """Set the trace file for subprocess logging."""
    global _runner
    _runner = SubprocessRunner(trace_file)

def target_build(staging_dir: Path, target_dir: Path, arch="x32"):
    colors.info(f"wireguard-tools: target_build ({arch})")
    repo_root = Path(__file__).parent
    make_jobs = multiprocessing.cpu_count()
    
    # We include our config and the RUNSTATEDIR macro in CFLAGS
    std_flags = os.environ.get("CFLAGS", "") + ' -DRUNSTATEDIR="\\"/run\\""'
    static_flags = os.environ.get("CFLAGS_STATIC", "")
    
    cmd = [
        "make",
        "-C", "src",
        "CC=clang",
        "LD=ld.lld",
        "AR=llvm-ar",
        "NM=llvm-nm",
        "STRIP=llvm-strip",
        f"CFLAGS={std_flags}",
        f"LDFLAGS={static_flags}",
        f"-j{make_jobs}",
        "V=1"
    ]
    _get_runner().run(cmd, cwd=repo_root, env=get_build_env(), check=True)

def target_install(staging_dir: Path, target_dir: Path, arch="x32"):
    colors.info(f"wireguard-tools: target_install ({arch})")
    repo_root = Path(__file__).parent
    
    std_flags = os.environ.get("CFLAGS", "") + ' -DRUNSTATEDIR="\\"/run\\""'
    static_flags = os.environ.get("CFLAGS_STATIC", "")

    # Install to both staging and target
    for dest in [staging_dir, target_dir]:
        cmd = [
            "make",
            "-C", "src",
            "install",
            f"DESTDIR={dest}",
            "PREFIX=/usr",
            "CC=clang",
            "LD=ld.lld",
            f"CFLAGS={std_flags}",
            f"LDFLAGS={static_flags}",
            "WITH_WGQUICK=no",
            "WITH_BASHCOMPLETION=no",
            "WITH_SYSTEMDUNITS=no"
        ]
        _get_runner().run(cmd, cwd=repo_root, env=get_build_env(), check=True)
