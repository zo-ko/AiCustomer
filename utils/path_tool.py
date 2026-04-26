"""
为工程提供绝对路径服务
"""

import os 

def get_project_root() -> str:
    """
    获取工程根目录
    """
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    project_dir = os.path.dirname(current_dir)

    return project_dir

def get_abs_path(relative_path : str) -> str:
    """
    传入相对路径，获取绝对路径
    """
    project_root = get_project_root()

    return os.path.join(project_root,relative_path)

if __name__ == '__main__':
    print(get_abs_path("file/add"))

