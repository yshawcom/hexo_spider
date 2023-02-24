#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import logging
import os
import re

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://zh.wikipedia.org'
TODAY = datetime.date.today().strftime('%#m月%#d日')
URL = BASE_URL + '/zh-cn/' + TODAY
PROXIES = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}
HEXO_CWD = 'D:/ProgramData/hexo'


def handle_tag_a(tag, text):
    """
    处理标签中的链接
    :param tag:
    :param text:
    :return:
    """
    for a in tag.find_all('a'):
        if a.get('href', False):
            md_link = ' [%s](%s%s)' % (a.get_text(), BASE_URL, a['href'])
            text = text.replace(str(a), md_link)
        else:
            text = text.replace(str(a), '')
    return text


def html_2_markdown(html):
    text_md = str(html) \
        .replace(' ', '') \
        .replace('<p>', '') \
        .replace('</p>', '') \
        .replace('<li>', '') \
        .replace('</li>', '') \
        .replace('<mark class="template-facttext" title="需要提供文献来源">', '') \
        .replace('</mark>', '') \
        .replace('<b>', '**') \
        .replace('</b>', '**') \
        .replace('\n', '') \
        .strip()
    text_md = re.sub('<span .*?/></span>', '', text_md)
    text_md = re.sub('<sup .*?>.*?</sup>', '', text_md)

    # 处理链接页面不存在的情况
    replace_text = ''
    if html.span is not None:
        span_class = html.span.get('class')
        if span_class is not None and span_class[0] == 'ilh-all':
            for descendant in html.span.descendants:
                if descendant.name == 'a' and descendant.get('class')[0] == 'new':
                    replace_text = descendant.get_text()
                    break
        text_md = text_md.replace(str(html.span), replace_text)

    # 链接
    try:
        text_md = str(handle_tag_a(html, text_md))
    except Exception as e:
        logging.exception(e)

    return text_md.replace('  ', ' ') + '\n'


def gen_markdown_line():
    resp = requests.get(BASE_URL + '/zh-cn/' + TODAY, proxies=PROXIES)
    soup = BeautifulSoup(resp.text, 'lxml')
    # soup = BeautifulSoup(open('16.html', encoding='utf-8'), 'lxml')

    md_lines = []

    div = soup.select('#mw-content-text > div.mw-parser-output')[0]
    for content in div.contents:
        if content.get_text() == '\n' \
                or content.name is None \
                or content.name == 'table' \
                or content.get('id') == 'toc':
            continue
        # 简介
        if content.name == 'p':
            md_lines.append(html_2_markdown(content))
            md_lines.append('\n<!-- more -->\n')
        # 二级标题
        elif content.name == 'h2':
            span = content.contents[1]
            if span.get('class')[0] == 'mw-headline' \
                    and span.get('id') != '脚注' \
                    and span.get('id') != '参考资料' \
                    and span.get('id') != '參考資料':
                md_lines.append('\n## ' + span.get_text() + '\n\n')
        # 三级标题
        elif content.name == 'h3':
            span = content.contents[1]
            if span.get('class')[0] == 'mw-headline':
                md_lines.append('\n### ' + span.get_text() + '\n\n')
        # 列表
        elif content.name == 'ul':
            for li in content.find_all('li'):
                md_lines.append('* ' + html_2_markdown(li))
    return md_lines


def handle_hexo(lines):
    """
    处理hexo博客
    :param lines:
    :return:
    """
    title = '历史上的今天-' + TODAY
    cwd_cmd = ' --cwd ' + HEXO_CWD
    md_file_path = '%s/source/_posts/%s.md' % (HEXO_CWD, title)

    # 新建博文
    cmd_new = 'hexo new "%s" --replace' % title
    os.system(cmd_new + cwd_cmd)

    # 读取md现有内容
    md_file = open(md_file_path, mode='r', encoding='UTF-8')
    front_matter = md_file.readlines()

    md_file = open(md_file_path, mode='w+', encoding='UTF-8')
    # 写入现有内容
    for line in front_matter:
        if line.startswith('tags:'):
            # 标签
            # md_file.writelines('tags: 历史上的今天\n')
            md_file.writelines(line)
        elif line.startswith('category:'):
            # 分类
            md_file.writelines('category:\n')
            md_file.writelines('    - 爬虫\n')
            md_file.writelines('    - 历史上的今天\n')
        else:
            md_file.writelines(line)
    # 写入文章
    md_file.writelines('\n')
    # 写入正文
    for line in lines:
        md_file.writelines(line)
    md_file.writelines('\n> 本文转载自 [维基百科 历史上的今天 ' + TODAY + '](' + URL + ')\n')
    md_file.close()

    # 生成html，部署到git
    # cmd_generate = 'hexo generate'
    cmd_generate = 'hexo generate --deploy'
    os.system(cmd_generate + cwd_cmd)


if __name__ == '__main__':
    md_lines = gen_markdown_line()

    if len(md_lines) > 0:
        handle_hexo(md_lines)
