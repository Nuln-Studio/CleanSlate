import subprocess
import shutil
import os
import time
import ctypes
from ctypes import wintypes
from pathlib import Path
from typing import Dict
from datetime import datetime

from config import (
    PATH_TEMP_SYSTEM, PATH_TEMP_USER, PATH_PREFETCH,
    PATH_UPDATE_CACHE, PATH_QQ, PATH_HIBERNATION,
    PATH_CHROME_CACHE, PATH_EDGE_CACHE, PATH_FIREFOX_CACHE,
    PATH_VSCODE_CACHE, PATH_PYCHARM_CACHE, PATH_INTELLIJ_CACHE,
    PATH_SYSTEM_LOGS, PATH_INSTALLER_CACHE,
    PATH_PIP_CACHE, PATH_NPM_CACHE, PATH_YARN_CACHE,
    PATH_MAVEN_REPO, PATH_GRADLE_CACHE, PATH_CONDA_PKGS,
    PATH_JDK_INSTALLS,
    CUSTOM_CACHE_DIRS,
    RECYCLE_BIN_ENABLED,
    CLEAN_RECYCLE_BIN,
    BACKUP_ENABLED,
    BACKUP_DIR,
    USER_HOME,
    SYSTEM_DRIVE
)

RISK_MAP = {
    'shadow': 'medium',
    'winsxs': 'medium',
    'temp_sys': 'low',
    'temp_user': 'low',
    'prefetch': 'low',
    'update_cache': 'low',
    'qq_residue': 'low',
    'wechat_cache': 'low',
    'hibernation': 'low',
    'duplicate_files': 'medium',
    'large_files': 'high',
    'empty_folders': 'low',
    'browser_cache': 'low',
    'ide_cache': 'low',
    'log_files': 'low',
    'installer_cache': 'low',
    'pip_cache': 'low',
    'npm_cache': 'low',
    'yarn_cache': 'low',
    'maven_repo': 'medium',
    'gradle_cache': 'medium',
    'conda_pkgs': 'low',
    'jdk_versions': 'high',
}

if CLEAN_RECYCLE_BIN:
    RISK_MAP['recycle_bin'] = 'low'

for idx, p in enumerate(CUSTOM_CACHE_DIRS):
    if p.exists():
        RISK_MAP[f'custom_{idx}'] = 'low'

