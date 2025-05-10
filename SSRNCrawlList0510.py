## -------------------------
## Notes--CN Version
## 使用 selenium 包爬取 SSRN 里面的论文List
## 在爬取前需提前准备好之前爬取好的 SSRN Category List 文件，已经手动收集 Social Science 全部 Categories 保存在 Github 中的 Data 文件内
## -------------------------
## Notes — EN Version
## Use the selenium package to scrape papers list from SSRN.
## Before scraping, prepare the previously collected SSRN Category List files, which I have manually collected all social science Categories from SSRN and has stored in the Data folder on GitHub.
## -------------------------

import pandas as pd
import time
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm


## Remember to get your cURL info from SSRN website and then transform into cookies and headers (May not used except 'user-agent', and just for safety)
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    # 'cookie': 'MXP_TRACKINGID=F18B07EE-428C-4C46-AB5303CD87A073B3; mobileFormat=false; cfid=bffcc951-3934-4cc7-a32d-7591e81c0b74; cftoken=0; SITEID=en; perf_dv6Tr4n=1; OptanonAlertBoxClosed=2025-05-06T04:00:18.389Z; AMCVS_4D6368F454EC41940A4C98A6%40AdobeOrg=1; at_check=true; AMCV_4D6368F454EC41940A4C98A6%40AdobeOrg=-1124106680%7CMCMID%7C46587967469318301363724789803628467401%7CMCAAMLH-1747108823%7C3%7CMCAAMB-1747108823%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1746511223s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.2.0%7CMCIDTS%7C20215; _hjSessionUser_823431=eyJpZCI6IjBkMDBjMzZiLTU5MDktNWZiMy1hZGE3LWYwODE4MGJhYzAzMSIsImNyZWF0ZWQiOjE3NDY1MDQwMjM5NzMsImV4aXN0aW5nIjp0cnVlfQ==; __cf_bm=x_VLkn1ww3HSCNaHO69djPnFlyZbmvKrflJ1otlrte0-1746507949-1.0.1.1-gIE2l1XA6qybbNSeHhUs9f4joCCKqMmlK2MuxS6N8DcVL4xxOBm2ULZREm4ZlADSBFuvRR0LB2pwMozNNNpTISPZLjfkCp5F1xAc10jtSI8; _hjSession_823431=eyJpZCI6IjhmNGNjMWZiLTVmYmEtNDNjZC1hNzczLTUxMWU4NDdlYWVkNSIsImMiOjE3NDY1MDc5NTAxNDUsInMiOjEsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; OptanonConsent=isGpcEnabled=0&datestamp=Tue+May+06+2025+13%3A10%3A05+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202411.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=9f7b8d71-7128-493b-84fd-c210cec8e0e2&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=1%3A1%2C3%3A1%2C2%3A1%2C4%3A1&intType=1&geolocation=US%3BCA&AwaitingReconsent=false; mbox=PC#90ad07559fd94d7a865a0cb03396cddc.38_0#1809753006|session#78bfeddd761e48c8a450bda84de0f98d#1746509810; s_pers=%20v8%3D1746508205502%7C1841116205502%3B%20v8_s%3DLess%2520than%25201%2520day%7C1746510005502%3B%20c19%3Dss%253Ahomepage%7C1746510005503%3B%20v68%3D1746508204900%7C1746510005504%3B; s_sess=%20s_cpc%3D0%3B%20s_sq%3D%3B%20e41%3D1%3B%20s_cc%3Dtrue%3B%20s_ppvl%3Dss%25253Ahomepage%252C14%252C14%252C823%252C853%252C823%252C1512%252C982%252C2%252CP%3B%20s_ppv%3Dss%25253Asubject-network%25253Adecisionscirn%25253Aindex%252C6%252C6%252C823%252C853%252C823%252C1512%252C982%252C2%252CP%3B',
}


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(f"user-agent={headers['user-agent']}")


service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

input_path = '/Users/samxie/Research/SSRNCrawl/Data/SSRN_CateList.csv'
output_path = '/Users/samxie/Research/SSRNCrawl/Data/Paper_List.csv'
df_input = pd.read_csv(input_path)
write_header = True  

