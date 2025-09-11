import random
from flask import Flask, jsonify
import requests
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# 从环境变量获取下游服务地址，如果未设置则使用默认的 GitHub API
# USER_API_URL = "http://localhost:8081/echo"
USER_API_URL = os.getenv("USER_API_URL", "https://api.github.com/users/apache")

@app.route("/")
def main_endpoint():
    """主入口，调用 /user 端点"""
    logging.info("主端点被调用，即将调用 /user 端点...")
    try:
        # 构造对 /user 端点的内部请求 URL
        # 在生产环境中，你可能需要更健壮的方式来确定主机和端口
        internal_user_url = "http://127.0.0.1:15000/user"
        response = requests.get(internal_user_url)
        response.raise_for_status()
        user_data = response.json()
        return jsonify({"status": "ok", "user_data": user_data})
    except requests.exceptions.RequestException as e:
        logging.error(f"调用 /user 端点失败: {e}")
        return jsonify({"error": f"调用 /user 端点失败: {e}"}), 500


@app.route("/user")
def get_user():
    """获取用户信息的端点，会发起一个外部 HTTP 请求"""
    logging.info(f"用户端点被调用，即将从 {USER_API_URL} 获取数据...")
    try:
        response = requests.get(USER_API_URL)
        import time
        time.sleep(random.uniform(0.5, 2.0))  # 模拟网络延迟
        response.raise_for_status()  # 如果请求失败 (状态码 4xx 或 5xx), 则抛出异常
        return {"status": "ok", "data": response.text}
    except requests.exceptions.RequestException as e:
        logging.error(f"从外部 API 获取数据失败: {e}")
        return jsonify({"error": f"从外部 API 获取数据失败: {e}"}), 500
    
@app.route("/error")
def error_endpoint():
    """一个故意触发错误的端点"""
    logging.info("错误端点被调用，触发异常...")
    try:
        # 故意触发一个异常
        1 / 0
    except ZeroDivisionError as e:
        logging.error(f"发生错误: {e}")
        return jsonify({"error": "发生错误: 除以零"}), 500
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=15000)