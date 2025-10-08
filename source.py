import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import math


class SimpleImageToGIF:
    def __init__(self, root):
        self.root = root
        self.root.title("图片转GIF工具") #多帧跳跃效果
        self.root.geometry("650x550")
        self.root.minsize(600, 500)

        # 存储图片路径和预览图像
        self.image_path = None
        self.original_image = None
        self.preview_image = None

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 主框架 - 使用grid布局管理器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重，使界面可调整大小
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)  # 预览区域可扩展

        # 标题
        title_label = ttk.Label(main_frame, text="图片转GIF工具", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 15), sticky=tk.W)

        # 选择图片区域
        select_frame = ttk.Frame(main_frame)
        #sticky控制控件在分配到的网格单元内的对齐方式,以及如何扩展,wesn四方位
        #pady参数用于设置控件在垂直方向上的外部间距(填充),(0, 10)表示上方不添加空格,下方添加10像素的空白
        select_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        select_frame.columnconfigure(1, weight=1)

        ttk.Label(select_frame, text="选择图片:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(select_frame, textvariable=self.file_path_var, state="readonly")
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        ttk.Button(select_frame, text="浏览", command=self.select_image).grid(row=0, column=2, padx=(10, 0))

        # 预览区域
        preview_label = ttk.Label(main_frame, text="图片预览:")
        preview_label.grid(row=2, column=0, sticky=tk.W, pady=(10, 5))

        # 创建画布框架，确保画布有固定大小
        canvas_frame = ttk.Frame(main_frame, relief="solid", borderwidth=1)
        canvas_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        self.preview_canvas = tk.Canvas(canvas_frame, width=400, height=250, bg="white")
        self.preview_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=1, pady=1)

        # 设置区域
        settings_frame = ttk.LabelFrame(main_frame, text="多帧跳跃效果设置", padding="10")
        settings_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)

        # 效果选择
        effect_frame = ttk.Frame(settings_frame)
        effect_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(effect_frame, text="跳跃类型:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.effect_var = tk.StringVar(value="平移")
        effect_combo = ttk.Combobox(effect_frame, textvariable=self.effect_var, state="readonly", width=15)
        effect_combo['values'] = ("平移", "弹跳", "缩放", "闪烁", "颜色反转")
        effect_combo.grid(row=0, column=1, sticky=tk.W)
        effect_combo.bind('<<ComboboxSelected>>', self.on_effect_change)

        # 帧数设置
        frame_count_frame = ttk.Frame(settings_frame)
        frame_count_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Label(frame_count_frame, text="帧数:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.frame_count_var = tk.StringVar(value="5")
        frame_count_spin = ttk.Spinbox(frame_count_frame, from_=2, to=30, textvariable=self.frame_count_var, width=8)
        frame_count_spin.grid(row=0, column=1, sticky=tk.W)

        # 参数设置
        self.params_frame = ttk.Frame(settings_frame)
        self.params_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        self.create_effect_params()

        # 动画设置
        anim_frame = ttk.Frame(settings_frame)
        anim_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Label(anim_frame, text="帧率 (fps):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.fps_var = tk.StringVar(value="10")
        fps_spin = ttk.Spinbox(anim_frame, from_=1, to=30, textvariable=self.fps_var, width=8)
        fps_spin.grid(row=0, column=1, sticky=tk.W, padx=(0, 30))

        ttk.Label(anim_frame, text="循环次数 (0=无限):").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.loop_var = tk.StringVar(value="0")
        loop_spin = ttk.Spinbox(anim_frame, from_=0, to=100, textvariable=self.loop_var, width=8)
        loop_spin.grid(row=0, column=3, sticky=tk.W)

        # 输出设置
        output_frame = ttk.Frame(settings_frame)
        output_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        output_frame.columnconfigure(1, weight=1)

        ttk.Label(output_frame, text="输出文件名:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.output_var = tk.StringVar(value="multi_frame_effect.gif")
        ttk.Entry(output_frame, textvariable=self.output_var).grid(row=0, column=1, sticky=(tk.W, tk.E))

        # 生成按钮
        generate_btn = ttk.Button(main_frame, text="生成GIF", command=self.generate_gif)
        generate_btn.grid(row=5, column=0, pady=(10, 0))

        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief="sunken")
        status_bar.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

    def create_effect_params(self):
        # 清除现有参数控件
        for widget in self.params_frame.winfo_children():
            widget.destroy()

        effect = self.effect_var.get()

        if effect == "平移":
            ttk.Label(self.params_frame, text="水平移动距离:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            self.x_offset_var = tk.StringVar(value="100")
            ttk.Spinbox(self.params_frame, from_=-300, to=300, textvariable=self.x_offset_var, width=8).grid(row=0,
                                                                                                             column=1,
                                                                                                             sticky=tk.W,
                                                                                                             padx=(
                                                                                                                 0, 30))

            ttk.Label(self.params_frame, text="垂直移动距离:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
            self.y_offset_var = tk.StringVar(value="0")
            ttk.Spinbox(self.params_frame, from_=-300, to=300, textvariable=self.y_offset_var, width=8).grid(row=0,
                                                                                                             column=3,
                                                                                                             sticky=tk.W)

        elif effect == "弹跳":
            ttk.Label(self.params_frame, text="弹跳高度:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            self.bounce_height_var = tk.StringVar(value="50")
            ttk.Spinbox(self.params_frame, from_=10, to=200, textvariable=self.bounce_height_var, width=8).grid(row=0,
                                                                                                                column=1,
                                                                                                                sticky=tk.W,
                                                                                                                padx=(
                                                                                                                    0,
                                                                                                                    30))

        elif effect == "缩放":
            ttk.Label(self.params_frame, text="起始大小(%):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            self.start_scale_var = tk.StringVar(value="100")
            ttk.Spinbox(self.params_frame, from_=10, to=200, textvariable=self.start_scale_var, width=8).grid(row=0,
                                                                                                              column=1,
                                                                                                              sticky=tk.W,
                                                                                                              padx=(
                                                                                                                  0,
                                                                                                                  30))

            ttk.Label(self.params_frame, text="结束大小(%):").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
            self.end_scale_var = tk.StringVar(value="150")
            ttk.Spinbox(self.params_frame, from_=10, to=200, textvariable=self.end_scale_var, width=8).grid(row=0,
                                                                                                            column=3,
                                                                                                            sticky=tk.W)

        elif effect == "闪烁":
            ttk.Label(self.params_frame, text="透明度变化:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            self.min_alpha_var = tk.StringVar(value="100")
            ttk.Spinbox(self.params_frame, from_=0, to=100, textvariable=self.min_alpha_var, width=8).grid(row=0,
                                                                                                           column=1,
                                                                                                           sticky=tk.W)

        elif effect == "颜色反转":
            # 颜色反转不需要额外参数
            ttk.Label(self.params_frame, text="将图像颜色进行反转").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

    def on_effect_change(self, event=None):
        self.create_effect_params()

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )

        if file_path:
            self.image_path = file_path
            self.file_path_var.set(file_path)
            self.load_and_preview_image()

    def load_and_preview_image(self):
        try:
            self.original_image = Image.open(self.image_path).convert("RGBA")
            self.update_preview()
            self.status_var.set("图片加载成功")

        except Exception as e:
            messagebox.showerror("错误", f"加载图片时出错: {str(e)}")
            self.status_var.set("图片加载失败")

    def update_preview(self):
        if not self.original_image:
            return

        # 调整预览图像大小以适应画布
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()

        if canvas_width <= 1:  # 如果画布尚未渲染，使用默认大小
            canvas_width = 400
            canvas_height = 250

        # 计算缩放比例
        img_width, img_height = self.original_image.size
        scale = min(canvas_width / img_width, canvas_height / img_height, 1)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)

        preview_img = self.original_image.copy()
        preview_img.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)
        self.preview_image = ImageTk.PhotoImage(preview_img)

        # 清除画布并显示图像
        self.preview_canvas.delete("all")
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        self.preview_canvas.create_image(x, y, anchor=tk.NW, image=self.preview_image)

    def generate_gif(self):
        if not self.image_path:
            messagebox.showwarning("警告", "请先选择一张图片")
            return

        try:
            # 获取参数
            fps = int(self.fps_var.get())
            frame_count = int(self.frame_count_var.get())
            loop_count = int(self.loop_var.get())
            effect = self.effect_var.get()

            # 打开原始图像
            img = self.original_image.copy()
            width, height = img.size

            # 生成多帧动画
            frames = []

            if effect == "平移":
                x_offset = int(self.x_offset_var.get())
                y_offset = int(self.y_offset_var.get())
                frames = self.create_multi_frame_translation(img, x_offset, y_offset, frame_count)

            elif effect == "弹跳":
                bounce_height = int(self.bounce_height_var.get())
                frames = self.create_multi_frame_bounce(img, bounce_height, frame_count)

            elif effect == "缩放":
                start_scale = int(self.start_scale_var.get()) / 100
                end_scale = int(self.end_scale_var.get()) / 100
                frames = self.create_multi_frame_scale(img, start_scale, end_scale, frame_count)

            elif effect == "闪烁":
                alpha = int(self.min_alpha_var.get()) / 100
                # frames = self.create_multi_frame_blink(img, alpha, frame_count)
                frames = self.create_multi_frame_blink(img, alpha)
            elif effect == "颜色反转":
                frames = self.create_multi_frame_invert(img, frame_count)

            # 保存GIF
            output_path = filedialog.asksaveasfilename(
                title="保存GIF文件",
                defaultextension=".gif",
                filetypes=[("GIF文件", "*.gif")],
                initialfile=self.output_var.get()
            )

            if output_path:
                # 计算帧间延迟（毫秒）
                delay = int(1000 / fps)

                # 保存GIF[1,2](@ref)
                frames[0].save(
                    output_path,
                    save_all=True,
                    append_images=frames[1:],
                    duration=delay,
                    loop=loop_count,
                    optimize=True
                )

                self.status_var.set(f"GIF生成成功: {output_path}")
                messagebox.showinfo("成功", f"{frame_count}帧GIF已成功生成并保存到:\n{output_path}")

        except Exception as e:
            messagebox.showerror("错误", f"生成GIF时出错: {str(e)}")
            self.status_var.set("生成GIF失败")

    def create_multi_frame_translation(self, img, x_offset, y_offset, frame_count):
        """创建多帧平移效果"""
        frames = []
        width, height = img.size

        for i in range(frame_count):
            # 计算当前帧的偏移量
            current_x = int(x_offset * i / (frame_count - 1)) if frame_count > 1 else 0
            current_y = int(y_offset * i / (frame_count - 1)) if frame_count > 1 else 0

            frame = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            frame.paste(img, (current_x, current_y), img)
            frames.append(frame)

        return frames

    def create_multi_frame_bounce(self, img, bounce_height, frame_count):
        """创建多帧弹跳效果"""
        frames = []
        width, height = img.size

        for i in range(frame_count):
            # 使用正弦函数创建弹跳效果
            progress = i / (frame_count - 1) if frame_count > 1 else 0
            # 计算当前帧的垂直偏移（弹跳高度）
            current_offset = -int(bounce_height * abs(math.sin(progress * math.pi)))

            frame = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            frame.paste(img, (0, current_offset), img)
            frames.append(frame)

        return frames

    def create_multi_frame_scale(self, img, start_scale, end_scale, frame_count):
        """创建多帧缩放效果"""
        frames = []
        width, height = img.size

        for i in range(frame_count):
            # 计算当前帧的缩放比例
            progress = i / (frame_count - 1) if frame_count > 1 else 0
            current_scale = start_scale + (end_scale - start_scale) * progress

            new_width = int(width * current_scale)
            new_height = int(height * current_scale)
            frame = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 如果缩放后尺寸不同，将图像居中放置在原始尺寸的画布上
            if new_width != width or new_height != height:
                canvas = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                x = (width - new_width) // 2
                y = (height - new_height) // 2
                canvas.paste(frame, (x, y))
                frame = canvas

            frames.append(frame)

        return frames

    # def create_multi_frame_blink(self, img, alpha, frame_count):
    def create_multi_frame_blink(self, img, alpha):
        #透明度这块传入为0-1间float，原本想平滑透明度蒙版处理或者sin函数润化，但是有点弄巧成拙
        #暂未想到好的方案
        frames = []
        # 第一帧：原始透明度
        frame1 = img.copy()
        frames.append(frame1)

        # 第二帧：调整透明度
        frame2 = img.copy()
        # 创建一个与图像相同大小的透明度蒙版
        alpha_mask = Image.new('L', img.size, int(255 * alpha))
        frame2.putalpha(alpha_mask)
        frames.append(frame2)
        return frames

    def create_multi_frame_invert(self, img, frame_count):
        """创建多帧颜色反转效果"""
        frames = []

        for i in range(frame_count):
            if i % 2 == 0:
                # 偶数帧：原始颜色
                frame = img.copy()
            else:
                # 奇数帧：颜色反转
                frame = img.copy()
                # 将图像转换为RGB模式（如果还不是）
                if frame.mode != 'RGB':
                    frame = frame.convert('RGB')
                # 反转颜色
                frame = Image.eval(frame, lambda x: 255 - x)

            frames.append(frame)

        return frames


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleImageToGIF(root)
    root.mainloop()