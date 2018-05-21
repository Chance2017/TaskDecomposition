# coding=utf-8
'''
Created on 2018年1月9日

@author: 张清明
'''
import operator
import Settings

def getLeafAndNotLeafTasks(task):
    "返回所有的（叶子任务集合，非叶子任务集合）"
    leafTasks = []
    notLeafTasks = []
    
    if task.isLeafTask():
        leafTasks.append(task)
    else:
        notLeafTasks.append(task)
    
        queue = [task]
        
        while queue.__len__() > 0:
            
            st = queue.pop()
            for t in st.subTasks:
                queue.insert(0, t)
                if t.isLeafTask():
                    leafTasks.append(t)
                else:
                    notLeafTasks.append(t)
                    
    return leafTasks, notLeafTasks


def getEveryLayerTasks(task, level, everyLayerTasks):
    "返回每一层的任务"
    subtasks = task.subTasks
    if subtasks.__len__() == 0:
        return 
    if everyLayerTasks.__len__() < level:
        everyLayerTasks.append([])
    for t in  subtasks:
        everyLayerTasks[level-1].append(t)
        getEveryLayerTasks(t, level+1, everyLayerTasks)
    
def getSortedSubtask(task):
    "按照minTotalCost值，对task对象的子任务进行排序"
    cmpAttribute = operator.attrgetter('minTotalCost')
    subtasks = task.subTasks[:]
    subtasks.sort(key=cmpAttribute)
    subtasks.reverse()
    
    return subtasks

def pruningOr(task):
    "剪枝，剪去“或”分支"
    for t in getLeafAndNotLeafTasks(task)[1][::-1]:
        if t.sub_association == Settings.Or:
            cost = [c.executionCost for c in t.subTasks]
            subtask = t.subTasks[cost.index(min(cost))]
            if not t.isRootTask():
                tIndex = t.parentsTask.subTasks.index(t)
                t.parentsTask.subTasks[tIndex] = subtask
                subtask.parentsTask = t.parentsTask
                
                if subtask.sub_association == t.parentsTask.sub_association:
                    t.parentsTask.subTasks.remove(subtask)
                    for st in subtask.subTasks[::-1]:
                        t.parentsTask.subTasks.insert(tIndex, st)
            else:
                t.name = subtask.name
                t.executionCost = subtask.executionCost
                t.inputCost = subtask.inputCost
                t.outputCost = subtask.outputCost
                t.minTotalCost = subtask.minTotalCost
                t.sub_association = subtask.sub_association
                t.subTasks = subtask.subTasks

def pruningSequential(task):
    pruningCost = 0   
    "从后往前确定每个非叶子节点的最小执行开销"
    for t in getLeafAndNotLeafTasks(task)[1][::-1]:
        # 并行关系
        if t.sub_association == Settings.concurrence:
            t.minTotalCost = max([c.minTotalCost for c in t.subTasks])
        # 串行关系
        elif t.sub_association == Settings.sequentially:
            #若分解后的总任务开销高于未分解的总开销，则最小总开销为未分解时的总开销，否则为分解后的总开销
            totalCost = t.executionCost + t.inputCost + t.outputCost
            subtaskTotalCost = sum([c.minTotalCost for c in t.subTasks])
            # 如果分解后的子任务总开销更大，则直接将子任务修剪掉
            if subtaskTotalCost > totalCost:
                t.minTotalCost = totalCost
                pruningCost += (subtaskTotalCost - totalCost)
                t.subTasks = []
            else:
                t.minTotalCost = subtaskTotalCost
        # 或关系
        else:
            t.minTotalCost = min([c.minTotalCost for c in t.subTasks])
    
    return pruningCost
    
def pruningConcurrence(task):
    "对并行分支进行修剪"
    everyLayerTasks = []
    getEveryLayerTasks(task, 1, everyLayerTasks)
    
    # 获得所有的子任务关联关系为并行关系的母任务列表
    concurrenceTasks = [t for t in getLeafAndNotLeafTasks(task)[1] if t.sub_association==Settings.concurrence]
    while concurrenceTasks.__len__() > 0:
        ct = concurrenceTasks.pop(0)
        # 获得对一个母任务的子任务按minTotalCost属性进行排序的序列
        subT = getSortedSubtask(ct)
        print "排序前：", [t.name + ":" + str(t.minTotalCost) for t in ct.subTasks]
        print "排序后：", [t.name + ":" + str(t.minTotalCost) for t in subT]
        # 其他任务分解时不能超过此最大成本
        maxTotalCost = subT[0].minTotalCost
        # 对除去最大minTotalCost的子任务进行重新自上而下的分解
        for t in [st for st in subT[1:] if not st.isLeafTask()]:
            # TODO
            print t.name + ":" + str(t.minTotalCost)
            if (t.executionCost+t.inputCost+t.outputCost) < maxTotalCost:
                t.minTotalCost = t.executionCost+t.inputCost+t.outputCost
                t.subTasks = []
                print '停止往下分解,', t.name + ":" + str(t.minTotalCost)
            else:
                print t.name + ":" + str(t.executionCost + t.inputCost + t.outputCost)
                print "继续往下分解:"
                t.minTotalCost = t.inputCost+t.executionCost+t.outputCost
                notDecomposedTasks = [x for x in t.subTasks]
                for x in notDecomposedTasks:
                    x.minTotalCost = x.inputCost+x.executionCost+x.outputCost
                while t.minTotalCost > maxTotalCost:
                    tempTask = notDecomposedTasks[-1]
                    pt = tempTask.parentsTask
                    while not pt==t:
                        if pt.sub_association == Settings.concurrence:
                            pt.minTotalCost = max([c.minTotalCost for c in pt.subTasks])
                        else:
                            pt.minTotalCost = sum([c.minTotalCost for c in pt.subTasks])
                        pt = pt.parentsTask
                    t.minTotalCost = sum([c.minTotalCost for c in t.subTasks])
                     
                    tempTask = notDecomposedTasks.pop(0)
                    while tempTask.isLeafTask() & (notDecomposedTasks.__len__() > 0):
                        tempTask = notDecomposedTasks.pop(0)
                    if not tempTask.isLeafTask():
                        notDecomposedTasks += tempTask.subTasks
                        for x in tempTask.subTasks:
                            x.minTotalCost = x.inputCost+x.executionCost+x.outputCost
                
                if notDecomposedTasks.__len__() > 0:
                    notDecomposedTasks[-1].parentsTask.subTasks = []
                    for x in notDecomposedTasks:
                        print "未分解的任务有：", x.name
                        x.subTasks = []
                print "新的最小总开销", t.minTotalCost
                
        concurrenceTasks = [x for x in [t for t in getLeafAndNotLeafTasks(task)[1] if t.sub_association==Settings.concurrence] if x in concurrenceTasks]
        print ""
    task.toString()
            