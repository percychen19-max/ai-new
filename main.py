import feedparser
import datetime
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from openai import OpenAI
import os

# 配置
SOURCES = {
    "English": [
        {"name": "Reddit ML", "url": "https://www.reddit.com/r/MachineLearning/.rss", "priority": 1},
        {"name": "Reddit Artificial", "url": "https://www.reddit.com/r/artificial/.rss", "priority": 1},
        {"name": "OpenAI News", "url": "https://openai.com/news/rss.xml", "priority": 3},
        {"name": "arXiv AI", "url": "https://arxiv.org/rss/cs.AI", "priority": 4},
    ],
    "Chinese": [
        {"name": "量子位", "url": "https://www.qbitai.com/feed", "priority": 2},
        {"name": "36Kr AI", "url": "https://36kr.com/feed", "priority": 2},
    ]
}

EMAIL_CONFIG = {
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "sender_email": "YOUR_QQ_EMAIL@qq.com", # 替换为您的 QQ 邮箱
    "password": "YOUR_AUTH_CODE",          # 替换为您生成的 16 位授权码
    "receiver_email": "YOUR_RECEIVER_EMAIL@qq.com" # 接收推送的邮箱
}

client = OpenAI()

def fetch_news():
    all_news = []
    now = datetime.datetime.now(datetime.timezone.utc)
    yesterday = now - datetime.timedelta(days=1)
    
    for lang, sources in SOURCES.items():
        for src in sources:
            print(f"Fetching {src['name']}...")
            feed = feedparser.parse(src['url'])
            for entry in feed.entries:
                published = getattr(entry, 'published_parsed', getattr(entry, 'updated_parsed', None))
                if published:
                    dt = datetime.datetime(*published[:6], tzinfo=datetime.timezone.utc)
                    if dt > yesterday:
                        all_news.append({
                            "title": entry.title,
                            "link": entry.link,
                            "lang": lang,
                            "source": src['name'],
                            "priority": src['priority'],
                            "summary": entry.get('summary', '')[:200]
                        })
    return all_news

def extract_hotspots(news_list):
    if not news_list:
        return "今日无重大AI资讯更新。"
    
    news_list.sort(key=lambda x: x['priority'])
    
    prompt = "以下是过去24小时内的AI资讯列表。请从中提取最热门、最重要的10条资讯。要求：\n"
    prompt += "1. 英文资讯需提供中英文对照标题和简要总结。\n"
    prompt += "2. 中文资讯直接总结。\n"
    prompt += "3. 严格控制在10条以内。\n"
    prompt += "4. 按照重要程度排序。\n\n资讯列表：\n"
    
    for i, news in enumerate(news_list[:50]):
        prompt += f"{i+1}. [{news['lang']}][{news['source']}] {news['title']}\nLink: {news['link']}\n"

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "你是一个专业的AI行业分析师，擅长从海量资讯中提取热点并进行双语总结。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def send_email(content):
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = formataddr((str(Header('percy的ai资讯收集助理', 'utf-8')), EMAIL_CONFIG['sender_email']))
    msg['To'] = EMAIL_CONFIG['receiver_email']
    msg['Subject'] = Header(f"每日AI热点资讯推送 - {datetime.date.today()}", 'utf-8')

    try:
        server = smtplib.SMTP_SSL(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['password'])
        server.sendmail(EMAIL_CONFIG['sender_email'], [EMAIL_CONFIG['receiver_email']], msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    news = fetch_news()
    hotspots = extract_hotspots(news)
    send_email(hotspots)
