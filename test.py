# import SimpleITK as sitk
#
# path = "/home/ff/CZW/xnyy/uploads/input/3885/brain_3885.nii.gz"
# try:
#     img = sitk.ReadImage(path)
#     print("✅ 成功读取图像")
# except Exception as e:
#     print("❌ 读取失败:", str(e))

import nibabel as nib

try:
    nii = nib.load("/home/ff/CZW/xnyy/uploads/input/3885/brain_3885.nii.gz")
    print("✅ nibabel 可以读取")
except Exception as e:
    print("❌ nibabel 无法读取:", str(e))
