#-*- coding:utf-8 -*-
'''
Created on 2019年4月8日

@author: Administrator
'''
import time
import sys
import json
import stomp
import cv2
import os
import numpy as np
import simplejson
from skimage import io
import shutil
import Configuration

# the path of saving image
path = Configuration.configs['path']
# transform all the data of image numpy array
np.set_printoptions(threshold=np.inf)

caffe_root=Configuration.configs['caffe_root']
sys.path.insert(0,caffe_root+'python')
##set parameters to sheild the lod display of caffe model 
os.environ["GLOG_minloglevel"]= '3'
import caffe

## define queue name and listener name for 3 queues
queue_name1 = 'Queue1'
listener_name1 = 'Listener1'
queue_name2 = 'Queue2'
listener_name2 = 'Listener2'
queue_name3 = 'Queue3'
listener_name3 = 'Listener3'
## define the post port
post=61613
address = '192.168.1.135'

## set a stomp Connection
# conn = stomp.Connection10([(address,post)])
    
# def send_to_queue1(conn,msg):
def send_to_queue1(msg):
    '''
    FUNCTION:RECEIVE MESSAGE FROM CLIENT AND SEND MESSAGE TO QUEUE1
    '''
    conn = stomp.Connection10([(address,post)])
    conn.start()
    conn.connect('admin','admin',wait=True)
    conn.send(queue_name1,msg)
    conn.disconnect()   
    
# def receive_from_queue1(conn):
def receive_from_queue1():
    '''
    FUNCTION:RECEIVE MESSAGE FROM QUEUE1 AND SEND MESSAGES TO QUEUE2 THROUGH LISTENER1
    '''
    conn = stomp.Connection10([(address,post)])
    conn.set_listener(listener_name1, Listener1())
    conn.start()
    conn.connect('admin','admin',wait=True)
    conn.subscribe(queue_name1)
    time.sleep(1) # secs
    conn.disconnect()

# def send_to_queue2(conn,listener1_value):
def send_to_queue2(listener1_value):
    '''
    FUNCTION:SEND MESSAGE TO QUEUE2
    '''
    conn = stomp.Connection10([(address,post)])
    conn.start()
    conn.connect('admin','admin',wait=True)
    conn.send(queue_name2,listener1_value)
    conn.disconnect()
        
# def receive_from_queue2(conn):
def receive_from_queue2():
    '''
    FUNCTION:RECEIVE PROCESSED DATA FORM QUEUE2 AND SEND MESSAGE TO QUEUE3
    NOTICE: GET THE CLASSIFICATION OF EACH IMAGES AND RETURN THE CLASSIFICATION RESULTS THROUGH LISTENER2
    '''
    conn = stomp.Connection10([(address,post)])
    conn.set_listener(listener_name2, Listener2())
    conn.start()
    conn.connect('admin','admin',wait=True)
    conn.subscribe(queue_name2)
    time.sleep(1) # secs
    conn.disconnect()

# def send_to_queue3(conn,listener2_value):
def send_to_queue3(listener2_value):
    '''
    FUNCITON:SEND MESSAGES TO QUEUE3
    '''
    conn = stomp.Connection10([(address,post)])
    conn.start()
    conn.connect('admin','admin',wait=True)
    conn.send(queue_name3,listener2_value)
    conn.disconnect()
        
# def receive_from_queue3(conn):
def receive_from_queue3():
    '''
    FUNCTION:GET THE RESULTS OF EACH IMAGE AND SEND THE FINAL RESULTS THROUGH LISTENER3    
    '''
    conn = stomp.Connection10([(address,post)])
    conn.set_listener(listener_name3, Listener3())
    conn.start()
    conn.connect('admin','admin',wait=True)
    conn.subscribe(queue_name3)
    time.sleep(1) # secs
    conn.disconnect()

class Listener1(object):
    '''
    FUNCTION: DEFINE A LISTENER CLASS FOR QUEUE1
            1\GET THE CLIENT MESSAGE-ID,TYPE,PICS,IMAGES OF VIDEO
            2\RETURN ALL THE DATA
    '''
    def on_message(self, headers, message1):
        # transform json data to dict type
        message = json.loads(message1.decode('utf-8'))
        
        # get relevant params
        id = message['id']
        type = message['type']
        pics = message['pics']
        video = message['video']
        video_img_list = []
        i = 0
        
        if not os.path.exists(path):
            os.makedirs(path)
        for pic in pics:
            url = pic.encode("utf-8")
            img = io.imread(url)
            cv2.imwrite(path+type+str(i)+'.jpg',img)
            i += 1
        # transform video into images and save images
        for v_url in video:
            video_images = self.video_process(v_url)
            for img in video_images:
                cv2.imwrite(path+type+str(i)+'.jpg',img)
                i +=1
        # define the param of listener1 which will be sent to queue2
        listener1_value = {"id":id,\
                           "type":type,\
                           "pic_addr":path
                }
        out1 = json.dumps(listener1_value)
        
#         send_to_queue2(conn,out1)
        send_to_queue2(out1)
        print out1
        print 'QUEUE1 SUCCESSD'
            
    def video_process(self,video_full_path):
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

