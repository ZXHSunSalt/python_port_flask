# -*- coding:utf-8 -*-
'''
Created on 2019年4月3日

@author: Administrator
'''
from flask import Flask,jsonify,request
import urllib2
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


def img_judgement(pic,input_type):
    result_num = []
    caffe.set_mode_gpu()

    model_def = 'D:/EclipseWorkspace/caffe_exe/deploy_full_conv.prototxt'
    model_weights = 'D:/EclipseWorkspace/caffe_exe/model_60000_conv.caffemodel'
    net=caffe.Net(model_def, model_weights, caffe.TEST)
    
    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
    transformer.set_transpose('data', (2, 0, 1))
    transformer.set_raw_scale('data', 255)
    transformer.set_channel_swap('data', (2, 1, 0))
    
    
    image=caffe.io.load_image(pic)

    transformed_image = transformer.preprocess('data',image)
    # copy the image data into the memory allocated for the net
    net.blobs['data'].data[...] = transformed_image
    
    ### perform classification
    output = net.forward()
    output_prob = output['prob'][0]  # the output probability vector for the first image in the batch
    type_result_num = output_prob.argmax()
    result_num.append(type_result_num)
    
    return result_num

app = Flask(__name__)

@app.route('/',methods=['POST'])
def driver_test():
    data = request.get_json()
    input_type = data['type']
    pics = data['pics']
    video = data['video']
    results = []
    for pic in pics:
        image_url = pic.encode('utf-8')
        result_num = img_judgement(image_url,input_type)
        result = type_judgement(result_num,input_type)
        results.append(result)
    return jsonify(results)

if __name__=='__main__':
    app.run(host='127.0.0.1',port=8080,debug=False)

    
    