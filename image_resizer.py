import os
from PIL import Image

def process_image(image_path, scale):
    try:
        with Image.open(image_path) as img:
            # 根据缩放比例计算新尺寸
            scale = float(scale)
            new_size = (int(img.width * scale), int(img.height * scale))
            
            # 保持图片模式（针对有透明通道的PNG等格式）
            resized_img = img.resize(new_size, Image.LANCZOS)
            
            # 覆盖保存原图（保持原始格式）
            resized_img.save(image_path, quality=95)
            print(f"已处理: {image_path}")
            
    except Exception as e:
        print(f"处理失败 {image_path}: {str(e)}")

def process_directory(root_dir, scale=0.5):
    # 支持的图片格式
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(valid_extensions):
                file_path = os.path.join(root, file)
                process_image(file_path, scale)

if __name__ == "__main__":
    target_dir = r'c:\Users\lmh\Desktop\me\素材'  # 修改为需要处理的目录
    process_directory(target_dir)