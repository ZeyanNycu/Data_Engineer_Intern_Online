import requests
from bs4 import BeautifulSoup

def main():
    # PTT Gossiping 需要年齡認證，所以我們設定 cookies
    url = 'https://www.ptt.cc/bbs/Gossiping/index.html'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    cookies = {'over18': '1'}  # 表示已滿18歲

    # 發送請求
    response = requests.get(url, headers=headers, cookies=cookies)

    # 解析 HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # 抓取文章列表
    articles = soup.find_all('div', class_='r-ent')

    for article in articles:
        # 抓取文章標題
        title_tag = article.find('a')
        if title_tag:
            title = title_tag.text
            link = 'https://www.ptt.cc' + title_tag['href']
            print(f'標題: {title}')
            print(f'連結: {link}')
            print('---')

if __name__ == "__main__":
    main()