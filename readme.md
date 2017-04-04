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
	"course_name": "课程名字，多个用,分割",
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
	"feature": "个人特色",
	"show": true/false, 是否在师资力量列表中显示
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
show: true/false  是否只显示师资力量的老师, 默认为false
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

#历史学生
##添加历史学生
| methond | url |
|:------: |:---:|
| POST | /api/history?user_id=xxxx |
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
| GET | /api/history |
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
| GET | /api/history?user_id=xxx |
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

#课程表
##添加课程
| methond | url |
|:------: |:---:|
| POST | /api/coursetable |
参数
```json
{
  "course_name": "托福读",
  "teacher_user_id": 1002,
  "student_user_id": 1001,
  "day": 1,
  "start_time": "19:00",
  "stop_time": "21:00"
}
```
返回
```json
{
	"message": "返回消息",
	"status_code": 200
}
```

##更新课程
| methond | url |
|:------: |:---:|
| PUT | /api/coursetable?table_id=xxx |
参数
```json
{
  "course_name": "托福读",
  "teacher_user_id": 1002,
}
```
返回
```json
{
	"message": "返回消息",
	"status_code": 200
}
```

##删除课程
| methond | url |
|:------: |:---:|
| DELETE | /api/coursetable?table_id=xxx |
参数
```json
无
```
返回
```json
{
	"message": "返回消息",
	"status_code": 200
}
```

##获取空闲老师列表
| methond | url |
|:------: |:---:|
| GET | /api/coursetable/available_teacher？day=2&start_time=10:00&stop_time=12:00 |
参数
```json
无
```
返回
```json
[
  {
    "chinese": "中文名称",
    "id": 1006
  }
]
```

##获取课程列表用户索引
| methond | url |
|:------: |:---:|
| GET | /api/coursetable/students |
参数
```json
page:
page_size:
key: "姓名或手机"
```
返回
```json
{
	"total": 1,
	"items": [
	    {
		  "id": 1001,
	      "chinese_name": "",
	      "course_name": "学习课程",
	      "create_time": "注册时间",
	      "learn_range": "学习范围",
	      "location": "目前地址",
	      "phone": "",
	      "status": "使用中/未创建",
	      "study_country": "期望学校",
	      "update_time": "2017-04-01"
	    }
	]
}
```

##获取指定用户课程表
| methond | url |
|:------: |:---:|
| GET | /api/coursetable/tables?user_id=xxx |
参数
```json
无
```
返回
```json
[
  {
    "id": 6,
    "chinese_name": "中文名称",
    "course_name": "托福读",
    "day": 5,
    "start_time": "19:00",
    "stop_time": "21:00"
  }
]
```

#学习反馈
##添加学习反馈
| methond | url |
|:------: |:---:|
| POST | /api/feedback?user_id=xxxx |
参数
```json
{
	"chinese_name": "中文名",
	"study_date": "2017-05-05", 日期
	"class_time": "8:30-10:00", 上课时间
	"study_time": "8:00-11:00", 学习时间
	"course_name": "托福",       课程类型
	"section": "听 说 读 写",     授课范围
	"contents": "课程内容",
	"homework": "课后作业",
	"feedback": "课堂反馈"
}
```
返回
```json
{
	"message": "返回消息",
	"status_code": 200
}
```

##获取学习反馈用户索引
| methond | url |
|:------: |:---:|
| GET | /api/feedback?page=1&page_size=10 |
参数
```json
无
```
返回
```json
{
  "items": [
    {
      "chinese_name": "中文名称",
      "count": 1, 卡片数
      "course_name": "学习课程",
      "create_time": "注册时间",
      "id": 1005,
      "learn_range": "学习范围",
      "location": "目前地址",
      "phone": "",
      "school": "期望学校",
      "update_time": "2017-04-03"
    }
  ],
  "total": 1
}
```

##获取指定用户学习反馈
| methond | url |
|:------: |:---:|
| GET | /api/feedback?user_id=xxxx?page=1&page_size=10 |
参数
```json
无
```
返回
```json
{
  "items": [
    {
      "chinese_name": "中文名",
      "class_time": "8:30-10:00",
      "contents": "课程内容",
      "course_name": "托福",
      "feedback": "课堂反馈",
      "homework": "课后作业",
      "id": 1,
      "section": "听 说 读 写",
      "study_date": "2017-05-05",
      "study_time": "8:00-11:00"
    }
  ],
  "total": 1
}
```

##更新学习反馈
| methond | url |
|:------: |:---:|
| PUT | /api/feedback?fb_id=xxx |
参数
```json
无
```
返回
```json
{
	"message": "返回消息",
	"status_code": 200
}
```

##删除学习反馈
| methond | url |
|:------: |:---:|
| DELETE | /api/feedback?fb_id=xxx |
参数
```json
无
```
返回
```json
{
	"message": "返回消息",
	"status_code": 200
}
```

#成功案例
##添加案例
| methond | url |
|:------: |:---:|
| POST | /api/success_case |
参数
```json
{
  "chinese_name": "学生姓名",
  "tag": "雅思|托福|ACT|SAT",
  "school": "录取学校", 可选
  "feeling": "同学感悟",
  "comment", "老师点评",
  "test1": "考试科目1",
  "score1": "科目1成绩",
  ...
}
```
返回
```json
{
	"message": "返回消息",
	"status_code": 200
}
```

##修改案例
| methond | url |
|:------: |:---:|
| PUT | /api/success_case?case_id=xxx |
参数
```json
同上
```
返回
```json
{
	"message": "返回消息",
	"status_code": 200
}
```

##删除案例
| methond | url |
|:------: |:---:|
| DELETE | /api/success_case?case_id=xxx |
参数
```json
无
```
返回
```json
{
	"message": "返回消息",
	"status_code": 200
}
```

##获取案例
| methond | url |
|:------: |:---:|
| GET | /api/success_case?page=1&page_size=10 |
参数
```json
无
```
返回
```json
{
  "items": [
    {
      "chinese_name": "学生姓名",
      "id": 1,
      "school": "",
      "tag": "雅思",
      "update_time": "2017-04-04"
    }
  ],
  "total": 1
}
```

##获取案例详情
| methond | url |
|:------: |:---:|
| GET | /api/success_case?page=1&page_size=10 |
参数
```json
tag:
case_id:
```
返回
```json
{
  "items": [
    {
      "chinese_name": "学生姓名",
      "comment": "老师点评",
      "feeling": "同学感悟",
      "id": 1,
      "school": "",
      "score1": "科目1成绩",
      "score2": "",
      "score3": "",
      "tag": "雅思",
      "test1": "考试科目1",
      "test2": "",
      "test3": "",
      "update_time": "2017-04-04"
    }
  ],
  "total": 1
}
```