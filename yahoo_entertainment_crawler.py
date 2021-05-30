import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as Soup

# yahoo娛樂連結
url = 'https://tw.news.yahoo.com/entertainment'

# 前 5 個文章的 xpaths
big_article_xpaths = ['//*[@id="Col1-1-Hero-Proxy"]/div/ul/li/a',
                      '//*[@id="Col1-2-CategoryWrapper-Proxy"]/div/div[1]/ul[1]/li/a',
                      '//*[@id="Col1-2-CategoryWrapper-Proxy"]/div/div[2]/ul[1]/li/a',
                      '//*[@id="Col1-3-CategoryWrapper-Proxy"]/div/div[1]/ul[1]/li/a',
                      '//*[@id="Col1-3-CategoryWrapper-Proxy"]/div/div[2]/ul[1]/li/a']
# 其餘文章的 xpaths
small_article_xpath = '//div[@class="Cf"]'


def get_news(article_url):
    # 取得指定 url 頁面內容
    content = requests.get(article_url).text
    soup = Soup(content, 'lxml')

    # 找到 title element (唯一)
    title_element = soup.find('h1', {'data-test-locator': 'headline'})

    # 確保有 title, 因為用 "small_article_xpath" 找到的 url 不見得皆是所想找的文章
    title = title_element.text if title_element else ''

    # 沒 title 就回傳空的資訊
    if not title:
        return {}

    # 嘗試找到第一張圖的 container
    img_container = soup.find('div', {'class': 'caas-img-container'})

    # 找得到就取其 url，反之空字串(如作業描述)
    img_url = img_container.findChild('img').get('src') if img_container else ''

    # 取所有文章內容(除了最後一個p element並非文章內文)並串接
    ps = soup.find('div', {'class': 'caas-body'}).find_all('p')[:-1]
    text_content = ''.join([p.text for p in ps])

    # 回傳作業所求資訊
    return {
        "title": title,
        "url": article_url,
        "yimg": img_url,
        "content": text_content
    }


# 如何執行此程式以抓取所求資訊？
# 於終端機執行如下指令
# python yahoo_entertainment_crawler.py
if __name__ == '__main__':
    driver = webdriver.Safari()

    # 所有 driver find 如果找不到 element 都會等5秒
    driver.implicitly_wait(5)

    # 最大化視窗
    driver.maximize_window()

    # 前往指定網頁(yahoo娛樂)
    driver.get(url)

    # 確保進入網頁(部分加載完畢)
    time.sleep(5)

    # 捲動條範圍
    start, end = 0, 50000

    # 測試結果 捲動 8 次可以將動態加載的部分全部加載完 (捲動至最底部)
    for i in range(8):
        # 捲動頁面
        driver.execute_script('window.scrollTo({}, {});'.format(start, end))
        end += 50000
        start = end
        time.sleep(2)

    # 完成全部頁面加載，含動態加載部分

    # 取得前 5 個 news 的 anchor element
    big_articles = [driver.find_element(By.XPATH, big_article_xpath)
                    for big_article_xpath in big_article_xpaths]
    # 取得剩餘 news 的 container element
    small_articles = driver.find_elements(By.XPATH, small_article_xpath)

    # 抓 anchor 的 attr: href 以得到 news 的 url
    big_urls = [element.get_attribute('href') for element in big_articles]
    small_urls = [element.find_element(By.TAG_NAME, 'a').get_attribute('href')
                  for element in small_articles]

    # 使用 get_news function 取得所求頁面資料
    articles = [get_news(url) for url in big_urls + small_urls]

    # 僅留下非空頁面資訊
    articles = [article for article in articles if article]

    driver.close()

    # 將 list of dict 存為 json
    with open('./static/yahoo-news.json', 'w') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
