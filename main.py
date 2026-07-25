import sys
import shutil
from scanner import get_all_scans
from cleaner import run_cleaner
from config import AGGRESSIVE_MODE_ENABLED

def get_disk_info():
    try:
        usage = shutil.disk_usage('C:')
        total_gb = usage.total / (1024**3)
        free_gb = usage.free / (1024**3)
        used_gb = usage.used / (1024**3)
        return f"C: 总 {total_gb:.2f} GB, 已用 {used_gb:.2f} GB, 剩余 {free_gb:.2f} GB"
    except Exception:
        return "无法获取磁盘信息"

def display_results(data):
    print("\n" + "=" * 70)
    print("磁盘清理工具 - 扫描结果")
    print("=" * 70)
    print(f"{'序号':<6} {'项':<20} {'大小(GB)':<10} {'风险':<8} 说明")
    print("-" * 70)
    total = 0
    id_map = {}
    idx = 1
    for item_id, info in data.items():
        size = info.get('size_gb', 0)
        total += size
        risk = info.get('risk', 'low')
        risk_cn = {'low': '低', 'medium': '中', 'high': '高'}.get(risk, '低')
        detail = info.get('detail', '')[:40]
        print(f"{idx:<6} {info.get('name', item_id):<20} {size:<10.2f} {risk_cn:<8} {detail}")
        id_map[idx] = item_id
        idx += 1
    print("-" * 70)
    print(f"总计可释放: {total:.2f} GB")
    print("=" * 70)
    print("风险等级: 低=安全可删  中=建议保留最近  高=需谨慎确认")
    print("=" * 70)
    return id_map

def show_clean_result(success_count, fail_count, disk_info):
    print("\n" + "-" * 70)
    print(f"清理完成: 成功 {success_count} 项, 失败 {fail_count} 项")
    print(f"当前磁盘状态: {disk_info}")
    print("-" * 70)

def main():
    print(get_disk_info())
    print("正在扫描磁盘，请稍候... (扫描过程中会显示进度，请耐心等待)")
    data = get_all_scans()
    
    while True:
        id_map = display_results(data)
        print("\n操作选项:")
        print("  1. 手动选择要清理的项")
        if AGGRESSIVE_MODE_ENABLED:
            print("  2. 选择一键清理模式 (安全 / 激进)")
        else:
            print("  2. 安全模式一键清理（清理低风险 + 中风险，中风险自动备份）")
        print("  3. 重新扫描")
        print("  4. 退出")
        choice = input("请选择 (1/2/3/4): ").strip()
        
        if choice == '1':
            print("\n手动选择清理项:")
            print("  1. 选择要删除的项 (输入序号，多个用逗号或空格分隔)")
            print("  2. 选择不删除的项 (输入序号，其余将全被删除)")
            print("  3. 全选")
            print("  4. 返回")
            sub = input("请选择 (1/2/3/4): ").strip()
            selected_ids = []
            if sub == '1':
                idx_input = input("请输入要删除的序号 (如: 1,3,5 或 1 3 5): ").strip()
                if not idx_input:
                    print("未输入任何序号，返回。")
                    continue
                idx_list = []
                for part in idx_input.replace(',', ' ').split():
                    if part.isdigit():
                        idx_list.append(int(part))
                selected_ids = [id_map[i] for i in idx_list if i in id_map]
                if not selected_ids:
                    print("没有有效序号，返回。")
                    continue
            elif sub == '2':
                idx_input = input("请输入不删除的序号 (如: 1,3,5 或 1 3 5): ").strip()
                if not idx_input:
                    print("未输入任何序号，将删除全部项。")
                    selected_ids = list(id_map.values())
                else:
                    exclude_set = set()
                    for part in idx_input.replace(',', ' ').split():
                        if part.isdigit():
                            exclude_set.add(int(part))
                    selected_ids = [id_map[i] for i in id_map if i not in exclude_set]
                if not selected_ids:
                    print("没有可删除的项，返回。")
                    continue
            elif sub == '3':
                selected_ids = list(id_map.values())
            else:
                continue
            
            print("\n即将清理以下项:")
            for item_id in selected_ids:
                info = data.get(item_id, {})
                print(f"  - {info.get('name', item_id)} ({info.get('size_gb', 0):.2f} GB)")
            confirm = input("确认清理？(y/N): ").strip().lower()
            if confirm != 'y':
                print("已取消。")
                continue
            
            print("\n开始清理...")
            success_count = 0
            fail_count = 0
            for item_id in selected_ids:
                if item_id not in data:
                    print(f"跳过未知项: {item_id}")
                    continue
                risk = data[item_id].get('risk', 'low')
                if risk == 'high':
                    sec = input(f"项 '{item_id}' 风险为高，是否继续？(y/N): ").strip().lower()
                    if sec != 'y':
                        print(f"跳过 {item_id}")
                        continue
                result = run_cleaner(item_id)
                if result['success']:
                    print(f"  [成功] {item_id} - {result['message']}")
                    success_count += 1
                else:
                    print(f"  [失败] {item_id} - {result['message']}")
                    fail_count += 1
            show_clean_result(success_count, fail_count, get_disk_info())
            input("按回车键继续...")
            print("重新扫描...")
            data = get_all_scans()
            
        elif choice == '2':

            if AGGRESSIVE_MODE_ENABLED:
                mode_choice = input("选择模式: 1-安全 (清理低+中风险，中风险备份)  2-激进 (清理全部，中高风险备份): ").strip()
                if mode_choice not in ['1', '2']:
                    print("无效选项")
                    continue
                is_aggressive = (mode_choice == '2')
            else:
                is_aggressive = False 
            selected_ids = []
            for item_id, info in data.items():
                size = info.get('size_gb', 0)
                if size < 0.01:
                    continue
                risk = info.get('risk', 'low')
                if is_aggressive:
                    selected_ids.append(item_id)
                else:
                    if risk in ('low', 'medium'):
                        selected_ids.append(item_id)
            
            if not selected_ids:
                print("没有项可清理。")
                continue
            
            print("\n将清理以下项:")
            for i in selected_ids:
                risk_disp = data[i].get('risk', 'low')
                risk_cn = {'low': '低', 'medium': '中', 'high': '高'}.get(risk_disp, '低')
                print(f"  - {data[i].get('name', i)} ({data[i].get('size_gb', 0):.2f} GB, 风险{risk_cn})")
            
            confirm = input("确认清理？(y/N): ").strip().lower()
            if confirm != 'y':
                print("取消。")
                continue
            
            print("开始清理...")
            success_count = 0
            fail_count = 0
            for item_id in selected_ids:
                risk = data[item_id].get('risk', 'low')
                if risk == 'high':
                    sec = input(f"项 '{item_id}' 风险为高，仍继续？(y/N): ").strip().lower()
                    if sec != 'y':
                        print(f"跳过 {item_id}")
                        continue
                result = run_cleaner(item_id)
                if result['success']:
                    print(f"  [成功] {item_id} - {result['message']}")
                    success_count += 1
                else:
                    print(f"  [失败] {item_id} - {result['message']}")
                    fail_count += 1
            show_clean_result(success_count, fail_count, get_disk_info())
            input("按回车键继续...")
            print("重新扫描...")
            data = get_all_scans()
            
        elif choice == '3':
            print("重新扫描中...")
            data = get_all_scans()
            print("扫描完成。")
            input("按回车键继续...")
            
        elif choice == '4':
            print("感谢使用，再见。")
            sys.exit(0)
        else:
            print("无效选项，请重新选择。")
            input("按回车键继续...")

if __name__ == "__main__":
    main()