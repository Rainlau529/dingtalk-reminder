# 钉钉待办备忘录

一个简单的待办备忘录系统，通过钉钉机器人推送到群聊。

## 文件说明

- `todo.txt` - 待办事项列表（每行一个）
- `dingtalk_reminder.py` - 主程序
- `requirements.txt` - Python 依赖
- `Procfile` - Render 部署配置

## 本地使用

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置钉钉 Webhook：
   - 打开钉钉群 → 设置 → 智能群助手 → 添加机器人
   - 选择「自定义」机器人
   - 复制 Webhook 地址

3. 设置环境变量：
```bash
# Windows
set DINGTALK_WEBHOOK=你的Webhook地址

# Linux/Mac
export DINGTALK_WEBHOOK=你的Webhook地址
```

4. 运行：
```bash
# 方式1：启动 Web 服务
python dingtalk_reminder.py

# 方式2：直接推送（无 Web 服务）
python dingtalk_reminder.py --send
```

## 部署到 Render

1. 创建 GitHub 仓库，上传所有文件
2. 登录 [Render](https://render.com/)
3. New → Web Service
4. 连接 GitHub 仓库
5. 配置环境变量：
   - 添加 `DINGTALK_WEBHOOK`，值为你的钉钉 Webhook 地址
6. Deploy Now

部署成功后访问：`https://你的应用.onrender.com/send`

## 接口说明

| 地址 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页，显示待办列表 |
| `/send` | GET | 推送到钉钉群 |
| `/add?content=内容` | GET | 添加待办 |
| `/clear` | GET | 清空待办 |
| `/list` | GET | 获取待办列表（JSON） |

## 待办格式

`todo.txt` 每行一个待办，例如：
```
1. 完成项目报告 - 张三 - 4月25日
2. 开会讨论方案 - 李四 - 4月26日
3. 提交报销单 - 王五 - 4月30日
```
