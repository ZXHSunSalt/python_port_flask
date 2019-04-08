# -*- coding=utf-8 -*-
'''
Created on 2019年4月8日

@author: Administrator
'''
def test():
    a = ["yes","yes","yes","yes","yes","yes","yes","yes","yes","yes","yes","yes","yes","yes","yes","yes","yes","yes","yes","yes","yes","yes","yes","yes"]
    count_y = 0
    count_n = 0
    for each in a:
        if each == "yes":
            count_y += 1
        else:
            count_n += 1
    
        if count_y >= count_n:
            result = 'yes'
        else:
            result = 'no'
    return result

result = test()
print result