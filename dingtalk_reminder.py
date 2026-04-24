# -*- coding: utf-8 -*-
"""
钉钉待办备忘录推送脚本
使用方式：
1. 本地运行：python dingtalk_reminder.py
2. 部署到 Render 后，访问 https://你的应用.onrender.com/send
"""

from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# 钉钉 Webhook URL（从钉钉群机器人设置中获取）
DINGTALK_WEBHOOK = os.environ.get("DINGTALK_WEBHOOK", "YOUR_DINGTALK_WEBHOOK_HERE")

# 待办文件路径
TODO_FILE = os.path.join(os.path.dirname(__file__), "todo.txt")


def read_todo_list():
    """读取待办事项列表"""
    if not os.path.exists(TODO_FILE):
        return []

    with open(TODO_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines


def build_dingtalk_message(todo_list):
    """构建钉钉消息"""
    if not todo_list:
        return {
            "msgtype": "text",
            "text": {"content": "📋 待办备忘录：\n暂无待办事项！"}
        }

    # 构建文字列表消息
    content = "📋 待办备忘录\n\n"
    for item in todo_list:
        content += f"• {item}\n"

    return {
        "msgtype": "text",
        "text": {"content": content}
    }


def send_to_dingtalk(message):
    """发送消息到钉钉"""
    if DINGTALK_WEBHOOK == "YOUR_DINGTALK_WEBHOOK_HERE":
        return False, "钉钉 Webhook 未配置"

    try:
        response = requests.post(
            DINGTALK_WEBHOOK,
            json=message,
            timeout=10
        )
        result = response.json()

        if result.get("errcode") == 0:
            return True, "发送成功"
        else:
            return False, f"发送失败：{result.get('errmsg', '未知错误')}"
    except Exception as e:
        return False, f"请求异常：{str(e)}"


@app.route("/")
def index():
    """首页 - 显示使用说明"""
    return """
    <html>
    <head><meta charset="utf-8"><title>钉钉待办备忘录</title></head>
    <body>
        <h2>📋 钉钉待办备忘录</h2>
        <p>当前待办列表：</p>
        <pre>{todo_list}</pre>
        <hr>
        <h3>操作</h3>
        <ul>
            <li><a href="/send">📤 推送到钉钉群</a></li>
            <li><a href="/add?content=新待办内容">➕ 添加待办</a></li>
            <li><a href="/clear">🗑️ 清空待办</a></li>
        </ul>
        <hr>
        <p><small>提示：修改 todo.txt 文件可自定义待办内容</small></p>
    </body>
    </html>
    """.format(todo_list="\n".join(read_todo_list()) or "(空)")


@app.route("/send")
def send():
    """推送待办到钉钉群"""
    todo_list = read_todo_list()
    message = build_dingtalk_message(todo_list)
    success, msg = send_to_dingtalk(message)

    if success:
        return jsonify({"code": 0, "message": msg})
    else:
        return jsonify({"code": -1, "message": msg}), 400


@app.route("/add")
def add_todo():
    """添加待办事项"""
    content = request.args.get("content", "").strip()
    if not content:
        return jsonify({"code": -1, "message": "待办内容不能为空"}), 400

    with open(TODO_FILE, "a", encoding="utf-8") as f:
        f.write(f"{content}\n")

    return jsonify({"code": 0, "message": f"已添加：{content}"})


@app.route("/clear")
def clear_todo():
    """清空待办列表"""
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        f.write("")
    return jsonify({"code": 0, "message": "已清空待办列表"})


@app.route("/list")
def list_todo():
    """获取待办列表"""
    todo_list = read_todo_list()
    return jsonify({"code": 0, "data": todo_list})


if __name__ == "__main__":
    # 本地测试时直接推送
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "--send":
        todo_list = read_todo_list()
        message = build_dingtalk_message(todo_list)
        success, msg = send_to_dingtalk(message)
        print(msg)
    else:
        # 启动 Web 服务
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port, debug=True)
