# WEB系统接口文档


[TOC]
#用户管理
##登录
| methond | url |
|:------: |:---:|
| POST | /api/account/login |
参数
```json
{
	"phone": "手机",
	"password": "密码"
}
```
返回
```json
{
   	"total": 总数,
	"items": [
		{
			"id": "序号",
			"name", "名字"
		},
		{
		   ...
		}
	]
}
```

##忘记密码验证
| methond | url |
|:------: |:---:|
| POST | /api/account/verify |
参数
```json
{
	"phone": "13800138000",
	"parent_phone": "1354",
	"study_country": "美国"
}
```
返回
```json
{
	"token": "xxxxxx"
}
```
```json
{
	"message": "返回消息",
	"status_code": 200
}
```

##修改密码
| methond | url |
|:------: |:---:|
| POST | /api/account/reset_password |
参数
```json
未登录时
{
	"token": "验证步骤的token",
	"password": "密码"
}

已登录时修改自己的密码
{
	"password": "密码"
}
```
返回
```json
{
	"message": "返回消息",
	"status_code": 200
}
```


##添加学生
| methond | url |
|:------: |:---:|
| POST | /api/account/add_student |
参数
```json
{
	"chinese_name": "中文名称",
	"english_name": "英文名称",
	"sexual": "性别， 可不填",   
	"location": "所在地",
	"age": "年龄， 可不填",
	"school": "学校",
	"grade": "年级",
	"study_country": "期望留学国家",
	"enrollment_time": "预计入学时间, 可不填",
	"major": "期望留学专业, 可不填",
	"course_name": "学习课程",
	"learn_range": "学习范围",
	"wechat": "微信",
	"phone": "手机号码",
	"parent_phone": "家长手机号码",
	"remark": "备注, 可不填"
}
```
返回
```json
{
	"message": "返回消息",
	"status_code": 200
}
```

##添加老师
| methond | url |
|:------: |:---:|
| POST | /api/account/add_teacher |
参数
```json
{
	"chinese_name": "中文名称",
	"english_name": "英文名称",
	"graduated": "毕业学校",   
	"major": "毕业专业",
	"country": "毕业国家",
	"phone": "手机号码",
	"wechat": "微信",
	"introduce": "个人简介",
	"success_case": "成功案例",
	"feature": "个人特色"
}
```
返回
```json
{
	"message": "返回消息",
	"status_code": 200
}
```

##上传头像(表单提交)
| methond | url |
|:------: |:---:|
| POST | /api/account/photo?user_id=1000 |
参数
```json
"file": 二进制图片 
```
返回
```json
{
	"message": "返回消息",
	"status_code": 200
}
```

##获取头像
| methond | url |
|:------: |:---:|
| GET | /api/account/photo?user_id=1000 |
返回
```json
二进制图片
```

##获取学生列表
| methond | url |
|:------: |:---:|
| GET | /api/account/students |
参数
```json
page:
page_size:
key: "姓名或手机"
```
返回
```json
  "items": [
    {
	  "id": 1001,
      "age": 18,
      "chinese_name": "中文名称",
      "course_name": "托福",
      "location": "成都",
      "phone": "13709065417",
      "school": "学校",
      "sexual": "男",
      "update_time": "2017-04-01 11:17:31"
    }
  ],
  "total": 1
```

##获取老师列表
| methond | url |
|:------: |:---:|
| GET | /api/account/teachers |
参数
```json
page:
page_size:
key: "姓名或手机"
```
返回
```json
  "items": [
    {
	  "id": 1001,
      "age": 18,
      "chinese_name": "中文名称",
      "course_name": "托福",
      "location": "成都",
      "phone": "13709065417",
      "school": "学校",
      "sexual": "男",
      "update_time": "2017-04-01 11:17:31"
    }
  ],
  "total": 1
```

##获取老师或学生详细信息
| methond | url |
|:------: |:---:|
| GET | /api/account/profile?user_id=1000 |
参数
```json
无
```
返回
```json
同添加学生/老师接口
```

##修改老师或学生详细信息
| methond | url |
|:------: |:---:|
| PUT | /api/account/profile?user_id=1000 |
参数
```json
同添加学生/老师接口
```
返回
```json
{
	"message": "返回消息",
	"status_code": 200
}
```

#归档
##学生归档
| methond | url |
|:------: |:---:|
| POST | /api/file?user_id=1001 |
参数
```json
{
	"admission_school": "录取学校",
	"admission_major": "录取专业, 可不填",
	"test1": "考试科目1",
	"score1": "科目1成绩",
	2,3,4,5考试科目和成绩可不填
}
```
返回
```json
{
	"message": "返回消息",
	"status_code": 200
}
```

##获取归档信息列表
| methond | url |
|:------: |:---:|
| GET | /api/file |
参数
```json
page:
page_size:
key: "姓名或手机"
```
返回
```json
同获取学生列表
```

##获取归档详细信息
| methond | url |
|:------: |:---:|
| GET | /api/file/profile?user_id=1001 |
参数
```json
无
```
返回
```json
{
	"chinese_name": "中文名称",
	"english_name": "英文名称",
	"sexual": "性别， 可不填",   
	"location": "所在地",
	"age": "年龄， 可不填",
	"school": "学校",
	"grade": "年级",
	"study_country": "期望留学国家",
	"enrollment_time": "预计入学时间, 可不填",
	"major": "期望留学专业, 可不填",
	"course_name": "学习课程",
	"learn_range": "学习范围",
	"wechat": "微信",
	"phone": "手机号码",
	"parent_phone": "家长手机号码",
	"admission_school": "录取学校",
	"admission_major": "录取专业",
	"test1": "考试科目1",
	"score1": "科目1成绩",
}
```