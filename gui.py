import tkinter as tk
from tkinter import filedialog, ttk
import threading
import webbrowser
from image_resizer import process_directory, process_image # 导入 process_image

class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        root.title('图片批量处理器') # 更新标题
        # 获取屏幕的宽度和高度
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # 计算窗口的宽度和高度
        window_width = 450 # 增加宽度以容纳新控件
        window_height = 300 # 增加高度

        # 计算窗口的左上角坐标
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # 设置窗口的位置
        root.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # 选择文件夹按钮
        self.select_btn = ttk.Button(root, text='选择文件夹', command=self.select_directory)
        self.select_btn.pack(pady=10)

        # --- 新增：模式选择 --- 
        self.mode_frame = ttk.LabelFrame(root, text="处理模式")
        self.mode_frame.pack(pady=5, padx=10, fill='x')

        self.resize_mode = tk.StringVar(value="scale") # 默认按比例

        self.scale_radio = ttk.Radiobutton(self.mode_frame, text="按比例缩放", variable=self.resize_mode, value="scale", command=self.toggle_inputs)
        self.scale_radio.grid(row=0, column=0, padx=5, pady=2, sticky='w')

        self.fixed_radio = ttk.Radiobutton(self.mode_frame, text="固定分辨率", variable=self.resize_mode, value="fixed", command=self.toggle_inputs)
        self.fixed_radio.grid(row=1, column=0, padx=5, pady=2, sticky='w')
        # --- 模式选择结束 ---

        # --- 修改：缩放比例输入（现在属于按比例模式）---
        self.scale_input_frame = ttk.Frame(self.mode_frame)
        self.scale_input_frame.grid(row=0, column=1, padx=5, pady=2, sticky='w')
        ttk.Label(self.scale_input_frame, text='缩放比例:').pack(side=tk.LEFT)
        self.scale_entry = ttk.Entry(self.scale_input_frame, width=5)
        self.scale_entry.insert(0, '0.5')
        self.scale_entry.pack(side=tk.LEFT, padx=5)
        # --- 缩放比例结束 ---

        # --- 新增：固定分辨率输入 --- 
        self.fixed_input_frame = ttk.Frame(self.mode_frame)
        self.fixed_input_frame.grid(row=1, column=1, padx=5, pady=2, sticky='w')
        ttk.Label(self.fixed_input_frame, text='宽度:').pack(side=tk.LEFT)
        self.width_entry = ttk.Entry(self.fixed_input_frame, width=6)
        self.width_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(self.fixed_input_frame, text='高度:').pack(side=tk.LEFT)
        self.height_entry = ttk.Entry(self.fixed_input_frame, width=6)
        self.height_entry.pack(side=tk.LEFT, padx=5)
        # --- 固定分辨率结束 ---

        # 处理按钮
        self.process_btn = ttk.Button(root, text='开始处理', command=self.start_processing, state=tk.DISABLED)
        self.process_btn.pack(pady=10)

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

        self.toggle_inputs() # 初始化输入框状态

    def toggle_inputs(self):
        """根据选择的模式启用/禁用相应的输入框"""
        mode = self.resize_mode.get()
        if mode == "scale":
            self.scale_entry.config(state=tk.NORMAL)
            self.width_entry.config(state=tk.DISABLED)
            self.height_entry.config(state=tk.DISABLED)
        elif mode == "fixed":
            self.scale_entry.config(state=tk.DISABLED)
            self.width_entry.config(state=tk.NORMAL)
            self.height_entry.config(state=tk.NORMAL)

    def select_directory(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.status_label.config(text=f'已选择文件夹：{self.folder_path}')
            self.process_btn.config(state=tk.NORMAL)

    def start_processing(self):
        self.select_btn.config(state=tk.DISABLED)
        self.process_btn.config(state=tk.DISABLED)
        self.scale_radio.config(state=tk.DISABLED) # 禁用模式选择
        self.fixed_radio.config(state=tk.DISABLED)
        self.scale_entry.config(state=tk.DISABLED) # 禁用所有输入
        self.width_entry.config(state=tk.DISABLED)
        self.height_entry.config(state=tk.DISABLED)
        self.progress.pack(pady=10)
        self.progress.start()
        self.status_label.config(text='正在处理中...')

        # 使用多线程避免界面冻结
        threading.Thread(target=self.process_images, daemon=True).start()

    def process_images(self):
        mode = self.resize_mode.get()
        params = {}
        try:
            if mode == "scale":
                scale = float(self.scale_entry.get())
                if not (0.01 <= scale <= 10.0): # 放宽比例限制
                    raise ValueError("缩放比例需在0.01到10.0之间")
                params['scale'] = scale
            elif mode == "fixed":
                width = int(self.width_entry.get())
                height = int(self.height_entry.get())
                if width <= 0 or height <= 0:
                    raise ValueError("宽度和高度必须是正整数")
                params['width'] = width
                params['height'] = height
            
            # 调用更新后的 process_directory
            process_directory(self.folder_path, mode=mode, **params)
            self.status_label.config(text='处理完成！')
        except ValueError as ve:
            self.status_label.config(text=f'输入错误：{str(ve)}')
        except Exception as e:
            self.status_label.config(text=f'处理出错：{str(e)}')
        finally:
            self.progress.stop()
            self.progress.pack_forget()
            self.select_btn.config(state=tk.NORMAL)
            self.process_btn.config(state=tk.NORMAL) # 重新启用处理按钮
            self.scale_radio.config(state=tk.NORMAL) # 重新启用模式选择
            self.fixed_radio.config(state=tk.NORMAL)
            self.toggle_inputs() # 根据当前模式恢复输入框状态

if __name__ == '__main__':
    root = tk.Tk()
    app = ImageResizerApp(root)
    root.mainloop()