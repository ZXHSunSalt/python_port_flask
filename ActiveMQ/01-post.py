#-*- coding:utf-8 -*-
'''
Created on 2019年4月8日

@author: Administrator
'''
import stomp
import time

queue_name = '/queue/SampleQueue'
topic_name = '/topic/SampleTopic'
listener_name = 'SampleListener'
post=1234

def send_to_queue(msg):
    conn = stomp.Connection10([('127.0.0.1'),post])
    conn.start()
    conn.connect()
    conn.send(queue_name, msg)
    conn.disconnect()   
    
    
    
if __name__ == '__main__':
    send_to_queue('len 123')