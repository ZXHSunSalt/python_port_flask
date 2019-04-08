# -*- coding:utf-8 -*-
'''
Created on 2019年4月3日

@author: Administrator
'''
import urllib2
import json

def post():
    url = "http://127.0.0.1:1234/"
    values = { "type":["smoke"],
               "pics":['http://img.rr95.com/remote/21221505806535.jpg',
                       'http://www.gx8899.com.img.800cdn.com/uploads/allimg/2018030309/tmokzgmp0cv.jpg',
                       'https://i.zgjm.org/uploads/allimg/150923/145031DG-0.png'],
               "video":["http://qnmov.a.yximgs.com/upic/2018/06/06/12/BMjAxODA2MDYxMjQwMTZfMTkzMDUyMjRfNjU2NzMwNzI5MF8xXzM=_hd3_Bc143c8abf799984d2cc75a52de7039f0.mp4"]
    }
    headers = {'Content-Type':'application/json'}
    request = urllib2.Request(url = url ,data = json.dumps(values), headers = headers)
    try:
        response = urllib2.urlopen(request)
        print response.read()
    except urllib2.HTTPError:
        pass
    
    
if __name__ == '__main__':
    post()