for index, row in tqdm(df_input.iterrows(), total=len(df_input), desc="Processing:", ncols=100):
    field, area, category, first_page_url = row['Field'], row['Area'], row['Category'], row['URL']
    print(f"Processing：{category}")
    page = 1
    stop_category = False
    max_page = float('inf')  

    while not stop_category:
        current_url = re.sub(r'page=\d+', f'page={page}', first_page_url)

        page_success = False
        for attempt in range(1, 4):
            try:
                driver.get(current_url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="network-papers"]/div[4]/ol/li[1]/div/div/div[1]/div[1]/a'))
                )
                page_success = True
                break
            except Exception as e:
                print(f"   第 {attempt} 次加载失败：{e}")
                time.sleep(2)

        if not page_success:
            print(f" {page} failed more then 3 times，skip this subcategory")
            break

        # Get max page from page one
        if page == 1:
            try:
                max_page_elem = driver.find_element(By.XPATH, '//*[@id="network-papers"]/div[2]/a[5]')
                max_page = int(max_page_elem.text.strip())
                print(f"最大页数：{max_page}")
            except:
                print("Max page not found，set 1 as default")
                max_page = 1

        if page > max_page:
            print(f"当前页 {page} 超过最大页 {max_page}，终止分类：{category}")
            break

        try:
            driver.find_element(By.XPATH, '//*[@id="network-papers"]/div[4]/ol/li[1]')
        except:
            print(f"第 {page} 页确实无论文，结束该分类翻页")
            break

        results_this_page = []

        for i in range(1, 51):
            try:
                title_xpath = f'//*[@id="network-papers"]/div[4]/ol/li[{i}]/div/div/div[1]/div[1]/a'
                title_elem = driver.find_element(By.XPATH, title_xpath)
                title = title_elem.text
                paper_url = title_elem.get_attribute("href")

                # Get paper posted time
                post_time = None
                time_xpaths = [
                    f'//*[@id="network-papers"]/div[4]/ol/li[{i}]/div/div/div[1]/div[2]/span[2]',
                    f'//*[@id="network-papers"]/div[4]/ol/li[{i}]/div/div/div[1]/div[3]/span[2]',
                    f'//*[@id="network-papers"]/div[4]/ol/li[{i}]/div/div/div[1]/div[3]/span',
                    f'//*[@id="network-papers"]/div[4]/ol/li[{i}]/div/div/div[1]/div[2]/span'
                ]
                for time_xpath in time_xpaths:
                    try:
                        time_elem = driver.find_element(By.XPATH, time_xpath)
                        post_time = driver.execute_script("""
                            let elem = arguments[0];
                            return elem.childNodes.length > 1 ? elem.childNodes[1].textContent.trim() : null;
                        """, time_elem)
                        if post_time:
                            break
                    except:
                        continue

                # if 2020, stop crawling this subcategory and go next one
                if post_time and post_time.strip()[-4:] == '2020':
                    print(f"Find paper in 2020，skip：{category}")
                    stop_category = True
                    break

                # See whether the post date meet our requirment
                try:
                    if not post_time:
                        raise ValueError("post_time is None or empty")
                    post_date = datetime.strptime(post_time.strip(), '%d %b %Y')
                    start_date = datetime(2021, 10, 1)
                    end_date = datetime(2023, 10, 31)

                    if start_date <= post_date <= end_date:
                        results_this_page.append({
                            'Field': field,
                            'Area': area,
                            'Category': category,
                            'URL': first_page_url,
                            'Title': title,
                            'PostTime': post_time,
                            'PaperURL': paper_url
                        })
                except Exception as e:
                    print(f"Fail：{post_time}，error：{e}，paper title：{title}")
                    continue

            except Exception as e:
                print(f"failed with no.{i} paper this page：{e}")
                continue

        if results_this_page:
            df_page = pd.DataFrame(results_this_page)
            df_page.to_csv(output_path, mode='a', index=False, header=write_header)
            write_header = False 

        print(f"{page} Done and save successfully")
        page += 1
        time.sleep(1)
        
driver.quit()
print(f"\nAll completed and saved in：{output_path}")
