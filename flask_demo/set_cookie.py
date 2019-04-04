#-*- coding:utf-8 -*-
'''
Created on 2019年4月3日

@author: Administrator
'''
from flask import Flask,make_response,url_for,request
app = Flask(__name__)

@app.route('/')
def v_index():
    rsp = make_response('go <a href=%s>page2</a>'%url_for("v_page2"))
    rsp.set_cookie('user','zxh')
    return rsp

@app.route('/page2')
def v_page2():
    user = request.cookies['user']
    return 'you are %s'%user

app.run(host='127.0.0.1',port=1234,debug=False)