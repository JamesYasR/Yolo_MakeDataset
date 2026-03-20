import cv2
import os
from tqdm import tqdm

# ========== 可调参数 ==========
interval = 6  # 每隔多少帧保存一帧
root_folder = "root"  # 输出子文件夹名，图片将保存到 ./images/root_folder
# =============================

# 路径设置
input_folder = "./videos"
output_base = "./images"
output_folder = os.path.join(output_base, root_folder)
os.makedirs(output_folder, exist_ok=True)

# 获取视频文件列表（常见视频格式）
video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.mpeg', '.mpg'}
video_files = [f for f in os.listdir(input_folder)
               if os.path.splitext(f)[1].lower() in video_extensions]

if not video_files:
    print(f"警告: {input_folder} 中未找到视频文件。")
else:
    print(f"找到 {len(video_files)} 个视频文件。")

# 处理每个视频
for video_file in video_files:
    video_path = os.path.join(input_folder, video_file)
    video_name = os.path.splitext(video_file)[0]  # 获取视频文件名（不带扩展名）

    # 打开视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"无法打开视频: {video_file}")
        continue

    # 获取视频总帧数
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        print(f"视频 {video_file} 总帧数无效，跳过。")
        cap.release()
        continue

    print(f"\n处理视频: {video_file} (总帧数: {total_frames})")

    seq_num = 1  # 图片序列号从1开始
    saved_count = 0

    # 使用tqdm创建进度条
    with tqdm(total=total_frames, desc=f"处理中", unit="帧") as pbar:
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 每隔interval帧保存一帧
            if frame_idx % interval == 0:
                # 生成图片文件名
                img_name = f"{video_name}_{str(seq_num).zfill(6)}.JPG"
                img_path = os.path.join(output_folder, img_name)

                # 保存图片
                cv2.imwrite(img_path, frame)
                saved_count += 1
                seq_num += 1

            frame_idx += 1
            pbar.update(1)

    cap.release()
    print(f"视频 {video_file} 处理完成，保存了 {saved_count} 张图片。")

print(f"\n所有视频处理完成。图片已保存到: {output_folder}")