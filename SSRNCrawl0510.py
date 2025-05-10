## -------------------------
## Notes--CN Version
## 使用 crawl4ai 包爬取 SSRN 里面的论文
## 需要先 pip install crawl4ai， 参考文档：https://docs.crawl4ai.com
## 若无法正常使用 crawl4ai，则使用 request 包的 request.get亦可完成任务，注意修改 soup 里提取的内容
## 在爬取前需提前准备好之前爬取好的 SSRN Paper List 文件，已经划分为20份保存在 Github 中的 Data 文件内
## -------------------------
## Notes — EN Version
## Use the crawl4ai package to scrape papers from SSRN.
## First run ’pip install crawl4ai‘; see the docs: https://docs.crawl4ai.com
## If crawl4ai does not work, you can fall back to ‘requests.get’, but make sure to adjust the BeautifulSoup selectors accordingly.
## Before scraping, prepare the previously collected **SSRN Paper List** files, which have been split into 20 parts and stored in the Data folder on GitHub.
## -------------------------

import pandas as pd
import os
import re
import json
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
from lxml import etree
import asyncio
from crawl4ai import AsyncWebCrawler
import nest_asyncio
nest_asyncio.apply()

async def cr4ai(inurl):
    ## -------------------------
    ## CN: 准备crawl4ai爬取，参考：https://docs.crawl4ai.com
    ## EN: Prepare crawl function with crawl4ai; see: https://docs.crawl4ai.com
    ## -------------------------
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=inurl)
        return result

def extract_abstract_id(url):
    ## -------------------------
    ## CN: 爬取paper的id
    ## EN: Get Paper id
    ## -------------------------
    match = re.search(r'abstract_id=(\d+)', url)
    return match.group(1) if match else url.strip('/').split('/')[-1]

def save_paper_info_to_csv(paper_info_list, csv_filename="Data/DS_PaperInfo.csv", json_filename="Data/DS_PaperText.json"):
    ## -------------------------
    ## CN: 保存 paper 信息为csv文件，其中paper title, Abstract和Keyword为json，注意保存路径为同路径下Data文件，可修改
    ## EN: Save paper information to a CSV file. The fields Paper Title, Abstract, 
    ##     and Keyword are written to a JSON file. Both outputs default to the **Data** sub-folder in the current directory.
    ## -------------------------
    paper_df = pd.DataFrame(paper_info_list)
    paper_df['AbstractID'] = paper_df['PaperURL'].apply(extract_abstract_id)

    text_data = paper_df[['AbstractID', 'Title_Scraped', 'Abstract', 'Keywords']].rename(
        columns={'Title_Scraped': 'Title', 'Keywords': 'Keyword'})
    text_records = text_data.to_dict(orient='records')

    if os.path.exists(json_filename):
        with open(json_filename, 'r+', encoding='utf-8') as f:
            existing = json.load(f)
            existing.extend(text_records)
            f.seek(0)
            json.dump(existing, f, ensure_ascii=False, indent=2)
    else:
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(text_records, f, ensure_ascii=False, indent=2)

    paper_df.rename(columns={'AuthorIDs': 'AuthorID', 'AuthorNames': 'Author', 'Institutions': 'Institution'}, inplace=True)
    csv_df = paper_df.drop(columns=['Abstract', 'Keywords', 'PaperURL'], errors='ignore')

    if not os.path.isfile(csv_filename):
        csv_df.to_csv(csv_filename, index=False)
    else:
        csv_df.to_csv(csv_filename, mode='a', header=False, index=False)


def save_author_info_to_json(author_info_list, filename="Data/DS_AuthorInfo.json"):
    ## -------------------------
    ## CN: 保存 author 信息为json文件，注意保存路径为同路径下Data文件，可修改
    ## EN: Save the author information to a JSON file. By default, it is written to the Data sub-folder in the current directory.
    ## -------------------------
    if not author_info_list:
        return

    author_dict = {}
    for author in author_info_list:
        author_id = author['id']
        if author_id not in author_dict:
            author_dict[author_id] = {
                'AuthorID': author_id,
                'Author': author['name'],
                'Affiliations': '; '.join(author['Affiliations']) if isinstance(author['Affiliations'], list) else author['Affiliations'],
                'ScholarlyPapers': author['ScholarlyPapers'],
                'TotalCitations': author['TotalCitations'],
                'AuthorPaper': []
            }

        cleaned_papers = []
        for p in author.get('AuthorPaper', []):
            cleaned = {
                'Title': p.get('TitleIn', ''),
                'Note': p.get('NoteList', ''),
                'AuthorName': p.get('AuthorName', ''),
                'Download': p.get('DownLoadNumIn', ''),
                'Citation': p.get('CitationNumIn', '')
            }
            cleaned_papers.append(cleaned)

        author_dict[author_id]['AuthorPaper'].extend(cleaned_papers)

    final_rows = list(author_dict.values())

    if os.path.exists(filename):
        with open(filename, 'r+', encoding='utf-8') as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []
            existing.extend(final_rows)
            f.seek(0)
            json.dump(existing, f, ensure_ascii=False, indent=2)
    else:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(final_rows, f, ensure_ascii=False, indent=2)

