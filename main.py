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
                                                                                                                                  import feedparser
import datetime
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from openai import OpenAI
import os
import asyncio
from playwright.async_api import async_playwright
import json

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
    "sender_email": "YOUR_QQ_EMAIL@qq.com",
    "password": "YOUR_AUTH_CODE",
    "receiver_email": "YOUR_RECEIVER_EMAIL@qq.com"
}

client = OpenAI()

async def fetch_douyin_hot():
    """抓取抖音实时热榜"""
    print("Fetching Douyin Hot List...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            await page.goto("https://www.douyin.com/hot", wait_until="load", timeout=90000)
            try:
                await page.wait_for_selector("//div[contains(@class, 'hot-list-container')]//li", timeout=30000)
            except:
                await page.wait_for_selector("text=热度", timeout=10000)
            
            hot_items = await page.query_selector_all("//div[contains(@class, 'hot-list-container')]//li")
            results = []
            for item in hot_items:
                text = await item.inner_text()
                if text:
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    if len(lines) >= 2:
                        title = lines[0] if not lines[0].isdigit() else lines[1]
                        results.append({
                            "title": title,
                            "hot_value": lines[-1],
                            "source": "抖音热榜"
                        })
            return results
        except Exception as e:
            print(`Error fetching Douyin: ${e}`)
            return []
        finally:
            await browser.close()

def fetch_news():
    all_news = []
    now = datetime.datetime.now(datetime.timezone.utc)
    yesterday = now - datetime.timedelta(days=1)
    
    for lang, sources in SOURCES.items():
        for src in sources:
            print(`Fetching ${src['name']}...`)
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

def extract_hotspots(news_list, douyin_list):
    if not news_list and not douyin_list:
        return "今日无重大AI资讯或抖音热点更新。"
    
    news_list.sort(key=lambda x: x['priority'])
    
    let prompt = "以下是过去24小时内的AI资讯列表以及抖音实时热榜。请从中提取最热门、最重要的10条资讯。要求：\n";
    prompt += "1. 英文资讯需提供中英文对照标题和简要总结。\n";
    prompt += "2. 中文资讯（包括抖音热点）直接总结。\n";
    prompt += "3. 抖音热点中，请优先提取与AI、科技、未来趋势相关的热点；如果没有明显的AI热点，可以提取1-2条最具代表性的社会/娱乐热点以丰富内容。\n";
    prompt += "4. 严格控制在10条以内。\n";
    prompt += "5. 按照重要程度排序。\n\n资讯列表：\n";
    
    for (let i = 0; i < Math.min(news_list.length, 40); i++) {
        const news = news_list[i];
        prompt += `${i+1}. [${news['lang']}][${news['source']}] ${news['title']}\nLink: ${news['link']}\n`;
    }
    
    prompt += "\n抖音热榜：\n";
    if (douyin_list) {
        for (let i = 0; i < Math.min(douyin_list.length, 30); i++) {
            const item = douyin_list[i];
            prompt += `${i+1}. [抖音][${item['source']}] ${item['title']} (热度: ${item['hot_value']})\n`;
        }
    }

    // Note: The rest of the Python code remains same, this JS just injects the text
    return prompt;
}
