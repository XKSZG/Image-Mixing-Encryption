# 库导入
import tkinter as tk
from tkinter import messagebox, filedialog, ttk, PhotoImage
from PIL import Image, ImageTk
import random
import os
import base64
import io
import pkg_resources
import zlib

# 打开图片
def open_image(path):
    try:
        image = Image.open(path)
        print("Image loaded successfully")
    except:
        print("Error: Image not found")
        return None

    # 输出图片信息
    print(image.format, image.size, image.mode)

    return image

# 修改图片大小，使其比例为1:1，以最大边加上边缘裁剪数量为准
def resize_image(image, edge_cut_num):
    # 获得图片的宽和高
    width, height = image.size

    # 计算最大边
    max_edge = max(width, height)

    # 计算新的边长
    new_edge = max_edge + edge_cut_num

    # 创建新的空白图片
    resized_image = Image.new("RGBA", (new_edge, new_edge))

    # 图片覆盖白色
    resized_image.paste((255, 255, 255, 255), (0, 0, new_edge, new_edge))

    # 将原图片粘贴到新的空白图片中，居中显示
    resized_image.paste(image, (0, 0))

    return resized_image

# 缩放图片，使其最大边缩放为指定大小，最小边按比例缩放
def scale_image(image, max_size):
    # 获得图片的宽和高
    width, height = image.size

    # 计算最大边
    max_edge = max(width, height)

    # 计算缩放比例
    scale = max_size / max_edge

    # 缩放图片
    scaled_image = image.resize((int(width * scale), int(height * scale)))

    # 创建空白图片
    blank_image = Image.new("RGBA", (max_size, max_size))

    # 图片覆盖白色
    blank_image.paste((255, 255, 255, 255), (0, 0, max_size, max_size))

    # 图片覆盖左上角显示
    blank_image.paste(scaled_image, (0, 0))

    return blank_image

# 图片裁剪
def cut_image(image, width, height):
    # 裁剪图片
    cropped_image = image.crop((0, 0, width, height))

    return cropped_image

# 获得图片高宽
def get_image_size(image):
    # 获得图片的宽和高
    width, height = image.size

    return width, height

# 获得每张小图片的宽和高
def get_piece_size(width, height, edge_cut_num):
    # 计算每张小图片的宽和高
    piece_width = width // edge_cut_num
    piece_height = height // edge_cut_num

    return piece_width, piece_height

# 获取图片裁剪数量
def get_cut_pictrue_num(edge_cut_num):
    cut_pictrue_num = edge_cut_num * edge_cut_num
    return cut_pictrue_num

# 生成种子
def generate_seed():
    seed = ""
    for i in range(16):
        seed += str(random.randint(0, 9))
    # 输出随机数种子
    print("Random seed:", seed)
    return seed

# 根据种子生成图片的组合顺序
def generate_composition_order(seed, pictrue_cut_num):
    random.seed(seed)
    composition_order = []

    # 生成一个无重复的1~100的随机数列表
    composition_order = random.sample(range(1, pictrue_cut_num + 1), pictrue_cut_num)

    # 输出图片的组合顺序
    print("Composition order:", composition_order)

    return composition_order

# 根据随机数种子生成图片的旋转顺序
def generate_rotation_order(seed, pictrue_cut_num):
    random.seed(seed + str(pictrue_cut_num))
    rotation_order = []

    for i in range(pictrue_cut_num):
        rotation_order.append(random.randint(0, 3))

    # 输出图片的旋转顺序
    print("Rotation order:", rotation_order)

    return rotation_order

# 流式处理图片裁剪，旋转， 组合
def process_image(image, composition_order, rotation_order, edge_cut_num, Progress = None):
    # 获得图片的宽和高
    width, height = get_image_size(image)

    # 获得每张小图片的宽和高
    piece_width, piece_height = get_piece_size(width, height, edge_cut_num)

    # 创建一个空白图片
    new_image = Image.new("RGBA", (width, height))

    # 图片编号
    index = 0

    # 流式处理图片裁剪，旋转， 组合
    for i in range(edge_cut_num):
        for j in range(edge_cut_num):

            # 裁剪图片
            piece = image.crop((j * piece_height, i * piece_width, (j + 1) * piece_height, (i + 1) * piece_width))

            # 旋转图片
            rotation_count = rotation_order[i * edge_cut_num + j]
            for k in range(rotation_count):
                piece = piece.rotate(90, expand=True)

            # 按照组合顺序组合图片
            x = (composition_order[index] - 1) % edge_cut_num
            y = (composition_order[index] - 1) // edge_cut_num
            x = x * piece_width
            y = y * piece_height
            new_image.paste(piece, (x, y))

            # 更新图片编号
            index += 1

            # 输出进度
            if Progress is not None:
                Progress["value"] = index / (edge_cut_num * edge_cut_num) * 100
                Progress.update()

            # 输出图片信息
            #print("Piece", i * edge_cut_num + j, "processed")

    return new_image

