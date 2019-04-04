#-*- coding:utf-8 -*-
'''
Created on 2019年4月4日

@author: Administrator
'''

import cv2

video_full_path = "http://qnmov.a.yximgs.com/upic/2018/06/06/12/BMjAxODA2MDYxMjQwMTZfMTkzMDUyMjRfNjU2NzMwNzI5MF8xXzM=_hd3_Bc143c8abf799984d2cc75a52de7039f0.mp4"
EXTRACT_FREQUENCY = 24# 帧提取频率

def video_process(video_full_path,EXTRACT_FREQUENCY):
    cap_video = cv2.VideoCapture(video_full_path)
    count = 1
    video_img = []
    while True:
        if cap_video.isOpened():#正常打开
            rval,frame = cap_video.read()
            if count % EXTRACT_FREQUENCY == 0:
                video_img.append(frame)
        count += 1
    cap_video.release()
    return  video_img

if __name__ == '__main__':
    video_img = video_process(video_full_path,EXTRACT_FREQUENCY)
    print video_img