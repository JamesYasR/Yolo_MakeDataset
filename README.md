# Yolo_MakeDataset

1.分割视频

2.分割学渣数据集

3.在labels里面新建子文件夹-classes.txt//也不必要吧

4.在学渣数据集中新建label/train&val

结构如下，并复制classes.txt进入两个文件夹

<img src="C:\Users\James\Desktop\Yolo_MakeDataset\note\屏幕截图 2026-04-08 104402.png" alt="屏幕截图 2026-04-08 104402" style="zoom: 50%;" />



打标签

```
conda activate labelimg

labelimg 训练集images路径 训练集classes.txt路径 训练集labels路径

labelimg 验证集images路径 验证集classes.txt路径 验证集labels路径
```

5.得到标准数据集后将其复制至yolo

写配置文件yaml

```
path: ./data/xz_dataset/yel
train: images/train
val: images/val

nc: 1
names: ['yel']
```

6.训练

```
python train.py --data ./data/yel.yaml --epochs 150 --batch-size 16 --img 320 --name train_yel --weight weights/yolov5s.pt


python train.py --data ./data/yel.yaml --epochs 400 --batch-size 16 --img 640 --project runs --name yel_Amz_640_0 --weight weights/yel_best640.pt --patience 400 --device 0
//微调法
python train.py --data ./data/yel.yaml --epochs 240 --batch-size 16 --img 640 --project runs --name yel_fine_640_1 --weight weights/yel_best640.pt --patience 220
//低分辨率微调
python train.py --data ./data/yel.yaml --epochs 400 --batch-size 16 --img 320 --name yel_sta2 --weights runs/train/yel_sta2/weights/best.pt 

python train.py --weights runs/train/stage1_640/weights/best.pt --data ./data/yel.yaml/ --epochs 400 --batch-size 16 --img 320  --lr 0.001 --lrf 0.001 --freeze 10 --cos-lr --name yel_sta2_1

python train.py \
  --weights runs/train/stage1_640/weights/best.pt \
  --data ./data/yel.yaml \
  --epochs 300 \
  --batch-size 16 \
  --img 320 \
  --hyp data/hyps/hyp.my_finetune.yaml \
  --freeze 10 \
  --name yel_sta2
  
  
  //新的开始，抛弃旧的差劲模型
python train.py --data ./data/yel.yaml --epochs 240 --batch-size 16 --img 640 --project runs --name yel_Amz_640_1 --weight weights/yolov5s.pt --patience 240 --device 0
```



7.在docker中部署

```
对于requirements
1.去掉和win相关的模块
2.去掉torch模块而用官方链接安装
pip install torch==2.3.1+cpu torchvision==0.18.1+cpu torchaudio==2.3.1+cpu --index-url https://download.pytorch.org/whl/cpu
3.opencv依赖问题
apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0
4，numpy降级
pip install numpy==1.24.3
5.降级pillow
pip install pillow==9.3.0
```

```
远程部署
ssh -p 47901 root@i-2.gpushare.com
fVw5cm6HaEMreCenAd5fvqeMXZaGSmgx
scp -P 47901 -r "C:\Users\James\Desktop\Yolo_MakeDataset\dataset\Amazdata" root@i-2.gpushare.com:/hy-tmp/y57/data/Amazdata
```



登录

```
sudo docker exec -it miniconda-dev /bin/bash
conda activate y57
cd y57
tensorboard --logdir runs/train --bind_all
```

