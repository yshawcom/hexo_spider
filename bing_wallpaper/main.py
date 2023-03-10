# -*- coding: utf-8 -*-


__author__ = 'shaw'

import os
import urllib.request

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
    title = image['title'].replace('?', '？')
    copyright = image['copyright']

    md_file = open(POST_FILE, mode='r', encoding='utf-8')
    md_file_lines = md_file.readlines()
    md_file = open(POST_FILE, mode='w+', encoding='utf-8')
    for line in md_file_lines:
        if line.startswith('cover:'):
            # 封面
            md_file.writelines('cover: %s\n' % image_url)
        elif line.startswith('thumbnail:'):
            # 缩略图
            md_file.writelines('thumbnail: %s\n' % image_url)
        elif line.startswith('<!-- title -->'):
            # 标题
            md_file.writelines('<!-- title -->%s\n' % title)
        elif line.startswith('<div class="justified-gallery">'):
            # 画廊
            md_file.writelines('<div class="justified-gallery">\n')
            md_file.writelines('\n![%s](%s)' % (copyright, image_url))
        else:
            md_file.writelines(line)
    md_file.close()

    # 生成html，部署到git
    cmd_generate = 'D: && cd ' + HEXO_CWD + ' && hexo clean && hexo generate'
    # cmd_generate = 'd: && cd ' + HEXO_CWD + ' && hexo clean && hexo generate --deploy'
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
