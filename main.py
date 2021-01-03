#!/usr/bin/env python3
# coding: utf-8

from flask import Flask, render_template, request, url_for, redirect, flash
from Utils.Utils import *
import os
import sys
app = Flask(__name__)
#设置密钥
app.config['SECRET_KEY'] = 'open_source'

#主页面函数
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        path = getImagePath(content='CommitNumber', type='default')
        return render_template('index.html', imgPath=path)
    else:
        content = request.form.get("content")
        if content.isdigit() and len(content) == 4:
            if isValidYear(content):
                path = getImagePath(content=content, type="year")
                infos = getRelevantGitInfos(content, type="year")
                return render_template('searchResult.html', imgPath=path, gitInfos = infos)
            else:
                flash('Invalid year ' + content + ', please choose between [2012,2020]')
                path = getImagePath(content='CommitNumber', type='default')
                return redirect(url_for('index', imgPath=path))
        elif isValidAuthor(content):
            path = getImagePath(content=content, type="author")
            infos = getRelevantGitInfos(content, type="author")
            return render_template('searchResult.html', imgPath=path, gitInfos = infos)
        else:
            flash('Invalid author name ' + content + ', please retry!')
            path = getImagePath(content='CommitNumber', type='default')
            return redirect(url_for('index', imgPath=path))

#小知识问答页面函数
@app.route('/knowledge/<int:question_id>', methods=['GET', 'POST'])
def knowledge(question_id):
    if request.method == 'GET':
        answer = getQuestionAnswer(question_id)
        return render_template('knowledge.html', answer=answer, id=question_id)
    else:
        content = request.form.get("content")
        if content.isdigit() and len(content) == 4:
            if isValidYear(content):
                path = getImagePath(content=content, type="year")
                infos = getRelevantGitInfos(content, type="year")
                return render_template('searchResult.html', imgPath=path, gitInfos=infos)
            else:
                flash('Invalid year ' + content + ', please choose between [2012,2020]')
                path = getImagePath(content='CommitNumber', type='default')
                return redirect(url_for('index', imgPath=path))
        elif isValidAuthor(content):
            path = getImagePath(content=content, type="author")
            infos = getRelevantGitInfos(content, type="author")
            return render_template('searchResult.html', imgPath=path, gitInfos=infos)
        else:
            flash('Invalid author name ' + content + ', please retry!')
            path = getImagePath(content='CommitNumber', type='default')
            return redirect(url_for('index', imgPath=path))


if __name__ == '__main__':

    BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            'visual_analysis_of_pytorch')
    os.chdir(BASE_DIR)

    #initDataBase()#如果不是第一次运行本程序，请注释此条语句
    app.run()