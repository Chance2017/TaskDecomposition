# coding=utf-8
'''
Created on 2018年1月2日

@author: 张清明
'''

import xml.etree.ElementTree as ET
from Task import Task
import TaskOperation
import Settings
import TaskCombination

# 将任务写到XML文件
def taskToXml(task, filepath):
    
    # 创建根节点
    if task.isRootTask():
        root = ET.Element('main-task')
    else:
        root = ET.Element('task')
        
    root.attrib = {"name": task.name}
#     root.attrib['type'] = "计算".decode('utf-8')
    root.attrib['isLeaf'] = 'True' if task.isLeafTask() else 'False'
    root.attrib['sub_association'] = str(task.sub_association)
    root.attrib['inputCost'] = str(task.inputCost)
    root.attrib['outputCost'] = str(task.outputCost)
    root.attrib['parentsTask'] = '' if task.parentsTask == None else task.parentsTask.name
    root.attrib['executionCost'] = str(task.executionCost)
    root.attrib['minTotalCost'] = str(task.minTotalCost)
    root.text = '\n'
    
    # 创建子节点，并添加属性
    addTaskNode(task, root, 1)
    
    # 创建ElementTree对象，写文件
    tree = ET.ElementTree(root)
    tree.write(filepath, 'utf-8', True)

def addTaskNode(task, parentsNode, level):
    '''
    添加xml节点，任务，父任务，层次数
    '''
    if not task.isLeafTask():
        for t in task.subTasks:
            node = ET.SubElement(parentsNode, "task-"+str(level))
            node.attrib = {"name": t.name}
#             node.attrib['type'] = "计算".decode('utf-8')
            node.attrib['isLeaf'] = 'True' if t.isLeafTask() else 'False'
            node.attrib['sub_association'] = str(t.sub_association)
            node.attrib['inputCost'] = str(t.inputCost)
            node.attrib['outputCost'] = str(t.outputCost)
            node.attrib['parentsTask'] = '' if t.parentsTask == None else t.parentsTask.name
            node.attrib['executionCost'] = str(t.executionCost)
            node.attrib['minTotalCost'] = str(t.minTotalCost)
            node.tail = '\n'
            if not t.isLeafTask():
                node.text = '\n'
                addTaskNode(t, node, level+1)

# 将XML文件读取到Task对象
def getTaskFromXml():
    tree = ET.parse('task.xml')
    root = tree.getroot()
    
    executionCost = float(root.attrib['executionCost'])
    minTotalCost = float(root.attrib['minTotalCost'])
    inputCost = float(root.attrib['inputCost'])
    outputCost = float(root.attrib['outputCost'])
    sub_association = int(root.attrib['sub_association'])
    
    task = Task(root.attrib['name'], [], None, sub_association, executionCost, minTotalCost, inputCost, outputCost)
    
    getSubTaskFromXml(task, root)

    return task
                
def getSubTaskFromXml(task, parentsNode):
    
    for child in parentsNode:
        executionCost = float(child.attrib['executionCost'])
        minTotalCost = float(child.attrib['minTotalCost'])
        inputCost = float(child.attrib['inputCost'])
        outputCost = float(child.attrib['outputCost'])
        sub_association = int(child.attrib['sub_association'])
        t = Task(child.attrib['name'], [], task, sub_association, executionCost, minTotalCost, inputCost, outputCost)
        task.subTasks.append(t)
        
        if len(child) > 0:
            getSubTaskFromXml(t, child)

# 格式化打印任务
def printTask(task):
    print task.toString().replace(':{}',',').replace(',}', '}').replace('}A', '},A')
    
    print "根节点：", task.name, ":", task.sub_association, "  "
    
    #打印出每一层节点
    everyLayerTasks = []
    TaskOperation.getEveryLayerTasks(task, 1, everyLayerTasks)
    index = 0
    for tlist in everyLayerTasks:
        print '第'+str(index+1)+'层：', [t.name+":"+str(t.sub_association) for t in tlist]
        index += 1
    
    a, b = TaskOperation.getLeafAndNotLeafTasks(task)
    print "叶子任务：", [x.name for x in a]
    print "非叶子任务：", [x.name for x in b]
    print ''

# if __name__ == '__main__':
def main():

    task = getTaskFromXml()
#     printTask(task)
    
    # 剪去或分支
    TaskOperation.pruningOr(task)
    taskToXml(task, 'pruningOR.xml')
    print '剪去或分支后：'
    printTask(task)
    
    # 剪去串行分支
    pruningCost = TaskOperation.pruningSequential(task)
    taskToXml(task, 'pruningSequential.xml')
    print '剪去串行分支后：'
    printTask(task)
    print '串行分支减掉：', pruningCost
    
    # 剪去并行分支
    TaskOperation.pruningConcurrence(task)
    taskToXml(task, 'pruningConcurrence.xml')
    print '剪去并行分支后：'
    printTask(task)
    
    for t in TaskOperation.getLeafAndNotLeafTasks(task)[1]:
        if t.sub_association == Settings.concurrence:
            TaskCombination.taskCombination(t)
    