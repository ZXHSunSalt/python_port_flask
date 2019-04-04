#*- coding=utf-8 -*-
'''
Created on 2019��3��26��

@author: Administrator
'''

from flask import Flask,jsonify,request

app = Flask(__name__,static_url_path = '/static')

# @app.route("/")
# def index():
#     print request.headers
#     return "see console output"
# 
# 
# if __name__=="__main__":
#     app.run(debug=True)


@app.route('/')
def hello_world():
    return app.send_static_file('00_06_6503_0_00d3caf8571b4ae69b55952986d1a2a0-12r.jpg')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000')