from PIL import Image
import os

# 图片所在文件夹的路径
input_folder = 'S:\P800\05_CCM_Models\04_DCFC_25C\20240830\cplt\BEC_TRML_BAR'

# 输出GIF的路径
output_path = 'BEC_TRML_BAR_NewApproach.gif'

# 读取文件夹中的所有图片文件
images = [img for img in os.listdir(input_folder) if img.endswith((".png", ".jpg", ".jpeg",".tif"))]

#按文件的修改时间进行排序
images.sort(key=lambda x:os.path.getmtime(os.path.join(input_folder, x)))  # 可能需要根据需要对文件名进行排序

# 创建一个空列表来存储打开的图片对象
frames = [Image.open(os.path.join(input_folder, image)) for image in images]

# 循环遍历图片，打开它们并添加到列表中
for image in images:
    img_path = os.path.join(input_folder, image)
    new_frame = Image.open(img_path)
    frames.append(new_frame)

# 将第一张图片以外的其他图片保存为GIF的其他帧
frames[0].save(output_path, format='GIF',
               append_images=frames[1:],
               save_all=True,
               duration=150, loop=0)

print(f"GIF saved at {output_path}")
