# SSRN_PaperCrawl - updated 20250510

### ----------- CN Notes ---------------
#### 完整的工作流程为：
1. 手动收集需要爬取的论文领域的**子分类**：进入SSRN页面 https://papers.ssrn.com/sol3/DisplayJournalBrowse.cfm <br>
   - 手动收集得到的论文子分类的参考模板为 Data 文件中的 SSRN_CateList.csv <br>
   - 选择子分类这一步很关键，因为当论文页超过200时，SSRN将无法加载论文信息，例如某个领域有400页论文，201页虽然应该有论文，但是却无法加载也无法爬取！<br>
   - 选择子分类就是为了尽可能将每个分类待爬取的论文控制在200页以内 <br>
2. 根据 SSRN_CateList.csv 爬取完整的 paper list <br>
   - 具体而言，就是使用目录中的 SSRNCrawlList.py 读取 SSRN_CateList.csv，得到 Paper_List.csv <br>
   - 注意安装相应的包，提供合适的headers，修改读取路径 <br>
3. 根据 Paper_List.csv 爬取 Paper info 和 Author info <br>
   - 具体而言，就是使用目录中 SSRNCrawl0510.py 读取 Data/Paper_List.zip 解压得到的20个csv文件，得到 PaperInfo.csv, PaperInfo.json 和 AuthorInfo.json <br>
      - PaperInfo.csv 包含了论文页的基本信息 <br>
      - PaperInfo.json 包含了论文的Title，Abstract和Keywords <br>
      - AuthorInfo.json 包含了作者的信息，其中 PaperList 是作者过往所有paper组成的列表 <br>
   - 注意 SSRNCrawl0510.py 默认使用 crawl4ai 爬取，参考页面：https://docs.crawl4ai.com；若不兼容，请手动改为 request.get <br>
### ----------- EN Notes ---------------
#### Workflow Overview
1. **Manually collect the *sub-categories* within the research area you want to scrape**  
   - Go to the SSRN browse page: <https://papers.ssrn.com/sol3/DisplayJournalBrowse.cfm>  
   - Use the reference template **`SSRN_CateList.csv`** in the *Data* folder to record the sub-categories you pick.  
   - Choosing the right sub-categories is critical: once a paper list exceeds 200 pages, SSRN stops loading paper data (e.g., page 201 of a 400-page list is blank and cannot be scraped).  
   - The goal of sub-categorisation is therefore to keep each paper list under 200 pages whenever possible.

2. **Generate a complete paper list from `SSRN_CateList.csv`**  
   - Run **`SSRNCrawlList.py`** (found in the project folder). It reads `SSRN_CateList.csv` and outputs **`Paper_List.csv`**.  
   - Make sure to install the required libraries, set appropriate HTTP headers, and adjust the file paths to match your environment.

3. **Scrape *Paper info* and *Author info* from `Paper_List.csv`**  
   - Run **`SSRNCrawl0510.py`**, which reads the 20 CSV files extracted from `Data/Paper_List.zip` and produces:  
     - **`PaperInfo.csv`** – basic metadata from each paper page  
     - **`PaperInfo.json`** – paper *Title*, *Abstract*, and *Keywords*  
     - **`AuthorInfo.json`** – author details, where **`PaperList`** stores a list of all past papers by the author  
   - `SSRNCrawl0510.py` uses **crawl4ai** by default (docs: <https://docs.crawl4ai.com>). If crawl4ai is not compatible with your setup, replace its calls with `requests.get` and adjust the BeautifulSoup selectors accordingly.
