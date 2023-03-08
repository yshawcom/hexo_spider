# -*- coding: utf-8 -*-


__author__ = 'shaw'

import datetime
import os
import urllib.request
from datetime import datetime

import requests


BASE_URL = 'https://www.bing.com'
IMAGE_ARCHIVE_URL = BASE_URL + '/HPImageArchive.aspx?idx=0&n=1&format=js'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
}
WALLPAPER_PATH = '\\\\192.168.50.3/photo/bing_wallpaper/'
HEXO_CWD = r'D:/ProgramData/hexo'
CWD_CMD = ' --cwd ' + HEXO_CWD
POST_FILE = HEXO_CWD + '/source/_posts/bing壁纸.md'
HEXO_CONFIG = 'D:/ProgramData/hexo/themes/landscape/_config.yml'


def handle_hexo(image, image_url):
    """
    hexo博客
    """
    start_date = datetime.strptime(image['startdate'], "%Y%m%d")
    _y_m_d = start_date.strftime('%Y.%m.%d')
    title = image['title'].replace('?', '？')
    copyright = image['copyright']
    copyrightlink = image['copyrightlink']

    md_file = open(POST_FILE, mode='r', encoding='utf-8')
    md_file_lines = md_file.readlines()
    md_file = open(POST_FILE, mode='w+', encoding='utf-8')
    for line in md_file_lines:
        if line.startswith('<!-- more -->'):
            pass
        elif line.startswith('微软 bing 每日壁纸图片。'):
            md_file.writelines('微软 bing 每日壁纸图片。\n')
            md_file.writelines('\n### %s %s\n' % (_y_m_d, title))
            md_file.writelines('\n[%s](%s)\n' % (copyright, copyrightlink))
            md_file.writelines('\n![%s](%s)\n' % (copyright, image_url))
            md_file.writelines('\n<!-- more -->\n')
            if start_date.day == 1:
                last_month_last_day = start_date - datetime.timedelta(days=1)
                md_file.writelines('\n## %s\n' % last_month_last_day.strftime('%Y.%m'))
        else:
            md_file.writelines(line)
    md_file.close()

    r"""
    # 更新banner
    config = open(HEXO_CONFIG, mode='r', encoding='UTF-8')
    config_lines = config.readlines()
    config = open(HEXO_CONFIG, mode='w+', encoding='UTF-8')
    for line in config_lines:
        if line.startswith('banner:'):
            config.writelines('banner: \"' + image_url + '\"\n')
        elif line.startswith('subtitle:'):
            config.writelines('subtitle: \"' + title + '\"\n')
        else:
            config.writelines(line)
    config.close()
    """

    # 生成html，部署到git
    # cmd_generate = 'D: && cd ' + HEXO_CWD + ' && hexo clean && hexo generate'
    cmd_generate = 'd: && cd ' + HEXO_CWD + ' && hexo clean && hexo generate --deploy'
    os.system(cmd_generate)


if __name__ == '__main__':
    resp = requests.get(IMAGE_ARCHIVE_URL, headers=HEADERS)
    image = resp.json()['images'][0]

    image_url = BASE_URL + image['urlbase'] + '_UHD.jpg'

    # 下载图片
    copyright = image['copyright']
    filename = '%s%s_%s.jpg' % (WALLPAPER_PATH, image['startdate'], copyright[:copyright.index('©') - 2])
    urllib.request.urlretrieve(image_url, filename=filename)

    # hexo博客
    handle_hexo(image, image_url)
