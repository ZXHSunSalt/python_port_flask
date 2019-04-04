# -*- coding:utf-8 -*-
'''
Created on 2019年4月3日

@author: Administrator
'''
from flask import Flask,request,url_for,make_response
app = Flask(__name__)

@app.route("/")
def v_index():
    
    return '''
    { "type":["Smoke"],
      "pic":["http://localhost:8080/00_06_6503_0_00d3caf8571b4ae69b55952986d1a2a0-9l.jpg",
             "http://localhost:8080/00_06_6503_0_00d3caf8571b4ae69b55952986d1a2a0-9r.jpg",
             "http://localhost:8080/00_06_6503_0_00d3caf8571b4ae69b55952986d1a2a0-12l.jpg"],
      "video":["http://localhost:8080/02_06_6503_0_f233dbcb8c5340d1a560b02114be521b.mp4"]
    }
    '''
    

# @app.route('/driver',methods=['POST'])
# def v_login():
#     data = request.get_json()
#     type = data['type']
#     pics = data['pic']
#     video = data['video']
#     for pic in pics:
#         print pic
#     
app.run(host='127.0.0.1',port=4321,debug=False)