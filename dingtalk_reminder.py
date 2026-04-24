# -*- coding: utf-8 -*-
"""
钉钉待办备忘录推送脚本
使用方式：
1. 本地运行：python dingtalk_reminder.py
2. 部署到 Render 后：
   - https://你的应用.onrender.com/          # 管理界面
   - https://你的应用.onrender.com/send       # 推送到钉钉
"""

from flask import Flask, request, jsonify, render_template_string, redirect
import os
import requests

app = Flask(__name__)

# 钉钉 Webhook URL（从钉钉群机器人设置中获取）
DINGTALK_WEBHOOK = os.environ.get("DINGTALK_WEBHOOK", "")

# 待办文件路径
TODO_FILE = os.path.join(os.path.dirname(__file__), "todo.txt")


def read_todo_list():
    """读取待办事项列表"""
    if not os.path.exists(TODO_FILE):
        return []

    with open(TODO_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines


def write_todo_list(todo_list):
    """写入待办事项列表"""
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        for item in todo_list:
            f.write(item + "\n")


def build_dingtalk_message(todo_list):
    """构建钉钉消息"""
    if not todo_list:
        return {
            "msgtype": "text",
            "text": {"content": "📋 待办备忘录：\n暂无待办事项！"}
        }

    content = "📋 待办备忘录\n\n"
    for i, item in enumerate(todo_list, 1):
        content += f"{i}. {item}\n"

    return {
        "msgtype": "text",
        "text": {"content": content}
    }


def send_to_dingtalk(message):
    """发送消息到钉钉"""
    if not DINGTALK_WEBHOOK:
        return False, "钉钉 Webhook 未配置，请联系管理员"

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


# HTML 模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>待办备忘录</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { text-align: center; color: #333; margin-bottom: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .todo-item { display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #eee; }
        .todo-item:last-child { border-bottom: none; }
        .todo-num { color: #999; font-size: 14px; width: 30px; }
        .todo-content { flex: 1; color: #333; }
        .todo-delete { color: #ff4d4f; cursor: pointer; text-decoration: none; font-size: 14px; }
        .todo-delete:hover { color: #ff7875; }
        .empty { text-align: center; color: #999; padding: 40px; }
        .btn { display: inline-block; padding: 10px 20px; background: #1890ff; color: white; text-decoration: none; border-radius: 4px; border: none; cursor: pointer; font-size: 14px; }
        .btn:hover { background: #40a9ff; }
        .btn-send { background: #52c41a; }
        .btn-send:hover { background: #73d13d; }
        .btn-danger { background: #ff4d4f; }
        .btn-danger:hover { background: #ff7875; }
        .form-group { display: flex; gap: 10px; margin-bottom: 15px; }
        .form-group input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        .actions { display: flex; gap: 10px; margin-top: 20px; }
        .message { padding: 10px; border-radius: 4px; margin-top: 10px; }
        .message.success { background: #f6ffed; border: 1px solid #b7eb8f; color: #52c41a; }
        .message.error { background: #fff2f0; border: 1px solid #ffccc7; color: #ff4d4f; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 待办备忘录</h1>

        <div class="card">
            <form action="/add" method="get">
                <div class="form-group">
                    <input type="text" name="content" placeholder="输入新待办事项，按回车添加" required>
                </div>
            </form>

            {% if message %}
            <div class="message {{ message_type }}">{{ message }}</div>
            {% endif %}
        </div>

        <div class="card">
            {% if todo_list %}
            {% for i, item in enumerate(todo_list) %}
            <div class="todo-item">
                <span class="todo-num">{{ i + 1 }}.</span>
                <span class="todo-content">{{ item }}</span>
                <a href="/delete?index={{ i }}" class="todo-delete" onclick="return confirm('确定删除？')">删除</a>
            </div>
            {% endfor %}
            {% else %}
            <div class="empty">暂无待办事项</div>
            {% endif %}
        </div>

        <div class="actions">
            <a href="/send" class="btn btn-send">📤 推送到钉钉群</a>
            <a href="/clear" class="btn btn-danger" onclick="return confirm('确定清空所有待办？')">🗑️ 清空</a>
        </div>
    </div>
</body>
</html>
'''


@app.route("/")
def index():
    """首页 - 显示待办列表"""
    message = request.args.get("message", "")
    message_type = request.args.get("type", "")
    todo_list = read_todo_list()
    return render_template_string(HTML_TEMPLATE, todo_list=todo_list, message=message, message_type=message_type, enumerate=enumerate)


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
        return index()

    todo_list = read_todo_list()
    todo_list.append(content)
    write_todo_list(todo_list)

    return index()


@app.route("/delete")
def delete_todo():
    """删除单个待办"""
    index_str = request.args.get("index", "")
    try:
        idx = int(index_str)
    except:
        idx = -1

    todo_list = read_todo_list()
    if 0 <= idx < len(todo_list):
        deleted = todo_list.pop(idx)
        write_todo_list(todo_list)
        return redirect("/?message=已删除：{}&type=success".format(deleted))
    else:
        return redirect("/?message=删除失败：索引无效&type=error")


@app.route("/clear")
def clear_todo():
    """清空待办列表"""
    write_todo_list([])
    return redirect("/?message=已清空所有待办&type=success")


@app.route("/list")
def list_todo():
    """获取待办列表（JSON）"""
    todo_list = read_todo_list()
    return jsonify({"code": 0, "data": todo_list})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
