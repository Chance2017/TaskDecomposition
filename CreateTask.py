# coding=utf-8
'''
Created on 2017年12月20日

@author: 张清明
'''

import random
from Task import Task
import Settings
from XmlOperation import taskToXml
import TaskOperation

def generateSubAssociation(parentsTask):
    "随机产生子任务的关联关系"
    randSubAssociationProbability = random.random()
    if parentsTask == None:
        sub_association = Settings.concurrence
        if (randSubAssociationProbability > 0.6) & (randSubAssociationProbability < 0.8): # 0.9
            sub_association = Settings.sequentially
        elif (randSubAssociationProbability >= 0.8) & (randSubAssociationProbability <= 1):
            sub_association = Settings.Or
        return sub_association
    else:
        if parentsTask.sub_association == Settings.concurrence:
            if randSubAssociationProbability <= 0.5: # 0.9
                sub_association = Settings.sequentially
            else:
                sub_association = Settings.Or
        elif parentsTask.sub_association == Settings.sequentially:
            if randSubAssociationProbability <= 0.5: # 0.9
                sub_association = Settings.concurrence
            else:
                sub_association = Settings.Or
        else:
            if randSubAssociationProbability <= 0.6:
                sub_association = Settings.concurrence
            else:
                sub_association = Settings.sequentially
        return sub_association

def CreateTask(MainTaskID, eachLayerNum=[0 for x in range(Settings.maxLayerNumber)]):
    "创建主任务"
    subtaskNum = random.randint(2,10)
    print '主任务可分解的子任务数量：', subtaskNum
    
    mainTask = Task(MainTaskID, [], None, generateSubAssociation(None))
    
    # 随机生成主任务的输入输出数据通信开销，单位：s
    mainTask.inputCost = round(random.uniform(5, 20), 2)
    mainTask.outputCost = round(random.uniform(5, 20), 2)
    
    for i in range(subtaskNum):
        CreateSubTask(MainTaskID, 1, mainTask, eachLayerNum)
    
    mainTask.eachLayerNum = eachLayerNum
    return mainTask
        

def CreateSubTask(MainTaskID, LayerNum, parentsTask, eachLayerNum):
    "创建子任务"
    
    # 最多分解Settings.maxLayerNumber层
    if LayerNum > Settings.maxLayerNumber:
#         print '此为叶节点'
        parentsTask.executionCost = round(random.uniform(5, 20), 2)
        parentsTask.sub_association = 9
        return
    
    eachLayerNum[LayerNum-1] += 1
    
    taskName = MainTaskID + str(LayerNum) + str(eachLayerNum[LayerNum-1])
#     print taskName
    task = Task(taskName, [], parentsTask, generateSubAssociation(parentsTask))
    parentsTask.subTasks.append(task)
    
    NoDecompProbability = random.random()
    if NoDecompProbability > 0.7:       # 如果概率大于0.7 则对任务进行分解
        for i in range(random.randint(2, 5)):
            CreateSubTask(MainTaskID, LayerNum + 1, task, eachLayerNum)
    else:
        # 不再分解，为叶节点
        task.executionCost = round(random.uniform(5, 20), 2)
        task.sub_association = 9
        pass

def geneInputOutputCost(MainTask):
    "根据主任务的输入/输出数据的通信开销，确定所有子任务的输入/输出数据的开销"
    if not MainTask.isLeafTask():
        queue = [MainTask]
        while len(queue) > 0:
            task = queue.pop()
            inputCost = task.inputCost
            outputCost = task.outputCost
            
            # 并行
            if task.sub_association == Settings.concurrence:
                for t in task.subTasks:
                    if t == task.subTasks[-1]:
                        t.inputCost = inputCost
                        t.outputCost = outputCost
                    else:
                        randInputCost = round(random.random()*inputCost, 2)
                        randOutputCost = round(random.random()*outputCost, 2)
                        t.inputCost = randInputCost
                        t.outputCost = randOutputCost
                        inputCost -= randInputCost
                        outputCost -= randOutputCost
                    if not t.isLeafTask():
                        queue.append(t)
            # 串行
            elif task.sub_association == Settings.sequentially:
                for i in range(len(task.subTasks)):
                    if i == 0:
                        task.subTasks[0].inputCost = inputCost
                        task.subTasks[0].outputCost = round(random.uniform(0.01, 10), 2)
                    elif (i > 0) & (i < (len(task.subTasks)-1)):
                        task.subTasks[i].inputCost = task.subTasks[i-1].outputCost
                        task.subTasks[i].outputCost = round(random.uniform(0.01, 10), 2)
                    else:
                        task.subTasks[i].inputCost = task.subTasks[i-1].outputCost
                        task.subTasks[i].outputCost = outputCost
                    
                    if not task.subTasks[i].isLeafTask():
                        queue.append(task.subTasks[i])
            # "或"
            else:
                for t in task.subTasks:
                    t.inputCost = inputCost
                    t.outputCost = outputCost
                    if not t.isLeafTask():
                        queue.append(t)
                        

# if __name__=='__main__':
def main():
#     for i in range(65, 91):
        task = CreateTask(chr(65))
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
        
        # 根据主任务的输入/输出数据的通信开销，确定所有子任务的输入/输出数据的开销
        geneInputOutputCost(task)
        
        for t in TaskOperation.getLeafAndNotLeafTasks(task)[0]:
            t.minTotalCost = t.executionCost + t.inputCost + t.outputCost
        
        # 从后往前确定每个非叶子节点的初始执行开销
        for t in TaskOperation.getLeafAndNotLeafTasks(task)[1][::-1]:
            # 或关系
            if t.sub_association == Settings.Or:
                t.executionCost = min([c.executionCost for c in t.subTasks])
            # 并、串行关系
            else:
                t.executionCost = sum([c.executionCost for c in t.subTasks])
        
        # 将Task对象写到XML文件中
        taskToXml(task, 'task.xml')
