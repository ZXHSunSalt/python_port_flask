#-*- coding:utf-8 -*-
'''
Created on 2019年4月2日

@author: Administrator
'''

import urllib2
import matplotlib.pyplot as plt
import cv2
import numpy as np
import os
import sys


caffe_root='D:\\caffe\\caffe-master'
sys.path.insert(0,caffe_root+'python')
os.environ["GLOG_minloglevel"]= '3'
import caffe

def type_judgement(result_num,input_type):
    type_dict = {'Smoke':0, 'Distraction':1, 'Abnormal driving':2,'Call':3,'Fatigue':4,'Other':5}
    input_type = "".join(input_type)
    results = []
    for i in result_num:
        if type_dict[input_type] == i:
            result = 'yes'
            results.append(result)
        else:
            result = 'no'
            results.append(result)
    return results

def url_to_image():
    url='http://localhost:8080/'
    values = {"type":["Smoke"],
              "pic":["http://localhost:8080/00_06_6503_0_00d3caf8571b4ae69b55952986d1a2a0-12r.jpg",
                     "http://localhost:8080/00_06_6503_0_00d3caf8571b4ae69b55952986d1a2a0-15l.jpg",
                     "http://localhost:8080/00_06_6503_0_00d3caf8571b4ae69b55952986d1a2a0-15r.jpg"],
              "video":["http://localhost:8080/02_06_6503_0_f233dbcb8c5340d1a560b02114be521b.mp4"]
    }
    pics = values["pic"]
    input_type = values["type"]
    print input_type
#     images = []
#     for each in pics:
#         header = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36',
#         'Cookie': 'AspxAutoDetectCookieSupport=1',
#     }
#         req = urllib2.Request(url=each,headers=header)
#         # 发送页面请求
#         response = urllib2.urlopen(req)
#         image = np.asarray(bytearray(response.read()),dtype="uint8")
#         img = cv2.imdecode(image,cv2.IMREAD_COLOR)
#         images.append(img)
    return pics,input_type

def img_judgement(pics,input_type):
    result_num = []
    caffe.set_mode_gpu()

    model_def = 'D:/EclipseWorkspace/caffe_exe/deploy_full_conv.prototxt'
    model_weights = 'D:/EclipseWorkspace/caffe_exe/model_60000_conv.caffemodel'
    net=caffe.Net(model_def, model_weights, caffe.TEST)
    
    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
    transformer.set_transpose('data', (2, 0, 1))
    transformer.set_raw_scale('data', 255)
    transformer.set_channel_swap('data', (2, 1, 0))
    
    for each in pics:
        image=caffe.io.load_image(each)
    
        transformed_image = transformer.preprocess('data',image)
        # copy the image data into the memory allocated for the net
        net.blobs['data'].data[...] = transformed_image
        
        ### perform classification
        output = net.forward()
        output_prob = output['prob'][0]  # the output probability vector for the first image in the batch
        type_result_num = output_prob.argmax()
        result_num.append(type_result_num)
    
    return result_num
    
 

if __name__ == '__main__':
    pics_url,input_type= url_to_image()
    type_result_num=img_judgement(pics_url,input_type)
    results = type_judgement(type_result_num,input_type)
    print results