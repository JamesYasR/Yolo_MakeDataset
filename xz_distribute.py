import os
import random
import shutil
from tqdm import tqdm

# ========== 可配置参数 ==========
MOVE_RATIO = 0.2  # 要移动的图片比例
TRAIN_RATIO = 0.7  # 移动到训练集的比例
MIDDLE_FOLDER = "root"  # 中间文件夹名称


# ==============================

def move_images():
    # 使用配置参数构建路径
    source_folder = f"./images/{MIDDLE_FOLDER}/"
    train_folder = f"./dataset/xz_dataset/{MIDDLE_FOLDER}/images/train/"
    val_folder = f"./dataset/xz_dataset/{MIDDLE_FOLDER}/images/val/"

    # 打印当前配置
    print("当前配置:")
    print(f"  移动比例: {MOVE_RATIO * 100}%")
    print(f"  训练集比例: {TRAIN_RATIO * 100}%")
    print(f"  中间文件夹: {MIDDLE_FOLDER}")
    print(f"  源文件夹: {source_folder}")
    print(f"  训练集目标: {train_folder}")
    print(f"  验证集目标: {val_folder}")
    print("=" * 50)

    # 确保源文件夹存在
    if not os.path.exists(source_folder):
        print(f"错误: 源文件夹 '{source_folder}' 不存在。")
        return

    # 创建目标文件夹
    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(val_folder, exist_ok=True)

    # 获取所有图片文件
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.JPG', '.JPEG', '.PNG'}
    image_files = [f for f in os.listdir(source_folder)
                   if os.path.splitext(f)[1] in image_extensions]

    if not image_files:
        print(f"错误: 源文件夹 '{source_folder}' 中没有找到图片文件。")
        return

    print(f"源文件夹中找到 {len(image_files)} 张图片")

    # 计算要移动的图片数量
    total_to_move = int(len(image_files) * MOVE_RATIO)
    if total_to_move < 1 and len(image_files) > 0:
        total_to_move = 1  # 至少移动1张图片

    # 随机选择要移动的图片
    images_to_move = random.sample(image_files, total_to_move)
    print(f"将移动 {len(images_to_move)} 张图片 ({len(images_to_move) / len(image_files) * 100:.1f}%)")

    # 分割为训练集和验证集
    train_count = int(len(images_to_move) * TRAIN_RATIO)
    if train_count < 1 and len(images_to_move) > 0:
        train_count = 1  # 至少1张到训练集

    train_images = random.sample(images_to_move, train_count)
    val_images = [img for img in images_to_move if img not in train_images]

    print(f"训练集: {len(train_images)} 张, 验证集: {len(val_images)} 张")

    # 移动图片到训练集
    print("\n移动图片到训练集...")
    for img in tqdm(train_images, desc="训练集", unit="张"):
        src_path = os.path.join(source_folder, img)
        dst_path = os.path.join(train_folder, img)
        shutil.move(src_path, dst_path)

    # 移动图片到验证集
    print("\n移动图片到验证集...")
    for img in tqdm(val_images, desc="验证集", unit="张"):
        src_path = os.path.join(source_folder, img)
        dst_path = os.path.join(val_folder, img)
        shutil.move(src_path, dst_path)

    # 统计结果
    remaining_images = [f for f in os.listdir(source_folder)
                        if os.path.splitext(f)[1] in image_extensions]

    print(f"\n操作完成!")
    print(f"原文件夹剩余图片: {len(remaining_images)} 张")
    print(f"训练集文件夹: {train_folder} ({len(train_images)} 张)")
    print(f"验证集文件夹: {val_folder} ({len(val_images)} 张)")


if __name__ == "__main__":
    move_images()