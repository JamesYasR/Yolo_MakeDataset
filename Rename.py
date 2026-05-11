#!/usr/bin/env python3
"""
文件名前缀批量修改脚本
将指定文件夹中所有以"19_"开头的文件改为"20_"开头
"""

import os
from pathlib import Path


def rename_files_prefix(folder_path, old_prefix, new_prefix):
    """
    重命名文件夹中指定前缀的文件

    Args:
        folder_path: 要处理的文件夹路径
        old_prefix: 旧前缀
        new_prefix: 新前缀
    """
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"错误: 文件夹 '{folder_path}' 不存在!")
        return

    # 获取文件夹中的所有文件
    folder = Path(folder_path)
    files = list(folder.iterdir())

    if not files:
        print(f"文件夹 '{folder_path}' 是空的!")
        return

    # 统计信息
    renamed_count = 0
    skipped_count = 0

    print(f"正在处理文件夹: {folder_path}")
    print(f"将文件前缀从 '{old_prefix}' 改为 '{new_prefix}'")
    print("-" * 50)

    # 遍历所有文件
    for file_path in files:
        # 只处理文件，不处理文件夹
        if not file_path.is_file():
            continue

        # 获取文件名
        filename = file_path.name

        # 检查是否以旧前缀开头
        if filename.startswith(old_prefix):
            # 构建新文件名
            new_filename = new_prefix + filename[len(old_prefix):]
            new_file_path = folder / new_filename

            # 检查新文件名是否已存在
            if new_file_path.exists():
                print(f"警告: 目标文件已存在，跳过重命名: {filename} -> {new_filename}")
                skipped_count += 1
                continue

            # 执行重命名
            try:
                file_path.rename(new_file_path)
                print(f"✓ 重命名: {filename} -> {new_filename}")
                renamed_count += 1
            except Exception as e:
                print(f"✗ 重命名失败: {filename} -> {new_filename}")
                print(f"  错误: {e}")
        else:
            # 不以指定前缀开头的文件
            skipped_count += 1

    # 输出统计信息
    print("-" * 50)
    print("处理完成!")
    print(f"成功重命名: {renamed_count} 个文件")
    print(f"跳过: {skipped_count} 个文件")

    # 显示一些示例
    if renamed_count > 0:
        print("\n重命名示例:")
        # 获取前几个重命名后的文件
        files_after = [f.name for f in folder.iterdir() if f.is_file()]
        new_prefixed_files = [f for f in files_after if f.startswith(new_prefix)]

        if new_prefixed_files:
            for i, filename in enumerate(new_prefixed_files[:5], 1):
                print(f"  {i}. {filename}")
            if len(new_prefixed_files) > 5:
                print(f"  ... 以及另外 {len(new_prefixed_files) - 5} 个文件")


def main():
    # 配置参数
    FOLDER_PATH = "./dataset/yel6/labels/train"  # 要处理的文件夹路径
    OLD_PREFIX = "19_"  # 旧前缀
    NEW_PREFIX = "20_"  # 新前缀

    # 执行重命名
    rename_files_prefix(FOLDER_PATH, OLD_PREFIX, NEW_PREFIX)

    # 可选：递归处理子文件夹
    # 如果需要递归处理子文件夹中的文件，取消下面的注释
    """
    print("\n" + "="*50)
    print("开始递归处理子文件夹...")

    folder = Path(FOLDER_PATH)
    for subfolder in folder.rglob("*"):
        if subfolder.is_dir():
            print(f"\n处理子文件夹: {subfolder}")
            rename_files_prefix(str(subfolder), OLD_PREFIX, NEW_PREFIX)
    """


if __name__ == "__main__":
    main()