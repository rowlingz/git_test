import json


user_file = 'user_message.txt'
user_info = 'user_info.txt'

url_rules = {
        'user_rule': '/rest/n/user/profile/v2',
        'feeds_rule': '/rest/n/feed/profile2',
        'comment_firstpage': '/rest/n/comment/list/firstPage?',
        'comment_others': '/rest/n/comment/list/v2?',

}

def save_to_file(filename, message):
    with open (filename, 'a') as f:
        f.write('====>' + '\n')
        f.write(message + '\n')


def response(flow):
    user_role = '/rest/n/user/profile/v2'
    current_url = flow.request.url

    if user_role in current_url:
        print('====== 开始爬取')
        data = flow.response.text

        user_message = json.loads(data)
        save_to_file(user_file, json.dumps(user_message))
        user_profile = user_message.get('userProfile')

        resp = {
                'user_id': user_profile.get('profile').get('user_id'),
                'city_name': user_profile.get('cityName'),
                'ownerCount': user_profile.get('ownerCount'),
                'user_name': user_profile.get('profile').get('user_name'),
                'user_text': user_profile.get('profile').get('user_text')
        }

        save_to_file(user_info, json.dumps(resp))
        print('=======数据存入完毕')


if if __name__ == "__main__":
        print('实在不知道加哪了～')