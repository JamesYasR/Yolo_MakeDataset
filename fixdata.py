#!/usr/bin/env python3
"""
YOLO数据集去重与重分配脚本
检查并处理重复的图片和标注文件，按7:3比例重新分配
"""

import os
import shutil
import random
from pathlib import Path
from collections import defaultdict

# ========== 配置参数 ==========
DATASET_ROOT = "./dataset/Amazdata"
IMAGES_TRAIN_DIR = f"{DATASET_ROOT}/images/train"
IMAGES_VAL_DIR = f"{DATASET_ROOT}/images/val"
LABELS_TRAIN_DIR = f"{DATASET_ROOT}/labels/train"
LABELS_VAL_DIR = f"{DATASET_ROOT}/labels/val"

# 训练集和验证集保留比例
TRAIN_RATIO = 0.7
VAL_RATIO = 0.3

# 随机种子（用于可重复性）
RANDOM_SEED = 42
if RANDOM_SEED is not None:
    random.seed(RANDOM_SEED)

# 支持的图片格式
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.JPG', '.JPEG', '.PNG', '.BMP'}


# ========== 辅助函数 ==========
def get_files_without_ext(directory, extensions=None):
    """获取目录中所有文件（不带扩展名）的列表"""
    if not os.path.exists(directory):
        return []

    files = []
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            if extensions is None or Path(file).suffix.lower() in extensions:
                # 返回不带扩展名的文件名
                files.append(Path(file).stem)
    return files


def find_duplicate_files(file_list1, file_list2):
    """查找两个文件列表中的重复项"""
    set1 = set(file_list1)
    set2 = set(file_list2)
    duplicates = set1.intersection(set2)
    return list(duplicates)


def get_file_with_extension(base_dir, filename, extensions=None):
    """根据文件名（不带扩展名）获取带扩展名的完整文件名"""
    for ext in extensions or ['']:
        for file in os.listdir(base_dir):
            if Path(file).stem == filename and (extensions is None or Path(file).suffix.lower() in extensions):
                return file
    return None


def remove_file_safely(filepath, dry_run=False):
    """安全删除文件（支持模拟运行）"""
    if os.path.exists(filepath):
        if dry_run:
            print(f"  [模拟] 删除: {filepath}")
        else:
            os.remove(filepath)
            print(f"  [实际] 删除: {filepath}")
        return True
    return False


def move_file_safely(src_path, dst_path, dry_run=False):
    """安全移动文件（支持模拟运行）"""
    if not os.path.exists(src_path):
        print(f"  [警告] 源文件不存在: {src_path}")
        return False

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)

    if dry_run:
        print(f"  [模拟] 移动: {src_path} -> {dst_path}")
    else:
        shutil.move(src_path, dst_path)
        print(f"  [实际] 移动: {src_path} -> {dst_path}")
    return True


