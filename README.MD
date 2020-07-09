# 斗鱼弹幕机器人
基于selenium python3实现的斗鱼弹幕自动回复机器人。

## 安装
#### 克隆项目至本地：
``

#### 安装环境：
`pip3 install -Ur requirements.txt`

#### 下载ChromeDriver驱动
弹幕的发送由seleium实现，因此你需要下载对应的[浏览器驱动](http://npm.taobao.org/mirrors/chromedriver/)（推荐谷歌，其他浏览器暂未测试），并替换至  `DouyuDanmuRobot/driver/` 目录下。


## 配置
#### 注册图灵机器人账户（可选）
你需要注册至[图灵机器人](http://www.tuling123.com/sso-web/register)，并将你的 `apiKey` 及 `userID` 替换至 `tuling.py` 文件中。
不进行替换或许也能正常运行，但每日使用次数受到平台限制。


##### 配置弹幕过滤条件及黑名单
修改 `tuling.py` 中的全局变量。

## 运行
- 弹幕机器人
执行： ` python3 danmu_robot.py`

- 弹幕发送器
执行： ` python3 sender.py`

- 弹幕爬取
执行： ` python3 crawler.py`

