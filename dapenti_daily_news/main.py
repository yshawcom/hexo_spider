#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import os
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup


BASE_URL = 'http://www.dapenti.com/blog/'
EXCLUDES_P = [
    '以下内容，有可能',
    '本文转摘的各类事',
    '欢迎转载，转载请',
    '广告',
    '友情提示：请各位',
    '喷嚏', '图卦'
]
EXCLUDES_TAGS = ['table', 'span', 'br', 'hr', 'script', 'ins']
HEXO_CWD = 'D:/ProgramData/hexo'
INDEX_AND_BANNER_IMG = ''
INDEX_MD = HEXO_CWD + '/source/_posts/dapenti/index.md'


def handle_list_page():
    """
    处理列表页，获取第一个链接
    :return: 详情页标题，详情页URL
    """
    list_page_url = 'blog.asp?subjectid=70&name=xilei'
    resp = requests.get(BASE_URL + list_page_url)
    # 指定编码为gb2312
    resp.encoding = 'gb18030'
    soup = BeautifulSoup(resp.text, 'lxml')
    # 列表中第一个连接
    # all_li = soup.ul.find_all('li')
    # a = all_li[1].a
    a = soup.ul.li.a
    # 详情页标题
    detail_title = a.string
    # 详情页链接
    detail_url = a['href']
    return detail_title, detail_url


def handle_detail_page(detail_url):
    """
    处理详情页
    :param detail_url: 详情页URL
    :return:
    """
    resp = requests.get(BASE_URL + detail_url)
    resp.encoding = 'gb18030'
    soup_html = BeautifulSoup(resp.text, 'lxml')
    tds = soup_html.select('body > table > tbody > tr > td.oblog_t_2 > div > table > tbody > tr:nth-child(2) > td')
    # 修正html格式错误
    td = str(tds[0]).replace('<span class="oblog_text"><p>', '') \
        .replace(' ', '') \
        .replace('­', '')

    soup_td = BeautifulSoup(td, 'lxml')

    lines = []
    # md_file = open(detail_title + '.md', mode='w+', encoding='UTF-8')

    tags = soup_td.body.td.contents
    for tag in tags:
        line = handle_tag(tag)
        if line:
            lines.append(line)
            # md_file.writelines(line)

    # md_file.close()
    return lines


def handle_tag(tag):
    """
    处理单个标签内容为markdown
    :param tag:
    :return:
    """
    # 排除不需要的标签
    if tag.name is not None:
        if any(e in tag.name for e in EXCLUDES_TAGS):
            return
        if tag.get('style', False):
            return
    else:
        text = tag.get_text().replace('	', '') \
            .replace('\n', '') \
            .strip()
        if text == '':
            return

    if '\n' == tag.get_text() or any(e in tag.get_text() for e in EXCLUDES_P):
        return

    text = str(tag).replace('	', '') \
        .replace('<p>', '') \
        .replace('</p>', '') \
        .replace('</div>', '') \
        .replace('<br/>', '') \
        .replace('\n', '') \
        .strip()
    text = re.sub('<div.*?>', '', text)

    # 链接
    try:
        text = str(handle_tag_a(tag, text))
    except Exception as e:
        logging.exception(e)

    # 图片
    try:
        text = str(handle_tag_img(tag, text))
    except Exception as e:
        logging.exception(e)

    # iframe
    try:
        text = str(handle_tag_iframe(tag, text))
    except Exception as e:
        logging.exception(e)

    # 标题序号
    if re.search('【[1-9][0-9]?】', text):
        text = text.replace('【', '## ').replace('】', '. ')
        # 标题过长时进行处理
        i = len(text) - 1
        if i >= 52:
            if '，' in text:
                i = text.index('，')
            if '。' in text:
                i = text.index('。')
            if '！' in text:
                i = text.index('！')
            if '：' in text:
                i = text.index('：')
            text = text[:i + 1] + '\n' + text[i + 1:]

    return '\n' + text + '\n'


def handle_tag_iframe(tag, text):
    """
    处理标签中的iframe
    :param tag:
    :param text:
    :return:
    """
    for iframe in tag.find_all('iframe'):
        md_link = ' [打开外部页面链接](%s) ' % (iframe['src'])
        text = text.replace(str(iframe).replace('\n', ''), md_link)
    return text


