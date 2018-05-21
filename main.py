# coding=utf-8
'''
Created on 2018年1月29日

@author: 张清明
'''
import CreateTask
import XmlOperation
import time

if __name__=='__main__':
    start = time.clock()
    CreateTask.main()
    XmlOperation.main()
    end = time.clock()
    print '程序执行时间:', end-start
    