def parse_author_papers_from_soup(soup):
    ## -------------------------
    ## CN: 爬取 author 页的 paper 页信息
    ## EN: Crawl for info of papers in author page
    ## -------------------------
    papers = []
    paper_divs = soup.find_all("div", class_=lambda x: x and "trow" in x and "abs" in x)

    for div in paper_divs:
        title_tag = div.select_one("h3 a.title")
        title = title_tag.get_text(strip=True) if title_tag else None
        if not title:
            continue

        note_spans = div.select("div.note.note-list span")
        note_list = ", ".join(span.get_text(strip=True) for span in note_spans)

        authors_xpath = div.select_one("div.authors-list")
        if authors_xpath:
            author_links = authors_xpath.find_all("a")
            names = [a.get_text(strip=True) for a in author_links]
            tail_text = authors_xpath.get_text(separator=" ", strip=True)
            tail_text = re.sub(r'\s*and\s*', ',', tail_text)
            others = [x.strip() for x in re.split(r',\s*', tail_text) if x.strip() not in names]
            all_names = names + others
            all_names_cleaned = ', '.join(all_names)
        else:
            all_names_cleaned = None

        downloads_div = div.find("div", class_="downloads")
        if downloads_div:
            spans = downloads_div.find_all("span")
            download_val = spans[1].get_text(strip=True) if len(spans) >= 2 else ""
            extra_note = spans[2].get_text(strip=True).strip("()") if len(spans) >= 3 else ""
            downloads = f"{download_val}({extra_note})" if extra_note else download_val
        else:
            downloads = None

        citations_div = div.find("div", class_="citations")
        citation_span = citations_div.select_one("span a") if citations_div else None
        citation_num = citation_span.get_text(strip=True) if citation_span else None

        papers.append({
            "TitleIn": title,
            "NoteList": note_list,
            "AuthorName": all_names_cleaned,
            "DownLoadNumIn": downloads,
            "CitationNumIn": citation_num
        })

    return papers


def parse_author_profile(author_url, max_retries=5, max_wait=10):
    ## -------------------------
    ## CN: 爬取 author 页的页信息
    ## EN: Crawl for info of author page
    ## -------------------------
    affiliations, sch_paper_num, total_citations, papers = [], None, None, []

    for attempt in range(1, max_retries + 1):
        try:
            resp = asyncio.get_event_loop().run_until_complete(cr4ai(author_url))
            soup = BeautifulSoup(resp.html, 'html.parser')

            # 0. Waite for block-quote or h1
            for _ in range(max_wait):
                if soup.find("div", class_="block-quote") or soup.find("h1"):
                    break
                time.sleep(1)
                resp = asyncio.get_event_loop().run_until_complete(cr4ai(author_url))
                soup = BeautifulSoup(resp.html, 'html.parser')
            else:
                raise ValueError("No block-quote 或 h1")

            # 1. affiliations
            for block in soup.find_all("div", class_="block-quote"):
                org = block.find("h2")
                info_block = block.find("div", class_="info")
                role = info_block.find("h4").get_text(strip=True) if info_block and info_block.find("h4") else ''
                if org:
                    org_text = org.get_text(strip=True)
                    aff = f"{org_text}, {role}" if role else org_text
                    affiliations.append(aff)

            # 2. Scholarly Papers
            sch_label = soup.find("span", class_="lbl", string=re.compile("SCHOLARLY PAPERS", re.I))
            if sch_label:
                h1_tag = sch_label.find_next("h1")
                if h1_tag:
                    sch_paper_num = h1_tag.get_text(strip=True)

            # 3. Total Citations
            tree = etree.HTML(resp.html)
            citation_xpath = '//*[@id="maincontent"]/div/div/div[1]/div/div[3]/h1[3]/text()'
            citations = tree.xpath(citation_xpath)
            total_citations = citations[0].strip() if citations else None

            # 4. Get all Paper
            papers = parse_author_papers_from_soup(soup)

            break 

        except Exception as e:
            print(f"⚠️  {attempt} time(s) failed: {e}")
            time.sleep(2)

    return {
        "affiliations": affiliations,
        "scholarly_papers": sch_paper_num,
        "total_citations": total_citations,
        "papers": papers
    }

