# SSRN_PaperCrawl

### ----------- CN Notes ---------------
完整的工作流程为：
1. 进入SSRN页面 https://papers.ssrn.com/sol3/DisplayJournalBrowse.cfm，手动收集需要爬取的论文领域的**子分类**
   手动收集得到的论文子分类的参考模板为 Data 文件中的 SSRN_CateList.csv
   选择子分类这一步很关键，因为当论文页超过200时，SSRN将无法加载论文信息，例如某个领域有400页论文，201页虽然应该有论文，但是却无法加载也无法爬取！
   选择子分类就是为了尽可能将每个分类待爬取的论文控制在200页以内
2. 根据 SSRN_CateList.csv 爬取完整的 paper list
   具体而言，就是使用目录中的 SSRNCrawlList.py 读取 SSRN_CateList.csv，得到 Paper_List.csv
   注意安装相应的包，提供合适的headers，修改读取路径
3. 根据 Paper_List.csv 爬取 Paper info 和 Author info
   具体而言，就是使用目录中 SSRNCrawl0510.py 读取 Data/Paper_List.zip 解压得到的20个csv文件，得到 PaperInfo.csv, PaperInfo.json 和 AuthorInfo.json
   PaperInfo.csv 包含了论文页的基本信息
   PaperInfo.json 包含了论文的Title，Abstract和Keywords
   AuthorInfo.json 包含了作者的信息，其中 PaperList 是作者过往所有paper组成的列表
   注意 SSRNCrawl0510.py 默认使用 crawl4ai 爬取，参考页面：https://docs.crawl4ai.com；若不兼容，请手动改为 request.get
### ----------- EN Notes ---------------EN
