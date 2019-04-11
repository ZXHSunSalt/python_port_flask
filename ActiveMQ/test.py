#-*- coding:utf-8 -*-
'''
Created on 2019年4月11日

@author: Administrator
'''
import stomp
import time
import cv2
import urllib
import json
import numpy as np
from skimage import io
import sys
import os

caffe_root='D:\\caffe\\caffe-master'
sys.path.insert(0,caffe_root+'python')
##set parameters to sheild the lod display of caffe model 
os.environ["GLOG_minloglevel"]= '3'
import caffe

post = 61613
queue_name1 = 'Queue1'
listener_name1 = 'Listener1'

np.set_printoptions(threshold=np.inf)
## set a stomp Connection
conn = stomp.Connection10([('192.168.1.135',post)])
    
def send_to_queue1(conn,msg):
# def send_to_queue1(msg):
    '''
    FUNCTION:RECEIVE MESSAGE FROM CLIENT AND SEND MESSAGE TO QUEUE1
    '''
    conn = stomp.Connection10([('192.168.1.135',post)])
    conn.start()
    conn.connect('admin','admin',wait=True)
    conn.send(queue_name1,msg)
    conn.disconnect()   
    
def receive_from_queue1(conn):
# def receive_from_queue1():
    '''
    FUNCTION:RECEIVE MESSAGE FROM QUEUE1 AND SEND MESSAGES TO QUEUE2 THROUGH LISTENER1
    '''
    conn = stomp.Connection10([('192.168.1.135',post)])
    conn.set_listener(listener_name1, Listener1())
    conn.start()
    conn.connect('admin','admin',wait=True)
    conn.subscribe(queue_name1)
    time.sleep(1) # secs
    conn.disconnect()
    
class Listener1(object):
    '''
    FUNCTION: DEFINE A LISTENER CLASS FOR QUEUE1
            1\GET THE CLIENT MESSAGE-ID,TYPE,PICS,IMAGES OF VIDEO
            2\RETURN ALL THE DATA
    '''
    def on_message(self, headers, message1):
        print '---3---'
        a = json.dumps(message1)
        b = a['image']
        c= np.array(b)
        print type(a)

#         print type(np.array(c))
#         print '---2---'
#         result = self.img_judgement(d)
#         print result
        
    def img_judgement(self,pic):
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
if __name__ == '__main__':
    msg = "http://qnmov.a.yximgs.com/upic/2018/06/06/12/BMjAxODA2MDYxMjQwMTZfMTkzMDUyMjRfNjU2NzMwNzI5MF8xXzM=_hd3_Bc143c8abf799984d2cc75a52de7039f0.mp4"
#     response = urllib.urlopen(msg)
#     image = np.asarray(bytearray(response.read()), dtype='uint8')
#     img = cv2.imdecode(image,cv2.IMREAD_COLOR)
    print '---!1---'
    video_img=video_process(msg)
    print '---0---'
    img = []
    for image in video_img:
        img.append(image)
    print '---00---'
    data = {'image':img}
    print '---000---'
    str_data = str(data)
    print '---0000---'
    str_data1 = str_data.replace('array(', '')
    print '---00000---'
    str_data2 = str_data1.replace(', dtype=uint8)', '')
    print '---1---'
#     f_data = eval(str_data)

#     image = io.imread(msg)
#     data = {'image':image}
#     json_data = str(data)
#     da1 = json_data.replace('array(', '')
#     da2 = da1.replace(', dtype=uint8)', '')
    send_to_queue1(conn,str_data2)
    print '---2---'
    receive_from_queue1(conn)