def parse_ssrn_paper(input_url, max_wait=3, max_retries=5):
    ## -------------------------
    ## CN: 爬取 paper 页的页信息
    ## EN: Crawl for info of paper page
    ## -------------------------
    paper_data = {
        'Title': None, 'PostTime': None, 'Abstract': None, 'Keywords': None,
        'AbstractViews': None, 'Downloads': None, 'Rank': None,
        'References': None, 'Citations': None, 'Authors': []
    }
    for attempt in range(1, max_retries + 1):
        try:
            for _ in range(max_wait):
                response = asyncio.get_event_loop().run_until_complete(cr4ai(input_url))
                html = etree.HTML(response.html)
                title = html.xpath('//*[@id="maincontent"]/div[3]/div[1]/div[1]/h1/text()')
                if not title:
                    title = html.xpath('//*[@id="maincontent"]/div[2]/div[3]/div[1]/div[1]/h1/text()')
                    if not title:
                        title = html.xpath('//*[@id="maincontent"]/div[3]/div[1]/div[2]/h1/text()')
                if title:
                    paper_data['Title'] = title[0].strip()
                    break
                time.sleep(1)
            else:
                raise ValueError("未找到标题") 
            
            # 1. Post Time
            post_time = html.xpath('//*[@id="maincontent"]/div[3]/div[1]/div[1]/p[1]/span[2]/text()')
            if not post_time:
                post_time = html.xpath('//*[@id="maincontent"]/div[2]/div[3]/div[1]/div[1]/p[1]/span[2]/text()')
            if not post_time:
                post_time = html.xpath('//*[@id="maincontent"]/div[3]/div[1]/div[2]/p[1]/span[2]/text()')
            if post_time and post_time[0].strip().startswith("Posted"):
                paper_data['PostTime'] = post_time[0].strip()
            else:
                paper_data['PostTime'] = 'N/A'
                
            soup = BeautifulSoup(response.html, 'html.parser')
            
            # 2. Keywords
            paths = [
                ('//*[@id="maincontent"]/div[3]/div[1]/div[1]/p[2]/text()', '//*[@id="maincontent"]/div[3]/div[1]/div[1]/p[3]/text()'),
                ('//*[@id="maincontent"]/div[2]/div[3]/div[1]/div[1]/p[2]/text()', '//*[@id="maincontent"]/div[2]/div[3]/div[1]/div[1]/p[3]/text()')
            ]
            keyword_candidate = ''
            for p2_path, p3_path in paths:
                p2 = html.xpath(p2_path)
                if p2 and not p2[0].strip().startswith("Date Written") and p2[0].strip():
                    keyword_candidate = p2[0].strip()
                    break
                p3 = html.xpath(p3_path)
                if p3 and p3[0].strip():
                    keyword_candidate = p3[0].strip()
                    break
            paper_data['Keywords'] = keyword_candidate or 'N/A'
            
            # 3. Abstract
            abstract = html.xpath('//*[@id="maincontent"]/div[3]/div[1]/div[1]/div[3]/p[1]/text()')
            if not abstract:
                abstract = html.xpath('//*[@id="maincontent"]/div[2]/div[3]/div[1]/div[1]/div[3]/p[1]/text()')
            if not abstract:
                abstract = html.xpath('//*[@id="maincontent"]/div[3]/div[1]/div[1]/div[4]/p[1]/text()')
            if not abstract:
                abstract = html.xpath('//*[@id="maincontent"]/div[3]/div[1]/div[2]/div[3]/p[1]/text()')
            paper_data['Abstract'] = abstract[0].strip() if abstract else 'N/A'
            
            # 4. Author -- Go into author page
            author_links = html.xpath('//*[@id="maincontent"]/div[3]/div[1]/div[1]/div[position() >= 2]//h2/a')
            if not author_links:
                author_links = html.xpath('//*[@id="maincontent"]/div[2]/div[3]/div[1]/div[1]/div[position() >= 2]//h2/a')
            if not author_links:
                author_links = html.xpath('//*[@id="maincontent"]/div[3]/div[1]/div[2]/div[position() >= 2]//h2/a')
            authors = []
            author_ids = []
            author_name_list = []
            institutions = []
            for a in author_links:
                name = a.text.strip() if a.text else 'N/A'
                link = a.attrib.get('href', '')
                match = re.search(r'per_id=(\d+)', link)
                author_id = match.group(1) if match else 'N/A'
                author_ids.append(author_id)
                author_name_list.append(name)
                author_info = parse_author_profile(link)
                institutions.extend(author_info.get('affiliations', []))
                authors.append({
                    'id': author_id,
                    'name': name,
                    'Affiliations': author_info.get('affiliations', []),
                    'ScholarlyPapers': author_info.get('scholarly_papers', 'N/A'),
                    'TotalCitations': author_info.get('total_citations', 'N/A'),
                    'AuthorPaper': author_info.get('papers', [])
                })
            paper_data['Authors'] = authors
            paper_data['AuthorIDs'] = ';'.join(author_ids)
            paper_data['AuthorNames'] = '; '.join(author_name_list)
            paper_data['Institutions'] = '; '.join(set(institutions)) or 'N/A'

            # 5. Stat info of Paper
            for stat in soup.find_all("div", class_="stat col-lg-4"):
                label = stat.find("div", class_="lbl")
                number = stat.find("div", class_="number")
                if label and number:
                    if "Abstract Views" in label.text:
                        paper_data['AbstractViews'] = number.text.strip()
                    elif "Downloads" in label.text:
                        paper_data['Downloads'] = number.text.strip()
                    elif "Rank" in label.text:
                        paper_data['Rank'] = number.text.strip()
            ref_tag = soup.find("a", href="#paper-references-widget")
            paper_data['References'] = ref_tag.find("span").text.strip() if ref_tag and ref_tag.find("span") else 'N/A'
            cit_tag = soup.find("a", href="#paper-citations-widget")
            paper_data['Citations'] = cit_tag.find("span").text.strip() if cit_tag and cit_tag.find("span") else 'N/A'

            break
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            time.sleep(2)

    return paper_data

