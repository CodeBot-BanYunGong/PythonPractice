import os
import re

def sanitize_filename(filename):
    """
    清理文件名中的非法字符
    :param filename: 原始文件名
    :return: 清理后的文件名
    """
    # 定义非法字符的正则表达式
    illegal_chars = r'[<>:"/\\|?*()+-]'
    # 用下划线替换非法字符
    sanitized_name = re.sub(illegal_chars, '_', filename)
    return sanitized_name

def rename_files_in_directory(directory):
    """
    重命名目录中的所有文件，将非法字符替换为下划线
    :param directory: 目标目录路径
    """
    for filename in os.listdir(directory):
        sanitized_name = sanitize_filename(filename)
        # 构建完整的文件路径
        old_file_path = os.path.join(directory, filename)
        new_file_path = os.path.join(directory, sanitized_name)

        # 检查是否需要重命名
        if old_file_path != new_file_path:
            # 重命名文件
            os.rename(old_file_path, new_file_path)
            print(f'Renamed: {old_file_path} -> {new_file_path}')
        else:
            print(f'No change needed: {old_file_path}')

if __name__ == "__main__":
    target_directory = "C:/Users/xwen14/Desktop/New folder"  # 替换为你的目标目录路径
    rename_files_in_directory(target_directory)