# 流式还原图片裁剪，旋转， 组合
def restore_image(image, composition_order, rotation_order, edge_cut_num, progress = None):
    # 获得图片的宽和高
    width, height = get_image_size(image)

    # 获得每张小图片的宽和高
    piece_width, piece_height = get_piece_size(width, height, edge_cut_num)

    # 创建一个空白图片
    new_image = Image.new("RGBA", (width, height))

    # 流式还原图片裁剪，旋转， 组合
    for i in range(0, len(composition_order)):
        elements = composition_order[i] - 1
        position_1 = (elements % edge_cut_num * piece_width, elements // edge_cut_num * piece_height)
        position_2 = ((elements % edge_cut_num + 1) * piece_width, (elements // edge_cut_num + 1) * piece_height)
        piece = image.crop(position_1 + position_2)
        x = i % edge_cut_num * piece_width
        y = i // edge_cut_num * piece_height

        # 旋转图片
        index = y // piece_height * edge_cut_num + x // piece_width
        for j in range(rotation_order[index]):
            piece = piece.rotate(-90, expand=True)

        # 组合图片
        new_image.paste(piece, (x, y))

        # 更新进度
        if progress is not None:
            progress["value"] = i / len(composition_order) * 100
            progress.update()

        # 输出图片信息
        #print("Piece", i, "at", x, "/", y, "rotated", rotation_order[i] * 90, "degrees", "restored")

    return new_image

# 使用zlib压缩数字文本
def compress_text(text):
    compressed_text = zlib.compress(text.encode())
    compressed_text = base64.b64encode(compressed_text).decode("utf-8")
    return compressed_text

# 使用zlib解压数字文本
def decompress_text(compressed_text):
    decompressed_text = zlib.decompress(base64.b64decode(compressed_text))
    decompressed_text = decompressed_text.decode("utf-8")
    return decompressed_text

# 解压密钥获取图片大小和边裁剪数量和种子
def get_key_info(key):
    # 解压密钥
    decompressed_key = decompress_text(key)

    # 获得图片大小和边裁剪数量和种子
    info = decompressed_key.split("/")
    originally_width = int(info[0])
    originally_height = int(info[1])
    edge_cut_num = int(info[2])
    seed = info[3]

    # 输出解密结果
    print("Original image size:", originally_width, "x", originally_height)
    print("Edge cut number:", edge_cut_num)
    print("Seed:", seed)

    return originally_width, originally_height, edge_cut_num, seed

# 加密图片
def encrypt_image(image, edge_cut_num, Progress=None):
    # 获得图片的宽和高
    originally_width, originally_height = get_image_size(image)

    # 修改图片大小，使其比例为1:1，以最小边为准
    image = resize_image(image, edge_cut_num)

    # 获得图片的宽和高
    width, height = get_image_size(image)

    # 获得每张小图片的宽和高
    piece_width, piece_height = get_piece_size(width, height, edge_cut_num)

    # 获得图片裁剪数量
    cut_pictrue_num = get_cut_pictrue_num(edge_cut_num)

    # 生成随机数种子
    seed = generate_seed()

    # 根据种子生成图片的组合顺序
    composition_order = generate_composition_order(seed, cut_pictrue_num)

    # 根据种子生成图片的旋转顺序
    rotation_order = generate_rotation_order(seed, cut_pictrue_num)

    # 流式处理图片裁剪，旋转， 组合
    new_image = process_image(image, composition_order, rotation_order, edge_cut_num, Progress = Progress)

    # 保存种子, 写入图片大小，边裁剪数量
    seed = str(originally_width) + "/" + str(originally_height) + "/" + str(edge_cut_num) + "/" + seed

    # 压缩种子作为密钥
    compressed_seed = compress_text(seed)

    # 输出加密结果
    print("Encrypted image saved as encrypted.png")
    print("Seed compressed as:", compressed_seed)
    print("Seed:", decompress_text(compressed_seed))

    return new_image, compressed_seed

# 解密图片
def decrypt_image(image, key, Progress=None):
    # 获取密钥信息
    originally_width, originally_height, edge_cut_num, seed = get_key_info(key)

    # 缩放图片至原大小（最大边加上边缘裁剪数量为准）
    max_edge = max(originally_width, originally_height)
    image = scale_image(image, max_edge + edge_cut_num)

    # 获取图片排列顺序
    composition_order = generate_composition_order(seed, get_cut_pictrue_num(edge_cut_num))

    # 获取图片旋转顺序
    rotation_order = generate_rotation_order(seed, get_cut_pictrue_num(edge_cut_num))

    # 流式还原图片裁剪，旋转， 组合
    new_image = restore_image(image, composition_order, rotation_order, edge_cut_num, progress = Progress)

    # 裁剪图片
    new_image = cut_image(new_image, originally_width, originally_height)

    return new_image
# ui界面
class Application(tk.Frame):
    def __init__(self, master=None):
        self.edge_cut_num = 5
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.image_name = ""
        self.input_image = None
        self.output_image = None

    def create_widgets(self):
        # 显示两个200*200的灰色方块（图片背景）
        self.canvas_input = tk.Canvas(self, width=200, height=200, bg="gray")
        self.canvas_input.grid(row=0, column=0, padx=0, pady=0)
        self.canvas_input.bind("<Button-1>", lambda event: self.on_canvas_input_click())

        self.canvas_output = tk.Canvas(self, width=200, height=200, bg="gray")
        self.canvas_output.grid(row=0, column=1, padx=0, pady=5)
        self.canvas_output.bind("<Button-1>", lambda event: self.on_canvas_output_click())


        # 显示空白图片的组件
        self.input_image = tk.PhotoImage(None)
        self.input_image_label = tk.Label(self, image=self.input_image)
        self.input_image_label.grid(row=0, column=0, padx=0, pady=0)
        self.input_image_label.bind("<Button-1>", lambda event: self.on_canvas_input_click())

        self.output_image = tk.PhotoImage(None)
        self.output_image_label = tk.Label(self, image=self.output_image)
        self.output_image_label.grid(row=0, column=1, padx=0, pady=5)
        self.output_image_label.bind("<Button-1>", lambda event: self.on_canvas_output_click())



        # 输入输出框，提示词靠左, 选择文件按钮靠右(图片路径)
        self.input_path_label = tk.Label(self, text="图片路径:")
        self.input_path_label.grid(row=1, column=0, padx=0, pady=3, sticky=tk.W)

        self.input_path_button = tk.Button(self, text="选择图片", command=self.select_input_path, width=10)
        self.input_path_button.grid(row=1, column=1, padx=0, pady=3)

        self.input_path_entry = tk.Entry(self, width=55)
        self.input_path_entry.grid(row=2, column=0, padx=0, pady=3, columnspan=2)
        self.input_path_entry.bind("<Return>", lambda event: self.input_path_entry_update())
        self.input_path_entry.bind("<FocusOut>", lambda event: self.input_path_entry_update())

        self.output_path_label = tk.Label(self, text="保存路径:")
        self.output_path_label.grid(row=3, column=0, padx=0, pady=3, sticky=tk.W)

        self.output_path_button = tk.Button(self, text="选择文件夹", command=self.select_output_path, width=10)
        self.output_path_button.grid(row=3, column=1, padx=0, pady=3)

        self.output_path_entry = tk.Entry(self, width=55)
        self.output_path_entry.grid(row=4, column=0, padx=0, pady=3, columnspan=2)
        self.output_path_entry.bind("<Return>", lambda event: self.output_path_entry_update())
        self.output_path_entry.bind("<FocusOut>", lambda event: self.output_path_entry_update())



        # 加密解密按钮，使用单选框形式，加密按钮不可用，解密按钮可用
        self.encrypt_button = tk.Button(self, text="加密模式", command=self.set_encrypt_patter, width=30, state=tk.DISABLED, relief=tk.SUNKEN)
        self.encrypt_button.grid(row=5, column=0, padx=0, pady=3)

        self.decrypt_button = tk.Button(self, text="解密模式", command=self.set_decrypt_patter, width=30, state=tk.NORMAL, relief=tk.RAISED)
        self.decrypt_button.grid(row=5, column=1, padx=0, pady=3)

        self.pattern = tk.StringVar()
        self.pattern.set("encrypt")



        # 边裁剪数量滑条, 不显示刻度
        self.edge_cut_num_label = tk.Label(self, text="边裁剪数量: 5")
        self.edge_cut_num_label.grid(row=6, column=0, padx=0, pady=3, sticky=tk.W)

        self.edge_cut_num_scale = tk.Scale(self, from_=1, to=6, orient=tk.HORIZONTAL, length=200, showvalue=0, command=self.edge_cut_num_scale_update)
        self.edge_cut_num_scale.grid(row=6, column=1, padx=0, pady=3)



        # 密钥输入框，提示词靠左, 密钥输入框靠右(密钥)，默认隐藏
        self.key_label = tk.Label(self, text="密钥:")
        self.key_label.grid(row=7, column=0, padx=0, pady=3, sticky=tk.W)

        self.key_entry = tk.Entry(self, width=55)
        self.key_entry.grid(row=8, column=0, padx=0, pady=3, columnspan=2)

        self.key_label.grid_forget()
        self.key_entry.grid_forget()



        # 开始按钮和进度条
        self.start_button = tk.Button(self, text="开始", command=self.start_patter, width=30)
        self.start_button.grid(row=9, column=0, padx=0, pady=3)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
        self.progress.place(x=230, y=412)



        # 密钥输出文本框，可编辑
        self.key_output_label = tk.Label(self, text="密钥输出:")
        self.key_output_label.grid(row=10, column=0, padx=0, pady=3, sticky=tk.W)

        self.key_output_entry = tk.Entry(self, width=55)
        self.key_output_entry.grid(row=11, column=0, padx=0, pady=3, columnspan=2)
        self.key_output_entry.bind("<FocusOut>", lambda event: self.key_output_entry_update())

        self.key_output = tk.StringVar()

    # 图片输入框点击事件
    def on_canvas_input_click(self):
        print("Input image clicked")
        # 弹窗选择文件
        self.select_input_path()

    # 图片输出框点击事件
    def on_canvas_output_click(self):
        print("Output image clicked")
        # 若存在图片则打开图片
        image = self.get_output_image()
        print(image)
        if image is not None:
            image.show()
        else:
            # 弹窗选择文件夹
            self.select_output_path()

    # 输入文本框更新
    def input_path_entry_update(self):
        self.get_input_image()

    # 输出文本框更新
    def output_path_entry_update(self):
        self.get_output_path()

    # 边裁剪数量滑条更新
    def edge_cut_num_scale_update(self, value):
        value = int(value)
        max_edge_cut_num = 0

        # 计算最大边裁剪数量
        if self.has_input_path():
            width, heith = self.get_input_image().size
            edge = max(width, heith)
            max_edge_cut_num = edge // 4
        else:
            max_edge_cut_num = 100

        # 边裁剪数量限制
        if value == 1:
            self.edge_cut_num = 5
        elif value == 2:
            self.edge_cut_num = 10
        elif value == 3:
            self.edge_cut_num = 20
        elif value == 4:
            self.edge_cut_num = 50
        elif value == 5:
            self.edge_cut_num = 100
        elif value == 6:
            self.edge_cut_num = max_edge_cut_num

        # 边裁剪数量限制
        if self.edge_cut_num > max_edge_cut_num:
            self.edge_cut_num = max_edge_cut_num

        # 显示边裁剪数量
        if value <= 5:
            self.edge_cut_num_label.config(text="边裁剪数量: " + str(self.edge_cut_num))
        else:
            self.edge_cut_num_label.config(text="边裁剪数量: 最大(" + str(max_edge_cut_num) + ")")

        # 输出边裁剪数量
        print("Edge cut number:", self.edge_cut_num)

    # 密钥输出框更新
    def key_output_entry_update(self):
        self.key_output_entry.delete(0, tk.END)
        self.key_output_entry.insert(0, self.key_output.get())

    # 选择输入文件路径
    def select_input_path(self):
        path = filedialog.askopenfilename(title="选择图片",  # 对话框标题
        filetypes=[("图片文件", "*.jpg *.png")])
        self.input_path_entry.delete(0, tk.END)
        self.input_path_entry.insert(0, path)

        # 显示图片
        image = self.get_input_image()
        if image is not None:
            self.show_image(image, self.input_image_label)
            self.input_image = image

    # 选择输出文件夹路径
    def select_output_path(self):
        path = filedialog.askdirectory()
        self.output_path_entry.delete(0, tk.END)
        self.output_path_entry.insert(0, path)

    # 是否存在输入文件路径
    def has_input_path(self):
        path = self.input_path_entry.get()
        if not os.path.exists(path):
            return False
        return True

    # 获得输入文件路径的图片
    def get_input_image(self):
        path = self.input_path_entry.get()
        if not os.path.exists(path):
            self.input_path_entry.config(fg="red")
            self.input_image_label.config(image=None)
            return None
        image = open_image(path)
        self.image_name = os.path.basename(path).split(".")[0] + "_" + str(self.edge_cut_num) + ".png"
        print("Input image:", self.image_name)
        self.input_path_entry.config(fg="black")
        self.show_image(image)
        return image

    # 获得输出文件路径的图片
    def get_output_image(self):
        return self.output_image

    # 获得输出文件路径
    def get_output_path(self):
        path = self.output_path_entry.get()
        if not os.path.exists(path):
            self.output_path_entry.config(fg="red")
            self.output_image_label.config(image=None)
            return None
        self.output_path_entry.config(fg="black")
        return path

    # 显示图片到input_image_label或output_image_label
    def show_image(self, image, label=None):
        # 缩放图片
        image = scale_image(image, 200)

        # 显示图片
        if label is None:
            label = self.input_image_label
        self.photo_image = ImageTk.PhotoImage(image)
        label.configure(image=self.photo_image)
        label.image = self.photo_image

    # 保存图片
    def save_image(self, image, path):
        print(path + "/" + self.image_name + ".png")
        try:
            image.save(path + "/" + self.image_name + ".png")
            print("Image saved successfully")
            return True
        except:
            print("Error: Failed to save image")
            return False

    # 设置加密模式
    def set_encrypt_patter(self):
        print("Encrypt mode")
        # 设置模式
        self.pattern.set("encrypt")
        # 设置加密按钮不可用，解密按钮可用
        self.encrypt_button.config(state=tk.DISABLED, relief=tk.SUNKEN)
        self.decrypt_button.config(state=tk.NORMAL, relief=tk.RAISED)
        # 隐藏密钥输入框
        self.key_label.grid_forget()
        self.key_entry.grid_forget()
        # 显示滑条，密钥输出框
        self.edge_cut_num_label.grid(row=6, column=0, padx=0, pady=3, sticky=tk.W)
        self.edge_cut_num_scale.grid(row=6, column=1, padx=0, pady=3)
        self.key_output_label.grid(row=10, column=0, padx=0, pady=3, sticky=tk.W)
        self.key_output_entry.grid(row=11, column=0, padx=0, pady=3, columnspan=2)
        # 设置进度条位置
        self.progress.place(x=230, y=412)

    # 设置解密模式
    def set_decrypt_patter(self):
        print("Decrypt mode")
        # 设置模式
        self.pattern.set("decrypt")
        # 设置解密按钮不可用，加密按钮可用
        self.encrypt_button.config(state=tk.NORMAL, relief=tk.RAISED)
        self.decrypt_button.config(state=tk.DISABLED, relief=tk.SUNKEN)
        # 隐藏滑条，密钥输出框
        self.edge_cut_num_label.grid_forget()
        self.edge_cut_num_scale.grid_forget()
        self.key_output_label.grid_forget()
        self.key_output_entry.grid_forget()
        # 显示密钥输入框
        self.key_label.grid(row=7, column=0, padx=0, pady=3, sticky=tk.W)
        self.key_entry.grid(row=8, column=0, padx=0, pady=3, columnspan=2)
        # 设置进度条位置
        self.progress.place(x=230, y=439)

    # 开始按钮
    def start_patter(self):
        print("Start")
        # 设置开始按钮不可用
        self.start_button.config(state=tk.DISABLED)
        # 获得输入文件路径的图片
        image = self.get_input_image()
        if image is None:
            # 输入文件路径不存在，弹窗提示
            print("Input file path not exists")
            messagebox.showerror("错误", "输入文件路径不存在！")
            return
        # 获得输出文件夹路径
        output_path = self.get_output_path()
        if output_path is None:
            # 输出文件夹路径不存在，弹窗提示
            print("Output folder path not exists")
            messagebox.showerror("错误", "输出文件夹路径不存在！")
            self.start_button.config(state=tk.NORMAL)
            return
        # 获取模式
        pattern = self.pattern.get()
        # 进行加密或解密
        if pattern == "encrypt":
            # 加密模式
            # 获取边裁剪数量
            self.edge_cut_num = self.edge_cut_num
            # 加密
            new_image, key_output = encrypt_image(image, self.edge_cut_num, self.progress)
            # 显示图片在output_image_label
            self.show_image(new_image, self.output_image_label)
            # 显示密钥输出框
            self.key_output.set(key_output)
            self.key_output_entry.delete(0, tk.END)
            self.key_output_entry.insert(0, key_output)
            # 保存图片
            self.output_image = new_image
            self.save_image(new_image, output_path)
            # 弹窗提示
            messagebox.showinfo("成功", "加密成功！")
        elif pattern == "decrypt":
            # 解密模式
            # 获取密钥
            key = self.key_entry.get()
            # 解密
            new_image = decrypt_image(image, key, self.progress)
            # 显示图片在output_image_label
            self.show_image(new_image, self.output_image_label)
            # 保存图片
            self.output_image = new_image
            self.save_image(new_image, output_path)
            # 弹窗提示
            messagebox.showinfo("成功", "解密成功！")
        # 设置开始按钮可用
        self.start_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    # 窗口标题
    root.title("图片加密")
    # 窗口不可最大化
    root.resizable(0, 0)
    # 窗口图标
    icon_base64 = "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u7Vqz7nF/v/U6cf8lP99+i3/TvoS/0//N/9p4mjrTpdJVsr/uxW4/az8fPyJ/1b7kv9//dHwJrb5BCax+QH///8A+lQxArxJMAC8SS8Av1I62vfEmv/8vFX//M9G//rlbf///9LHk5ZMscnMd+7v/2j/0Pog/838P//c/a3kaPPqvXDx3cj//tXo0P2V/4/6Jv9k+gj/af83/3/hceZYm05R4P/HD8T9r9a0/ajjovyl4ZX8u/8nw/kEJrf5Af///wD6RzcC7Lm2AO29ugDCT0rT96yE//qGEf/6pAD/+s4z////xL2TkUiqysZu6vT7UP/U9AD/0voj/9/9nuFq/eC6c/3Uxv//zezm/rz/1Pye/8b8kv/H/6H/reCV9jhxKntvpWQD2v/CMsj9ujax/Ks2mvu3RCnS+QT///8A////APo8QAP///8A////ANRIU8L4rZX9/I5B//ukMf/8zFj///zBzI2SRbTJxXPo/fqT/+72cv3u+4T/5/6732X/wLRr/LPF//3Q4v//3vH//eb6//3k9f//4ufJ6rfSHaFKgnrNWwCS/XoAhfx7AKj9rQCY+7oALPbsBP///wD///8A+jNIA/yDlgD8gpVZ8pyl4v3g2P7+1Ln//dmz//3jsv/+6rjy0ceI5+nipvH+/NH6/P7b+vv/2f/3/+Thf+2kwCnTY81x2XrNf+9wvH3+YbZy+2u6d/1/wGfvks4qznKVq/97LWT7TS9e+1gvpP2uKp78sQAs+s0E////AP///wD6LVEB+h5KAPkXQ8D/4OH//tPQ//3Lwv/9y7v//s+1//3ZtP//6sL//+24/fzsqvv88ar8+far/v36w/PP7bzlhNme3oHfoc+J75O+if6Csn/8jL1f/H22LvRcqJblndaT/WO7Y/tFvVv7T72l/ayypP2nAC36pAT///8A////APosXAH6L2MA+ilevP7P1fz7b3H/+2FU/vtoSP/8imP//tfA//3jyf/80o7/+8dF//nQMP/24Tz+9e51///+3P////zz///S7vz/vvP1/cP1///n+NP9yM1h+1dw9//J8IL5Of9a+hr/Tvom/6j9o/+l/Z8ALPp4BP///wD///8A+ixoAfovbwD6KWu9/svW/Po9S//6KSj++jIX//tnQv/+3ND//ujd//zCgf/6phv++bYD//fQE//45mX//fvV//f+xv/g+1L/xPoL/7P6Fv/N/HP/vPyg43L6XIrw/cbYm/o4/3f6Fv9q+iX/sP2b8K39lwAs+lIE////AP///wD6LHUB+i96APopd77+y9n8+jtd//ooP/76LC7/+2BU//7e2f/+8ez//b2R//uMJv76mwz/+r8e//vea//++tj8+vvJ+un0TP3Q9QD/w/oJ/9r8bf/F/KDkePtRl/r/zt/Q/oP/u/5t/7P+dP/D/6P3wv+hAC/6OgT///8A////APosgwL6LooA+iSCvP7S3/z7SnP/+zZa/vo4Sv77amv+/uTi//7z8P/9upz/+4I4//qOIf76szH++9Zz//71zv3898b68/B2/OfzPv7g+UX+6/yP/879nuaD+Umb5/G4y93ysejW8qjn0PKj6MLylt7C8pcAPvovAv///wD///8A+i2RAvosow36OJe4/+fx+/7r8f/+4ef//d3k//7g4//+6On//uXi//7c0//92cj//d3H//3ixf/+5r7//uy7+/3wv/X89sH1+vnC+Pj7xPj7/s7/2f2l7nfiKptvpS9xdq42eHWuNHd0rjN3ca0xcXGtMQBS+iwC////AP///wD6LKID+iyhjv/0+ej////+///////7/P//8/b//u3w//7q6f/+6Ob//uXh//7k2v/+5tn//ujY//7pz//+6sH//u7B/v71y/78+c/++/rQ/v/+1v/W6KL/X6EX92qlJupqpiXqaqYl6mqmJt1opiLRaKYiAGb6LQP///8A////APsrsQH8Kq2G/+34+v/3+///9vn///T3///x9v//8PP//uvt//7o6P/+4uD//t7Y//7bz//+3sz//ufR//7t2f/+57z//dh8//vcav/352z/9e57//f6v//w/Mv85/qn9uL5ofXe+aX33fqw85n3Kpuc9y8AfPotBP///wD///8A////AP8otnb/7vj3+kae//o3iv76MXn/+kR6/v7d5v///f7//9ze//pbXP/5QTX++lEq/vt6TP/90rv//vz4//3dtf/7tjz++rkV/vfRG//14Db++vi9//b/xf/Z/Dr+zfst/sb7RP/b/qD6qfsrnav7LwCO+i0F////AP///wD///8A/yK1VP/t+PX6OaX/+ieN/vogef76NXv+/tvn////////4uf/+klb/vkoL/76OSL++2dI/v3Qv//+/////dO1//uZNf76mgz++rsT//nSMf789L7/9/u9/9/yGf/T9wz/zfsl/9/9l/q1+iugt/ovAJ36LAb///8A31j/AP///wD/F8VH/+r59Portf/6F5v++g6E/volgv7+2Oj////////k6v/6NVj++Qop/voXGf/7TkP+/c/G/v7////90b//+4k///qDFP/6pxz++8Q6//7wvf/7+MD/7+9R/uXzQv3i+VH+6fye+cP6K6PE+i8ArPotBv///wDXANcA////AP8V10v/6fr1+1/S//tOwP77SKz++1mp//7i7////////+vw//tlh/76QWP++0RT/vtsbv7+1dH//v78//3i2v/8wqn//buQ//3Hi//91ZH//u2+//71xv76+Lj59vim+fT7pfrw/KL4zvoppM/6LgC5+iwG////AP///wD///8A+CfsWf7p/fX+2PX//tPx//7S7P/+1uv///j7////////+vv//tni//7P2f/+z9X//tTZ//7m5//+6+j//vHv//7////+/v3//vfy//7w3v/+6MP//u7E//30xfz89LP9+fau/fL4m/nY+Sql2fkvAMb6LAj///8A////AP///wDUOfyC/Ov/+P////////////////////////////////////////////////////////////X2///o6f//6ur+/uLh/v3d2P/92s7+/dfC/v3hxv/85Ln/+9Fq//vaWv/45WL/9fSX++D1K6jh9S8A0vosCv///wD///8A////AKI0/6756v/69tD8//nM+f/8yfX//s30///2/f////////n8//7R5v/9xt3+/sXX//7U3v//7vH///n6///V2f78fX7++2VY/vt0VP77jGP+/dXA//zasf/6rCr/+r8e/vnUL//68Jv75u8qrOfvLgDc+CwM0votAQIA/wFHEP8BbB//vvPl//rWXPr/4k/w//BF4/75U93+/+D4////////6/b/+1+s/vo4jv77NXn++2WS/v7X4f///////szU//tCT/76Ghr++jQa//taNP7+ybn//c2s//qJH/76nBH/+rkj//zqovvt6Cqv7uguAOTxLA3///8A////ACgA/wEzCf+159v/+bAu/v7IJPb+3xno/u8r3v792fn////////l9P/6NaP++QR///oAYv77PH7+/s7d///////+zNb/+zxd//oQLP/6Jyj/+0s+/v3Euf/9zrb//IxH//ubPf/7uFH//O23/vPjKbbz4y4A6+otDv///wD///8AAAD/AQkA/6LVzf/5eyv//qQu//7FLPr+3j3w/vrc+////////+L3//pAvf75FZ7++hGD/vtFlf7+z+H///////7V3v/8X4L/+zlc//tGVv/8aGn//cG8//ynovz9nYj7/KqK/P24lPz8yp7598ArxvfBLwD///8A////AAAA/wD///8AAAD/kNPR//llPP//j0H//7pK///WWfj/+t/7///////+3/j//FvR//s3uf/7NqP//F+s//3W5v/+8vj//cjf+/6/1fr9t8v6/a/A+/24w/z9mqXp+iY5rfo5Oan6RDGs+k8prfpfJqz6bi2f+m0tAP///wD///8AAAD/AP///wAAAP+LwsL/7c7O//PVzv/z39L/8+rW//Py2f7z99r+8/rY+vL81/nx/tb28f7W8/L+1/Dy/uX0+P2Qx9/6JIi4+iN3rfonbLL6JmC0+iVTvfosToP6Q1AA+kNAAPpOOQD6WjMA+moyAPp3LQD6di0A////AP///wD///8AAAD/AQAA/2MAAP+iAAD/qwsA/6k5DP+odCP/qKc1/6rGOfuo2jfxn+ky5pr2Ldmb+izKn/osuqb6Kai++z2iXPtClQD6LX0A+jByAPovZgD6L1oA+jRUAPpCTwD6Q0AA+k45APpaMwD6ajIA+nctAPp2LQD///8A////AP///wAAAP8BAAD/BAAA/wgAAP8FAAD/BAAA/wQ4AP8EmAD/BOkR/wP/EP8D/xf7A/8c5wP/HtQE/x/EBv8fsQj/H50K/x+KDv8feg//H2sP/x9dD/8fUA//JUkP/jFFEPo8PxP6RzcT+lQxEvpjLBH///8A////AP///wD///8A////A////wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wB4AAP+gAAAAb///4GwAAABsAAAALAAAACwAAABsAAAfaAAAAWgAAAFoAAABaAAAAWgAAAFoAAABYAAAAWAAAAFgAAABcAAAAXAAAAFwAAABcAA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LQD6LKMA+iyjAPoenRn6KaJ2/aXXwf/2++///v78///////+/v///P3///j6///z9v/+7/L//uzt//7q6f/+6Of//ufk//7l4f/+5Nz//uXa//7m2P/+59f//ujU//7pzv/+6sf//uzC//7twP7+8L/+/fK+/vz1v/7798D+/frF//j5w//i7q3/qc1t/HiwNvZ+szvvgLQ97H+0O+1+tDztf7U+6Hy0O99xsSjObbAhY3F5GwBm/zoBavotAmr6LQD7K6wA/CqrAPsbpRf8KKpx/qbcxP/y+vn/+fz+//r8///5+v//9/n///X4///y9v//8PP//u3v//7q6//+6en//ubl//7j4P/+4dv//t/W//7e0f/+4M///uTQ//7o0v/+7NT//uvL//7mtP/935L//N6B//vjfP/46X3/9+6C//byk//y9rL/5fK2/tfsqPvT7Jf20OyP9M7rjvTM65D1zOyY9cPsjOWc50KyiOUcULPCIABs/zACefotAnn6LQD7K7UA/imyAP0YrBX9JrFp/6zhwP/h8fv9rdT//JjG//2WwP/8k7n//JS2//2owf/+2uT///H0///y8///5eb//cDB//ycmv/8kor//JKA/vyaf//8qIn//cSo//7hzf/+8eT//u3V//3dqP/8y2n/+8dI//rNPf/32T//9eFH//XqZ//5963/+v3N/vX/wP3n/oT73/1t+tr9bfrW/Xb72/6W/dj+numy/UurnP0cSv//IgB5+S4DhvotAob6LQAAAAAA/ye2AP8TrxL/JLVd/7Xnt/7R6fn7YK7/+jWS//oyh/76Lnv/+jF0/vtbi/79wtT///T3///5+v//4+b//Zqe//pSVP/5Pzn++UIr/vpTLf77b0T//KSC//3ax//+9vD//u/e//3UoP/7uE/++7Ai/vq4E/74yRj/9tUi/vbiTP7686f/+fzK//H+rP/f+0z+0/on/sz6Kf7I+zn/0v1y/9b+kuy3/EiupvseS///HACH+i0DkfotA5H6LQAAAAAA/yO1AP8JrA7/H7RK/77qqv7P6vj7WLH/+iuV//oniP76Inv++iZ0/vtSjP79wNT///T3///7/P//5+v//Zah//pFUv75LzX++TEm/vpDKP77YUH+/J2C//3Zyv/++PX//u3g//3Ln//7p0v++psd/vqkDf76uRL/+cke/vnaSf7776f/+vrI//P6o//i9Tj/1/UQ/9D4FP/M+iT/1vxk/9n9jOy++0awrvofTP//AACT+i0Em/osA5v6LAAAAAAA/x28AP8Asgz/F7o+/8Lto/7M7Pf7T7n++iCe//obj/76FYH++hl5/vtIj/79vNX///P4///8/P//6e3//ZCh/vo1T/75GzH++Rsf/votIf77UDz+/JSC/v3Yzv/++Pb//uzj//3Go//7mUz/+okc/vqRDP76qRH++rwe/vvRSv/966b//PfH//b4pv/q8Uj/4fIk/tv2Jf7Y+TP/3vts/9/8jezG+0axuPofTgD8fgCd+i0EpPotA6T6LQAAAAAA/xbIAP8AwAv/Ecc6/8HxoP7L7vf7UsT++iOs//odnf76GI7++huF/vtKmP79vdn///P4///8/f//6+///ZGm/vo0V/75GDj++hQn/volJ//7SEL+/JGI/v3Z0v7++Pf//u3n//3IsP/7nWP/+4s4//qRKf/6piz++7k3//zOXP/+6ar//fXG//r2sf/z8nL97PJX/ef1VPzl+F396PuC/ub8kezO+0azwfoeTv//AACn+i4ErvotA676LQAAAAAA/xXUAP8Azgv/ENM9/73zov7Q8vj8b9X/+0jD//tCtv77Pqj++0Gg/vtor//9yOH///X6///9/f//7vL//aS4/vtVeP76PF7++jZO/vtCTP77XmD+/J2a/v7c2P/++Pb//vHt//3Yy//8vqH//LOH//y0ev/8vnj//cl7//3XjP/+6bT//vLF//32wP359qz79ved+vP4lfrx+pf68fyf/Ov8k+vU+kWzyPocT//8AACw+i0Et/osA7f6LAAAAAAA/R7iAP0A3gz9GeFC/rj2pf7c+Pj9qej//JTe//2Q1/79js/+/JDK//2m0v/+3+7///n8///+/v//9fj//snW//ybsf78jKL+/IeY/vyNl/78nKH+/b7A//7i4P/+8e///vHt//3p4//95dv//eHS//7gy//+4cX//uK///7lvP/+6cD//u7D//7zxv7898b7+/e8+vn3s/v4+bD79fqp/e36kOza+kS00PodT0D8PQC7+i0FwPosBMD6LAAAAAAA8SvwAO8U7g/wJ+9P+rL6rv7o/Pj+4vj//t31//7b8//+2/D//tvv//7j8f//9fr///3+/////////Pz//+7y//7f5v/+2uH//tje//7Z3v/+2+D//uPl//7p6f/+6uj//u3r//7y8f/++fn//vv7//759//+9O///vDk//7s1//+6Mf//unD//7twP/97rj9/O+t/fvwpP3586L99vWg/u/3jOzf+ES11/geUJv/MQDF+iwGyPosBMj6LAAAAAAA2Tf6ANUm+hTYNPpm8Kz9vf3u//r/+P7///r9///5/f//+fz///n8///6/f///f7//////////////v////z9///6+///+fr///j5///4+f//+fr///b3///x8v//6ur//+rq///r6/7+6ej+/ubk//3j3v/94df+/d7O/v3dx/794cb//eXC//zjsP/82YX/+9pv//vgav/55m7/9++G//L1iu7k9kS23PYfUbf/LgHO+ywH0PosBdD6LAAAAAAAuTf+ALQq/hm5Nf5/4aT/zvvs//v87f7//Oz9//3r/f/+6vz//ur7///u/P//+f7///7//////////f7///X6///s9f/+6vP//unx///q8P//7vL///H0///z9P//8fL//+nr/v/Y2f79uLj+/Kij/vyjmP78p5P+/KyR/vy5m/791Lv//ODC//zaov/7xFr/+sQ8//rPO//52kT/+Ohz//Xyi+/o8kS54fIfUsj/LgHW+iwI1/ksBtH6LQABAP8AnDL/AJIk/x2XLv+Tz5v/2/fj/vvzxfz/87j6//a29v/5tPP//LTw//7C8v//6fr///v+///+////+fz//tvs//272v/9sNL+/azL/v2wyf/9vs///tbg///t8f//+Pn//+vt//7DyP78g4b++2Fe/vtaTP77ZUn++3RO/vuRbP79xq7//drA//zPmf/6rj7/+q0c/vq9Hf75zCn/+uBo//jvju/s7kW75e4eU9P/LgHc+CwJ3fcsB9H6LQEBAP8BgSf/AGwX/yBzIP+cvJP/4fDT/vvghPv/4Gb2/+hi7//wXOj+9l3i/vt85f7+z/X///b9///9/v//8fn//bDX//tssf77VZ/++0yQ/vtTjP77cJr+/arB//7i6f//+fv//+vv//64wP/8YWv++zM4/vopI/76OSL/+k0q/vt0Uf79uqX//tO9//zElf/6mTj++pUU/vqmFP/6uSD/+9Vm//rrku/v6ka86ukeVNr7LgHh8ywJ4/IsB7z/LgABAP8BVhb/AEYI/yBOEv+bqYz/4OfG//vLXfz+yzb4/9kz8P7lK+f+7yzf/vZV4f79wfP///T9///9/v//7ff//ZjO/vo9n/76H4j++hN0/vodbf77Qn/+/I+x/v7b5f//+fr//+zv//2zv//7VGn/+iA1/voVHv/6JR3/+jol/vtkTP79s6P//dG+//3DnP/7lEb/+44l//qeJv/6sjP//NN3//vsnfHz6EjA7+YcVuHzLwHn7i0K6O0tB+jtLQAhAP8ALQj/ACEA/x4qBf+Ul4X/29q8//qyS/7+siT7/sYj9f7XHe3+5B7l/u9K5f76vfX//vP9///8/v//6vf//Y7P/votof75DYn/+QFz/voLa/77Mnz+/Yav/v7Y5P//+Pr//+3w//62xP/8WXb/+yZH//oZMv/6Jy//+zo2//tjWf79sKb//cy+//2/o//8mWP//JRL//uiTf/7tFn//NGN//vnovT24EjG89wcWt/8MgHq7C4I6+otBuvqLQAGAP8AEQL/AAMA/xwOAP+JiIH/1cq0//qTR//+kyb+/q8r/f7EKfj+1Svx/uVV7/72wPj//vT+///8/v//6fj//ZHY/vo1s/75GJ7++QyJ/voVgP77OY3+/Ym4/v7Y5v//+Pv//+/y//6/zP/8bYz/+0Bk//szUv/7PU7/+05U//xzcf/9sq3//by1/vyrn/39noT8/KB8/fyrf/39tof9/cWa/vvPkvP4yEPO9sUgYPy0KgDM/zQB6+otAevqLQAAAP8AAwD/AAAA/xkAAP9+hoT/zsK0//t9Sv//eyv//500//+3Nv7/yzr4/95h9f/1xfr//vX9///7/v//5/n//Zbg//tCwv/6J6//+h2d//smk//7Rpz//JDB//7a6P/+9vn//uvy//7I2f/9nrf//Yai//x9lv/8fpD//ImU//2an/79rK/5/JKX6ftvctr8cmvY+3lo2fuCaNr8imna/JRs2vubYdT5mji/+JknW/mZLAD5mSwAAAAAAAAAAAAAAAAAAAD/AAAA/xcAAP93hYX/yMK7//mHav/9hVP//qJa//67YP/+zmT8/t+B+v70zPv+/fH9/v72/v7+5Pr9/afp/fxq1P38Vsf9+0+5/fxWsf38bbb9/ajQ/v3c6/7+4/D7/czj9v2x0vH9rcvv/ajF7/2kve/9n7bw/aK18/2ise/9k6He/GJys/on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"
    icon_data = base64.b64decode(icon_base64)
    icon_image = Image.open(io.BytesIO(icon_data))
    root.iconphoto(True, ImageTk.PhotoImage(icon_image))
    app.mainloop()