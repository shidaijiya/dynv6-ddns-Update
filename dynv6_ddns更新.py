#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import requests
#you token
# 你的token#
you_token = ''
#you hostname
# 你的域名
you_hostname = ''
# 获取ipv6地址
def getIPv6Address():
    text = requests.get('https://v6.ident.me').text
    return text


if __name__ == "__main__":
    # get请求地址
    ipv6_hostname = f'http://dynv6.com/api/update?hostname={you_hostname}&ipv6={getIPv6Address()}&token={you_token}'

# get请求
url = ipv6_hostname
p = {"key": "abf91475fc19f66c2f1fe567edd75257",
     "date": "2014-09-11"}
a = requests.get(url, params=p)  # 发请求
# print(ipv6_hostname)  #dynv6_API的Request URL
# print(a.status_code)  # 状态码
# print(a.text)  # raw 文本内容
Success_status_code = 200
Success_return_value = 'addresses updated'
if a.status_code == Success_status_code:
    if a.text == Success_return_value:
        print('服务器成功响应,服务器返回值正确')
    else:
        print(f'服务器返回值错误,服务器的返回值为{a.text}')
else:
    print(f'状态码错误,错误的状态码为{a.status_code}')

# 保存获取的ipv6地址
f = open("ipv6_address.txt", 'w')  # 打开txt
f.write(getIPv6Address())  # 写入获取到的ipv6地址
f.close()  # 关闭txt
time.sleep(1)