# ========== 主程序 ==========
def main():
    print("=" * 60)
    print("YOLO数据集去重与重分配脚本")
    print("=" * 60)

    # 检查目录是否存在
    for dir_path in [IMAGES_TRAIN_DIR, IMAGES_VAL_DIR, LABELS_TRAIN_DIR, LABELS_VAL_DIR]:
        if not os.path.exists(dir_path):
            print(f"错误: 目录不存在: {dir_path}")
            return

    print("\n1. 扫描文件...")

    # 获取所有图片和标注文件（不带扩展名）
    train_images = get_files_without_ext(IMAGES_TRAIN_DIR, IMAGE_EXTENSIONS)
    val_images = get_files_without_ext(IMAGES_VAL_DIR, IMAGE_EXTENSIONS)
    train_labels = get_files_without_ext(LABELS_TRAIN_DIR, {'.txt'})
    val_labels = get_files_without_ext(LABELS_VAL_DIR, {'.txt'})

    print(f"训练集图片: {len(train_images)} 个")
    print(f"验证集图片: {len(val_images)} 个")
    print(f"训练集标注: {len(train_labels)} 个")
    print(f"验证集标注: {len(val_labels)} 个")

    # 检查图片和标注的对应关系
    print("\n2. 检查图片-标注对应关系...")

    # 训练集：图片对应标注
    train_missing_labels = [img for img in train_images if img not in train_labels]
    train_missing_images = [label for label in train_labels if label not in train_images]

    # 验证集：图片对应标注
    val_missing_labels = [img for img in val_images if img not in val_labels]
    val_missing_images = [label for label in val_labels if label not in val_images]

    if train_missing_labels:
        print(f"  训练集警告: {len(train_missing_labels)} 个图片没有对应的标注")
        if len(train_missing_labels) <= 10:
            for img in train_missing_labels[:10]:
                print(f"    - {img}")

    if train_missing_images:
        print(f"  训练集警告: {len(train_missing_images)} 个标注没有对应的图片")

    if val_missing_labels:
        print(f"  验证集警告: {len(val_missing_labels)} 个图片没有对应的标注")
        if len(val_missing_labels) <= 10:
            for img in val_missing_labels[:10]:
                print(f"    - {img}")

    if val_missing_images:
        print(f"  验证集警告: {len(val_missing_images)} 个标注没有对应的图片")

    # 检查重复文件
    print("\n3. 检查重复文件...")

    # 训练集和验证集之间的重复
    duplicate_images = find_duplicate_files(train_images, val_images)
    duplicate_labels = find_duplicate_files(train_labels, val_labels)

    # 训练集内部的重复
    train_dup_images = [item for item, count in defaultdict(int).fromkeys(train_images).items()
                        if train_images.count(item) > 1]
    train_dup_labels = [item for item, count in defaultdict(int).fromkeys(train_labels).items()
                        if train_labels.count(item) > 1]

    # 验证集内部的重复
    val_dup_images = [item for item, count in defaultdict(int).fromkeys(val_images).items()
                      if val_images.count(item) > 1]
    val_dup_labels = [item for item, count in defaultdict(int).fromkeys(val_labels).items()
                      if val_labels.count(item) > 1]

    # 合并所有重复
    all_duplicates = set(duplicate_images + duplicate_labels +
                         train_dup_images + train_dup_labels +
                         val_dup_images + val_dup_labels)

    print(f"  训练集-验证集重复图片: {len(duplicate_images)} 个")
    print(f"  训练集-验证集重复标注: {len(duplicate_labels)} 个")
    print(f"  训练集内部重复图片: {len(train_dup_images)} 个")
    print(f"  训练集内部重复标注: {len(train_dup_labels)} 个")
    print(f"  验证集内部重复图片: {len(val_dup_images)} 个")
    print(f"  验证集内部重复标注: {len(val_dup_labels)} 个")
    print(f"  总计唯一重复文件: {len(all_duplicates)} 个")

    if not all_duplicates:
        print("\n✓ 没有发现重复文件!")
        return

    # 显示重复文件详情
    print("\n4. 重复文件详情:")
    print("-" * 40)

    if duplicate_images:
        print(f"\n训练集和验证集重复的图片 ({len(duplicate_images)}个):")
        for i, dup in enumerate(duplicate_images[:20], 1):
            print(f"  {i:2d}. {dup}")
        if len(duplicate_images) > 20:
            print(f"  ... 以及另外 {len(duplicate_images) - 20} 个")

    if duplicate_labels:
        print(f"\n训练集和验证集重复的标注 ({len(duplicate_labels)}个):")
        for i, dup in enumerate(duplicate_labels[:20], 1):
            print(f"  {i:2d}. {dup}")
        if len(duplicate_labels) > 20:
            print(f"  ... 以及另外 {len(duplicate_labels) - 20} 个")

    if train_dup_images:
        print(f"\n训练集内部重复的图片 ({len(train_dup_images)}个):")
        for i, dup in enumerate(set(train_dup_images)[:10], 1):
            print(f"  {i:2d}. {dup} (重复 {train_images.count(dup)} 次)")

    if val_dup_images:
        print(f"\n验证集内部重复的图片 ({len(val_dup_images)}个):")
        for i, dup in enumerate(set(val_dup_images)[:10], 1):
            print(f"  {i:2d}. {dup} (重复 {val_images.count(dup)} 次)")

    # 计算需要处理的数据
    print("\n5. 处理计划:")
    print("-" * 40)

    # 训练集-验证集之间的重复（需要重新分配）
    cross_duplicates = duplicate_images
    print(f"  需要重新分配的文件: {len(cross_duplicates)} 个")
    if cross_duplicates:
        train_keep_count = int(len(cross_duplicates) * TRAIN_RATIO)
        val_keep_count = len(cross_duplicates) - train_keep_count
        print(f"  分配计划: {train_keep_count} 个保留在训练集, {val_keep_count} 个保留在验证集")

        # 随机决定哪些留在训练集，哪些留在验证集
        random.shuffle(cross_duplicates)
        to_train = cross_duplicates[:train_keep_count]
        to_val = cross_duplicates[train_keep_count:]

        print(f"  将移动到训练集: {len(to_train)} 个")
        print(f"  将移动到验证集: {len(to_val)} 个")

    # 内部重复（需要删除多余副本）
    internal_duplicates = {
        'train_images': set(train_dup_images),
        'train_labels': set(train_dup_labels),
        'val_images': set(val_dup_images),
        'val_labels': set(val_dup_labels)
    }

    internal_dup_count = (len(internal_duplicates['train_images']) +
                          len(internal_duplicates['train_labels']) +
                          len(internal_duplicates['val_images']) +
                          len(internal_duplicates['val_labels']))

    print(f"  需要删除的内部重复: {internal_dup_count} 组")

    # 等待用户确认
    print("\n" + "=" * 60)
    response = input("是否继续执行处理操作? (输入 'yes' 继续, 其他任意键取消): ").strip().lower()

    if response != 'yes':
        print("操作已取消。")
        return

    print("\n6. 开始处理...")
    print("-" * 40)

    # 处理训练集内部重复
    print("\n处理训练集内部重复:")
    for filename in internal_duplicates['train_images']:
        # 获取这个文件的所有实例
        files = [f for f in os.listdir(IMAGES_TRAIN_DIR)
                 if Path(f).stem == filename and Path(f).suffix.lower() in IMAGE_EXTENSIONS]

        if len(files) > 1:
            # 保留第一个，删除其他
            keep_file = files[0]
            for file in files[1:]:
                filepath = os.path.join(IMAGES_TRAIN_DIR, file)
                remove_file_safely(filepath)
            print(f"  {filename}: 保留 {keep_file}, 删除 {len(files) - 1} 个重复")

    for filename in internal_duplicates['train_labels']:
        # 获取这个文件的所有实例
        files = [f for f in os.listdir(LABELS_TRAIN_DIR)
                 if Path(f).stem == filename and Path(f).suffix == '.txt']

        if len(files) > 1:
            # 保留第一个，删除其他
            keep_file = files[0]
            for file in files[1:]:
                filepath = os.path.join(LABELS_TRAIN_DIR, file)
                remove_file_safely(filepath)
            print(f"  {filename}: 保留 {keep_file}, 删除 {len(files) - 1} 个重复")

    # 处理验证集内部重复
    print("\n处理验证集内部重复:")
    for filename in internal_duplicates['val_images']:
        # 获取这个文件的所有实例
        files = [f for f in os.listdir(IMAGES_VAL_DIR)
                 if Path(f).stem == filename and Path(f).suffix.lower() in IMAGE_EXTENSIONS]

        if len(files) > 1:
            # 保留第一个，删除其他
            keep_file = files[0]
            for file in files[1:]:
                filepath = os.path.join(IMAGES_VAL_DIR, file)
                remove_file_safely(filepath)
            print(f"  {filename}: 保留 {keep_file}, 删除 {len(files) - 1} 个重复")

    for filename in internal_duplicates['val_labels']:
        # 获取这个文件的所有实例
        files = [f for f in os.listdir(LABELS_VAL_DIR)
                 if Path(f).stem == filename and Path(f).suffix == '.txt']

        if len(files) > 1:
            # 保留第一个，删除其他
            keep_file = files[0]
            for file in files[1:]:
                filepath = os.path.join(LABELS_VAL_DIR, file)
                remove_file_safely(filepath)
            print(f"  {filename}: 保留 {keep_file}, 删除 {len(files) - 1} 个重复")

    # 处理训练集-验证集之间的重复（重新分配）
    print(f"\n重新分配训练集-验证集重复文件 ({len(cross_duplicates)}个):")

    moved_to_train = 0
    moved_to_val = 0

    for filename in to_train:
        # 确保文件在训练集中
        if filename in val_images:
            # 从验证集移动到训练集
            # 移动图片
            val_img_file = get_file_with_extension(IMAGES_VAL_DIR, filename, IMAGE_EXTENSIONS)
            if val_img_file:
                src_img = os.path.join(IMAGES_VAL_DIR, val_img_file)
                dst_img = os.path.join(IMAGES_TRAIN_DIR, val_img_file)
                move_file_safely(src_img, dst_img)

            # 移动标注
            val_label_file = get_file_with_extension(LABELS_VAL_DIR, filename, {'.txt'})
            if val_label_file:
                src_label = os.path.join(LABELS_VAL_DIR, val_label_file)
                dst_label = os.path.join(LABELS_TRAIN_DIR, val_label_file)
                move_file_safely(src_label, dst_label)

            moved_to_train += 1

    for filename in to_val:
        # 确保文件在验证集中
        if filename in train_images:
            # 从训练集移动到验证集
            # 移动图片
            train_img_file = get_file_with_extension(IMAGES_TRAIN_DIR, filename, IMAGE_EXTENSIONS)
            if train_img_file:
                src_img = os.path.join(IMAGES_TRAIN_DIR, train_img_file)
                dst_img = os.path.join(IMAGES_VAL_DIR, train_img_file)
                move_file_safely(src_img, dst_img)

            # 移动标注
            train_label_file = get_file_with_extension(LABELS_TRAIN_DIR, filename, {'.txt'})
            if train_label_file:
                src_label = os.path.join(LABELS_TRAIN_DIR, train_label_file)
                dst_label = os.path.join(LABELS_VAL_DIR, train_label_file)
                move_file_safely(src_label, dst_label)

            moved_to_val += 1

    print(f"\n移动完成: {moved_to_train} 个文件移动到训练集, {moved_to_val} 个文件移动到验证集")

    # 验证处理结果
    print("\n7. 验证处理结果...")
    print("-" * 40)

    # 重新扫描文件
    train_images_after = get_files_without_ext(IMAGES_TRAIN_DIR, IMAGE_EXTENSIONS)
    val_images_after = get_files_without_ext(IMAGES_VAL_DIR, IMAGE_EXTENSIONS)
    train_labels_after = get_files_without_ext(LABELS_TRAIN_DIR, {'.txt'})
    val_labels_after = get_files_without_ext(LABELS_VAL_DIR, {'.txt'})

    # 检查重复
    remaining_duplicates = find_duplicate_files(train_images_after, val_images_after)

    print(f"处理后训练集图片: {len(train_images_after)} 个")
    print(f"处理后验证集图片: {len(val_images_after)} 个")
    print(f"处理后训练集标注: {len(train_labels_after)} 个")
    print(f"处理后验证集标注: {len(val_labels_after)} 个")

    if not remaining_duplicates:
        print("✓ 已成功消除训练集-验证集之间的重复文件!")
    else:
        print(f"⚠ 警告: 仍有 {len(remaining_duplicates)} 个重复文件未处理")
        for dup in remaining_duplicates[:10]:
            print(f"  - {dup}")
        if len(remaining_duplicates) > 10:
            print(f"  ... 以及另外 {len(remaining_duplicates) - 10} 个")

    # 检查图片-标注对应关系
    print("\n图片-标注对应关系检查:")
    train_missing_after = len([img for img in train_images_after if img not in train_labels_after])
    val_missing_after = len([img for img in val_images_after if img not in val_labels_after])

    if train_missing_after == 0 and val_missing_after == 0:
        print("✓ 所有图片都有对应的标注文件")
    else:
        print(f"⚠ 警告: 训练集有 {train_missing_after} 个图片没有标注")
        print(f"⚠ 警告: 验证集有 {val_missing_after} 个图片没有标注")

    # 统计最终比例
    total_images = len(train_images_after) + len(val_images_after)
    if total_images > 0:
        actual_train_ratio = len(train_images_after) / total_images
        print(f"\n最终比例: 训练集 {len(train_images_after)}/{total_images} = {actual_train_ratio:.1%}, "
              f"验证集 {len(val_images_after)}/{total_images} = {1 - actual_train_ratio:.1%}")

        if abs(actual_train_ratio - TRAIN_RATIO) < 0.05:  # 允许5%的误差
            print("✓ 比例符合预期 (7:3)")
        else:
            print(f"⚠ 比例与预期有差异 (期望: {TRAIN_RATIO:.1%}:{VAL_RATIO:.1%})")

    print("\n" + "=" * 60)
    print("处理完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()