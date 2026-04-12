from pathlib import Path
from datetime import datetime


def main() -> None:
    post_path = Path("content/posts/hello-world-test.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"""---
title: "Hello World Test"
date: "{datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')}"
draft: true
tags: ["demo", "hello"]
categories: ["test"]
---

# Hello World

这是一段由 `hello_edit.py` 自动写入的测试内容。

- 写入时间：{timestamp}
- 目的：验证 Python 脚本可以直接编辑 Hugo 文章
"""
    post_path.write_text(content, encoding="utf-8")
    print(f"OK: wrote {post_path}")


if __name__ == "__main__":
    main()
