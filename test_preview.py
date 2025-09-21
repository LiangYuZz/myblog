#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for markdown preview functionality
"""

import tkinter as tk
from tkinter import scrolledtext
import re

def setup_preview_tags(text_widget):
    """设置预览文本的格式标签"""
    text_widget.tag_configure("h1", font=('Microsoft YaHei', 18, 'bold'), spacing1=15, spacing3=10, foreground='#2c3e50')
    text_widget.tag_configure("h2", font=('Microsoft YaHei', 16, 'bold'), spacing1=12, spacing3=8, foreground='#34495e')
    text_widget.tag_configure("h3", font=('Microsoft YaHei', 14, 'bold'), spacing1=10, spacing3=6, foreground='#34495e')
    text_widget.tag_configure("bold", font=('Microsoft YaHei', 11, 'bold'), foreground='#2c3e50')
    text_widget.tag_configure("italic", font=('Microsoft YaHei', 11, 'italic'), foreground='#7f8c8d')
    text_widget.tag_configure("code", font=('Consolas', 10), background='#f8f9fa', foreground='#e74c3c', relief='solid', borderwidth=1)
    text_widget.tag_configure("code_block", font=('Consolas', 10), background='#f8f9fa', lmargin1=20, lmargin2=20, spacing1=5, spacing3=5)
    text_widget.tag_configure("blockquote", lmargin1=20, lmargin2=20, foreground='#7f8c8d', font=('Microsoft YaHei', 11, 'italic'))
    text_widget.tag_configure("link", font=('Microsoft YaHei', 11), foreground='#3498db', underline=True)

def insert_formatted_line(text_widget, text):
    """插入格式化的文本行到预览窗口"""
    if not text.strip():
        text_widget.insert(tk.END, '\n')
        return
        
    # Find all markdown patterns and their positions
    patterns = [
        (r'\*\*(.*?)\*\*', 'bold'),      # **bold**
        (r'\*(.*?)\*', 'italic'),        # *italic*
        (r'`(.*?)`', 'code'),            # `code`
        (r'\[(.*?)\]\((.*?)\)', 'link'), # [text](url)
    ]
    
    # Find all matches
    matches = []
    for pattern, tag in patterns:
        for match in re.finditer(pattern, text):
            matches.append((match.start(), match.end(), match, tag))
    
    # Sort by position
    matches.sort(key=lambda x: x[0])
    
    # Insert text with formatting
    current_pos = 0
    for start, end, match, tag in matches:
        # Insert plain text before this match
        if start > current_pos:
            text_widget.insert(tk.END, text[current_pos:start])
        
        # Insert formatted text
        if tag == 'link':
            link_text = match.group(1)
            link_url = match.group(2)
            text_widget.insert(tk.END, link_text, 'link')
            text_widget.insert(tk.END, f" ({link_url})", 'link')
        else:
            text_widget.insert(tk.END, match.group(1), tag)
        
        current_pos = end
    
    # Insert remaining text
    if current_pos < len(text):
        text_widget.insert(tk.END, text[current_pos:])
        
    text_widget.insert(tk.END, '\n')

def test_preview():
    root = tk.Tk()
    root.title("Markdown Preview Test")
    root.geometry("800x600")
    
    # Create text widget
    text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=('Microsoft YaHei', 11))
    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Setup tags
    setup_preview_tags(text_widget)
    
    # Test markdown content
    test_content = """# 这是一级标题

## 这是二级标题

### 这是三级标题

这是普通文本，包含 **粗体文本** 和 *斜体文本*。

这里有一个 `代码片段` 在行内。

这里有一个链接：[百度](https://www.baidu.com)

> 这是一个引用块
> 可以有多行内容

```python
def hello():
    print("Hello World")
```

最后一段普通文本。"""
    
    # Parse and display
    text_widget.configure(state=tk.NORMAL)
    lines = test_content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        
        if line.startswith('# '):
            text_widget.insert(tk.END, line[2:] + '\n\n', 'h1')
        elif line.startswith('## '):
            text_widget.insert(tk.END, line[3:] + '\n\n', 'h2')
        elif line.startswith('### '):
            text_widget.insert(tk.END, line[4:] + '\n\n', 'h3')
        elif line.startswith('> '):
            text_widget.insert(tk.END, line[2:] + '\n', 'blockquote')
        elif line.startswith('```'):
            # Handle code blocks
            i += 1
            code_content = ""
            while i < len(lines) and not lines[i].startswith('```'):
                code_content += lines[i] + '\n'
                i += 1
            text_widget.insert(tk.END, code_content, 'code_block')
        elif line.strip() == '':
            text_widget.insert(tk.END, '\n')
        else:
            # Handle inline formatting
            insert_formatted_line(text_widget, line)
            
        i += 1
    
    text_widget.configure(state=tk.DISABLED)
    
    root.mainloop()

if __name__ == "__main__":
    test_preview()
