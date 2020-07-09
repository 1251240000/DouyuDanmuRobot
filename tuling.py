import requests
import json

url = 'http://openapi.tuling123.com/openapi/api/v2'
data = {'perception': {'inputText': {'text': ''}}, 'userInfo': {'apiKey': 'd15d4c03170d478dbcce9467a662c8ed', 'userId': 'ae49c7d5f8114a31'}}


class Tuling():
    @staticmethod
    def converse(message):
        try:
            data['perception']['inputText']['text'] = message
            req = requests.post(url, json.dumps(data).encode('utf8'))
            res = json.loads(req.text)
            return res['results'][0]['values']['text']
        except Exception as e:
            print("图灵机器人会话错误，", e)


if __name__ == "__main__":
    txt = input("输入对话内容与机器人进行对话,或输入q退出。\n> ")
    while txt != 'q':
        txt and print(Tuling.converse(txt))
        txt = input('> ')
