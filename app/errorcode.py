# -*- coding:utf-8 -*-
UNAUTHORIZED        = 101
DUPLICATE           = 102
BAD_REQUEST         = 103
BAD_STATUS          = 104
OUT_OF_RANGE        = 105
TOKEN_ERROR         = 106
INVALID_USER        = 107
BAD_USER            = 108
NOT_LOGINED         = 109
DATABASE_ERROR      = 110
REQUEST_ERROR       = 111
INVALID_CERTS       = 112
NOT_FOUND           = 113
POLO_ERROR          = 114
HOSTNAME_ERROR      = 115
REQUEST_HTTP_ERROR  = 116
DNS_ACCESS_STATE_ERROR  = 117
INDUSTRY_ERROR  = 118
NS_RESOLVE_ERROR = 119
LOGIN_MAX_TIMES = 120
VERIFY_USER_ERROR = 121

BAD_REQUEST_FORMAT  = 1031
BAD_REQUEST_LENGTH  = 1032
BAD_REQUEST_USER    = 1033
BAD_REQUEST_MIRROR  = 1034
BAD_REQUEST_PHONE    = 1035
BAD_REQUEST_TIME    = 1036
BAD_REQUEST_WEBSITE = 1037
BAD_REQUEST_IP      = 1038
BAD_REQUEST_HOSTNAME = 1039
BAD_REQUEST_USER_CONFLICT = 1040

DUPLICATE_EMAIL     = 1021
DUPLICATE_USERNAME  = 1022
DUPLICATE_PHONE     = 1023


ErrorMsg = {
    UNAUTHORIZED:   u'未授权',
    DUPLICATE:      u'资源已存在',
    BAD_REQUEST:    u'提交数据错误',
    BAD_STATUS:     u'该子域名已被禁用',
    OUT_OF_RANGE:   u'超出最大使用数量',
    TOKEN_ERROR:    u'验证码错误',
    INVALID_USER:   u'用户名或密码错误',
    LOGIN_MAX_TIMES:u'用户登录错误次数过多，锁定30分钟',
    BAD_USER:       u'账号已禁用，请联系管理员',
    NOT_LOGINED:    u'未登录',
    DATABASE_ERROR: u'数据库操作错误',
    REQUEST_ERROR:  u'请求失败',
    INVALID_CERTS:  u'无效的证书',
    NOT_FOUND:      u'资源不存在',
    POLO_ERROR:     u'用户数据库错误',
    HOSTNAME_ERROR: u'域名解析错误',
    REQUEST_HTTP_ERROR: u'IP或域名HTTP访问失败',
    DNS_ACCESS_STATE_ERROR : u'子域名未接入',
    INDUSTRY_ERROR : u'行业不存在',
    NS_RESOLVE_ERROR : u'NS解析错误, 请检查是否存在网站未备案、不存在等原因',
    VERIFY_USER_ERROR: u'验证失败',

    BAD_REQUEST_FORMAT: u'参数格式错误',
    BAD_REQUEST_LENGTH: u'参数长度错误',
    BAD_REQUEST_MIRROR: u'无效的镜像配置',
    BAD_REQUEST_USER:   u'用户名与用户数据库不匹配',
    BAD_REQUEST_PHONE:  u'邮箱手机不匹配',
    BAD_REQUEST_TIME:   u'有效期错误',
    BAD_REQUEST_WEBSITE: u'无效的网站名',
    BAD_REQUEST_IP:       u'回源IP/域名不符合规范',
    BAD_REQUEST_HOSTNAME: u'主机名不符合规范',
    BAD_REQUEST_USER_CONFLICT: u'用户被占用',

    DUPLICATE_EMAIL:    u'邮箱已存在',
    DUPLICATE_PHONE:    u'手机号已存在',
    DUPLICATE_USERNAME: u'用户名已存在',
}


