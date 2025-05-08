import sys
sys.path.append(r"C:\Users\admin\Desktop\back_end\microexp")

from .real_time_video_me_copy import Emotion_Rec
from os import getcwd
import numpy as np
import cv2
import time
from base64 import b64decode
from os import remove
from .slice_png import img as bgImg
import codecs
import chardet as chardet
import os

# def change_encoding(file_path):
# 	# 文件新名称
#     file = "model.hdf5"
#     with open(file_path, "rb") as f_in:
#         data = f_in.read()
#         # code_type 原文件的编码格式提取
#         code_type = chardet.detect(data)['encoding']
#         file_convert(file_path, file, code_type, 'UTF-8')

# def file_convert(file_path, file, in_code="GBK", out_code="UTF-8"):
#     """
#     该程序用于将目录下的文件从指定格式转换到指定格式，默认的是GBK转到UTF-8
#     :param file:    文件路径
#     :param in_code:  输入文件格式
#     :param out_code: 输出文件格式
#     :return:
#     """
#     out_path = r"C:\Users\admin\Desktop\基于轻量网络模型的人脸表情识别系统\models\new_models"
#     try:
#     	# ignore 可以忽略不必要的错误导致无法打开
#         with codecs.open(file_path, 'r', in_code, 'ignore') as f_in:
#             new_content = f_in.read()
#             f_out = codecs.open(os.path.join(out_path, file), 'w', out_code)
#             f_out.write(new_content)
#             f_out.close()
#     except IOError as err:
#         print("I/O error: {0}".format(err))
# # -*- coding: utf-8 -*-
# with open('models/_mini_XCEPTION.102-0.66.hdf5', 'rb') as f:
#     result = chardet.detect(f.read())  # 或者只读取一部分 f.read(10000)
# encoding = result['encoding']
# file_path = "models/_mini_XCEPTION.102-0.66.hdf5"
# change_encoding(file_path)
# with open(r"C:\Users\admin\Desktop\基于轻量网络模型的人脸表情识别系统\models\new_models\model.hdf5", "rb") as f:
#     result = chardet.detect(f.read())['encoding']
# print(result)
def main(origin_file_path, save_file_path):
    model_path = None
    emotion_model = Emotion_Rec(model_path)
    # 读取背景图
    tmp = open('slice.png', 'wb')
    tmp.write(b64decode(bgImg))
    tmp.close()
    canvas = cv2.imread('slice.png')
    remove('slice.png')
    image = cv2.imread(origin_file_path)  # 读取选择的图片
    # 计时并开始模型预测
    result = emotion_model.run(image, canvas)
    cv2.imwrite(save_file_path, result)



