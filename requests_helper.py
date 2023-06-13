import datetime
import hashlib
import json
import hmac
import requests
import math
from hashlib import sha1
import pytz


class RequestHelper:
    def __init__(self, channel_id: str, account_id: str, secret: str, hook_api_version="v2"):
        self.__secret = secret
        self.__account_id = account_id
        self.__channel_id = channel_id
        self.url_base = "https://amojo.amocrm.ru"
        self.__hook_api_version = hook_api_version
        self.__scope_id = channel_id + "_" + account_id

    def create_headers(self, method_path, method, request_body):
        uct_1 = pytz.timezone("Europe/Berlin")
        now_date = datetime.datetime.now(uct_1)
        now_date = now_date.strftime("%a, %d %b %Y %H:%M:%S +0100")
        md5 = hashlib.md5(request_body.encode('utf-8')).hexdigest()
        content_type = 'application/json'
        params = [method, md5, content_type, now_date, method_path]
        params_string = "\n".join(params)
        signature = hmac.new(key=bytes(self.__secret, 'UTF-8'), msg=bytes(params_string, 'UTF-8'),
                             digestmod=sha1).hexdigest()
        return {
            'Date': now_date,
            "Content-Type": content_type,
            "Content-MD5": md5.lower(),
            "X-Signature": signature.lower(),
            "User-Agent": "amoCRM-Chats-Doc-Example/1.0"
        }

    def session_sample(self, url_to_method, request_sample, method="POST"):
        session = requests.session()
        url = self.url_base + url_to_method

        request_body = json.dumps(request_sample)
        headers = self.create_headers(method_path=url_to_method, method=method, request_body=request_body)
        session.headers = headers
        response = "Void"
        if method == "POST":
            response = session.post(url=url, data=request_body)
        elif method == "DELETE":
            response = session.delete(url=url, data=request_body)
        elif method == "GET":
            response = session.get(url=url)
        session.close()
        # try:
        #     response_code = response.status_code
            # print("Status: ", response_code)
        # except Exception as e:
        #     print("Response error: ", e)
        # try:
        #     print(response.json())
        # except Exception as e:
        #     print(e)

    def connect_channel(self):
        url_to_method = f'/v2/origin/custom/{self.__channel_id}/connect'
        request_sample = {
            "account_id": self.__account_id,
            "title": 'Ekaterina Info',
            'hook_api_version': self.__hook_api_version
        }
        self.session_sample(url_to_method, request_sample, "POST")

    def disconnect_channel(self):
        url_to_method = f'/v2/origin/custom/{self.__channel_id}/connect'
        request_sample = {
            "account_id": self.__account_id
        }
        self.session_sample(url_to_method, request_sample, "DELETE")

    def create_new_chat(self):
        url_to_method = f"/v2/origin/custom/{self.__scope_id}/chats"
        request_sample = {
            "conversation_id": "1",
            "user": {
                "id": "user-1",
                "avatar": "https://pic.rutubelist.ru/user/66/37/66370b638af9d17b6d6a359d2e7c29d5.jpg",
                "name": "Example Client",
                "profile": {
                    "phone": "77777777777",
                    "email": "example.client@example.com"
                }
            }
        }
        self.session_sample(url_to_method, request_sample, "POST")

    def send_message(self, msg_id, conversation_id, user_id, user_name, text, user_avatar="", profile_link="",
                     user_phone="", user_mail="", message_type="text", media_link: str = None, file_name: str = None,
                     file_size: int = None):
        url_to_method = f"/v2/origin/custom/{self.__scope_id}"
        ts = datetime.datetime.now().timestamp()
        timestamp = math.floor(ts)
        msec_timestamp = math.floor(ts * 1000)
        request_sample = {
            "event_type": "new_message",
            "payload": {
                "timestamp": timestamp,
                "msec_timestamp": msec_timestamp,
                "msgid": msg_id,
                "conversation_id": conversation_id,
                "sender": {
                    "id": user_id,
                    "avatar": user_avatar,
                    "profile": {
                        "phone": user_phone,
                        "email": user_mail
                    },
                    "name": user_name,
                    "profile_link": profile_link
                },
                "message": {
                    "type": message_type,
                    "text": text,
                    "media": media_link,
                    "file_name": file_name,
                    "file_size": file_size
                },
                "silent": False
            }
        }

        self.session_sample(url_to_method, request_sample, "POST")


# from config import ACC_ID, CH_ID, SECRET
#
# helper = RequestHelper(account_id=ACC_ID,
#                        channel_id=CH_ID, secret=SECRET)
# helper.connect_channel()
