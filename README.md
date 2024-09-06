# Data_Engineer_Intern_Online
## Task1
爬取PPT熱門看板的列表名稱與網址，例：列表名稱 Gossiping
網址 https://www.ptt.cc/bbs/Gossiping/index.html
### How to start
``` bash
python3 task1.py
```

## Task2
爬取八卦看板內 7 天內的貼文與留言
1. 貼文資料需包含作者、標題、發文時間、內文、類別
2. 留言資料需包含作者、發文時間、內文
3. 每則貼文與所屬留言存成一個檔案
### How to start
``` bash
python3 task2.py -o $output_dir // Default is ./ptt_articles
```

## Task3
爬取「古騰堡計劃」前兩百本中文電子書
網址：https://www.gutenberg.org/browse/languages/zh
每本書為一個檔案,檔案名稱為書名，每本書需抓取標題、作者、時間、內文。
### How to start
``` bash
python3 task3.py -o $output_dir // Default is ./gutenberg_books
```