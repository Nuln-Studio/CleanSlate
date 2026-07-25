import subprocess
import shutil
import os
import time
from pathlib import Path
from typing import Dict

from config import (
    PATH_TEMP_SYSTEM, PATH_TEMP_USER, PATH_PREFETCH,
    PATH_UPDATE_CACHE, PATH_QQ, PATH_HIBERNATION,
    PATH_CHROME_CACHE, PATH_EDGE_CACHE, PATH_FIREFOX_CACHE,
    PATH_VSCODE_CACHE, PATH_PYCHARM_CACHE, PATH_INTELLIJ_CACHE,
    PATH_SYSTEM_LOGS, PATH_INSTALLER_CACHE,
    PATH_PIP_CACHE, PATH_NPM_CACHE, PATH_YARN_CACHE,
    PATH_MAVEN_REPO, PATH_GRADLE_CACHE, PATH_CONDA_PKGS,
    PATH_JDK_INSTALLS,
    USER_HOME,
    SYSTEM_DRIVE
)

def _run_cmd(cmd: str) -> bool:
    try:
        return subprocess.run(cmd, shell=True, capture_output=True).returncode == 0
    except Exception:
        return False

def _delete_folder(path: Path) -> bool:
    if not path.exists():
        return True
    try:
        shutil.rmtree(path, ignore_errors=True)
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False

def _delete_files(path: Path) -> bool:
    if not path.exists():
        return True
    try:
        for f in path.glob('*'):
            if f.is_file():
                f.unlink()
        return True
    except Exception:
        return False

def clean_shadow_storage() -> bool:
    return _run_cmd("vssadmin delete shadows /all /quiet")

def clean_winsxs() -> bool:
    return _run_cmd("Dism /Online /Cleanup-Image /StartComponentCleanup /ResetBase")

def clean_temp_system() -> bool:
    return _delete_folder(PATH_TEMP_SYSTEM)

def clean_temp_user() -> bool:
    return _delete_folder(PATH_TEMP_USER)

def clean_prefetch() -> bool:
    return _delete_files(PATH_PREFETCH)

def clean_update_cache() -> bool:
    return _delete_folder(PATH_UPDATE_CACHE)

def clean_qq_residue() -> bool:
    return _delete_folder(PATH_QQ)

def clean_wechat_cache() -> bool:
    return True

def clean_hibernation() -> bool:
    return _run_cmd("powercfg -h off")

def clean_duplicate_files() -> bool:
    return False

def clean_large_files() -> bool:
    return False

def clean_empty_folders() -> bool:
    target_dirs = [
        USER_HOME / 'Documents',
        USER_HOME / 'Downloads',
        USER_HOME / 'Desktop',
        USER_HOME / 'Pictures',
        USER_HOME / 'Music',
        USER_HOME / 'Videos',
        Path(f'{SYSTEM_DRIVE}/Users/Public'),
    ]
    deleted = 0
    for base in target_dirs:
        if not base.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(base, topdown=False):
            if not filenames and not dirnames:
                try:
                    os.rmdir(dirpath)
                    deleted += 1
                except OSError:
                    pass
    return deleted > 0

def clean_browser_cache() -> bool:
    dirs = [PATH_CHROME_CACHE, PATH_EDGE_CACHE]
    if PATH_FIREFOX_CACHE.exists():
        for profile in PATH_FIREFOX_CACHE.glob('*.default*'):
            cache_dir = profile / 'cache2'
            if cache_dir.exists():
                dirs.append(cache_dir)
    ok = True
    for p in dirs:
        if p.exists():
            ok &= _delete_folder(p)
    return ok

def clean_ide_cache() -> bool:
    dirs = []
    if PATH_VSCODE_CACHE.exists():
        dirs.append(PATH_VSCODE_CACHE)
    for p in PATH_PYCHARM_CACHE.parent.glob('PyCharm*'):
        cache_dir = p / 'cache'
        if cache_dir.exists():
            dirs.append(cache_dir)
    for p in PATH_INTELLIJ_CACHE.parent.glob('IntelliJIdea*'):
        cache_dir = p / 'cache'
        if cache_dir.exists():
            dirs.append(cache_dir)
    ok = True
    for p in dirs:
        ok &= _delete_folder(p)
    return ok

