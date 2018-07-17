## PSTN号码保护 Python SDK

> PSTN号码保护是专为解决用户手机号码（座机）泄露的融合通信解决方案，在提供优质通话服务的同时，隐藏真实号码，保护用户隐私，适用于网购、打车、求职、外卖等使用场景

支持 PSTN 回拨 和 小号直拨

[官方文档](https://cloud.tencent.com/document/product/610/12084)

参考代码:

```python
## appid host id 由腾讯分配
appid = '123'
host = 'pstn.cloud.com'
id = 1234
client = VirtualNum(appid, host, id)
num = client.get_num()
```
