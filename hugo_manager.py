#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hugo Article Manager - A GUI application for managing Hugo blog articles
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import re
import subprocess
import datetime
from pathlib import Path
import markdown
import webbrowser
import tempfile
from tkinter import font

class HugoManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Hugo Article Manager")
        self.root.geometry("1400x900")
        
        # Configuration
        self.blog_path = Path.cwd()  # Current working directory
        self.posts_path = self.blog_path / "content" / "posts"
        self.current_file = None
        
        # Create GUI
        self.create_widgets()
        self.refresh_articles()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="新建文章", command=self.new_article).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="刷新列表", command=self.refresh_articles).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="保存", command=self.save_article).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="预览", command=self.preview_article).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="上传博客", command=self.upload_blog, 
                  style="Accent.TButton").pack(side=tk.RIGHT, padx=(5, 0))
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Article list
        left_frame = ttk.LabelFrame(content_frame, text="文章列表", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Article listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.article_listbox = tk.Listbox(list_frame, width=30)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.article_listbox.yview)
        self.article_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.article_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.article_listbox.bind('<<ListboxSelect>>', self.on_article_select)
        
        # Right panel - Editor and preview
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Notebook for editor and preview tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Editor tab
        editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(editor_frame, text="编辑器")
        
        # Article info frame
        info_frame = ttk.LabelFrame(editor_frame, text="文章信息", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        ttk.Label(info_frame, text="标题:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(info_frame, textvariable=self.title_var, width=50)
        self.title_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=(0, 10))
        
        # Tags
        ttk.Label(info_frame, text="标签:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.tags_var = tk.StringVar()
        self.tags_entry = ttk.Entry(info_frame, textvariable=self.tags_var, width=30)
        self.tags_entry.grid(row=0, column=3, sticky=tk.W+tk.E)
        
        # Categories
        ttk.Label(info_frame, text="分类:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.categories_var = tk.StringVar()
        self.categories_entry = ttk.Entry(info_frame, textvariable=self.categories_var, width=50)
        self.categories_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=(0, 10))
        
        # Draft status
        self.draft_var = tk.BooleanVar()
        self.draft_check = ttk.Checkbutton(info_frame, text="草稿", variable=self.draft_var)
        self.draft_check.grid(row=1, column=2, sticky=tk.W, padx=(10, 5))
        
        info_frame.columnconfigure(1, weight=1)
        info_frame.columnconfigure(3, weight=1)
        
        # Text editor
        editor_text_frame = ttk.Frame(editor_frame)
        editor_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_editor = scrolledtext.ScrolledText(
            editor_text_frame, 
            wrap=tk.WORD,
            font=('Consolas', 11),
            undo=True
        )
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        
        # Preview tab
        preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(preview_frame, text="预览")
        
        # Preview text widget
        self.preview_text = scrolledtext.ScrolledText(
            preview_frame,
            wrap=tk.WORD,
            font=('Microsoft YaHei', 10),
            state=tk.DISABLED
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def refresh_articles(self):
        """刷新文章列表"""
        self.article_listbox.delete(0, tk.END)
        
        if not self.posts_path.exists():
            self.status_var.set("文章目录不存在")
            return
            
        articles = []
        for file_path in self.posts_path.glob("*.md"):
            articles.append(file_path.name)
            
        articles.sort()
        for article in articles:
            self.article_listbox.insert(tk.END, article)
            
        self.status_var.set(f"找到 {len(articles)} 篇文章")
        
    def on_article_select(self, event):
        """选择文章时的处理"""
        selection = self.article_listbox.curselection()
        if not selection:
            return
            
        filename = self.article_listbox.get(selection[0])
        self.load_article(filename)
        
    def load_article(self, filename):
        """加载文章内容"""
        file_path = self.posts_path / filename
        self.current_file = file_path
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse front matter and content
            front_matter, body = self.parse_markdown(content)
            
            # Update UI
            self.title_var.set(front_matter.get('title', ''))
            self.tags_var.set(', '.join(front_matter.get('tags', [])))
            self.categories_var.set(', '.join(front_matter.get('categories', [])))
            self.draft_var.set(front_matter.get('draft', False))
            
            self.text_editor.delete(1.0, tk.END)
            self.text_editor.insert(1.0, body)
            
            self.status_var.set(f"已加载: {filename}")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载文章失败: {str(e)}")
            
    def parse_markdown(self, content):
        """解析Markdown文件的front matter和正文"""
        front_matter = {}
        body = content
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                front_matter_text = parts[1].strip()
                body = parts[2].strip()
                
                # Parse YAML-like front matter
                for line in front_matter_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        
                        # Handle arrays
                        if value.startswith('[') and value.endswith(']'):
                            value = [item.strip().strip('"\'') for item in value[1:-1].split(',')]
                        elif value.lower() in ['true', 'false']:
                            value = value.lower() == 'true'
                            
                        front_matter[key] = value
                        
        return front_matter, body

    def new_article(self):
        """创建新文章"""
        dialog = ArticleDialog(self.root, "新建文章")
        if dialog.result:
            title, filename = dialog.result

            # Create new article file
            file_path = self.posts_path / f"{filename}.md"

            if file_path.exists():
                messagebox.showerror("错误", "文件已存在")
                return

            # Create front matter
            now = datetime.datetime.now()
            front_matter = f"""---
title: "{title}"
date: {now.strftime('%Y-%m-%dT%H:%M:%S+08:00')}
draft: true
author: "你的名字"
tags: []
categories: []
description: ""
---

"""

            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(front_matter)

                self.refresh_articles()
                self.load_article(f"{filename}.md")
                self.status_var.set(f"已创建新文章: {filename}.md")

            except Exception as e:
                messagebox.showerror("错误", f"创建文章失败: {str(e)}")

    def save_article(self):
        """保存当前文章"""
        if not self.current_file:
            messagebox.showwarning("警告", "没有打开的文章")
            return

        try:
            # Build front matter
            front_matter = {
                'title': self.title_var.get(),
                'tags': [tag.strip() for tag in self.tags_var.get().split(',') if tag.strip()],
                'categories': [cat.strip() for cat in self.categories_var.get().split(',') if cat.strip()],
                'draft': self.draft_var.get()
            }

            # Read existing front matter to preserve other fields
            with open(self.current_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()

            existing_front_matter, _ = self.parse_markdown(existing_content)
            existing_front_matter.update(front_matter)

            # Build new content
            content = "---\n"
            for key, value in existing_front_matter.items():
                if isinstance(value, list):
                    if value:  # Only add non-empty lists
                        formatted_list = '[' + ', '.join(f'"{item}"' for item in value) + ']'
                        content += f'{key}: {formatted_list}\n'
                elif isinstance(value, bool):
                    content += f'{key}: {str(value).lower()}\n'
                elif isinstance(value, str):
                    content += f'{key}: "{value}"\n'
                else:
                    content += f'{key}: {value}\n'

            content += "---\n\n"
            content += self.text_editor.get(1.0, tk.END).rstrip()

            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)

            self.status_var.set(f"已保存: {self.current_file.name}")

        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")

    def preview_article(self):
        """预览文章"""
        if not self.current_file:
            messagebox.showwarning("警告", "没有打开的文章")
            return

        try:
            # Get markdown content
            markdown_content = self.text_editor.get(1.0, tk.END)

            # Convert to HTML
            md = markdown.Markdown(extensions=['extra', 'codehilite'])
            html_content = md.convert(markdown_content)

            # Create a simple HTML template
            html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{self.title_var.get()}</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; margin: 40px; }}
        h1, h2, h3 {{ color: #333; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #ddd; margin: 0; padding-left: 20px; color: #666; }}
    </style>
</head>
<body>
    <h1>{self.title_var.get()}</h1>
    {html_content}
</body>
</html>
"""

            # Save to temporary file and open in browser
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_template)
                temp_file = f.name

            webbrowser.open(f'file://{temp_file}')
            self.status_var.set("已在浏览器中打开预览")

        except Exception as e:
            messagebox.showerror("错误", f"预览失败: {str(e)}")

    def upload_blog(self):
        """上传博客 - 执行updateblog.bat"""
        if messagebox.askyesno("确认", "确定要构建并上传博客吗？\n这将执行hugo构建和git推送操作。"):
            try:
                # Change to blog directory and run updateblog.bat
                result = subprocess.run(
                    ['updateblog.bat'],
                    cwd=str(self.blog_path),
                    capture_output=True,
                    text=True,
                    shell=True
                )

                if result.returncode == 0:
                    messagebox.showinfo("成功", "博客上传成功！")
                    self.status_var.set("博客上传完成")
                else:
                    messagebox.showerror("错误", f"上传失败:\n{result.stderr}")
                    self.status_var.set("博客上传失败")

            except Exception as e:
                messagebox.showerror("错误", f"执行上传脚本失败: {str(e)}")


class ArticleDialog:
    def __init__(self, parent, title):
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="文章标题:").pack(anchor=tk.W)
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=40)
        self.title_entry.pack(fill=tk.X, pady=(5, 15))
        self.title_entry.focus()

        # Filename
        ttk.Label(main_frame, text="文件名 (不含.md扩展名):").pack(anchor=tk.W)
        self.filename_var = tk.StringVar()
        self.filename_entry = ttk.Entry(main_frame, textvariable=self.filename_var, width=40)
        self.filename_entry.pack(fill=tk.X, pady=(5, 15))

        # Auto-generate filename from title
        self.title_var.trace('w', self.update_filename)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.RIGHT)

        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())

    def update_filename(self, *args):
        """根据标题自动生成文件名"""
        title = self.title_var.get()
        # Convert to URL-friendly filename
        filename = re.sub(r'[^\w\s-]', '', title)
        filename = re.sub(r'[-\s]+', '-', filename).strip('-').lower()
        self.filename_var.set(filename)

    def ok_clicked(self):
        title = self.title_var.get().strip()
        filename = self.filename_var.get().strip()

        if not title:
            messagebox.showerror("错误", "请输入文章标题")
            return

        if not filename:
            messagebox.showerror("错误", "请输入文件名")
            return

        # Validate filename
        if not re.match(r'^[a-zA-Z0-9_-]+$', filename):
            messagebox.showerror("错误", "文件名只能包含字母、数字、下划线和连字符")
            return

        self.result = (title, filename)
        self.dialog.destroy()

    def cancel_clicked(self):
        self.dialog.destroy()


def main():
    root = tk.Tk()
    app = HugoManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
