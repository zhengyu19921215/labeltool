# -*- coding: UTF-8 -*-

import os
import filetype
import tkinter as tk
from lib import XML_LIB
import tkinter.ttk as ttk
from tkinter import simpledialog
from PIL import Image, ImageTk
import tkinter.messagebox as mb
import tkinter.filedialog as dir
from tkinter import PhotoImage,Label,Scrollbar,HORIZONTAL,VERTICAL
import shutil
'''
这是一个基于tkinter库的图像标注工具，目前支持标注矩形区域，标注文件支持txt格式
'''

IMAGE_FILE_TYPE = ['jpg','JPG','PNG','png','bmp','BMP']

class MainGUI(tk.Frame):
    '''继承tkinker中的frame类，实现可以自动化调整串口的大小'''
    img = None
    def __init__(self,root):
        super().__init__(root)
        self.root = root
        self.image_index = 0 #当前处理的图像索引
        self.image_paths = []  #工作目录下的所有文件路径
        self.image_names = []
        self.image_label = []
        self.work_dir = ''
        self.factor = 1.0 #图像缩放因子
        self.x = 0;self.y = 0 #存储坐标
        self.clicked = False
        self.save_lables = 'False'

        self.number = 0 #用于矩形画图时直线提醒

        self.lable_Type = 0 #标注类型

        self.scatter_point = []

        self.lable_save_file = XML_LIB.XMLWrite('.','test')

        self.initComponent(root)
        #self.initMenu(root)

    def initComponent(self,root):
        '''初始化界面上的控件'''
        root.rowconfigure(0,weight=1)
        root.columnconfigure(0,weight=1)
        #self.initMenu(root)  # 为顶级窗体添加菜单项
        # 设置grid布局位置
        self.grid(row=0, column=0, sticky=tk.NSEW)
        # 设置行列权重，保证内建子组件会拉伸填充
        self.rowconfigure(0, weight=1);
        self.columnconfigure(0, weight=1)

        #水平方向推拉组件
        self.panedwin = ttk.PanedWindow(self,orient=tk.HORIZONTAL)
        self.panedwin.grid(row=0, column=0, sticky=tk.NSEW)

        self.frame_left = ttk.Frame(self.panedwin, relief=tk.SUNKEN)
        self.frame_left.grid(row=0, column=0, sticky=tk.NS)
        self.panedwin.add(self.frame_left, weight=1)
        self.initPlayList()

        self.frame_right = ttk.Frame(self.panedwin,relief=tk.SUNKEN)
        self.frame_right.grid(row=0,column=0,sticky=tk.NSEW)
        self.frame_right.columnconfigure(0,weight=1)
        # self.frame_right.rowconfigure(0,weight=1)
        # self.frame_right.rowconfigure(1,weight=9)
        self.panedwin.add(self.frame_right,weight=50)

        lable = tk.Label(self.frame_right,font='Times 9 bold',text="图片展示",fg='#4876FF',anchor='nw')
        lable.grid(row=1, column=0,padx=6,pady=6,sticky=tk.NSEW)

        canvas_frame = ttk.Frame(self.frame_right)
        canvas_frame.grid(row=2, column=0)

        self.canvas = tk.Canvas(canvas_frame,background='white')
        self.canvas.grid(row=0, column=0,sticky=tk.NSEW)
        scrollY = Scrollbar(canvas_frame, orient=VERTICAL, command=self.canvas.yview)
        scrollY.grid(row=0, column=1, sticky='ns')

        scrollX = Scrollbar(canvas_frame, orient=HORIZONTAL, command=self.canvas.yview)
        scrollX.grid(row=1, column=0, sticky='ew')
        self.canvas['xscrollcommand'] = scrollX.set
        self.canvas['yscrollcommand'] = scrollY.set


        self.canvas.bind("<Motion>", self.mouse_on_canvas)#self.canvas.bind("<B1-Motion>", self.mouse_move)
        self.canvas.bind('<Button-1>',self.left_mouse_click)
        #self.canvas.bind('<Button-1>',self.left_mouse_click_press)
        #self.canvas.bind('<ButtonRelease-1>', self.left_mouse_click_release)
       # self.showImage('1_0.png')

        # 右侧Frame帧第二行添加控制按钮
        self.frm_control = ttk.Frame(self.frame_right, relief=tk.RAISED)  # 四个方向拉伸
        self.frm_control.grid(row=0, column=0, sticky=tk.NSEW)
        self.initCtrl()  # 添加滑块及按钮

    def initMenu(self, master):
        '''初始化菜单'''
        mbar = tk.Menu(master)  # 定义顶级菜单实例
        fmenu = tk.Menu(mbar, tearoff=False)  # 在顶级菜单下创建菜单项
        mbar.add_cascade(label=' 文件 ', menu=fmenu, font=('Times', 20, 'bold'))  # 添加子菜单
        fmenu.add_command(label="打开", command=self.menu_click_event)
        fmenu.add_command(label="保存", command=self.menu_click_event)
        fmenu.add_separator()  # 添加分割线
        fmenu.add_command(label="退出", command=master.quit())

        etmenu = tk.Menu(mbar, tearoff=False)
        mbar.add_cascade(label=' 编辑 ', menu=etmenu)
        for each in ['复制', '剪切', '合并']:
            etmenu.add_command(label=each, command=self.menu_click_event)
        master.config(menu=mbar)  # 将顶级菜单注册到窗体

    def initCtrl(self):
        '''初始化控制滑块及按钮'''
        frm_but = ttk.Frame(self.frm_control, padding=2)  # 控制区第二行放置按钮及标签
        frm_but.grid(row=0, column=0, sticky=tk.EW)
        self.initButton()

    def initPlayList(self):
        '''初始化树状视图'''
        self.frame_left.rowconfigure(0, weight=1)  # 左侧Frame帧行列权重配置以便子元素填充布局
        self.frame_left.columnconfigure(0, weight=1)  # 左侧Frame帧中添加树状视图

        self.frame_left.rowconfigure(1, weight=1)  # 左侧Frame帧行列权重配置以便子元素填充布局
        self.frame_left.columnconfigure(1, weight=1)  # 左侧Frame帧中添加树状视图
        #文件名称列表
        self.image_name_tree = ttk.Treeview(self.frame_left, selectmode='browse', show='tree', padding=[0, 0, 0, 0])
        self.image_name_tree.grid(row=0, column=0, sticky=tk.NSEW)  # 树状视图填充左侧Frame帧
        self.image_name_tree.column('#0', width=150)  # 设置图标列的宽度，视图的宽度由所有列的宽决定
        # 一级节点parent='',index=第几个节点,iid=None则自动生成并返回，text为图标右侧显示文字
        # values值与columns给定的值对应
        #标签名称列表
        self.lable_tree = ttk.Treeview(self.frame_left, selectmode='browse', show='tree', padding=[0, 0, 0, 0])
        self.lable_tree.grid(row=1, column=0, sticky=tk.NSEW)  # 树状视图填充左侧Frame帧
        self.lable_tree.column('#0', width=150)  # 设置图标列的宽度，视图的宽度由所有列的宽决定
        # 一级节点parent='',index=第几个节点,iid=None则自动生成并返回，text为图标右侧显示文字
        # values值与columns给定的值对应
        self.create_lable_tree(self.lable_tree)

    def menu_click_event(self):
        '''菜单事件'''
        pass

    def create_image_tree(self,tree,work_path):
        tr_root = tree.insert("", 0, None, open=True, text='工作目录',values=('root'))  # 树视图添加根节点
        node = tree.insert(tr_root, 0, None, open=True, text=work_path,values=('path'))  # 根节点下添加一级节点

        for i in range(len(self.image_names)):
            tree.insert(node, 0, None, text=self.image_names[i],values=(self.image_names[i]))  # 添加二级节点
        tree.bind('<ButtonRelease-1>', self.image_tree_click)  # 绑定单击离开事件
    #树形条目点击事件
    def image_tree_click(self,event):  # 单击
        for item in self.image_name_tree.selection():
            item_text = self.image_name_tree.item(item, "values")
            if item_text[0] in ['root','path']:
                continue
            image_path = self.work_dir + '/' + item_text[0]
            self.showImage(image_path)

    #创建标签树
    def create_lable_tree(self,tree):
        self.tr_root = tree.insert("", 0, None, open=True, text='标签类别',values=('root'))  # 树视图添加根节点
        tree.bind('<Button-1>', self.lable_tree_click)  # 绑定单击离开事件
        tree.bind('<Button-3>',self.lable_tree_Rclick)

    # 插入新的标签到标签树
    def insert_label_tree(self,tree,lable_list):
        tree.insert(self.tr_root, 0, None, text=lable_list, values=(lable_list))  # 添加二级节点

    def lable_tree_click(self,event):  # 单击
        for item in self.lable_tree.selection():
            item_text = self.lable_tree.item(item, "values")
            if item_text[0] == 'root':
                continue
            print(item_text[0])
    #lable 树右键点击事件
    def lable_tree_Rclick(self,event):
        for item in self.lable_tree.selection():
            item_text = self.lable_tree.item(item, "values")
            if item_text[0] == 'root':
                print('已经点击了右键' + 'root')
            else:
                print('已经点击了右键')


    def initButton(self):
        lable = tk.Label(self.frm_control, font='Times 9 bold', text="控制界面", fg='#4876FF', anchor='nw')
        lable.grid(row=0, column=0, sticky=tk.NSEW,padx=6,pady=6)

        self.set_work_dir = ttk.Button(self.frm_control,text='设置目录',command=self.set_work_dir)
        self.set_work_dir.grid(row=1, column=0, padx=5,sticky=tk.NSEW)

        self.next_image = ttk.Button(self.frm_control,text='下一张',state=tk.DISABLED,command=self.get_next_image)
        self.next_image.grid(row=1, column=1, padx=5,sticky=tk.NSEW)

        self.pre_image = ttk.Button(self.frm_control, text='上一张',state=tk.DISABLED,command=self.get_pre_image)
        self.pre_image.grid(row=1, column=2, padx=5,sticky=tk.NSEW)

        self.label_rect = ttk.Button(self.frm_control, text='创建矩形',state=tk.DISABLED,command=self.create_label_rect)
        self.label_rect.grid(row=2, column=0, padx=5,sticky=tk.NSEW)

        self.save_lable = ttk.Button(self.frm_control, text='创建矩形保存标注', state=tk.DISABLED, command=self.save_lable_file)
        self.save_lable.grid(row=2, column=1, padx=5,sticky=tk.NSEW)

        self.revise_lable = ttk.Button(self.frm_control, text='修改标注', state=tk.DISABLED, command=self.revise_lable_file)
        self.revise_lable.grid(row=2, column=2, padx=5, sticky=tk.NSEW)

        self.up_zoom = ttk.Button(self.frm_control, text='放大图像', state=tk.DISABLED, command=self.zoomin_image)
        self.up_zoom.grid(row=1, column=3, padx=5, sticky=tk.NSEW)

        self.zoomin = ttk.Button(self.frm_control, text='缩小图像', state=tk.DISABLED, command=self.zoomout_image)
        self.zoomout.grid(row=2, column=3, padx=5, sticky=tk.NSEW)

    def zoomin_image(self):
        self.factor=1.2
    def zoomup_image(self):
        self.factor=1.2


    def revise_lable_file(self):
        img_dir = []
        labels = []
        f1 = open(label_name, "r")
        label_list = f1.readlines()
        for index in range(int(len(label_list) / 2)):
            file = label_list[2 * index]
            file = file.replace("\n", "")
            label = label_list[2 * index + 1]
            label = label.replace("\n", "")
            img_dir.append(file)
            labels.append(label)

        for root, dirs, files in os.walk(self.work_dir):
            for i in range(0, len(files)):
               # img = cv2.imread(file_name + files[i])
                text = labels[img_dir.index(files[i])]
                win = tk.Toplevel()
                photo = PhotoImage(format="png",
                                   file=self.work_dir + '/'+files[i])  # PhotoImagecan be used for GIF and PPM/PGM color bitmaps
                imgLabel = Label(win, image=photo)
                imgLabel.pack()

                entry = tk.Entry(win, width=80, font=("宋体", 20, "normal"), bg="white", fg="black")
                entry.insert(0, text)
                entry.pack()
                button = tk.Button(win, text="确认", command=lambda: write(files[i], entry, win))
                button.pack()  # 加载到窗体，
                win.mainloop()




    # Radiobutton选择时回调
    def radiobutton_change(self):
        #print(self.lable_Type.get())
        self.number = 0

    #设置工作目录
    def set_work_dir(self):
        work_dir = dir.Directory()
        temp_dir = work_dir.show(initialdir='.', title='设置工作目录')

        if temp_dir != '':
            self.work_dir = temp_dir
            self.get_all_img(self.work_dir)
            if len(self.image_paths) < 1:
                mb.showinfo("提醒","当前目录没有图片！")
                return
            self.showImage(self.image_paths[self.image_index])
            #self.image_index = self.image_index + 1
            self.next_image.config(state=tk.ACTIVE)
            self.create_image_tree(self.image_name_tree, self.work_dir)

            self.revise_lable.config(state=tk.ACTIVE)
            self.label_rect.config(state=tk.ACTIVE)
            self.up_zoom.config(state=tk.ACTIVE)
            self.down_zoom.config(state=tk.ACTIVE)
            self.save_lable.config(state=tk.ACTIVE)
        else:
            mb.showinfo("提醒", "目录选择失败！")

    #下一张图片
    def get_next_image(self):
        if len(self.image_paths) < 1:
            mb.showerror("错误", "当前目录中没有图片，请重新设置目录！")
            return
        if len(self.image_paths) - 1 < self.image_index + 1:
            mb.showinfo('提醒', '已经到最后一张！')
            self.next_image.config(state=tk.DISABLED)
            return
        if self.image_index == 0:
            self.pre_image.config(state=tk.ACTIVE)
        self.canvas.delete(tk.ALL)
        names = self.image_paths[self.image_index + 1]
        self.showImage(names)
        self.image_index = self.image_index + 1
        self.x = 0
        self.y = 0

    #前一张图片
    def get_pre_image(self):
        if self.image_index < 1:
            mb.showinfo("提醒", "已经是第一张照片了！")
            self.pre_image.config(state=tk.DISABLED)
            return
        if self.image_index == len(self.image_paths) - 1:
            self.next_image.config(state=tk.ACTIVE)
        names = self.image_paths[self.image_index - 1]
        self.showImage(names)
        self.image_index = self.image_index - 1
        self.x = 0
        self.y = 0

    #获取工作目录下面的所有图像名称
    def get_all_img(self,path):
        file_list = os.listdir(path)
        for i in range(len(file_list)):
            name = path + '/' + file_list[i]
            kind = filetype.guess(name)
            if kind and kind.extension in IMAGE_FILE_TYPE:
                self.image_paths.append(name)
                self.image_names.append(file_list[i])

    #在canvas上显示图片
    def showImage1(self,image_path):
        img = Image.open(image_path)


    def showImage(self,image_path):
        img = Image.open(image_path)
        w, h = img.size
        img = self.img_resize(img,w,h,800,600)
        w, h = img.size
        img = ImageTk.PhotoImage(img)
        self.canvas.configure(width=w, height=h)
        self.canvas.create_image(0,0,image=img,anchor='nw', tags='show_image')


    def mouse_on_canvas(self,event):

        if self.lable_Type == 1 and self.work_dir != '' and self.clicked:
            self.canvas.delete('mouse_move_paint_line' + str(self.number - 1))
            self.canvas.delete('mouse_move_paint_rect' + str(self.number - 1))
            self.canvas.create_line((self.x,self.y),(event.x,event.y),width=3,fill='red', tags='mouse_move_paint_line' + str(self.number))
            self.canvas.create_rectangle((self.x,self.y),(event.x,event.y),width=3, fill='#000', outline='green', stipple='gray12',tags='mouse_move_paint_rect' + str(self.number))
            self.number = self.number + 1



    #点击鼠标左键监听事件，用于获取点击鼠标的位置（x,y）,没有使用
    def left_mouse_click(self,event):

        self.canvas.create_oval((event.x - 5, event.y - 5, event.x + 5, event.y + 5), fill='red',tags='oval')

        if self.lable_Type == 1:
            if self.clicked:
                self.clicked = False
                origin_img=Image.open(self.image_paths[self.image_index])
                box=[self.x/self.factor ,self.y/self.factor  ,event.x/self.factor,event.y/self.factor]
                new_img=origin_img.crop(box)
                all_image=self.image_paths[self.image_index].split('/')
                new_filename=all_image[-1][:-4]+'_'+str(int(self.factor * self.x))+'_'+str(int(self.factor * self.y))+'.png'
                new_filename_path='new_image/'+new_filename
                new_img.save(new_filename_path)
                if self.save_lables:
                   tk_scale(new_filename_path)
            else:
                self.x = event.x
                self.y = event.y
                self.clicked = True

    #
    def create_label_rect(self):
        self.lable_Type = 1
        self.canvas.delete(tk.ALL)
        self.save_lables=False
        if len(self.image_paths) < 1:
            return
        self.showImage(self.image_paths[self.image_index])


    #
    def create_label_scat(self):
        self.lable_Type = 2
        self.canvas.delete(tk.ALL)
        if len(self.image_paths) < 1:
            return
        self.showImage(self.image_paths[self.image_index])
        self.label_rect.config(state=tk.DISABLED)

    #保存标签
    def save_lable_file(self):
        self.save_lables=True
        self.lable_Type = 1
        self.canvas.delete(tk.ALL)
        if len(self.image_paths) < 1:
            return
        self.showImage(self.image_paths[self.image_index])


    #重置大小
    def img_resize(self,pil_image,w, h, w_box=0, h_box=0):
        if w_box == 0 or h_box == 0:
            w_box = w
            h_box = h
        f1 = 1.0 * w_box / w
        f2 = 1.0 * h_box / h
        self.factor = min([f1, f2])
        width = int(w * self.factor)
        height = int(h * self.factor)
        return pil_image.resize((width, height), Image.ANTIALIAS)


