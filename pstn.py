# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import requests

from helpers import params_filter
from settings import Config

'''
腾讯 pstn 通讯平台接口

statusFlag 状态参数:

主叫发起呼叫状态：1      被叫发起呼叫状态：256
主叫响铃状态：2          被叫响铃状态：512
主叫接听状态：4          被叫接听状态：1024
主叫拒绝接听状态：8      被叫拒绝接听状态：2048
主叫正常挂机状态：16     被叫正常挂机状态：4096
主叫呼叫异常：32         被叫呼叫异常：8192

    例如：
    值为0：表示所有状态不需要推送
    值为4：表示只要推送主叫接听状态
    值为16191：表示所有状态都需要推送(上面所有值和)
'''

ID = Config.PSTN_ID
APPID = Config.PSTN_APPID
PSTN_HOST = Config.PSTN_HOST
CDR_NOTIFY_URL = Config.PSTN_CDR_NOTIFY_URL
STATUS_NOTIFY_URL = Config.PSTN_STATUS_NOTIFY_URL


HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json;charset=utf-8',
}


def get_response(url, params):
    data, _ = params_filter(params)
    resp = requests.post(url, json=data, headers=HEADERS)
    return resp


def callback(req_id, from_mobile, to_mobile, biz_id='meet'):
    # 呼叫请求接口
    url = 'http://{host}/201511v3/callBack?id={id}'.format(host=PSTN_HOST, id=ID)
    params = {
        'appId': APPID,   # appid
        'requestId': req_id,  # 最大长度不超过48字节， 在后边回拨请求会用到
        'src': '0086%s' % from_mobile,    # 主叫号码 必须为11位手机号，前加0086
        'dst': '0086%s' % to_mobile,      # 被叫号码 必须为11位手机号，前加0086
        'srcDisplayNum': '',  # 主叫显400 号码（不填显被叫号码）
        'dstDisplayNum': '',  # 被叫显400 号码（不填显主叫号码）
        'record': '0',  # 是否录音，0不录 1 录
        'maxAllowTime': '60',  # 允许最大通话时间
        'statusFlag': 10280,   # 状态推送 具体参数见上文文档
        'statusUrl': STATUS_NOTIFY_URL,  # 状态回调通知地址
        'hangupUrl': CDR_NOTIFY_URL,     # 话单回调通知地址
        'recordUrl': '',  # 录音url回调地址
        'bizId': biz_id,  # 业务应用key（只能包含数字字母）用于区分内部业务或产品
        'lastCallId': '',  # 最后一次呼叫called 带上改字段后，平台会参考该callid分配线路，有限不分配该callid通话线路
    }
    return get_response(url, params)


def call_cancel(call_id):
    # 呼叫取消接口
    url = 'http://{host}/201511v3/callCancel?id={id}'.format(host=PSTN_HOST, id=ID)
    params = {
        'appId': APPID,     # appid
        'callId': call_id,  # 回拨请求响应中返回的callId
        # 0 不管通话状态直接拆线
        # 1 主叫响铃以后状态不拆线
        # 2 主叫接听以后状态不拆线
        # 3 被叫响铃以后状态不拆线
        # 4 被叫接听以后状态不拆线
        'cancelFlag': 0
    }
    return get_response(url, params)


def get_status(call_id):
    # 通话状态获取接口
    url = 'http://{host}/201511v3/getStatus?id={id}'.format(host=PSTN_HOST, id=ID)
    params = {
        'appId': APPID,     # appid
        'callId': call_id,  # 回拨请求响应中返回的callId
    }
    return get_response(url, params)


def get_cdr(call_id):
    # 话单获取接口
    url = 'http://{host}/201511v3/getCdr?id={id}'.format(host=PSTN_HOST, id=ID)
    params = {
        'appId': APPID,     # appid
        'callId': call_id,  # 回拨请求响应中返回的callId
    }
    return get_response(url, params)


if __name__ == '__main__':
    res_id = '123456'
    from_mobile, to_mobile = 'xxxxx', 'xxxxx'
    callback(res_id, from_mobile, to_mobile)