def clean_log_files() -> bool:
    p = PATH_SYSTEM_LOGS
    if not p.exists():
        return True
    now = time.time()
    cutoff = now - 30 * 24 * 3600
    deleted = 0
    for f in p.rglob('*.log'):
        if f.is_file():
            try:
                if f.stat().st_mtime < cutoff:
                    f.unlink()
                    deleted += 1
            except OSError:
                pass
    return deleted > 0

def clean_installer_cache() -> bool:
    p = PATH_INSTALLER_CACHE
    return _delete_folder(p) if p.exists() else True

def clean_pip_cache() -> bool:
    p = PATH_PIP_CACHE
    return _delete_folder(p) if p.exists() else True

def clean_npm_cache() -> bool:
    p = PATH_NPM_CACHE
    return _delete_folder(p) if p.exists() else True

def clean_yarn_cache() -> bool:
    p = PATH_YARN_CACHE
    return _delete_folder(p) if p.exists() else True

def clean_maven_repo() -> bool:
    p = PATH_MAVEN_REPO
    return _delete_folder(p) if p.exists() else True

def clean_gradle_cache() -> bool:
    p = PATH_GRADLE_CACHE
    return _delete_folder(p) if p.exists() else True

def clean_conda_pkgs() -> bool:
    p = PATH_CONDA_PKGS
    return _delete_folder(p) if p.exists() else True

def clean_jdk_versions() -> bool:
    """
    删除除最新版本外的所有 JDK
    通过扫描所有 java.exe 确定哪些是 JDK 安装目录
    """
    java_paths = []
    try:
        result = subprocess.run(
            'where java 2>nul',
            shell=True,
            capture_output=True,
            text=True
        )
        for line in result.stdout.splitlines():
            p = Path(line.strip())
            if p.exists() and p.name.lower() == 'java.exe':
                jdk_root = p.parent.parent
                if jdk_root not in java_paths:
                    java_paths.append(jdk_root)
    except Exception:
        pass
    
    if len(java_paths) <= 1:
        return True
    java_paths.sort(key=lambda x: x.name)
    latest = java_paths[-1]
    deleted = 0
    for p in java_paths[:-1]:
        try:
            shutil.rmtree(p, ignore_errors=True)
            deleted += 1
        except Exception:
            pass
    return deleted > 0

CLEAN_MAP = {
    'shadow': clean_shadow_storage,
    'winsxs': clean_winsxs,
    'temp_sys': clean_temp_system,
    'temp_user': clean_temp_user,
    'prefetch': clean_prefetch,
    'update_cache': clean_update_cache,
    'qq_residue': clean_qq_residue,
    'wechat_cache': clean_wechat_cache,
    'hibernation': clean_hibernation,
    'duplicate_files': clean_duplicate_files,
    'large_files': clean_large_files,
    'empty_folders': clean_empty_folders,
    'browser_cache': clean_browser_cache,
    'ide_cache': clean_ide_cache,
    'log_files': clean_log_files,
    'installer_cache': clean_installer_cache,
    'pip_cache': clean_pip_cache,
    'npm_cache': clean_npm_cache,
    'yarn_cache': clean_yarn_cache,
    'maven_repo': clean_maven_repo,
    'gradle_cache': clean_gradle_cache,
    'conda_pkgs': clean_conda_pkgs,
    'jdk_versions': clean_jdk_versions,
}

def run_cleaner(item_id: str) -> Dict[str, bool]:
    func = CLEAN_MAP.get(item_id)
    if not func:
        return {"success": False, "message": f"未知任务 {item_id}"}
    try:
        ok = func()
        return {"success": ok, "message": "完成" if ok else "失败"}
    except Exception as e:
        return {"success": False, "message": f"异常: {str(e)}"}