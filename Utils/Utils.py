#!/usr/bin/env python3
# coding: utf-8

import pymongo
import matplotlib.pyplot as plt
import os
import subprocess
import csv
from collections import Counter


client = pymongo.MongoClient()
db = client['visual_analysis']
collection = db['pytorch']

def gitLog():
    """
    获取开源库pytorch的git历史，并按照[date,author,commit,message]格式存入MongoDB数据库。

    """
    global collection
    #改变项目路径
    os.chdir(os.getcwd()+"/pytorch")
    #运行gitlog命令
    ret = subprocess.run("git log --pretty=format:%ci::%an::%H::%f", shell=True, stdout=subprocess.PIPE)

    for line in ret.stdout.decode("utf-8").splitlines():
        line = line.strip()
        fields = line.split("::")
        if len(fields) != 4:
            print(f"extracting error, line: {line}")
            continue
        date, author, commit, message = fields
        #数据存入gitlog表
        collection.insert_one({"date": date,
                   "author": author,
                   "commit": commit,
                   "message": message})
                   
def initDataBase():
    '''
    通过csv数据文件初始化数据库
    '''
    #与数据库建立连接
    client = pymongo.MongoClient()
    db = client['visual_analysis']
    collect = db['pytorch']
    #csv文件路径
    rootPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csvPath = os.path.join(rootPath, "Utils", "CommitInfo.csv")
    i = 0
    with open(csvPath, 'r', encoding = 'utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if i == 0:
                i = i + 1
                continue #跳过第一行
            collect.insert_one({"date": row[1],
                                   "author": row[2],
                                   "commit": row[3],
                                   "message": row[4]})

def searchImagePath(content):
    """
    搜索/static/image目录下是否已有对应的图片，若有，返回图片路径，无则返回空字符串。
    :param content: 图片名 类型：str
    :return: 路径 类型：str
    """
    picPath = os.path.join(os.getcwd(), "static","image", content + ".png")
    if os.path.isfile(picPath):
        print("i am a file! " + picPath)
        return picPath
    else:
        print("i am not a file! " + picPath)
        return ""
        
def isValidYear(year):
    """
    检验年份是否有效，若有效则返回True，若无效则返回False
    :param year: 年份 类型：str
    :return: 布尔值
    """
    yearDict = getYearCommitDict()
    if year in yearDict.keys():
        return True
    return False

def isValidAuthor(author):
    """
    检验该作者是否参与编写pytorch，若参与则返回True，若未参与则返回False
    :param author: 作者名 类型：str
    :return: 布尔值
    """
    authorDict = getAuthorCommitDict()
    if author in authorDict.keys():
        return True
    return False
    
def findThePersonWhoContributedTheMostLastYear():
    """
    得到pytorch库中去年提交次数最多的人每月提交的次数,转为字典
    :return: 对应的字典LastyearauthorDict，格式为{month:num}
    """
    global collection
    result = collection.find()
    LastyearauthorDict={}
    authorDict = {}
    for item in result:
        authorString = item['author']
        dateString =item['date']
        year = dateString[0:4]
        if authorString in authorDict.keys() and year=='2019':
            authorDict[authorString] = authorDict[authorString] + 1
        else:
            authorDict[authorString] = 1
    sortedList = Counter(authorDict).most_common()
    author=sortedList[0][0]
    result2=collection.find()
    for item in result2:
        tempyear = item['date']
        year = tempyear[0:4]
        if author == item['author'] and year=='2019':
            month= tempyear[5:7]
            if month in LastyearauthorDict.keys():
                LastyearauthorDict[month]=LastyearauthorDict[month] + 1
            else:
                LastyearauthorDict[month]=1
    return LastyearauthorDict
     
def selectTopFive(sortedList):
    """
    从sortedList中选出前五，返回对应的名字与commit数量列成的列表
    :param sortedList:按值从大到小进行排序的authorDict
    :return:size -- [commit数量]
            labels -- [名字]
    """
    size = []
    labels = []
    for i in range(5):
        labels.append(sortedList[i][0])
        size.append(sortedList[i][1])
    return size, labels    

def getYearCommitDict():
    """
    得到pytorch库每一年commit的数量，转为字典
    :return: 对应的字典yearDict，格式为{year:num}
    """
    global collection
    result = collection.find()
    yearDict = {}
    for item in result:
        dateString =item['date']
        year = dateString[0:4]
        if year in yearDict.keys():
            yearDict[year] = yearDict[year] + 1
        else:
            yearDict[year] = 1
    return yearDict

def getAuthorCommitDict():
    """
    得到pytorch库每一位提交者commit的数量，转为字典
    :return: 对应的字典authorDict，格式为{author:num}
    """
    global collection
    result = collection.find()
    authorDict = {}
    for item in result:
        authorString = item['author']
        if authorString in authorDict.keys():
            authorDict[authorString] = authorDict[authorString] + 1
        else:
            authorDict[authorString] = 1
    return authorDict

def getImagePath(content, type):
    """
    搜索/static/image目录下是否已有对应的图片，若有，返回图片短路径，
    若无，则根据type以及content绘制相应图片，保存至/static/image，并返回图片短路径。
    :param content: 图片名
    :param type: 图片内容类型
    :return: 图片短路径
    """
    picPath = searchImagePath(content)
    if picPath:
        shortPath = "image/" + content + ".png"
        return shortPath
    else:
        if type == 'year':
            plotFigureForCertainYear(year=content)
        elif type == 'author':
            plotFigureForCertainAuthor(author=content)
        elif type == 'default':
            print("Error! Cannot find default picture!")
        shortPath = "image/" + content + ".png"
        return shortPath

def getParticipantsNumberDict():
    """
    得到pytorch库每年参与者的数量，转为字典
    :return: 对应的字典participantsDict，格式为{year:num}
    """
    global collection
    result = collection.find()
    yearDict = {}
    participantsDict = {}
    for item in result:
        dateString =item['date']
        authorString = item['author']
        year = dateString[0:4]
        if (year,authorString) not in yearDict.keys():
            yearDict[(year,authorString)]=1
        else:
             yearDict[(year,authorString)]=yearDict[(year,authorString)]+1


    for (tempyear,author) in yearDict.keys():
        if tempyear in participantsDict.keys():
            participantsDict[tempyear]=participantsDict[tempyear]+1
        else:
            participantsDict[tempyear]=1
    return participantsDict

def getTheNightBird():
    """
    得到在夜晚(01-04时)向pytorch库提交次数最多者的commit的数量，写入txt文件
    """
    global collection
    result = collection.find()
    authorDict = {}
    for item in result:
        authorString = item['author']
        dateString =item['date']
        time1 = dateString[11:13]
        time2 = ('01','02','03','04')
        if time1 in time2:
            if authorString in authorDict.keys():
                authorDict[authorString] = authorDict[authorString] + 1
            else:
                authorDict[authorString] = 0
    sortedList = Counter(authorDict).most_common()
    author = sortedList[0][0]
    number = sortedList[0][1]
    content = str(author) + ' used to submit code between 1 am and 4 am for ' + str(number) + ' days, and he was a heavy late sleeper.'
    fp = open('Nightbird.txt', 'w+')
    fp.write(content)
    fp.close

def getRelevantGitInfos(content, type):
    '''
    在数据库中搜索与{content}有关的提交信息，并返回[{'date': , 'author': , 'message': }]
    :param content: 搜索信息
    :param type: 内容信息
    :return: 提交信息列表
    '''
    global collection
    relevantGitInfos = []
    result = collection.find()
    if type == 'year':
        for item in result:
            if content == item['date'][0:4]:
                infoDict = {'date': item['date'][0:20], 'author': item['author'], 'message': item['message']}
                relevantGitInfos.append(infoDict)
    else:
        for item in result:
            if content == item['author']:
                infoDict = {'date': item['date'][0:20], 'author': item['author'], 'message': item['message']}
                relevantGitInfos.append(infoDict)
    return relevantGitInfos

def getQuestionAnswer(question_id):
    """
    读取/static/txt目录下的文本文件，返回文本Str
    :param question_id: 问题序号
    :return: 问题对应的文本文件Str
    """
    #文本文件基本路径
    fileBasicPath = os.path.join(os.getcwd(), "static", "txt")
    if question_id == 0:
        filePath = os.path.join(fileBasicPath, "The_Source_of_PyTorch.txt")
    if question_id == 1:
        filePath = os.path.join(fileBasicPath, "When_was_PyTorch_widely_known__.txt")
    if question_id == 2:
        filePath = os.path.join(fileBasicPath, "PyTorch_vs__.txt")
    with open(filePath, 'r', encoding='UTF-8') as f:
        textList = f.readlines()
        text = "\n".join(textList)
    return text

def plotTopFiveContributors():
    """
    根据authorDict绘制扇形图，并保存至/staic/image，名为TopFiveContributors.png
    """
    authorDict = getAuthorCommitDict()
    # 按值从大到小进行排序
    sortedList = Counter(authorDict).most_common()
    size, labels = selectTopFive(sortedList)
    # 偏移量
    explode = [0.02, 0.02, 0.02, 0.02, 0.02]
    plt.pie(size, labels=labels, explode=explode)
    # 将横、纵坐标轴标准化处理
    plt.title('The top five contributors for PyTorch')
    dir = os.path.join(os.getcwd(), "static", "image", "TopFiveContributors.png")
    # 将图片保存至/static/image，名为TopFiveContributors.png
    plt.savefig(dir, format='png', dpi=300)

def plotFigureForYearDict():
    """
    根据yearDict绘制条形图，并保存至/static/image，名为CommitNumber.png
    """
    yearDict = getYearCommitDict()
    with plt.xkcd():
        fig = plt.figure(figsize=(20,10))
        r = plt.bar(range(len(yearDict)), list(yearDict.values()), align='center')
        plt.xticks(range(len(yearDict)), list(yearDict.keys()))
        #添加数据标签
        for rects in r:
            height = rects.get_height()
            plt.text(rects.get_x() + rects.get_width() / 2, 1.015 * height, '%s' % int(height), fontsize=16, ha='center')
        #坐标轴
        plt.xlabel('Year', loc="center", fontsize=20)
        plt.ylabel('the number of commit', fontsize=20)
        plt.title('The number of code submissions per year for PyTorch', fontsize=30)
        dir = os.path.join(os.getcwd(), "static", "image", "CommitNumber.png")
        #将图片保存至/static/image，名为CommitNumber.png
        plt.savefig(dir,format='png',dpi = 300)


def plotFigureForCertainYear(year):
    """
    为指定的年份绘制条形图，横轴为月，纵轴为commit数。
    绘制的条形图将会保存到/static/image，名为{year}.png
    :param year: 指定的年份
    """
    global collection
    result = collection.find()
    monthDict = {}
    for item in result:
        for item in result:
            if item['date'][0:4] == year:
                month = int(item['date'][5:7])
                if month in monthDict.keys():
                    monthDict[month] = monthDict[month] + 1
                else:
                    monthDict[month] = 1
    with plt.xkcd():
        fig = plt.figure(figsize=(20,10))
        r = plt.bar(range(len(monthDict)), list(monthDict.values()), align='center')
        plt.xticks(range(len(monthDict)), list(monthDict.keys()))
        #添加数据标签
        for rects in r:
            height = rects.get_height()
            plt.text(rects.get_x() + rects.get_width() / 2, 1.015 * height, '%s' % int(height), fontsize=16, ha='center')
        #坐标轴
        plt.xlabel('Month',loc="center", fontsize=20)
        plt.ylabel('the number of commit', fontsize=20)
        plt.title('The number of code submissions per month in ' + year, fontsize=30)
        dir = os.path.join(os.getcwd(), "static","image", year + ".png")
        #将图片保存至/static/image，名为{year}.png
        plt.savefig(dir,format='png',dpi = 300)

def plotFigureForCertainAuthor(author):
    """
    为指定的提交者绘制条形图，横轴为年，纵轴为commit数。
    绘制的条形图将会保存到/static/image，名为{author}.png
    :param author: 提交者姓名
    """
    global collection
    result = collection.find()
    yearDict = {}
    for item in result:
        for item in result:
            if item['author'] == author:
                year = int(item['date'][0:4])
                if year in yearDict.keys():
                    yearDict[year] = yearDict[year] + 1
                else:
                    yearDict[year] = 1
    with plt.xkcd():
        fig = plt.figure(figsize=(20, 10))
        r = plt.bar(range(len(yearDict)), list(yearDict.values()), align='center')
        plt.xticks(range(len(yearDict)), list(yearDict.keys()))
        # 添加数据标签
        for rects in r:
            height = rects.get_height()
            plt.text(rects.get_x() + rects.get_width() / 2, 1.015 * height, '%s' % int(height), fontsize=16,
                     ha='center')
        # 坐标轴
        plt.xlabel('Month', loc="center", fontsize=20)
        plt.ylabel('the number of commit', fontsize=20)
        plt.title('The number of code submissions per month in ' + author, fontsize=30)
        dir = os.path.join(os.getcwd(), "static", "image", author + ".png")
        # 将图片保存至/static/image，名为{author}.png
        plt.savefig(dir, format='png', dpi=300)
    
def plotFigureForParticipantsDict():
    """
    根据participantsDict绘制条形图，并保存至/static/image，名为NumberofParticipantsPerYear.png
    """
    participantsDict = getParticipantsNumberDict()
    with plt.xkcd():
        fig = plt.figure(figsize=(20,10))
        r = plt.bar(range(len(participantsDict)), list(participantsDict.values()), align='center')
        plt.xticks(range(len(participantsDict)), list(participantsDict.keys()))
        #添加数据标签
        for rects in r:
            height = rects.get_height()
            plt.text(rects.get_x() + rects.get_width() / 2, 1.015 * height, '%s' % int(height), fontsize=16, ha='center')
        #坐标轴
        plt.xlabel('Year ', loc="center", fontsize=20)
        plt.ylabel('the number of participants', fontsize=20)
        plt.title('The number of participants per year', fontsize=30)
        dir = os.path.join(os.getcwd(), "static", "image", "NumberofParticipantsPerYear.png")
        #将图片保存至/static/image，名为NumberofParticipantsPerYear.png
        plt.savefig(dir,format='png',dpi = 300)

    
def plotFigureForLastYearAuthorDict():
    """
    根据monthDict绘制条形图，将图片保存至/static/image，名为LastYear'sBestContributor.png
    """
    LastyearauthorDict = findThePersonWhoContributedTheMostLastYear()
    with plt.xkcd():
        fig = plt.figure(figsize=(20,10))
        r = plt.bar(range(len(LastyearauthorDict)), list(LastyearauthorDict.values()), align='center')
        plt.xticks(range(len(LastyearauthorDict)), list(LastyearauthorDict.keys()))
        #添加数据标签
        for rects in r:
            height = rects.get_height()
            plt.text(rects.get_x() + rects.get_width() / 2, 1.015 * height, '%s' % int(height), fontsize=16, ha='center')
        #坐标轴
        plt.xlabel('Month ', loc="center", fontsize=20)
        plt.ylabel('the number of commit', fontsize=20)
        plt.title("The number of code submissions per month for the biggest contributor last year", fontsize=30)
        dir = os.path.join(os.getcwd(), "static", "image", "Last year's best contributor.png")
        #将图片保存至/static/image，名为Last year's best contributor.png
        plt.savefig(dir,format='png',dpi = 300)