def _get_backup_zip_path() -> Path:
    """生成备份zip文件路径：D:/CleanSlate_Backup/CleanSlate_Backup_2026-07-25_14-30-00.zip"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return BACKUP_DIR / f"CleanSlate_Backup_{timestamp}.zip"

def _backup_to_zip(file_paths, zip_path) -> bool:
    """将文件/文件夹列表打包成zip"""
    try:
        import zipfile
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for p in file_paths:
                if not p.exists():
                    continue
                if p.is_file():
                    zf.write(p, p.name)
                elif p.is_dir():
                    for root, dirs, files in os.walk(p):
                        for f in files:
                            full_path = Path(root) / f
                            arc_name = full_path.relative_to(p.parent)
                            zf.write(full_path, arc_name)
        return True
    except Exception:
        return False

def _send_to_recycle_bin(path: Path) -> bool:
    if not path.exists():
        return True
    try:
        path_str = str(path.resolve()) + '\0\0'
        SHFileOperationW = ctypes.windll.shell32.SHFileOperationW
        SHFileOperationW.argtypes = [ctypes.POINTER(wintypes.SHFILEOPSTRUCTW)]
        file_op = wintypes.SHFILEOPSTRUCTW()
        file_op.wFunc = 2
        file_op.pFrom = ctypes.create_unicode_buffer(path_str)
        file_op.fFlags = 0x0001 | 0x0004 | 0x0008
        file_op.hwnd = None
        result = SHFileOperationW(ctypes.byref(file_op))
        return result == 0
    except Exception:
        try:
            shutil.rmtree(path, ignore_errors=True)
            return True
        except Exception:
            return False

def _delete_folder(path: Path, item_id: str = None) -> bool:
    if not path.exists():
        return True
    risk = RISK_MAP.get(item_id, 'low')
    force_backup = risk in ('medium', 'high')
    if force_backup or (BACKUP_ENABLED and risk == 'low'):
        file_paths = [path]
        zip_path = _get_backup_zip_path()
        _backup_to_zip(file_paths, zip_path)
    if force_backup or RECYCLE_BIN_ENABLED:
        return _send_to_recycle_bin(path)
    try:
        shutil.rmtree(path, ignore_errors=True)
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False

def _delete_files(path: Path, item_id: str = None) -> bool:
    if not path.exists():
        return True
    risk = RISK_MAP.get(item_id, 'low')
    force_backup = risk in ('medium', 'high')
    if force_backup or (BACKUP_ENABLED and risk == 'low'):
        file_paths = list(path.glob('*'))
        if file_paths:
            zip_path = _get_backup_zip_path()
            _backup_to_zip(file_paths, zip_path)
    if force_backup or RECYCLE_BIN_ENABLED:
        return _send_to_recycle_bin(path)
    try:
        for f in path.glob('*'):
            if f.is_file():
                f.unlink()
        return True
    except Exception:
        return False

def _run_cmd(cmd: str) -> bool:
    try:
        return subprocess.run(cmd, shell=True, capture_output=True).returncode == 0
    except Exception:
        return False

def clean_shadow_storage(item_id: str = None) -> bool:
    return _run_cmd("vssadmin delete shadows /all /quiet")

def clean_winsxs(item_id: str = None) -> bool:
    return _run_cmd("Dism /Online /Cleanup-Image /StartComponentCleanup /ResetBase")

def clean_temp_system(item_id: str = None) -> bool:
    return _delete_folder(PATH_TEMP_SYSTEM, item_id)

def clean_temp_user(item_id: str = None) -> bool:
    return _delete_folder(PATH_TEMP_USER, item_id)

def clean_prefetch(item_id: str = None) -> bool:
    return _delete_files(PATH_PREFETCH, item_id)

def clean_update_cache(item_id: str = None) -> bool:
    return _delete_folder(PATH_UPDATE_CACHE, item_id)

def clean_qq_residue(item_id: str = None) -> bool:
    return _delete_folder(PATH_QQ, item_id)

def clean_wechat_cache(item_id: str = None) -> bool:
    return True

def clean_hibernation(item_id: str = None) -> bool:
    return _run_cmd("powercfg -h off")

def clean_duplicate_files(item_id: str = None) -> bool:
    return False

def clean_large_files(item_id: str = None) -> bool:
    return False

def clean_empty_folders(item_id: str = None) -> bool:
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

def clean_browser_cache(item_id: str = None) -> bool:
    dirs = [PATH_CHROME_CACHE, PATH_EDGE_CACHE]
    if PATH_FIREFOX_CACHE.exists():
        for profile in PATH_FIREFOX_CACHE.glob('*.default*'):
            cache_dir = profile / 'cache2'
            if cache_dir.exists():
                dirs.append(cache_dir)
    ok = True
    for p in dirs:
        if p.exists():
            ok &= _delete_folder(p, item_id)
    return ok

def clean_ide_cache(item_id: str = None) -> bool:
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
        ok &= _delete_folder(p, item_id)
    return ok

def clean_log_files(item_id: str = None) -> bool:
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

def clean_installer_cache(item_id: str = None) -> bool:
    p = PATH_INSTALLER_CACHE
    return _delete_folder(p, item_id) if p.exists() else True

def clean_pip_cache(item_id: str = None) -> bool:
    p = PATH_PIP_CACHE
    return _delete_folder(p, item_id) if p.exists() else True

def clean_npm_cache(item_id: str = None) -> bool:
    p = PATH_NPM_CACHE
    return _delete_folder(p, item_id) if p.exists() else True

def clean_yarn_cache(item_id: str = None) -> bool:
    p = PATH_YARN_CACHE
    return _delete_folder(p, item_id) if p.exists() else True

def clean_maven_repo(item_id: str = None) -> bool:
    p = PATH_MAVEN_REPO
    return _delete_folder(p, item_id) if p.exists() else True

def clean_gradle_cache(item_id: str = None) -> bool:
    p = PATH_GRADLE_CACHE
    return _delete_folder(p, item_id) if p.exists() else True

def clean_conda_pkgs(item_id: str = None) -> bool:
    p = PATH_CONDA_PKGS
    return _delete_folder(p, item_id) if p.exists() else True

def clean_jdk_versions(item_id: str = None) -> bool:
    all_jdks = []
    for base in PATH_JDK_INSTALLS:
        if not base.exists():
            continue
        for item in base.glob('jdk*'):
            if item.is_dir():
                all_jdks.append(item)
    if len(all_jdks) <= 1:
        return True
    all_jdks.sort(key=lambda x: x.name)
    deleted = 0
    for p in all_jdks[:-1]:
        try:
            _delete_folder(p, item_id)
            deleted += 1
        except Exception:
            pass
    return deleted > 0

def clean_recycle_bin(item_id: str = None) -> bool:
    return _run_cmd("rd /s /q C:\\$Recycle.bin")

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

if CLEAN_RECYCLE_BIN:
    CLEAN_MAP['recycle_bin'] = clean_recycle_bin

for idx, p in enumerate(CUSTOM_CACHE_DIRS):
    if p.exists():
        def make_custom_cleaner(dir_path):
            return lambda item_id=None: _delete_folder(dir_path, item_id)
        CLEAN_MAP[f'custom_{idx}'] = make_custom_cleaner(p)

def run_cleaner(item_id: str) -> Dict[str, bool]:
    func = CLEAN_MAP.get(item_id)
    if not func:
        return {"success": False, "message": f"未知任务 {item_id}"}
    try:
        ok = func(item_id)
        return {"success": ok, "message": "完成" if ok else "失败"}
    except Exception as e:
        return {"success": False, "message": f"异常: {str(e)}"}