def process_papers_from_csv(csv_file_path):
    ## -------------------------
    ## CN: 处理输入的 paper list csv文件
    ## EN: Process the input paper list csv
    ## -------------------------

    df = pd.read_csv(csv_file_path)
    if 'PaperURL' not in df.columns:
        print("'PaperURL' column not found in the CSV")
        return

    with tqdm(total=len(df), desc="Processing Papers", ncols=100) as pbar:
        for _, row in df.iterrows():
            paper_url = row['PaperURL']
            print(f"Processing: {paper_url}")
            try:
                paper_data = parse_ssrn_paper(paper_url)
                paper_info = {
                    'Field': row.get('Field', ''),
                    'Area': row.get('Area', ''),
                    'Category': row.get('Category', ''),
                    'Title': row.get('Title', ''),
                    'PostTime': row.get('PostTime', ''),
                    'PaperURL': paper_url,
                    'Title_Scraped': paper_data['Title'],
                    'PostTime_Scraped': paper_data['PostTime'],
                    'Abstract': paper_data['Abstract'],
                    'Keywords': paper_data['Keywords'],
                    'AbstractViews': paper_data['AbstractViews'],
                    'Downloads': paper_data['Downloads'],
                    'Rank': paper_data['Rank'],
                    'References': paper_data['References'],
                    'Citations': paper_data['Citations'],
                    'AuthorIDs': paper_data['AuthorIDs'],
                    'AuthorNames': paper_data['AuthorNames'],
                    'Institutions': paper_data['Institutions']
                }
                save_paper_info_to_csv([paper_info])
                save_author_info_to_json(paper_data['Authors'])
                print(f"✅ Done: {paper_url}")
            except Exception as e:
                print(f"Failed: {e}")
            pbar.update(1)

## Remember to put Paper_List_1 to Paper_List_20 into your input folder and adjust the path!!!!!
csv_file_path = "/Users/samxie/Research/SSRNCrawl/Data/Paper_List.csv"
process_papers_from_csv(csv_file_path)