# -*- coding: utf-8 -*-


__author__ = 'shaw'

import os
import requests
import urllib.request

BASE_URL = 'https://www.bing.com'
IMAGE_ARCHIVE_URL = BASE_URL + '/HPImageArchive.aspx?idx=0&n=1&format=js'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
}
WALLPAPER_PATH = 'C:/Users/yshaw/Desktop/wallpaper/'
HEXO_CWD = 'D:/ProgramData/hexo'
CWD_CMD = ' --cwd ' + HEXO_CWD
HEXO_CONFIG = 'D:/ProgramData/hexo/themes/landscape/_config.yml'


def handle_hexo(image, image_url):
    """
    hexo博客
    """
    startdate = image['startdate']
    title = image['title']
    copyright = image['copyright']
    copyrightlink = image['copyrightlink']

    post_title = 'bing壁纸-%s-%s' % (startdate, title)
    md_file_path = '%s/source/_posts/%s.md' % (HEXO_CWD, post_title)

    # 新建博文
    cmd_new = 'hexo new "%s" --replace' % post_title
    os.system(cmd_new + CWD_CMD)

    # 读取md现有内容
    md_file = open(md_file_path, mode='r', encoding='UTF-8')
    front_matter = md_file.readlines()

    md_file = open(md_file_path, mode='w+', encoding='UTF-8')
    # 写入现有内容
    for line in front_matter:
        if line.startswith('tags:'):
            # 添加标签
            # md_file.writelines('tags: \n')
            md_file.writelines(line)
        elif line.startswith('category:'):
            # 分类
            md_file.writelines('category:\n')
            md_file.writelines('    - 爬虫\n')
            md_file.writelines('    - bing壁纸\n')
        elif line.startswith('date:'):
            # 时间
            # date = datetime.strptime(startdate, '%Y%m%d')
            # datetime_str = date.strftime('%Y-%m-%d 16:05:00')
            # md_file.writelines('date: ' + datetime_str + '\n')
            md_file.writelines(line)
        else:
            md_file.writelines(line)
    # 写入文章
    md_file.writelines('\n')
    md_file.writelines(title + '\n')
    md_file.writelines('\n')
    md_file.writelines('[' + copyright + '](' + copyrightlink + ')\n')
    md_file.writelines('\n')
    md_file.writelines('<!-- more -->\n')
    md_file.writelines('\n')
    md_file.writelines('![' + copyright + '](' + image_url + ')\n')
    md_file.close()

    # 更新banner
    config = open(HEXO_CONFIG, mode='r', encoding='UTF-8')
    config_lines = config.readlines()
    config = open(HEXO_CONFIG, mode='w+', encoding='UTF-8')
    for line in config_lines:
        if line.startswith('banner: '):
            config.writelines('banner: \"' + image_url + '\"\n')
        else:
            config.writelines(line)
    config.close()

    cmd_clean = 'hexo clean'
    os.system(cmd_clean + CWD_CMD)
    # 生成html，部署到git
    # cmd_generate = 'hexo generate'
    cmd_generate = 'hexo generate --deploy'
    os.system(cmd_generate + CWD_CMD)


if __name__ == '__main__':
    resp = requests.get(IMAGE_ARCHIVE_URL, headers=HEADERS)
    image = resp.json()['images'][0]

    image_url = BASE_URL + image['urlbase'] + '_UHD.jpg'

    # 下载图片
    copyright = image['copyright']
    filename = '%s%s_%s.jpg' % (WALLPAPER_PATH, image['startdate'], copyright[:copyright.index('©') - 2])
    urllib.request.urlretrieve(image_url, filename=filename)

    # # hexo博客
    handle_hexo(image, image_url)
