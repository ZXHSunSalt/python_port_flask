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
##set parameters to sheild the lod display of caffe model 
os.environ["GLOG_minloglevel"]= '3'
import caffe

def video_process(video_full_path):
    '''
    This function is designed for getting video image and return a list of image in the video
    video_full_path:the url of image
    '''
    # the frequency of extracting frames
    EXTRACT_FREQUENCY = 48
    # read video data
    cap_video = cv2.VideoCapture(video_full_path)
    # flag for the frequency of reading video
    count = 1
    video_img = []
    
    # extract the frames/images 
    while True:
        rval,frame = cap_video.read()
        if rval == True:
            if count % EXTRACT_FREQUENCY == 0:
                video_img.append(frame)
        else:
            break
        count += 1
    
    # finish video process
    cap_video.release()
    cv2.destroyAllWindows()
    return  video_img


def type_judgement(result_num,input_type):
    '''
    This function is designed for judging whether the original results are consistent with the predicted results
    '''
    type_dict = {'smoke':0, 'distraction':1, 'abnormal driving':2,'call':3,'fatigue':4,'other':5}
    # transform input type-list to str
    input_type = "".join(input_type)
    # the output of result is 'yes' or 'no'
    flag_y = 0
    flag_n = 0
    for i in result_num:
        if type_dict[input_type] == i:
            result = 'yes'
            flag_y += 1
        else:
            result = 'no'
            flag_n += 1
    if flag_y >= flag_n:
        result = 'yes'
    else:
        retult = 'no'
    return result

def get_final_result(output_results):
    '''
    THIS FUNCTION IS DESIGNED FOR OUTPUT THE FINAL RESULT ACCORDING THE IMAGE AND VIDEO CLASSIFICAITON OUTPUT RESUTLS
    '''
    
    # COUNT THAT HOW MANY YES AND NO IN THE OUTPUT RESUTL
    count_y = 0
    count_n = 0
    for each in output_results:
        if each == "yes":
            count_y += 1
        else:
            count_n += 1
    
        if count_y >= count_n:
            final_result = 'yes'
        else:
            final_result = 'no'
    return final_result

def img_judgement(pic):
    '''
    This function is designed for image classification.
    There are several steps in this function: 1.import caffe model
                                              2.do image pre-processing
                                              3.do classification according to the caffe model and return the output result
                                                (the type of output result is int number )
    '''
    result_nums = []
    caffe.set_mode_gpu()
    
    # import caffe model
    model_def = 'D:/EclipseWorkspace/caffe_exe/deploy_full_conv.prototxt'
    model_weights = 'D:/EclipseWorkspace/caffe_exe/model_60000_conv.caffemodel'
    net=caffe.Net(model_def, model_weights, caffe.TEST)
    
    # do image pre-processing
    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
    transformer.set_transpose('data', (2, 0, 1))
    transformer.set_raw_scale('data', 255)
    transformer.set_channel_swap('data', (2, 1, 0))
    
    transformed_image = transformer.preprocess('data',pic)
    # copy the image data into the memory allocated for the net
    net.blobs['data'].data[...] = transformed_image
    
    # perform classification
    output = net.forward()
    # the output probability vector for the first image in the batch
    output_prob = output['prob'][0]  
    type_result_num = output_prob.argmax()
    result_nums.append(type_result_num)
    
    return result_nums

app = Flask(__name__)

@app.route('/',methods=['POST'])
def driver_test():
    '''
    This function is designed for communicating with other client and return the classification result.
    1.get data from client
    2.read image and video data
    3.process data and return the result to the client
    '''
    
    # transform data from the client into json data
    data = request.get_json()
    input_type = data['type']
    pics = data['pics']
    video = data['video']
    results = []
    
    # do some process for image
    for pic in pics:
        # transform unicode type data into str
        image_url = pic.encode('utf-8')
        # load image url 
        image=caffe.io.load_image(image_url)
        result_num = img_judgement(image)
        pic_result = type_judgement(result_num,input_type)
        results.append(pic_result)
    
    for v_url in video:
        video_images = video_process(v_url.encode("utf-8"))
        for image in video_images:
            video_result_num = img_judgement(image)
            video_result = type_judgement(video_result_num,input_type)
            results.append(video_result)
            
    final_result = get_final_result(results)
    return jsonify(final_result)

if __name__=='__main__':
    app.run(host='127.0.0.1',port=1234,debug=False)

    
    