class Listener2(object):
    '''
    FUNCTION: RECEIVE DATA FROM QUEUE1 AND CLASSIFY THE DATA,FINALLY, SEND THE CLASSIFICAITON RESULT TO QUEUE3
    '''
    receive_from_queue1()
    def on_message(self, headers, message2): 
        results = []
        output_type_list = []
        message = json.loads(message2)

        id = message['id']
        input_type = message['type']
        pic_addr = message['pic_addr']
        
        img_lists = os.listdir(pic_addr)

        # do some process for image
        for pic in img_lists:
            # transform unicode type data into str
            image_url = pic.encode('utf-8')
            # load image url 
            new_pic=caffe.io.load_image(pic_addr + image_url)
            result_num = self.img_judgement(new_pic)
            pic_result ,output_type= self.type_judgement(result_num,input_type)
            results.append(pic_result)
            output_type_list.append(output_type)
            
        final_result = self.get_final_result(results)
        final_output_type = self.get_final_type(output_type_list)

        listener_value = {'id':id,
                      'input_type':input_type,
                      'results':final_result,
                      'output_type':final_output_type
#                     'video_images':new_img
            }
        final_out = json.dumps(listener_value)
        
#         send_to_queue3(conn,message2)
        send_to_queue3(final_out)
        if os.path.exists(path):
            shutil.rmtree(path)
        print 'QUEUE2 SUCCESED'
    
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
        model_def = Configuration.configs['model_prototxt_path']
        model_weights = Configuration.configs['caffe_model_path']
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
    
    def type_judgement(self,result_num,input_type):
        '''
        This function is designed for judging whether the original results are consistent with the predicted results
        '''
        type_dict1 = {'smoke':0, 'distraction':1, 'abnormal driving':2,'call':3,'fatigue':4,'other':5}
        type_dict2 = {0:'smoke', 1:'distraction', 2:'abnormal driving',3:'call',4:'fatigue',5:'other'}
        output_type = []
        
        # transform input type-list to str
        input_type = "".join(input_type)
        # the output of result is 'yes' or 'no'
        flag_y = 0
        flag_n = 0
        for i in result_num:
            output_type.append(type_dict2[i])
            if type_dict1[input_type] == i:
                result = 'yes'
                flag_y += 1
            else:
                result = 'no'
                flag_n += 1
                
        output_type = "".join(output_type)  
        
        if flag_y >= flag_n:
            result = 'yes'
        else:
            retult = 'no'
            
        return result,output_type
    def get_final_result(self,output_results):
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
    
    def get_final_type(self,output_type):
        '''
        THIS FUNCTION IS DESIGNED FOR OUTPUT THE FINAL RESULT ACCORDING THE IMAGE AND VIDEO CLASSIFICAITON OUTPUT RESUTLS
        '''
        # COUNT THAT HOW MANY YES AND NO IN THE OUTPUT RESUTL
        count_0 = 0
        count_1 = 0
        count_2 = 0
        count_3 = 0
        count_4 = 0
        count_5 = 0
        type_dict = {0:'smoke', 1:'distraction', 2:'abnormal driving',3:'call',4:'fatigue',5:'other'}
        for i in range(len(output_type)):
            if output_type[i] == "smoke":
                count_0 += 1
            elif output_type[i] == "distraction":
                count_1 += 1
            elif output_type[i] == "abnormal driving":
                count_2 += 1
            elif output_type[i] == "call":
                count_3 += 1
            elif output_type[i] == "fatigue":
                count_4 += 1
            elif output_type[i] == "other":
                count_5 += 1
        counts = [count_0,count_1,count_2,count_3,count_4,count_5]
        # get the index of the maxmium value in counts
        out_index = np.array(counts).argmax()
        final_output_type =  type_dict[out_index]
        return final_output_type
    
#     def remove_files(self):
        
class Listener3(object):
    '''
    FUNCITON: RECEIVE PIC AND PICS OF VIDEO'S RESULTS, GET THE FINAL RESULTS  
    '''
    receive_from_queue2()
    def on_message(self, headers, message3): 
        message = json.loads(message3)
        print message3
        print 'QUEUE3 SUCCESED'
        
    
if __name__ == '__main__':
    values = '{ "id": "1234567",\
                "type":"smoke",\
                "pics":["http://img.rr95.com/remote/21221505806535.jpg",\
                       "http://www.gx8899.com.img.800cdn.com/uploads/allimg/2018030309/tmokzgmp0cv.jpg",\
                       "https://i.zgjm.org/uploads/allimg/150923/145031DG-0.png"],\
                "video":["http://qnmov.a.yximgs.com/upic/2018/06/06/12/BMjAxODA2MDYxMjQwMTZfMTkzMDUyMjRfNjU2NzMwNzI5MF8xXzM=_hd3_Bc143c8abf799984d2cc75a52de7039f0.mp4"]\
    }'
    
    send_to_queue1(values)
#     receive_from_queue1()
#     receive_from_queue2()
    receive_from_queue3()
#     send_to_queue1(conn,values)
#     receive_from_queue1(conn)
#     receive_from_queue2(conn)
#     receive_from_queue3(conn)