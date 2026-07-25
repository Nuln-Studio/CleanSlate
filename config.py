"""配置文件(尽量不要修改可能会误删重要文件)"""
import os
import yaml
from pathlib import Path

SYSTEM_DRIVE = os.environ.get('SystemDrive', 'C:')
CURRENT_USER = os.environ.get('USERNAME', 'Administrator')
USER_HOME = Path(os.environ.get('USERPROFILE', f'{SYSTEM_DRIVE}\\Users\\{CURRENT_USER}'))

CONFIG_FILE = Path(__file__).parent / 'config.yaml'

def load_config():
    default = {
        "custom_cache_dirs": [],
        "recycle_bin": {
            "enabled": False,
            "clean_recycle_bin": True
        },
        "backup": {
            "enabled": True,
            "dir": "D:/ClSl_bin"
        },
        "aggressive_mode_enabled": False
    }
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f)
            if cfg is None:
                cfg = {}
            for key in default:
                if key not in cfg:
                    cfg[key] = default[key]
            return cfg
        except Exception as e:
            print(f"[Config] 配置文件解析失败，使用默认配置: {e}")
            return default
    else:
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                f.write("""# 配置文件可按需修改

custom_cache_dirs: []  # 自定义缓存目录列表

recycle_bin:
  enabled: false  # false 不走回收站，直接删除（释放空间）
  clean_recycle_bin: true  # true 扫描列表显示回收站项，默认清除

backup:
  enabled: true  # true 删除前自动备份，false 不备份（中高风险项强制备份）
  dir: "D:/ClSl_bin"  # 备份根目录，不存在会自动创建

aggressive_mode_enabled: false  # true 显示激进模式选项，false 只显示安全模式
""")
            print(f"[Config] 已生成配置文件: {CONFIG_FILE}")
            print("[Config] 如需自定义清理行为，请修改 config.yaml")
        except Exception:
            pass
        return default

CONFIG = load_config()

CUSTOM_CACHE_DIRS = [Path(p) for p in CONFIG.get("custom_cache_dirs", []) if p]
RECYCLE_BIN_ENABLED = CONFIG.get("recycle_bin", {}).get("enabled", False)
CLEAN_RECYCLE_BIN = CONFIG.get("recycle_bin", {}).get("clean_recycle_bin", True)
BACKUP_ENABLED = CONFIG.get("backup", {}).get("enabled", True)
BACKUP_DIR = Path(CONFIG.get("backup", {}).get("dir", "D:/ClSl_bin"))
AGGRESSIVE_MODE_ENABLED = CONFIG.get("aggressive_mode_enabled", False)

PATH_TEMP_SYSTEM = Path(f'{SYSTEM_DRIVE}/Windows/Temp')
PATH_TEMP_USER = Path(os.environ.get('TEMP', f'{SYSTEM_DRIVE}\\Users\\{CURRENT_USER}\\AppData\\Local\\Temp'))
PATH_PREFETCH = Path(f'{SYSTEM_DRIVE}/Windows/Prefetch')
PATH_UPDATE_CACHE = Path(f'{SYSTEM_DRIVE}/Windows/SoftwareDistribution/Download')
PATH_DOCUMENTS = USER_HOME / 'Documents'
PATH_QQ = PATH_DOCUMENTS / 'Tencent Files'
PATH_WECHAT_CANDIDATES = [
    PATH_DOCUMENTS / 'WeChat Files',
    Path(f'{SYSTEM_DRIVE}/wx'),
    Path(f'{SYSTEM_DRIVE}/WeChat'),
]
PATH_HIBERNATION = Path(f'{SYSTEM_DRIVE}/hiberfil.sys')

