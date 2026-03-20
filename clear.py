#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据集清理工具 - 简化版
功能：清理指定文件夹及其子文件夹中的图片和标签文件
"""

import os
import glob
import sys
from tkinter import Tk, messagebox, simpledialog


def scan_files(paths, image_extensions, txt_extension):
    """扫描指定路径下的图片和标签文件"""
    files_to_delete = []

    for path in paths:
        if not os.path.exists(path):
            print(f"警告: 路径不存在: {path}")
            continue

        # 扫描图片文件
        for ext in image_extensions:
            pattern = os.path.join(path, "**", f"*{ext}")
            for file in glob.glob(pattern, recursive=True):
                files_to_delete.append(file)

        # 扫描txt文件
        pattern = os.path.join(path, "**", f"*{txt_extension}")
        for file in glob.glob(pattern, recursive=True):
            files_to_delete.append(file)

    return files_to_delete


def main():
    # 图片文件扩展名
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.JPG', '.JPEG', '.PNG']
    txt_extension = '.txt'

    # 默认清理路径 - 用户可以在此处修改或添加
    paths_to_clean = [
        "./images",
        "./datasets",
        "./labels"
        # 用户可以在此处添加更多路径，例如：
        # "./output",
        # "./temp",
    ]

    # 初始化Tkinter
    root = Tk()
    root.withdraw()  # 隐藏主窗口

    # 第一步：警告信息
    warning_result = messagebox.askyesno(
        "⚠️ 数据集清理工具警告",
        "此工具将永久删除以下文件夹及其子文件夹中的文件：\n" +
        "\n".join([f"- {path}" for path in paths_to_clean]) +
        "\n\n文件类型：图片文件(.jpg/.png等)和标签文件(.txt)\n\n" +
        "⚠️ 警告：此操作不可逆！\n" +
        "请确保已备份重要数据！\n\n" +
        "是否继续？"
    )

    if not warning_result:
        print("用户取消操作")
        sys.exit(0)

    # 第二步：扫描文件
    print("开始扫描文件...")
    files_to_delete = scan_files(paths_to_clean, image_extensions, txt_extension)

    if not files_to_delete:
        messagebox.showinfo("扫描结果", "没有找到任何可清理的文件。")
        sys.exit(0)

    # 统计文件类型
    image_files = [f for f in files_to_delete if os.path.splitext(f)[1].lower() in image_extensions]
    txt_files = [f for f in files_to_delete if f.lower().endswith(txt_extension)]

    # 第三步：确认删除
    file_count = len(files_to_delete)

    confirm_result = messagebox.askyesno(
        "确认删除",
        f"扫描完成！找到 {file_count} 个文件：\n"
        f"  - 图片文件: {len(image_files)} 个\n"
        f"  - 标签文件: {len(txt_files)} 个\n\n"
        f"将在以下路径中删除这些文件：\n" +
        "\n".join([f"- {path}" for path in paths_to_clean]) +
        "\n\n⚠️ 警告：此操作不可撤销！\n"
        "确定要删除这些文件吗？"
    )

    if not confirm_result:
        print("用户取消删除操作")
        sys.exit(0)

    # 第四步：执行删除
    deleted_count = 0
    error_count = 0

    print(f"开始删除 {file_count} 个文件...")

    for i, file in enumerate(files_to_delete, 1):
        try:
            os.remove(file)
            deleted_count += 1
            print(f"[{i}/{file_count}] ✓ 已删除: {file}")
        except Exception as e:
            error_count += 1
            print(f"[{i}/{file_count}] ✗ 删除失败: {file} - {str(e)}")

    # 第五步：显示结果
    if error_count > 0:
        messagebox.showwarning(
            "清理完成（有错误）",
            f"清理完成！\n\n"
            f"成功删除: {deleted_count} 个文件\n"
            f"删除失败: {error_count} 个文件\n\n"
            f"失败原因可能是文件被占用或权限不足。"
        )
    else:
        messagebox.showinfo(
            "清理完成",
            f"清理完成！\n\n"
            f"成功删除 {deleted_count} 个文件。"
        )

    print(f"\n清理完成: 成功 {deleted_count} 个，失败 {error_count} 个")


if __name__ == "__main__":
    main()