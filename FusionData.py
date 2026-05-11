#!/usr/bin/env python3
"""
YOLO数据集分割与移动脚本
将指定文件夹中的图片和标注文件按比例分割并移动到 train/val 文件夹
"""

import os
import shutil
import random
from tqdm import tqdm
from pathlib import Path

# ========== 可配置参数 ==========
# 原始数据集路径（已修正：使用正斜杠，避免转义问题）
SOURCE_IMAGES_DIR = "./dataset/yel6/images"
SOURCE_LABELS_DIR = "./dataset/yel6/labels"

# 目标数据集路径（已修正：使用正斜杠，并确保目标文件夹与源文件夹分离）
TARGET_ROOT = "./dataset/yel6_s"  # 新的根目录，避免与源文件夹混淆
TARGET_TRAIN_IMAGES = f"{TARGET_ROOT}/images/train"
TARGET_TRAIN_LABELS = f"{TARGET_ROOT}/labels/train"
TARGET_VAL_IMAGES = f"{TARGET_ROOT}/images/val"
TARGET_VAL_LABELS = f"{TARGET_ROOT}/labels/val"

# 分割比例
SELECT_RATIO = 1.0  # 选择100%的数据
TRAIN_RATIO = 0.7  # 从选择的数据中，70%作为训练集

# 随机种子（用于可重复性，设为None表示完全随机）
RANDOM_SEED = 42

# 支持的图片格式
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.JPG', '.JPEG', '.PNG', '.BMP'}


