#-*- coding:utf-8 -*-
'''
Created on 2019年4月4日

@author: Administrator
'''

import cv2
import numpy as np
import sys
import os

caffe_root='D:\\caffe\\caffe-master'
sys.path.insert(0,caffe_root+'python')
os.environ["GLOG_minloglevel"]= '3'
import caffe

video_full_path = "http://qnmov.a.yximgs.com/upic/2018/06/06/12/BMjAxODA2MDYxMjQwMTZfMTkzMDUyMjRfNjU2NzMwNzI5MF8xXzM=_hd3_Bc143c8abf799984d2cc75a52de7039f0.mp4"
EXTRACT_FREQUENCY = 24# 帧提取频率

def video_process(video_full_path,EXTRACT_FREQUENCY):
    result_num = []
    caffe.set_mode_gpu()

    model_def = 'D:/EclipseWorkspace/caffe_exe/deploy_full_conv.prototxt'
    model_weights = 'D:/EclipseWorkspace/caffe_exe/model_60000_conv.caffemodel'
    net=caffe.Net(model_def, model_weights, caffe.TEST)
    
    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
    transformer.set_transpose("data", (2,0,1))
    transformer.set_raw_scale('data', 255)
    transformer.set_channel_swap('data', (2, 1, 0))
    
    EXTRACT_FREQUENCY = 24
    cap_video = cv2.VideoCapture(video_full_path)
    count = 1
    video_img = []
    video_result_num = []
    while True:
        rval,frame = cap_video.read()
        if rval == True:
            if count % EXTRACT_FREQUENCY == 0:
                video_img.append(frame)
                net.blobs["data"].data[...] = transformer.preprocess("data", frame)
                output = net.forward()
                output_prob = output['prob'][0].argmax()
                video_result_num.qppend(output_prob) 
        else:
            break
        count += 1
    cap_video.release()
    cv2.destroyAllWindows()
    return  video_img

if __name__ == '__main__':
    video_img = video_process(video_full_path,EXTRACT_FREQUENCY)
    print len(video_img)