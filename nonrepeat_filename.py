# 时间：2025/2/2810:12
import os
from os import PathLike
try:
    from typing_extensions import TypeAlias
    StrOrBytesPath: TypeAlias = str | bytes | PathLike[str] | PathLike[bytes]
except:
    StrOrBytesPath=None
def generate_unique_path(file_path:StrOrBytesPath,sep='()'):
    """
    生成一个唯一的文件路径，避免重复。
    如果文件路径已存在，在文件名后缀前添加数字序号（如 _1, _2 等）。

    :param file_path: 原始文件路径
    :return: 唯一的文件路径
    """
    if len(sep) not in (0,1,2):
        raise ValueError('不支持连接符长于2')
    left_sep = right_sep = ''
    if len(sep)==2:
        left_sep = sep[0]
        right_sep = sep[1]
    elif len(sep)==1:
        left_sep = sep
    # 如果路径不存在，直接返回
    if not os.path.exists(file_path):
        return file_path

    # 分离路径的文件名和扩展名
    directory, filename = os.path.split(file_path)
    name, ext = os.path.splitext(filename)
    # 初始化序号
    counter = 1

    # 生成新路径，直到找到一个不重复的路径
    while True:
        new_filename = f"{name}{left_sep}{counter}{right_sep}{ext}"
        new_path = os.path.join(directory, new_filename)
        if not os.path.exists(new_path):
            return new_path
        counter += 1
gup = generate_unique_path

# 测试
if __name__ == "__main__":
    # 测试路径
    test_path = r"C:\Users\12398\Desktop\screenshot4.png"
    # 生成唯一路径
    unique_path = generate_unique_path(test_path)
    print("生成的唯一路径:", unique_path)
