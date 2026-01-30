# AI 每日资讯热点推送系统

这是一个基于 Python 的自动化系统，旨在每天聚合全球（中英文）AI 资讯，提取热点并通过邮件推送。

## 功能特点
- **多渠道聚合**：涵盖 Reddit、OpenAI 官方博客、arXiv 学术论文、量子位、36氪等。
- - **智能提取**：利用 GPT-4 模型自动筛选过去 24 小时内最热门的 10 条资讯。
  - - **中英双语**：英文资讯提供中英文对照标题及总结。
    - - **定时推送**：支持 Linux Crontab 定时任务，确保每天早上 10 点准时送达。
     
      - ## 部署步骤
     
      - ### 1. 环境准备
      - 确保系统已安装 Python 3.11+，并安装依赖库：
      - ```bash
        sudo pip3 install feedparser openai
        ```

        ### 2. 配置参数
        编辑 `main.py` 文件中的 `EMAIL_CONFIG` 部分：
        - `smtp_server`: 您的邮件服务 SMTP 地址（如 `smtp.qq.com`）。
        - - `sender_email`: 发件人邮箱。
          - - `password`: 邮箱授权码/应用密码（非登录密码）。
            - - `receiver_email`: 您的接收邮箱。
             
              - 同时确保环境变量 `OPENAI_API_KEY` 已设置。
             
              - ### 3. 设置定时任务
              - 使用 `crontab -e` 添加以下行（假设脚本路径为 `/home/yourpath/main.py`）：
              - ```bash
                # 每天北京时间 10:00 运行 (对应 UTC 02:00)
                0 2 * * * /usr/bin/python3 /home/yourpath/main.py >> /home/yourpath/ai_news.log 2>&1
                ```

                ## 优先级说明
                1. **社媒** (Reddit/HN)
                2. 2. **聚合社区** (36Kr/量子位)
                   3. 3. **官方博客** (OpenAI/DeepMind)
                      4. 4. **学术前沿** (arXiv)
                        
                         5. 