PATH_CHROME_CACHE = USER_HOME / 'AppData/Local/Google/Chrome/User Data/Default/Cache'
PATH_EDGE_CACHE = USER_HOME / 'AppData/Local/Microsoft/Edge/User Data/Default/Cache'
PATH_FIREFOX_CACHE = USER_HOME / 'AppData/Local/Mozilla/Firefox/Profiles'
PATH_VSCODE_CACHE = USER_HOME / 'AppData/Roaming/Code/Cache'
PATH_PYCHARM_CACHE = USER_HOME / 'AppData/Local/JetBrains/PyCharm*/cache'
PATH_INTELLIJ_CACHE = USER_HOME / 'AppData/Local/JetBrains/IntelliJIdea*/cache'
PATH_SYSTEM_LOGS = Path(f'{SYSTEM_DRIVE}/Windows/Logs')
PATH_INSTALLER_CACHE = Path(f'{SYSTEM_DRIVE}/Windows/Installer')

PATH_PIP_CACHE = USER_HOME / 'AppData/Local/pip/cache'
PATH_NPM_CACHE = USER_HOME / 'AppData/Local/npm-cache'
PATH_YARN_CACHE = USER_HOME / 'AppData/Local/Yarn/Cache'
PATH_MAVEN_REPO = USER_HOME / '.m2/repository'
PATH_GRADLE_CACHE = USER_HOME / '.gradle/caches'
PATH_CONDA_PKGS = USER_HOME / '.conda/pkgs'
PATH_JDK_INSTALLS = [
    Path(f'{SYSTEM_DRIVE}/Program Files/Java'),
    Path(f'{SYSTEM_DRIVE}/Program Files (x86)/Java'),
]

SCAN_ITEMS = [
    {'id': 'shadow', 'name': '系统还原点', 'risk': 'medium'},
    {'id': 'winsxs', 'name': 'WinSxS 组件存储', 'risk': 'medium'},
    {'id': 'temp_sys', 'name': '系统临时文件', 'risk': 'low'},
    {'id': 'temp_user', 'name': '用户临时文件', 'risk': 'low'},
    {'id': 'prefetch', 'name': '预读缓存', 'risk': 'low'},
    {'id': 'update_cache', 'name': 'Windows 更新缓存', 'risk': 'low'},
    {'id': 'qq_residue', 'name': 'QQ 残留', 'risk': 'low'},
    {'id': 'wechat_cache', 'name': '微信缓存', 'risk': 'low'},
    {'id': 'hibernation', 'name': '休眠文件', 'risk': 'low'},
    {'id': 'duplicate_files', 'name': '重复文件', 'risk': 'medium'},
    {'id': 'large_files', 'name': '大文件 (>1GB)', 'risk': 'high'},
    {'id': 'empty_folders', 'name': '空文件夹', 'risk': 'low'},
    {'id': 'browser_cache', 'name': '浏览器缓存', 'risk': 'low'},
    {'id': 'ide_cache', 'name': 'IDE 缓存', 'risk': 'low'},
    {'id': 'log_files', 'name': '日志文件 (.log)', 'risk': 'low'},
    {'id': 'installer_cache', 'name': '安装包缓存', 'risk': 'low'},
    {'id': 'pip_cache', 'name': 'pip 缓存', 'risk': 'low'},
    {'id': 'npm_cache', 'name': 'npm 缓存', 'risk': 'low'},
    {'id': 'yarn_cache', 'name': 'yarn 缓存', 'risk': 'low'},
    {'id': 'maven_repo', 'name': 'Maven 本地仓库', 'risk': 'medium'},
    {'id': 'gradle_cache', 'name': 'Gradle 缓存', 'risk': 'medium'},
    {'id': 'conda_pkgs', 'name': 'Conda 包缓存', 'risk': 'low'},
    {'id': 'jdk_versions', 'name': 'JDK 多版本残留', 'risk': 'high'},
]

if CLEAN_RECYCLE_BIN:
    SCAN_ITEMS.append({'id': 'recycle_bin', 'name': '回收站', 'risk': 'low'})

if CUSTOM_CACHE_DIRS:
    for idx, p in enumerate(CUSTOM_CACHE_DIRS):
        if p.exists():
            SCAN_ITEMS.append({
                'id': f'custom_{idx}',
                'name': f'自定义缓存 {p.name}',
                'risk': 'low'
            })