def set_mainUI(root):
    root.title('图片标注工具')
    root.option_add("*Font", "宋体")
    center_window(root, 960, 640)
    #root.maxsize(960, 640)
    root.minsize(640,480)
    #root.iconbitmap('app.ico')
    root.config(background='SteelBlue')
    app = MainGUI(root)
    root.mainloop()
def tk_scale(new_filename_path):
    win1 = tk.Toplevel()
    photo = PhotoImage(format="png",
                       file=new_filename_path)  # PhotoImagecan be used for GIF and PPM/PGM color bitmaps
    imgLabel = Label(win1,text="标注界面" ,image=photo)
    imgLabel.pack()

    # label = tk.Label(win, text="请输入:", bg="white", fg="black")
    # label.pack(side=RIGHT)
    entry = tk.Entry(win1, width=80, font=("宋体", 20, "normal"), bg="white", fg="black")
    entry.pack()
    button = tk.Button(win1, text="确认", command=lambda: write(new_filename_path, entry, win1))
    button.pack()  # 加载到窗体，
    win1.mainloop()
def write(file, entry, win):
    global pressure
    pressure = entry.get()
    file_handle = open('2.txt', mode='a+')
    file_handle.write(file + '\n' + pressure + ' \n')
    file_handle.close()
   # shutil.move('split_result/' + file, 'result_data/' + file)
    win.destroy()
#获取屏幕大小
def get_screen_size(window):
    return window.winfo_screenwidth(), window.winfo_screenheight()

#获取串口大小
def get_window_size(window):
    return window.winfo_reqwidth(), window.winfo_reqheight()

#设置串口居中
def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    root.geometry(size)

if (__name__ == '__main__'):
    root = tk.Tk()
    label_name='label.txt'
    set_mainUI(root)
