import os
import re
import datetime
import random
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import send_file
import zipfile
import io

app = Flask(__name__)
CORS(app)

FIXED_APPS = [
    "91视频", "台湾Swag", "Porn高清", "Pornbest", "Pornhub", "tiktok成人版",
    "50度灰", "黄瓜视频", "香蕉视频", "樱桃视频", "蜜桃视频", "幸福宝",
    "中国X站", "果冻传媒", "麻豆传媒", "天美传媒", "精东传媒", "大象传媒",
]

FIXED_URLS = [
    "最新在线地址", "入口地址发布页", "当前可用地址", "永久地址", "官方最新地址",
    "在线观看入口", "免费观看入口", "不用付费观看", "无广告在线播放", "高清视频免费看",
]

OUTPUT_FOLDER = "generated_markdown_files"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def log_error(msg):
    with open("error.log", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def sanitize_filename(text):
    return re.sub(r'[\\/*?:"<>|]', "_", text)

TEMPLATES = [
    """# {title}

✨ 欢迎访问 {app}{url} 官方导航页面！  
尊敬的用户，感谢您选择本站作为您的首选资源平台。本站致力于为您提供最快速、最稳定的访问体验，确保无论您身处何地，都能畅享优质内容。

关键词：{keywords_text}  
页面更新时间：{date}  

本站设有多个访问入口，保证即使部分链接受限，您依然可以通过其他镜像地址顺利访问：  
- 主入口：{domain}  
- 备用入口一：{domain}  
- 备用入口二：{domain}  

请您务必收藏本页或添加书签，以便随时访问最新内容。我们承诺持续更新维护，确保服务的稳定性与安全性。

────────────────────────────────────────────  
网络环境复杂多变，可能出现访问异常时，您可尝试以下方法恢复连接：  
- 刷新页面或重启浏览器  
- 清除浏览器缓存或切换浏览器  
- 使用隐私/无痕模式访问  
- 更换网络环境或使用VPN  
────────────────────────────────────────────

感谢您的理解与支持，祝您浏览愉快！""",

    """# {title}

🎉 欢迎来到 {app}{url} 专属资源导航！  
在这里，您将体验到最快速的访问速度和最丰富的内容资源。我们特别提供多个可用入口，助您跨越网络限制，稳定访问无忧。

关键词列表：{keywords_text}  
页面更新日期：{date}  

为保障您的访问体验，我们每日监测所有镜像地址，确保链接畅通无阻：  
- 主要访问地址：{domain}  
- 备用访问地址一：{domain}  
- 备用访问地址二：{domain}  

我们建议您保存所有入口，任何一个失效都能迅速切换，保障不中断访问。

────────────────────────────────────────────  
若您遇到访问困难，请尝试以下操作：  
- 刷新页面并检查网络连接  
- 清理浏览器缓存及Cookies  
- 启用隐私浏览模式  
- 更换或优化网络环境（例如使用VPN）  
────────────────────────────────────────────

本站严格保护用户隐私，无任何追踪和数据记录。感谢您的信任与支持！""",

    """# {title}

🔥 {app} + {url} 官方访问页面  
尊敬的用户您好，本站为您精心准备了多条访问通道，力求保障内容的持续可用性，帮助您轻松绕过各类网络限制。

相关关键词：{keywords_text}  
页面最新更新时间：{date}  

可用访问链接如下，建议收藏备用：  
- 主入口链接：{domain}  
- 镜像入口一：{domain}  
- 镜像入口二：{domain}  

无论您在任何设备或网络环境下，都可通过以上任意入口访问本站。

────────────────────────────────────────────  
如果出现访问不畅现象，建议您：  
- 检查本地网络设置  
- 切换不同网络或VPN  
- 清理浏览器缓存和Cookie  
- 使用隐私浏览功能  
────────────────────────────────────────────

我们持续关注用户反馈，不断优化访问质量。感谢您的支持与理解！""",

    """# {title}

💡 感谢访问 {app} 的 {url} 页面！  
本站专注于为您提供优质、稳定、快速的访问服务，多个访问地址每日更新检测，确保不因网络限制而中断您的浏览体验。

关键词包含：{keywords_text}  
页面更新日期：{date}  

当前可用入口（请收藏）：  
- 入口一：{domain}  
- 入口二：{domain}  
- 入口三：{domain}  

遇到访问问题时，可尝试刷新、切换浏览器或网络，或使用VPN辅助访问。

────────────────────────────────────────────  
隐私安全是我们的核心原则，本站不保存任何用户访问数据，确保您的信息安全无忧。

感谢您的关注与使用，祝您使用愉快！""",

    """# {title}

🌟 {app}{url} 官方资源导航站点  
欢迎访问本站，您将获得最佳的浏览体验和最新的资源内容。我们为用户精心准备了多条备用访问路径，保障您的访问始终顺畅。

相关关键词：{keywords_text}  
更新时间：{date}  

推荐访问链接（建议全部收藏）：  
- 主访问地址：{domain}  
- 备用地址一：{domain}  
- 备用地址二：{domain}  

为了确保顺利访问，您可以尝试更换网络环境，启用隐私模式，或使用VPN等工具。

────────────────────────────────────────────  
本站承诺：不追踪、不记录任何用户信息，保障您的上网安全与隐私。

谢谢您的支持与信赖！"""
]

def generate_md_content(app, url, keyword_list, suffix):
    title = f"{app}-{url}-{'-'.join(keyword_list)}-{suffix}"
    date_now = datetime.datetime.now().strftime("%Y-%m-%d")
    keywords_text = "，".join(keyword_list)
    subdomain = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=3))
    domain_link = f"https://{subdomain}.zaixianyule.top/"

    template = random.choice(TEMPLATES)
    content = template.format(
        title=title,
        app=app,
        url=url,
        keywords_text=keywords_text,
        suffix=suffix,
        date=date_now,
        domain=domain_link
    )
    return content