# ========== 主程序 ==========
def main():
    # 设置随机种子
    if RANDOM_SEED is not None:
        random.seed(RANDOM_SEED)
        print(f"使用随机种子: {RANDOM_SEED}")

    # 创建目标文件夹（全新的目录树，与源文件夹分离）
    os.makedirs(TARGET_TRAIN_IMAGES, exist_ok=True)
    os.makedirs(TARGET_TRAIN_LABELS, exist_ok=True)
    os.makedirs(TARGET_VAL_IMAGES, exist_ok=True)
    os.makedirs(TARGET_VAL_LABELS, exist_ok=True)

    # 获取所有图片文件（关键修正：确保只扫描源目录下的文件，不包含子目录）
    print("正在扫描图片文件...")
    source_images_path = Path(SOURCE_IMAGES_DIR)

    # 方法：遍历源目录下的所有条目，筛选出文件且扩展名匹配的
    image_files = []
    for item in source_images_path.iterdir():
        if item.is_file() and item.suffix in IMAGE_EXTENSIONS:
            image_files.append(item)

    if not image_files:
        print(f"错误: 在 {SOURCE_IMAGES_DIR} 中未找到图片文件!")
        print(f"支持的文件格式: {', '.join(IMAGE_EXTENSIONS)}")
        return

    print(f"找到 {len(image_files)} 个图片文件")

    # 检查对应的标注文件是否存在
    print("检查图片和标注文件的对应关系...")
    valid_pairs = []
    missing_labels = []

    for img_path in tqdm(image_files, desc="检查文件对应关系"):
        # 构建对应的标注文件路径
        label_name = img_path.stem + ".txt"
        label_path = Path(SOURCE_LABELS_DIR) / label_name

        if label_path.exists():
            valid_pairs.append((img_path, label_path))
        else:
            missing_labels.append(img_path.name)

    if missing_labels:
        print(f"警告: {len(missing_labels)} 个图片文件没有对应的标注文件")
        if len(missing_labels) > 5:
            print(f"前5个缺失标注的图片: {missing_labels[:5]}")

    if not valid_pairs:
        print("错误: 没有找到任何有效的图片-标注对!")
        return

    print(f"找到 {len(valid_pairs)} 个有效的图片-标注对")

    # 随机选择 SELECT_RATIO 比例的数据
    select_count = int(len(valid_pairs) * SELECT_RATIO)
    if select_count < 1:
        select_count = 1

    print(f"随机选择 {select_count} 个文件 (占总有效文件的 {SELECT_RATIO * 100:.1f}%)")
    selected_pairs = random.sample(valid_pairs, select_count)

    # 从选择的数据中，分割为训练集和验证集
    train_count = int(len(selected_pairs) * TRAIN_RATIO)
    val_count = len(selected_pairs) - train_count

    # 随机打乱后分割
    random.shuffle(selected_pairs)
    train_pairs = selected_pairs[:train_count]
    val_pairs = selected_pairs[train_count:]

    print(f"分割结果:")
    print(f"  训练集: {train_count} 个文件 (占选择数据的 {TRAIN_RATIO * 100:.1f}%)")
    print(f"  验证集: {val_count} 个文件 (占选择数据的 {(1 - TRAIN_RATIO) * 100:.1f}%)")
    print(f"  总计处理: {len(selected_pairs)} 个文件")

    # 移动训练集文件（关键修改：将 shutil.copy2 改为 shutil.move）
    print("\n移动训练集文件...")
    for img_path, label_path in tqdm(train_pairs, desc="训练集"):
        # 移动图片文件
        target_img_path = Path(TARGET_TRAIN_IMAGES) / img_path.name
        shutil.move(str(img_path), str(target_img_path))  # 使用 move

        # 移动标注文件
        target_label_path = Path(TARGET_TRAIN_LABELS) / label_path.name
        shutil.move(str(label_path), str(target_label_path))  # 使用 move

    # 移动验证集文件
    print("移动验证集文件...")
    for img_path, label_path in tqdm(val_pairs, desc="验证集"):
        # 移动图片文件
        target_img_path = Path(TARGET_VAL_IMAGES) / img_path.name
        shutil.move(str(img_path), str(target_img_path))  # 使用 move

        # 移动标注文件
        target_label_path = Path(TARGET_VAL_LABELS) / label_path.name
        shutil.move(str(label_path), str(target_label_path))  # 使用 move

    # 统计与验证
    print("\n" + "=" * 50)
    print("处理完成!")
    print("=" * 50)
    print(f"原数据集有效文件对: {len(valid_pairs)} 个")
    print(f"本次处理文件对: {len(selected_pairs)} 个")
    print(f"训练集: {train_count} 个文件 (移动至: {TARGET_TRAIN_IMAGES})")
    print(f"验证集: {val_count} 个文件 (移动至: {TARGET_VAL_IMAGES})")

    # 验证移动后的文件数量
    train_imgs_count = len(list(Path(TARGET_TRAIN_IMAGES).glob("*")))
    train_labels_count = len(list(Path(TARGET_TRAIN_LABELS).glob("*.txt")))
    val_imgs_count = len(list(Path(TARGET_VAL_IMAGES).glob("*")))
    val_labels_count = len(list(Path(TARGET_VAL_LABELS).glob("*.txt")))

    print("\n验证结果:")
    print(f"训练集图片: {train_imgs_count}, 标注: {train_labels_count}",
          "✓" if train_imgs_count == train_labels_count == train_count else "✗")
    print(f"验证集图片: {val_imgs_count}, 标注: {val_labels_count}",
          "✓" if val_imgs_count == val_labels_count == val_count else "✗")

    # 显示示例文件
    if train_pairs:
        print("\n训练集示例文件:")
        for img_path, _ in train_pairs[:3]:
            print(f"  - {img_path.name}")
    if val_pairs:
        print("验证集示例文件:")
        for img_path, _ in val_pairs[:3]:
            print(f"  - {img_path.name}")

    # 重要提示：说明源文件已被移动
    print("\n注意: 原始文件已被移动至目标文件夹，原文件夹中的对应文件已不存在。")


if __name__ == "__main__":
    # 检查源文件夹是否存在
    if not os.path.exists(SOURCE_IMAGES_DIR):
        print(f"错误: 源图片文件夹不存在: {SOURCE_IMAGES_DIR}")
    elif not os.path.exists(SOURCE_LABELS_DIR):
        print(f"错误: 源标注文件夹不存在: {SOURCE_LABELS_DIR}")
    else:
        main()