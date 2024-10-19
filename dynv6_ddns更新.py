#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
import dns.resolver
import portalocker
import psutil
import requests



# 你的token
your_token = '你的token'
# 你的域名
your_domain = '你的域名'


# 创建log目录
os.makedirs("./log", exist_ok=True)
# 获取当前时间的时间戳
timestamp = time.time()
# 设置日志记录
logging.basicConfig(filename=f'./log/{timestamp}.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    filemode='w')
lock_file_name = 'up_update.lock'  # 锁文件名称


def check_if_process_running(pid):
    """检查给定的 PID 是否对应一个正在运行的进程"""
    try:
        # 使用 psutil 来检查指定 pid 的进程是否还在运行
        process = psutil.Process(pid)
        return process.is_running()
    except psutil.NoSuchProcess:
        # 如果找不到该进程，说明它已经不在运行
        return False


def make_lock_file():
    # 获取系统的临时目录
    temp_dir = tempfile.gettempdir()
    lock_file_path = os.path.join(temp_dir, lock_file_name)

    # 打开锁文件，并尝试锁定
    with open(lock_file_path, 'a+') as f:
        try:
            # 尝试获取文件锁，确保其他进程不能访问文件
            portalocker.lock(f, portalocker.LOCK_EX | portalocker.LOCK_NB)
        except portalocker.LockException:
            print("其他进程正在运行，退出...")
            logging.info("其他进程正在运行，退出...")
            sys.exit(1)

        # 移动文件指针到文件开始位置，读取锁文件中的PID
        f.seek(0)
        lock_content = f.read().strip()

        # 如果锁文件不为空，检查PID是否对应一个正在运行的进程
        if lock_content:
            try:
                old_pid = int(lock_content)
                if check_if_process_running(old_pid):
                    print(f"另一个pid为:{old_pid}的实例正在运行，正在执行单次更新...\n"
                          f"[注意本次更新完其他实例会继续运行,本实例将会退出]")
                    logging.info(f"另一个pid为:{old_pid}的实例正在运行，正在执行单次更新...\n"
                          f"[注意本次更新完其他实例会继续运行,本实例将会退出]")

                    while True:
                        up_ipv6 = post_up_requests(your_domain, your_token)
                        if up_ipv6:
                            logging.info(f"{your_domain}单次记录更新成功！")
                            break
                        else:
                            logging.error("单次更新失败1分钟后重试")
                            time.sleep(60)
                    sys.exit(1)
                else:
                    pass
            except ValueError:
                print("锁文件内容无效，继续运行")
                logging.error("锁文件内容无效，继续运行")

        # 到这一步，说明当前是唯一运行的实例，写入当前进程的PID
        f.seek(0)  # 将文件指针移到开始位置
        f.truncate()  # 清空文件内容
        f.write(str(os.getpid()))  # 写入当前进程的PID
        f.flush()  # 确保写入到磁盘

    print("当前实例正在运行")
    logging.info("当前实例正在运行")
    return lock_file_path


def get_primary_ipv6_address():
    """获取Windows操作系统的首个全球唯一IPv6地址"""
    try:
        # 定义不显示窗口的标志 (仅适用于Windows)
        creationflags = subprocess.CREATE_NO_WINDOW
        # 执行ipconfig命令并获取输出，尝试使用UTF-8编码
        result = subprocess.check_output("ipconfig", encoding='gbk', errors='ignore', creationflags=creationflags)
        # print(result)
        # 使用正则表达式查找IPv6地址，排除链路本地地址
        ipv6_addresses = re.findall(r"IPv6 地址[ .]*: ([\da-fA-F:]+(?::[\da-fA-F:]+)?)", result)
        for address in ipv6_addresses:
            # 排除链路本地地址
            if not address.startswith("fe80::"):
                return address  # 返回第一个非链路本地的IPv6地址
    except Exception as e:
        logging.error(f"Error getting IPv6 address: {e}")
    return None


def post_up_requests(hostname, token):
    ipv6_address = get_primary_ipv6_address()
    print(f"ipv6地址:{ipv6_address}")
    logging.info(f"ipv6地址:{ipv6_address}")
    if ipv6_address is None:
        logging.error("未能获取IPv6地址")
        return False

    try:
        result = dns.resolver.resolve(hostname, 'AAAA')
        dns_address = str(result[0])
        logging.info(f"dns获取地址:{dns_address}")
    except Exception as e:
        logging.error(f"DNS查询出错: {e}")
        return False

    if dns_address == ipv6_address:
        logging.info("IP地址与DNS记录一致，不进行上传")
        return True

    proxies = {
        "http": None,
        "https": None
    }
    # get请求地址
    url = f'https://dynv6.com/api/update?hostname={hostname}&ipv6={ipv6_address}&token={token}'

    try:
        response = requests.get(url, proxies=proxies)
        logging.info(f"响应代码{response.status_code}\n返回值{response.text}")
        if response.status_code == 200 and response.text == "addresses updated":
            logging.info("响应和返回值正确，IP已更新")
            return True
        else:
            logging.error("响应或返回值错误等待重试")
            return False
    except Exception as e:
        logging.error(f"Error making request: {e}")
        return False


if __name__ == '__main__':
    # 生成锁文件
    lock_file_path = make_lock_file()

    try:
        while True:
            up_ipv6 = post_up_requests(your_domain, your_token)
            if up_ipv6:
                logging.info(f"{your_domain}记录更新成功！将在一小时后再次检查")
                time.sleep(3600)
            else:
                logging.info(f"{your_domain}更新失败！将在一分钟后重试")
                time.sleep(300)
    finally:
        # 程序正常或异常退出时，都尝试删除锁文件
        if os.path.exists(lock_file_path):
            os.remove(lock_file_path)
            print(f"锁文件已删除")
