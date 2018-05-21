# coding=utf-8
'''
Created on 2017年12月21日

@author: 张清明

并行分解合并

'''

import numpy as np
import time
import operator

def taskCombination(task):
    
    combination = []   # 最终子任务的组合
    cost = {}
    name = {'A':'', 'B':'', 'C':'', 'D':'', 'E':''}
    
    # 按照minTotalCost对子任务进行排序
    cmpAttribute = operator.attrgetter('minTotalCost')
    subtasks = task.subTasks[:]
    subtasks.sort(key=cmpAttribute)
    
    # 开销最大的任务及其开销，并单独成为了一个组合
    maxTask = subtasks.pop()
    max_value = maxTask.minTotalCost
    combination.append([maxTask.name])
    
    # 去掉所有的非叶子任务
    for t in subtasks:
        if not t.isLeafTask():
            subtasks.remove(t)
            combination.append([t.name])
    
    # 子任务数量
    taskNum = len(subtasks)
    for i in range(taskNum):
        name[chr(65+i)] = subtasks[i].name
        cost[chr(65+i)] = subtasks[i].minTotalCost
    for key, value in name.items():
        print key + ":" + value + " ",
    print ''
#     print "cost列表：", cost
    
    cost_copy = cost.copy()
    
    keys = cost_copy.keys()
#     print "去掉最大值对应键的键集合：", keys
    
    preSubsets = {key:cost_copy[key] for key in keys} # 每一个子集只有一个元素的子集的集合
    subsets = preSubsets.copy() # 所有可行子集的集合
#     print "一元子集-集合：", preSubsets
    
    
    while not cost_copy == {}:
        temp_subsets1 = {}
        
        for key in cost_copy.keys():
        
            temp_subsets2 = {}
            
            for k in preSubsets.keys():
                totalCost = cost_copy[key] + preSubsets[k]
                if (not key in k) & (totalCost <= max_value):
                    string = ''
                    for s in sorted(list(key + k)):
                        string += s
                    temp_subsets2[string] = totalCost
            
            if temp_subsets2 == {}:
                del cost_copy[key]
            else:
                temp_subsets1 = dict(temp_subsets1.items() + temp_subsets2.items())
                
        if temp_subsets1 == {}:
            break
        else:
            preSubsets = temp_subsets1.copy()
            subsets = dict(subsets.items() + temp_subsets1.items())
#             print 'preSubsets:', len(preSubsets), preSubsets
#             print 'cost_copy:', cost_copy
    
#     print '可取的所有子集的集合：', len(subsets), subsets
    
    
    # 根据key的长度分别将key存储在相应的列表序号中
    subsets_keys = []
    for i in range(taskNum):
        subsets_keys.append([])
    for key in subsets.keys():
        subsets_keys[len(key)-1].append(key)
    
    for s in subsets_keys:
        s.sort()
    if [] in subsets_keys:
        for i in range(subsets_keys.index([]), taskNum):    # 删除掉空值
            subsets_keys.remove([])
        
#     print ''
#     print '根据key的长度分别将key存储在相应的列表序号中：', subsets_keys
    
    # 已选的子集集合
    selectedSubsets = []
    num = 0
    for i in range(len(subsets_keys)-1):
        
        for k1 in subsets_keys[len(subsets_keys)-1-i]:
            temp_keys = keys[:]
            
            selectedSubsets.append([k1])
            
            for s in k1:
                if s in temp_keys:
                    temp_keys.remove(s)
                
            if len(temp_keys) >= len(subsets_keys):
                for k2 in subsets_keys[len(subsets_keys)-1-i]:
                    flap = 0
                    for k3 in selectedSubsets[num]:
                        if len(set(k3) & set(k2)) > 0:
                            flap = 1    # 表示这两个子集有交集
                            break
                    
                    if flap == 0:        
                        selectedSubsets[num].append(k2)
                        for s in k2:
                            if s in temp_keys:
                                temp_keys.remove(s)
            
            # TODO
            while len(temp_keys) > 0:
                for j in range(len(subsets_keys)-1):
                    for k2 in subsets_keys[len(subsets_keys)-2-j]:
                        flap = 0
                        for k3 in selectedSubsets[num]:
                            if len(set(k3) & set(k2)) > 0:
                                flap = 1    # 表示这两个子集有交集
                                break
                        
                        if flap == 0:        
                            selectedSubsets[num].append(k2)
                            for s in k2:
                                if s in temp_keys:
                                    temp_keys.remove(s)
                                
                        if len(temp_keys) == 0:
                            break
                    if len(temp_keys) == 0:
                        break
                
            num += 1
            
            selectedSubsets[num-1].sort()
#             print num, ':', selectedSubsets[num-1]
    
    print '所有的覆盖子集集合：', selectedSubsets
    
    selectedSubsetsNum = []     # 存储每个全覆盖子集集合的子集个数
    for s in selectedSubsets:
        selectedSubsetsNum.append(len(s))
#     print '存储每个全覆盖子集集合的子集个数:', len(selectedSubsetsNum), "-", selectedSubsetsNum
    
    
    if not selectedSubsetsNum == []:
        selectedSubsetsVar = []     # 存储每个全覆盖子集集合的子集方差
        for s in selectedSubsets:
            selectedSubsetsVar.append(np.var([subsets[k] for k in s]))
    #     print '存储每个全覆盖子集集合的子集方差:', len(selectedSubsetsVar), "-", selectedSubsetsVar
        
        minSubsets = min(selectedSubsetsNum)
        count = selectedSubsetsNum.count(minSubsets)
    #     print '子集数量最少的集合的个数：', count
        index = []
        pos = -1
        for i in range(count):
            pos = selectedSubsetsNum.index(minSubsets, pos + 1)
            index.append(pos)
    #     print '子集数量最少的集合的下标：', index
        minSubsetVar = []
        for i in index:
            minSubsetVar.append(selectedSubsetsVar[i])
    #     print '子集数量最少的集合的方差：', minSubsetVar
        result = selectedSubsets[index[minSubsetVar.index(min(minSubsetVar))]]
        print '子集数量最少且方差最小的集合：', result, '其对应的执行开销是：', [subsets[s] for s in result], '其在已选集合中的下标为：', index[minSubsetVar.index(min(minSubsetVar))], '方差为：', min(minSubsetVar)
        
        for r in result:
            combination.append([])
            for t in r:
                combination[-1].append(name[t])
        print combination
        print ''
