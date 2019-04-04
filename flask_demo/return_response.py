# -*- coding:utf-8 -*-
'''
Created on 2019年4月3日

@author: Administrator
'''
from flask import Flask,request,url_for,make_response
app = Flask(__name__)

@app.route("/")
def v_index():
    return '<a href="%s">ping</a>'%url_for('v_ping')

@app.route('/ping')
def v_ping():
    rsp = make_response('pong')
    rsp.mimetype = 'text/plain'
    rsp.headers['x-tag'] = 'sth.magic'
    return rsp
   
app.run(host='127.0.0.1',port=8888,debug=False)