import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import argparse

base_url = 'https://www.ptt.cc'
gossiping_url = f'{base_url}/bbs/Gossiping/index.html'
headers = {'User-Agent': 'Mozilla/5.0'}
cookies = {'over18': '1'}  # 繞過年齡驗證

# 定義時間範圍（過去 7 天）
today = datetime.now()
seven_days_ago = today - timedelta(days=7)

def get_soup(url):
    """發送 GET 請求並返回 BeautifulSoup 物件"""
    response = requests.get(url, headers=headers, cookies=cookies)
    return BeautifulSoup(response.text, 'html.parser')

def parse_article_page(url):
    """解析文章的內容，包括作者、標題、發文時間、內文和類別"""
    soup = get_soup(url)
    metadata = soup.find_all('span', class_='article-meta-value')
    if len(metadata) < 4:
        return None

    author = metadata[0].text
    title = metadata[2].text
    post_time_str = metadata[3].text
    post_time = datetime.strptime(post_time_str, '%a %b %d %H:%M:%S %Y')
    
    # 檢查是否超過 7 天
    if post_time < seven_days_ago:
        return None

    # 抓取內文和分類
    main_content = soup.find(id='main-content')
    content = main_content.text.split('--')[0].strip()
    category_tag = soup.find('span', class_='article-meta-tag', string='看板')
    category = category_tag.find_next_sibling('span').text if category_tag else "Unknown"

    # 抓取留言
    comments = []
    comment_blocks = soup.find_all('div', class_='push')
    
    for comment_block in comment_blocks:
        push_tag = comment_block.find('span', class_='push-tag').text.strip()
        push_user = comment_block.find('span', class_='push-userid').text.strip()
        push_content = comment_block.find('span', class_='push-content').text.strip(': ')
        push_time = comment_block.find('span', class_='push-ipdatetime').text.strip()
        comments.append({
            'tag': push_tag,
            'user': push_user,
            'content': push_content,
            'time': push_time
        })
    
    # 回傳文章及留言的資訊
    return {
        'author': author,
        'title': title,
        'post_time': post_time_str,
        'content': content,
        'category': category,
        'comments': comments
    }

def save_article_data(article_data, file_path):
    """將文章及留言存成檔案"""
    with open(file_path, 'w', encoding='utf-8') as f:
        # 儲存文章資訊
        f.write(f"作者: {article_data['author']}\n")
        f.write(f"標題: {article_data['title']}\n")
        f.write(f"發文時間: {article_data['post_time']}\n")
        f.write(f"類別: {article_data['category']}\n")
        f.write(f"內文:\n{article_data['content']}\n\n")
        f.write("留言:\n")
        # 儲存留言
        for comment in article_data['comments']:
            f.write(f"[{comment['tag']}] {comment['user']} ({comment['time']}): {comment['content']}\n")

def crawl_gossiping(output_dir):
    """爬取八卦板 7 天內的文章及留言，並存成檔案"""
    page_url = gossiping_url
    page_num = 1

    while True:
        soup = get_soup(page_url)
        articles = soup.find_all('div', class_='r-ent')

        for article in articles:
            title_tag = article.find('a')
            if title_tag:
                article_url = base_url + title_tag['href']
                article_data = parse_article_page(article_url)
                if article_data:
                    # 儲存檔案，檔名以文章標題與發文時間為名
                    safe_title = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', article_data['title'])
                    safe_timeline = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', article_data['post_time'])
                    file_name = f"{safe_title}_{safe_timeline}.txt"
                    file_path = os.path.join(output_dir, file_name)
                    save_article_data(article_data, file_path)

        # 檢查是否超過 7 天的文章，若超過則停止
        last_article = articles[-1]
        post_time_str = last_article.find('div', class_='date').text.strip()
        last_post_time = datetime.strptime(f"{today.year}/{post_time_str}", '%Y/%m/%d')
        if last_post_time < seven_days_ago:
            break

        # 爬取上一頁
        prev_page = soup.find('a', string='‹ 上頁')
        if prev_page:
            page_url = base_url + prev_page['href']
            page_num += 1
        else:
            break



if __name__ == "__main__":
    # 創建資料夾來儲存文章
    parser = argparse.ArgumentParser(description="Crawl PTT Gossiping posts and comments.")
    parser.add_argument('--output_dir', type=str, default='./ptt_posts', help="Directory to save post files.")
    
    args = parser.parse_args()
    
    # 建立輸出目錄
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    crawl_gossiping(args.output_dir)