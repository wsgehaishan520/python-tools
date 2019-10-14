#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import re
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

import requests


"""
牛客网 在线编程 代码爬取
"""
class CodeSpider():
    def __init__(self):
        self.base_url = 'https://www.nowcoder.com/'
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 100)

    def login(self, username, password):
        """
        打开浏览器并登陆牛客网（不登陆看不到具体代码）
        """
        self.driver.get(self.base_url + 'login')
        user_element = self.wait.until(EC.presence_of_element_located((By.ID, 'jsEmailIpt')))
        pass_element = self.wait.until(EC.presence_of_element_located((By.ID, 'jsPasswordIpt')))
        user_element.clear()
        pass_element.clear()
        user_element.send_keys(username)
        pass_element.send_keys(password)
        login_btn = self.driver.find_element_by_id('jsLoginBtn')
        login_btn.click()
        time.sleep(1)

    def grab(self, uid):
        """
        爬取题目列表，返回题目信息字典
        """
        self.driver.get(self.base_url + 'profile/' + uid + '/codeBooks?onlyAcc=1&page=1')
        # print(self.driver.page_source)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        trs = [tr.find_all('td') for tr in soup.find_all('tr')]
        headers = [td.get_text(strip = True) for td in trs[0]]
        headers.append('代码链接')
        data = trs[1:]

        content_list = []
        title_map = {}
        # 处理第一页
        for td_list in data:
            # 去重
            title = td_list[0].get_text(strip = True).replace('\n', '')
            if title_map.get(title, -1) == -1:
                title_map.update({title: 1})
            else: continue
            content = [td_list[i].get_text(strip = True).replace('\n', '') for i in range(len(headers)-1)]
            content.append(self.base_url + td_list[0].find('a').get('href'))
            content_list.append(content)

        # 计算总页数
        stats_times = self.driver.find_element_by_class_name('stats-times')
        total_page = int(int(re.findall(r"\d+\.?\d*", stats_times.text)[0]) / 10) + 1
        print('total_page: ', total_page)
        
        # 处理后续页
        for i in range(total_page - 1):
            # <a data-page="9" href="javascript:void(0)">下一页</a>
            self.driver.find_element_by_link_text('下一页').click()

            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            trs = [tr.find_all('td') for tr in soup.find_all('tr')]
            data = trs[1:]

            for td_list in data:
                title = td_list[0].get_text(strip = True).replace('\n', '')
                if title_map.get(title, -1) == -1:
                    title_map.update({title: 1})
                else: continue
                content = [td_list[i].get_text(strip = True).replace('\n', '') for i in range(len(headers)-1)]
                content.append(self.base_url + td_list[0].find('a').get('href'))
                content_list.append(content)
            time.sleep(1)

        question_data = {
            'headers' : [headers[i] for i in range(len(headers))],
            'content' : content_list
        }
        # print(question_data)
        return question_data

    def write_ques_md(self, question_data, path):
        """
        生产题目信息的 md 表格文件
        """
        headers = question_data['headers']
        content = question_data['content']
        md_str = '|'.join(headers) + '\n'
        md_str += '|'.join(['-' for i in range(len(headers))]) + '\n'
        for item in content:
            md_str += '|'.join(item[:len(item)-1])
            md_str += '| [URL](' + item[-1] + ')\n'
        # print(md_str)
        with open(path + 'question_table.md', 'w') as f:
            f.write(md_str)
        print('md done')

    def write_code_file(self, question_data, path):
        """
        获取具体代码并写入文件
        """
        for item in question_data['content']:
            title = item[0]
            code_url = item[len(item) - 1]
            self.driver.get(code_url)
            code_content = self.driver.find_element_by_class_name('container').text
            # print(code_content)
            submissionId = code_url.split('=')[1]
            
            dirPath = path + submissionId + '_' + title
            if not os.path.exists(dirPath): os.makedirs(dirPath)
            with open(dirPath + '/Solution.java', 'w') as f:
                f.write(code_content)

if __name__ == '__main__':
    print('开始爬取')
    codeSpider = CodeSpider()
    codeSpider.login('xxx', 'xxx') # 牛客账号密码（需要登陆才能查看提交的代码）
    question_data = codeSpider.grab('68829779') # 爬取对象的牛客用户ID（个人页面的url上可获取）
    # codeSpider.write_ques_md(question_data , '/Users/wuweijie/Documents/[github]/onlinejudge/nowcoder/')
    # codeSpider.write_code_file(question_data, '/Users/wuweijie/Documents/[github]/onlinejudge/nowcoder/')
    print('爬取完毕')
