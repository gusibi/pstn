#! -*- coding: utf-8 -*-
import requests

TIMEOUT = 2


def params_filter(params):
    # 过滤 值为 None 的参数
    # new_params = dict(filter(lambda item: item[1] is not None, d.items()))
    new_params = {k: v for k, v in params.items() if v is not None}
    return new_params


class ClientError(Exception):

    def __init__(self, code, description):
        self.code = code
        self.description = description

    def __str__(self):
        return '%s: %s' % (self.code, self.description)


class VirtualNum:

    def __init__(self, appid, host):
        self.appid = appid
        self.host = host

    def prepare_request(self, method, path, params):
        _params = {
            'appid': self.appid
        }
        params.update(_params)
        params = params_filter(params)
        url = 'http://{host}{path}'.format(host=self.host, path=path)
        return method, url, params

    def make_request(self, method, url, json_body):
        headers = {
            'Host': 'pstn.avc.qcloud.com',
            'Accept': 'application/json;',
            'Content-Type': 'application/json;charset=utf-8;',
            # 'Content-Length' requests 会自动加上
        }
        req = requests.request(method, url, headers=headers, json=json_body,
                               timeout=(TIMEOUT, TIMEOUT))
        result = req.josn
        error_code = result['errorCode']
        if error_code != '0':  # error_code == 0 成功
            raise ClientError(error_code, result['msg'])
        return result

    def get_num(self, dst, src=None, request_id=None, accredit_list=None,
                assign_vitual_num=None, callee_display_num=None, record=0,
                city_id=None, biz_id=None, status_flag=16191,
                max_allow_time=30, max_assign_time=24*3600,
                status_url=None, hangup_url=None, record_url=None):
        '''直拨 PSTN 获取虚拟中间号（App 使用方发起）

        :params dst: 被叫号码
        :params src : 主叫号码
        :params request_id: session buffer，字符串最大长度不超过 48 字节，
                该 requestId 在后面回拨请求响应和回调中都会原样返回
        :params accredit_list: {“accreditList”:[“008613631686024”,”008612345678910”]}，
                主要用于 N-1 场景，号码绑定非共享是独占型，指定了 dst 独占中间号绑定,
                accreditList 表示这个列表成员可以拨打 dst 绑定的中间号，默认值为空，
                表示所有号码都可以拨打独占型中间号绑定，最大集合不允许超过 30 个
        :params assign_vitual_num: 指定中间号，如果该中间号已被使用返回绑定失败，
                如果不带该字段由腾讯侧从号码池里自动分配
        :params callee_display_num: 被叫显号，如果指定了该字段，被叫透传强显该号码，
                如果该字段为空，被叫默认显虚拟中间号
        :params record: 是否录音，0 表示不录音，1 表示录音。默认为不录音
        :params city_id: 主被叫号码归属地
        :params biz_id: 应用二级业务 ID，bizId 需保证在该 appId 下全局唯一，
                最大长度不超过 16 个字节。
        :params max_allow_time: 允许最大通话时间，不填默认为 30 分钟，单位分钟
        :params max_assign_time: 号码最大绑定时间，不填默认为 24 小时，单位秒
        :params status_url: 状态回调通知地址，正式环境可以配置默认推送地址
        :params hangup_url: 话单回调通知地址，正式环境可以配置默认推送地址
        :params record_url: 录单 URL 回调通知地址，正式环境可以配置默认推送地址
        :params status_flag: 主叫发起呼叫状态：1
                             被叫发起呼叫状态：256
                             主叫响铃状态：2
                             被叫响铃状态：512
                             主叫接听状态：4
                             被叫接听状态：1024
                             主叫拒绝接听状态：8
                             被叫拒绝接听状态：2048
                             主叫正常挂机状态：16
                             被叫正常挂机状态：4096
                             主叫呼叫异常：32
                             被叫呼叫异常：8192

                             例如：
                             值为 0：表示所有状态不需要推送
                             值为 4：表示只要推送主叫接听状态
                             值为 16191：表示所有状态都需要推送（上面所有值和）
        '''
        path = '/201511v3/getVirtualNum'
        params = {
            'dst': dst,
            'src': src,
            'requestId': request_id,
            'accreditList': accredit_list,
            'assignVirtualNum': assign_vitual_num,
            'calleeDisplayNum': callee_display_num,
            'record': record,
            'cityId': city_id,
            'bizId': biz_id,
            'maxAllowTime': max_allow_time,
            'maxAssignTime': max_assign_time,
            'statusFlag': status_flag,
            'statusUrl': status_url,
            'hangupUrl': hangup_url,
            'recordUrl': record_url,
        }
        method, url, json_body = self.prepare_request('POST', path, params)
        return self.make_request(method, url, json_body)

    def del_num(self, bind_id, request_id=None, biz_id=None):
        '''直拨 PSTN 解绑虚拟中间号（APP 使用方发起）
        :params bind_id: 双方号码 + 中间号绑定 ID，该 ID 全局唯一
        :params request_id: session buffer，字符串最大长度不超过 48 字节，
                该 requestId 在后面回拨请求响应和回调中都会原样返回
        :params biz_id: 应用二级业务 ID，bizId 需保证在该 appId 下全局唯一，
                最大长度不超过 16 个字节。
        '''
        path = '/201511v3/delVirtualNum'
        params = {
            'requestId': request_id
        }
        method, url, json_body = self.prepare_request('POST', path, params)
        return self.make_request(method, url, json_body)

    def get400cdr(self, call_id=None, src=None,
                  start_time_stamp=None, end_time_stamp=None, compress=0):
        '''直拨 PSTN 虚拟中间号话单获取
        :params call_id: 通话唯一标识 callId
        :params src: 查询主叫用户产生的呼叫话单，如填 0 表示拉取这个时间段所有话单
        :params start_time_stamp: 话单开始时间戳
        :params end_time_stamp: 话单结束时间戳
        :params compress: 是否压缩（0：不压缩 1：使用 zlib 压缩）默认不压缩
        '''
        path = '/201511v3/get400Cdr'
        params = {
            'callId': call_id,
            'src': src,
            'startTimeStamp': start_time_stamp,
            'endTimeStamp': end_time_stamp,
            'compress': compress,
        }
        method, url, json_body = self.prepare_request('POST', path, params)
        return self.make_request(method, url, json_body)
