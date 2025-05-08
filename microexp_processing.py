import cv2
import numpy as np

def add_text_watermark(input_path, output_path):
    # 读取原始图片
    image = cv2.imread(input_path)
    if image is None:
        raise ValueError("图片加载失败，请检查路径是否正确")

    # 设置水印参数
    text = "microexp"
    position = (image.shape[1]//2, image.shape[0]//2)  # 居中显示
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.5
    color = (0, 0, 255)  # OpenCV 使用 BGR 格式（红色）
    thickness = 2
    line_type = cv2.LINE_AA  # 抗锯齿

    # 添加水印文本
    cv2.putText(image, text, position, font, font_scale, color, thickness, line_type)

    # 保存处理后的图片
    cv2.imwrite(output_path, image)
    print(f"水印已添加，保存为：{output_path}")
