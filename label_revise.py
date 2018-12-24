#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import cv2
import tkinter as tk

global point1, point2
global pressure, ensure
import shutil
from tkinter import *


def write(file, entry, win):
    global pressure
    pressure = entry.get()
    file_handle = open(save_label_file, mode='a+')
    file_handle.write(file + '\n' + pressure + ' \n')
    file_handle.close()
    shutil.move(file_name + file, remove_file + file)
    win.destroy()


def main():
    img_dir=[]
    labels=[]
    f1 = open(label_name, "r")
    label_list = f1.readlines()
    for index in range(int(len(label_list) / 2)):
        file = label_list[2 * index]
        file = file.replace("\n", "")
        label = label_list[2 * index + 1]
        label = label.replace("\n", "")
        img_dir.append(file)
        labels.append(label)

    for root, dirs, files in os.walk(file_name):
        for i in range(0, len(files)):
            img = cv2.imread(file_name + files[i])
            text=labels[img_dir.index(files[i])]
            win = tk.Tk()
            photo = PhotoImage(format="png",
                               file=file_name + files[i])  # PhotoImagecan be used for GIF and PPM/PGM color bitmaps
            imgLabel = Label(win, image=photo)
            imgLabel.pack()

            entry = tk.Entry(win, width=80, font=("宋体", 20, "normal"), bg="white", fg="black")
            entry.insert(0, text)
            entry.pack()
            button = tk.Button(win, text="确认", command=lambda: write(files[i], entry, win))
            button.pack()  # 加载到窗体，
            win.mainloop()
    win = tk.Tk()
    label = tk.Label(win, width=50, text="已完成!!", bg="white", fg="black")
    label.pack()
    win.mainloop()


if __name__ == '__main__':
    file_name = 'split_result/'
    label_name = '1.txt'
    remove_file = 'result_data/'
    save_label_file = '2.txt'
    main()




