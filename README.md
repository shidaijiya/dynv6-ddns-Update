# ReadMe: Python Dynv6 IPv6 Address Updater 
## 简介 / Overview
该Python脚本用于自动更新Dynv6域名的IPv6地址。脚本会定期检查系统的当前IPv6地址，并与Dynv6 DNS记录进行对比，如果不同则更新DNS记录。

This Python script automatically updates the IPv6 address for a Dynv6 domain. It regularly checks the system's current IPv6 address and compares it with the Dynv6 DNS record. If they are different, it updates the DNS record.

## 功能 / Features
- **文件锁机制**：防止多个脚本实例同时运行。
  
  **Locking Mechanism**: Prevents multiple instances of the script from running.
  
- **IPv6地址检测**：获取系统的主要IPv6地址，排除链路本地地址 (`fe80::`)。

  **IPv6 Detection**: Retrieves the system’s primary IPv6 address, excluding link-local addresses (`fe80::`).
  
- **DNS查询**：获取域名的当前IPv6 DNS记录。

  **DNS Query**: Fetches the current IPv6 DNS record for the domain.
  
- **API请求**：将新的IPv6地址更新到Dynv6。

  **API Request**: Updates the IPv6 address to Dynv6 if needed.

- **日志记录**：记录脚本的运行状态和结果。

  **Logging**: Logs the script's running status and results.

## 依赖 / Requirements
安装以下Python库：

Install the following Python libraries:

```bash
pip install psutil portalocker dnspython requests
```

## 配置 / Configuration
在脚本中设置以下两个参数：

Set the following two parameters in the script:

```python
your_token = '你的token'  # Dynv6 API Token
your_domain = '你的域名'  # Your Domain
```

## 运行 / Running the Script
在命令行运行脚本：

Run the script from the command line:

```bash
python script_name.py
```

## 日志 / Logs
日志文件保存在 `log/` 目录中，文件名为当前时间戳。

Log files are saved in the `log/` directory, with the filename based on the current timestamp.

## 示例日志 / Example Log Output
```
2024-10-19 12:00:00 INFO: 当前实例正在运行
2024-10-19 12:00:05 INFO: ipv6地址: 2001:db8::1
2024-10-19 12:00:10 INFO: dns获取地址: 2001:db8::2
2024-10-19 12:00:15 INFO: 响应代码200
2024-10-19 12:00:15 INFO: 返回值addresses updated
```

## 注意 / Notes
- 该脚本为Windows系统设计，获取IPv6地址时使用`ipconfig`命令。若在Linux或macOS使用，请调整相关部分代码。

  This script is designed for Windows systems, using the `ipconfig` command to get the IPv6 address. For Linux or macOS, adjust the relevant code.