def handle_tag_img(tag, text):
    """
    处理标签中的图片
    :param tag:
    :param text:
    :return:
    """
    global INDEX_AND_BANNER_IMG
    for img in tag.find_all('img'):
        alt = img.get('alt', '')
        if alt.startswith('[') and alt.endswith(']'):
            alt = ''

        img_url = img['src']
        if INDEX_AND_BANNER_IMG == '':
            INDEX_AND_BANNER_IMG = img_url

        md_link = ' ![%s](%s) ' % (alt, img_url)
        text = text.replace(str(img), md_link)

    return text


def handle_tag_a(tag, text):
    """
    处理标签中的链接
    :param tag:
    :param text:
    :return:
    """
    for a in tag.find_all('a'):
        if a.get('href', False):
            md_link = ' [%s](%s) ' % (a.get_text(), a['href'])
            text = text.replace(str(a), md_link)
        else:
            text = text.replace(str(a), '')
    return text


def handle_hexo(full_title, url, lines):
    """
    处理hexo博客
    :param full_title:
    :param url:
    :param lines:
    :return:
    """
    index = full_title.index('】')
    title = full_title[index + 1:]
    title_rename = full_title[1:index]
    date_ymd_str = full_title[5:index]
    ori_url = BASE_URL + url
    permalink = '/dapenti/%s/' % date_ymd_str
    date_ymd = datetime.strptime(date_ymd_str, "%Y%m%d")
    date_y_m_d = date_ymd.strftime('%Y.%m.%d')

    cwd_cmd = ' --cwd ' + HEXO_CWD
    md_file_path = '%s/source/_posts/dapenti/%s.md' % (HEXO_CWD, date_ymd_str)

    # 新建博文
    cmd_new = 'hexo new --path dapenti/%s "%s" --replace' % (date_ymd_str, date_ymd_str)
    os.system(cmd_new + cwd_cmd)

    # 读取md现有内容
    md_file = open(md_file_path, mode='r', encoding='UTF-8')
    front_matter = md_file.readlines()

    md_file = open(md_file_path, mode='w+', encoding='UTF-8')
    # 写入现有内容
    for line in front_matter:
        if line.startswith('title:'):
            md_file.writelines('title: %s\n' % title)
        # elif line.startswith('category:'):
        #     md_file.writelines('category: 喷嚏图卦\n')
        elif line.startswith('tags:'):
            # 添加标签和封面图
            md_file.writelines('tags:\n')
            md_file.writelines('permalink: %s\n' % permalink)
            md_file.writelines('hidden: true\n')
        else:
            md_file.writelines(line)
    # 写入文章
    md_file.writelines('\n')
    md_file.writelines(title_rename + '\n')
    md_file.writelines('\n')
    md_file.writelines('<!-- more -->\n')
    md_file.writelines('\n')
    # 写入正文
    for line in lines:
        md_file.writelines(line)
    md_file.writelines('> 本文转载自 铂程斋 [%s](%s)\n' % (full_title, ori_url))
    md_file.close()

    # 列表页
    index_md = open(INDEX_MD, mode='r', encoding='utf-8')
    index_md_lines = index_md.readlines()
    index_md = open(INDEX_MD, mode='w+', encoding='utf-8')
    for line in index_md_lines:
        if line.startswith('<!-- today -->'):
            index_md.writelines('<!-- today -->\n')
            index_md.writelines('\n')
            index_md.writelines('* %s [%s](%s)\n' % (date_y_m_d, title, permalink))
            index_md.writelines('<!-- more -->\n')
        elif line.startswith('<!-- more -->'):
            pass
        else:
            index_md.writelines(line)
    index_md.close()

    # 生成html，部署到git
    cmd_generate = 'D: && cd ' + HEXO_CWD + ' && hexo clean && hexo generate'
    # cmd_generate = 'd: && cd ' + HEXO_CWD + ' && hexo clean && hexo generate --deploy'
    os.system(cmd_generate)


if __name__ == '__main__':
    # 处理列表页，获取第一个链接
    title, url = handle_list_page()

    # 处理详情页
    lines = handle_detail_page(url)

    if len(lines) > 0:
        # hexo博客
        handle_hexo(title, url, lines)
