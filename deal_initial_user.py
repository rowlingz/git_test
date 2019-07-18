import pandas as pd
import pymysql
from sqlalchemy import create_engine
import requests
from bs4 import BeautifulSoup
import time
import re
import datetime


def get_realUrl(text):
    # 利用正则匹配出合格url
    result = re.search(r"http://www.gifshow.com/s/[^\s]{8}", text)
    if result:
        target_url = result[0]
        return target_url
    else:
        return


def uid_from_homepageUrl(url):
    # 进行网页访问，提取uid--adb语句
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 '
                      '(KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
        # 这里为手机端的headers
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        resp_text = resp.text
        if resp_text:
            bf = BeautifulSoup(resp.text, 'html.parser')
            user_info = bf.find('div', class_='avatar')['data-scheme-url']
            uid = user_info.split('/')[-1]
            # print(url, user_info, uid)
            time.sleep(0.25)
            return uid


def get_uid_to_mysql():
    # 将文件存入mysql
    data = pd.read_excel('./resp_text/2.xlsx', sheet_name='快手')
    print(data.shape)
    data['realUrl'] = data['主页链接'].apply(lambda x: get_realUrl(x))
    # data['adb_url'] = [''] * data.shape[0]
    # data['uid'] = [''] * data.shape[0]

    #
    data['uid'] = data['realUrl'].apply(lambda x: uid_from_homepageUrl(x))
    print(data['uid'])
    data['adb_url'] = data['uid'].apply(lambda x: 'kwai://profile/'+x)

    print(data['realUrl'])

    connect = create_engine('mysql+pymysql://root@localhost:3306/yingtu?charset=utf8')
    data.to_sql(name='initialUser_uid', con=connect, if_exists='replace')
    print('end')


def read_info_from_mysql_to_excel():
    conn = pymysql.connect(host='localhost', user='root', password='root', database='yingtu', port=3306, charset='utf8')
    sql_select = "select * from initialUser_uid"
    df = pd.read_sql(sql_select, conn)

    df.to_excel('initial_uid.xls', index=False)


def creat_to_crawler_jobs():
    # 将文件存到爬虫库中
    conn_init = pymysql.connect(host='localhost', user='root', password='root', database='yingtu', port=3306, charset='utf8')
    cursor_init = conn_init.cursor()
    sql_select = "select adb_url from initialUser_uid"
    df = pd.read_sql(sql_select, conn_init)
    rows = df.shape[0]
    print(rows)

    # print(df)
    #
    conn_target = pymysql.connect(host='localhost', user='root', password='root',
                                  database='yingtu_crawler', port=3306, charset='utf8')
    cursor_target = conn_target.cursor()
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    sql_insert = "insert into crawler_jobs_inital " \
                 "select 0, 0, 0, %(url)s, 8, 1, '{}', '', 6, 0, 0, 0, " \
                 "%(now)s, %(now)s, %(now)s from dual " \
                 "where not exists " \
                 "(SELECT url, job_type FROM crawler_jobs_inital WHERE url = %(url)s AND job_type = 1) limit 1"

    sql_insert_test = "insert into initialUser " \
                      "select 0, '', '', %(now)s, 0, 0, %(now)s, '', '', %(url)s from dual where not exists " \
                      "(select url from initialUser where url = %(url)s) limit 1"

    try:
        for i in range(rows):
            print({'url': df.iloc[i, 0], 'now': now_time})
            cursor_target.execute(sql_insert, {'url': df.iloc[i, 0], 'now': now_time})
        conn_target.commit()
        print('插入成功')
    except Exception as e:
        print(e)
        conn_target.rollback()
        print('插入失败')
    finally:
        cursor_target.close()
        cursor_init.close()
        conn_target.close()
        conn_init.close()


if __name__ == '__main__':
    creat_to_crawler_jobs()
    print('存入完毕')