# Route test để kiểm tra server có hoạt động không
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"msg": "pong"})

# Route root trả về mã 200 và thông báo thân thiện
@app.route("/", methods=["GET"])
def root_home():
    return jsonify({"msg": "Welcome to the Flask API. Use /ping to test or /generate to create markdown files."}), 200

@app.route("/generate", methods=["POST"])
def generate_markdown_files():
    print("[INFO] /generate endpoint was called")   
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        keywords = data.get("keywords")
        cy = data.get("cy")

        if not keywords or not isinstance(keywords, list) or not all(isinstance(k, str) for k in keywords):
            return jsonify({"error": "Invalid or missing 'keywords' list"}), 400
        if not cy or not isinstance(cy, str):
            return jsonify({"error": "Invalid or missing 'cy' string"}), 400

        today_str = datetime.datetime.now().strftime("%m%d")
        suffix = f"{today_str}{cy}|881比鸭"

        used_filenames = set()
        created_files = []

        app_fixed = random.choice(FIXED_APPS)
        url_fixed = random.choice(FIXED_URLS)

        memory_zip = io.BytesIO()
        with zipfile.ZipFile(memory_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for keyword in keywords:
                safe_keyword = sanitize_filename(keyword)
                filename = f"{safe_keyword}.md"
                if filename in used_filenames:
                    base, ext = os.path.splitext(filename)
                    i = 2
                    while f"{base}_{i}{ext}" in used_filenames:
                        i += 1
                    filename = f"{base}_{i}{ext}"
                used_filenames.add(filename)

                other_keywords = random.sample(keywords, min(2, len(keywords)))
                if keyword not in other_keywords:
                    keyword_list = [keyword] + other_keywords
                else:
                    keyword_list = other_keywords

                content = generate_md_content(app_fixed, url_fixed, keyword_list, suffix)
                zf.writestr(filename, content)

                created_files.append(filename)

        memory_zip.seek(0)

        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        zip_filename = f"Tool-MARKDOWN-TCTL-PYC-{today_date}.zip"

        return send_file(
            memory_zip,
            as_attachment=True,
            download_name=zip_filename,
            mimetype="application/zip"
        )

    except Exception as e:
        err = f"Error: {e}\n{traceback.format_exc()}"
        log_error(err)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
