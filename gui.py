import tkinter as tk
from tkinter import filedialog, ttk
import threading
import webbrowser
from image_resizer import process_directory

class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        root.title('图片批量处理器(缩减为当前分辨率)')
        # 获取屏幕的宽度和高度
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # 计算窗口的宽度和高度
        window_width = 400
        window_height = 230

        # 计算窗口的左上角坐标
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # 设置窗口的位置
        root.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # 选择文件夹按钮
        self.select_btn = ttk.Button(root, text='选择文件夹', command=self.select_directory)
        self.select_btn.pack(pady=10)

        # 缩放比例输入
        self.scale_frame = ttk.Frame(root)
        self.scale_frame.pack(pady=5)
        ttk.Label(self.scale_frame, text='缩放比例:').pack(side=tk.LEFT)
        self.scale_entry = ttk.Entry(self.scale_frame, width=5)
        self.scale_entry.insert(0, '0.5')
        self.scale_entry.pack(side=tk.LEFT, padx=5)

        # 处理按钮
        self.process_btn = ttk.Button(root, text='开始处理', command=self.start_processing, state=tk.DISABLED)
        self.process_btn.pack(pady=5)

        # 警告标签
        self.warning_label = ttk.Label(root, text='警告：递归处理文件夹下所有图片，请备份好原始图像到其他文件夹', foreground='red')
        self.warning_label.pack(side=tk.BOTTOM, pady=5)

        # 进度标签
        self.status_label = ttk.Label(root, text='等待选择文件夹')
        self.status_label.pack(pady=5)

        # 进度条
        self.progress = ttk.Progressbar(root, mode='indeterminate')

        # GitHub链接
        self.github_label = ttk.Label(root, text="GitHub项目地址", foreground="blue", cursor="hand2")
        self.github_label.pack(side=tk.BOTTOM, pady=3)
        self.github_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/dependon/image_resizer"))

    def select_directory(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.status_label.config(text=f'已选择文件夹：{self.folder_path}')
            self.process_btn.config(state=tk.NORMAL)

    def start_processing(self):
        self.select_btn.config(state=tk.DISABLED)
        self.process_btn.config(state=tk.DISABLED)
        self.progress.pack(pady=10)
        self.progress.start()
        self.status_label.config(text='正在处理中...')

        # 使用多线程避免界面冻结
        threading.Thread(target=self.process_images, daemon=True).start()

    def process_images(self):
        try:
            scale = float(self.scale_entry.get())
            if not (0.1 <= scale <= 2.0):
                raise ValueError("缩放比例需在0.1到2.0之间")
            process_directory(self.folder_path, scale)
            self.status_label.config(text='处理完成！')
        except ValueError as ve:
            self.status_label.config(text=f'输入错误：{str(ve)}')
        except Exception as e:
            self.status_label.config(text=f'处理出错：{str(e)}')
        finally:
            self.progress.stop()
            self.progress.pack_forget()
            self.select_btn.config(state=tk.NORMAL)

if __name__ == '__main__':
    root = tk.Tk()
    app = ImageResizerApp(root)
    root.mainloop()