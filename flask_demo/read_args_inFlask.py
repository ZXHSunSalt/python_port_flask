# -*- coding:utf-8 -*-
'''
Created on 2019年4月3日

@author: Administrator
'''
from flask import Flask,request,url_for
app = Flask(__name__)

@app.route("/")
def v_index():
    return '''
    <form method="GET" action="/search">
        <input type="text" placeholder="input keywords" value="Python Flask" name="q"> <br />
        <input type="text" name="page"> <br />
        <input type="submit" value="search">
    </form>

    '''
@app.route('/search')
def v_search():
    if 'q' in request.args:
        ret = '<p>searching %s...</p><p> %s </p>' % (request.args['q'], request.args['page'])
    else:
        ret = 'what do you want to search?'
    return ret
   
app.run(host='127.0.0.1',port=888,debug=False)