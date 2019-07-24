import requests
from bs4 import BeautifulSoup
from lxml import html
import os
from mitmproxy import ctx
import json
import re


# http://m.gifshow.com[^\s]* 目标url 正则

def split_url(text):
    """利用正则表达式筛选出匹配的快手feed分享url"""
    result = re.search("http://m.gifshow.com[^\s]*", text)
    if result:
        target_url = result[0]
        return target_url
    else:
        print('提交信息有误，请重新输入')


def uid_from_feedurl(feed_url):
    """
    根据博文的url,可以得到 对应的user_id及作品Id, 在申请入驻和提交测评的两个方面都可以调用。
    :param feed_url:
    :return:
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',        # 这里为手机端的headers
        'Host': 'm.gifshow.com'
    }

    resp = requests.get(feed_url, headers=headers)

    if resp.status_code == 200:

        refactor_url = resp.url
        real_url = refactor_url.split('?')[0]
        resp_text = resp.text

        if resp_text:
            bf = BeautifulSoup(resp.text, 'html.parser')
            user_info = bf.find('div', 'follow-card open-or-download-app')['data-scheme-url']
            user_id = user_info.split('/')[-1]

            feed_info = bf.find('div', class_='btn open-or-download-app')['data-scheme-url']
            feed_id = feed_info.split('/')[-1]

            current_name = bf.find('div', class_='name').text

            return {'user_id': user_id, 'feed_id': feed_id, 'current_name': current_name, 'real_url': real_url}
    return


def control(devices_name, user_id):
    """
    控制APP跳转至博主个人主页
    :param devices_name:
    :param user_id:
    :return:
    """
    adb_open = f'adb -s {devices_name} shell am start -a  android.intent.action.VIEW -d kwai://profile/{user_id}'
    status = os.popen(adb_open)
    return status


def user_task(flow, user_id):
    user_rule = '/rest/n/user/profile/v2?'

    if user_rule in flow.request.url:
        user_text = flow.response.text
        user_json = json.loads(user_text)
        user_profile = user_json.get('userProfile')
        true, false = 1, 0
        user_message = {
            'user_id': user_id,
            'city_name': user_profile.get('cityName'),
            'constellation': user_profile.get('constellation'),
            'fan': user_profile.get('ownerCount').get('fan'),           # 粉丝
            'follow': user_profile.get('ownerCount').get('follow'),     # 关注
            'photo': user_profile.get('ownerCount').get('photo'),       # 作品总数
            'user_name': user_profile.get('profile').get('user_name'),
            'verified': user_profile.get('profile').get('verified'),
            'sex': user_profile.get('profile').get('user_sex'),
            'user_text': user_profile.get('profile').get('user_text'),
            'kwauId': user_profile.get('profile').get('kwaiId')
        }

        return user_message


def feed_task(flow, feed_id):
    feeds_rule = '/rest/n/feed/profile2?'
    if feeds_rule in flow.request.url:
        feeds_resp = json.loads(flow.response.text)
        feeds = feeds_resp.get('feeds')
        for feed in feeds:
            serverExpTag = feed.get('serverExpTag')
            current_feed = int(serverExpTag.split('|')[1])
            if current_feed == feed_id:
                # type = 1

                # 判断是视频还是图文类型
                main_mv_urls = feed.get('main_mv_urls')
                if main_mv_urls:
                    feed_type = 'mv'
                    main_mv_urls = feed.get('main_mv_urls')[1].get('url')
                    picture_url = None
                else:
                    feed_type = 'picture'
                    main_mv_urls = None

                if feed_type == 'picture':
                    picture_list = feed.get('ext_params').get('atlas').get('list')
                    picture_url = list(map(lambda x: 'http://tx2.a.yximgs.com' + x, picture_list))

                feed_message = {
                    'feed_id': feed_id,
                    'feed_type': feed_type,
                    'time': feed.get('time'),
                    'cover_url': feed.get('cover_thumbnail_urls')[0].get('url'),        # 封面图url
                    'main_mv_urls': main_mv_urls,                                       # 视频的url
                    'picture_url': picture_url,                                  # 图文拼接类（上下、左右） 内容图片url
                    'like_count': feed.get('like_count'),
                    'view_count': feed.get('view_count'),
                    'comment_count': feed.get('comment_count'),
                    'caption': feed.get('caption')
                }
                return feed_message
            else:
                continue
        print('当前url中未找到目标feed，需下滑')
        return

def git_test():
    print('just test git push')

if __name__ == '__main__':
    """
    输出结果为
    ==分析url:  http://m.gifshow.com/s/BD27iyd9
    其结果为： {'user_id': '1156783917', 'feed_id': '5220516406649090490', 'current_name': '韵桀音乐'}
    ==分析url:  http://m.gifshow.com/s/dGhklfHc
    其结果为： {'user_id': '895423732', 'feed_id': '5199405785604211156', 'current_name': '小H的成长日记'}
    """
    feed_urls = ['http://m.gifshow.com/s/BD27iyd9', 'http://m.gifshow.com/s/dGhklfHc']
    for url in feed_urls:
        print('==分析url: ', url)
        info = uid_from_feedurl(url)
        print('其结果为：', info)
