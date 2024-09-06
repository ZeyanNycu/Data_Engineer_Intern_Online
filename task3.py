import os
import requests
from bs4 import BeautifulSoup
import argparse

# 設定目標網站 URL
base_url = 'https://www.gutenberg.org'
zh_url = f'{base_url}/browse/languages/zh'
headers = {'User-Agent': 'Mozilla/5.0'}

# 發送請求並返回 BeautifulSoup 物件
def get_soup(url):
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.text, 'html.parser')

# 解析電子書的詳細頁面，抓取標題、作者、時間和內文
def parse_book_page(book_url):
    soup = get_soup(book_url)

    # 提取書名、作者、出版時間等基本信息
    title_tag = soup.find('h1')
    title = title_tag.text.strip() if title_tag else "Unknown"

    author_tag = soup.find('a', href=lambda href: href and 'author' in href)
    author = author_tag.text.strip() if author_tag else "Unknown"

    # 提取出版時間
    details = soup.find('table', class_='bibrec')
    time = "Unknown"
    if details:
        for row in details.find_all('tr'):
            if "Release Date" in row.text:
                time = row.find('td').text.strip()
                break

    # 查找可以下載的 txt 版本鏈接
    download_link = None
    link_tags = soup.find_all('a')
    for link in link_tags:
        if 'Plain Text' in link.text and '.txt' in link['href']:
            download_link = link['href']
            break

    # 如果找到了txt鏈接，下載內文
    content = ''
    if download_link:
        if not download_link.startswith('http'):
            download_link = base_url + download_link
        response = requests.get(download_link)
        content = response.text

    return {
        'title': title,
        'author': author,
        'time': time,
        'content': content
    }

# 保存書籍資料到文件
def save_book(book_data,output_dir):
    # 安全處理書名為檔案名
    safe_title = book_data['title'].replace('/', '_').replace('\\', '_')
    file_path = os.path.join(output_dir, f"{safe_title}.txt")

    # 儲存書名、作者、出版時間和內文
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"標題: {book_data['title']}\n")
        f.write(f"作者: {book_data['author']}\n")
        f.write(f"出版時間: {book_data['time']}\n\n")
        f.write("內文:\n")
        f.write(book_data['content'])

# 主函數：爬取前 200 本書籍
def crawl_gutenberg_books(output_dir):
    soup = get_soup(zh_url)

    # 抓取前 200 本書籍的鏈接
    book_links = []
    book_tags = soup.find_all('li')
    for tag in book_tags:
        link = tag.find('a', href=lambda href: href and 'ebooks' in href)
        if link:
            book_links.append(base_url + link['href'])
        if len(book_links) >= 200:
            break

    # 創建資料夾來存儲書籍
    if not os.path.exists('gutenberg_books'):
        os.makedirs('gutenberg_books')

    # 解析每本書籍的頁面並保存
    for book_url in book_links:
        print(f"正在爬取: {book_url}")
        book_data = parse_book_page(book_url)
        save_book(book_data,output_dir)

# 開始爬取
if __name__ == "__main__":
    # 創建資料夾來儲存文章
    parser = argparse.ArgumentParser(description="Crawl gutenberg books and comments.")
    parser.add_argument('--output_dir', type=str, default='./gutenberg_books', help="Directory to save post files.")
    
    args = parser.parse_args()
    
    # 建立輸出目錄
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    crawl_gutenberg_books(args.output_dir)