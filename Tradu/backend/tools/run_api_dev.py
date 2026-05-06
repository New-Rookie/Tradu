import os
import sys
from pathlib import Path

import uvicorn


def main():
    # 当前文件路径：
    # backend/tools/run_api_dev.py
    # parents[2] = 项目根目录
    project_root = Path(__file__).resolve().parents[2]

    # 切换到项目根目录，避免 Windows 下 uvicorn 子进程找不到 backend 包
    os.chdir(project_root)

    # 把项目根目录加入 Python 模块搜索路径
    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    # 同步写入 PYTHONPATH，保证 uvicorn reload 子进程也能找到 backend
    old_pythonpath = os.environ.get("PYTHONPATH", "")
    if root_str not in old_pythonpath:
        os.environ["PYTHONPATH"] = (
            root_str if not old_pythonpath else root_str + os.pathsep + old_pythonpath
        )

    uvicorn.run(
        "backend.app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(project_root / "backend")],
    )


if __name__ == "__main__":
    main()