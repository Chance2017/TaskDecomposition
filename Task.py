# coding=utf-8
'''
Created on 2017年12月20日

@author: 张清明
'''

import Settings

class Task:
    "任务类"
    
    eachLayerNum = [0 for x in range(Settings.maxLayerNumber)]          # 记录每一层的任务数量
    
    def __init__(self, name, subTasks, parentsTask, sub_association, executionCost=-1, minTotalCost=-1, inputCost=-1, outputCost=-1):
        "构造函数，参数包括任务名，子任务列表，父任务，子任务的关联关系"
        self.name = name
        self.subTasks = subTasks
        self.parentsTask = parentsTask
        self.sub_association = sub_association
        self.executionCost = executionCost
        self.inputCost = inputCost
        self.outputCost = outputCost
        self.minTotalCost = minTotalCost

    def isRootTask(self):
        "是否为根任务"
        if self.parentsTask == None:
            return True
        else:
            return False
    
    def isLeafTask(self):
        "是否为叶任务"
        if len(self.subTasks)==0:
            return True
        else:
            return False
    
    def countSubTask(self):
        "返回子任务数量"
        return len(self.subTasks)
        
    def toString(self):
        "任务对象格式化打印"
        taskStr = str(self.name) + ":{"
        for task in self.subTasks:
            taskStr += task.toString()
        taskStr += "}"
        return taskStr1
    
