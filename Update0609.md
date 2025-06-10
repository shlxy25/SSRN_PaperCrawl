# SSRN_PaperCrawl_Modified - updated 20250609

#### 1. **`SSRN_CateList_0609.csv`**

主要更新内容如下：

- **链接结构问题：** 原始列表中部分链接在更改页码参数（如 page=1）后仍重复加载第
  一页内容，导致无法爬取多页数据，因此对这类链接进行了替换。
- **文章数量过多超过展示上限：** 某些分类文章数量超过 SSRN 网站的展示上限（200
  页），为确保数据完整性，已将此类类别替换为其更细分的子类别链接。
- **其他更新内容：**
  - `Anthropology & Archaeology Research Network` Anthropology & Archaeology
    Research Centers Papers 无链接，暂无法提取。
  - `Legal Scholarship Network` & `Financial Economics Network` 均包含名为
    Regulation of Financial Institutions eJournal 的子类别，为避免混淆，使用 LSN
    与 FEN 后缀区分。
  - SSRN 对每个类别最多展示 200 页内容，超出部分无法抓取，例如：
    https://www.ssrn.com/index.cfm/en/heliyon/?page=200&sort=0。 因此该链接只可
    提取部分内容，无法完整提取。

#### 2. **`SSRNCrawlList_0609.py`**

主要针对旧版代码无法提取总页数不足 5 页（或缺少分页导航）的链接，进行以下更新：

- **修改：关于页面加载逻辑**

  旧版

  ```python
  WebDriverWait(driver, 10).until(
     EC.presence_of_element_located((By.XPATH, '//*[@id="network-papers"]/div[4]/ol/li[1]/div/div/div[1]/div[1]/a'))
     )
  ```

  新版

  ```python
  WebDriverWait(driver, 10).until(
      lambda d: d.execute_script("return document.readyState") == "complete"
  )
  try:
      WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.ID, "network-papers"))
      )
  except TimeoutException:
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="papers-list"]'))
      )
  ```

- **修改：关于页码提取**

  旧版

  ```python
  max_page_elem = driver.find_element(By.XPATH, '//*[@id="network-papers"]/div[2]/a[5]')
  max_page = int(max_page_elem.text.strip())
  ```

  新版

  ```python
  page_links = driver.find_elements(By.XPATH, '//*[@id="network-papers"]//a')
  page_texts = [a.text for a in page_links]
  page_numbers = [int(a.text) for a in page_links if a.text.strip().isdigit()]
  max_page = max(page_numbers) if page_numbers else 1
  ```

- **修改：关于论文提取**

  旧版

  ```python
  for i in range(1, 51):
      try:
          title_xpath = f'//*[@id="network-papers"]/div[4]/ol/li[{i}]/div/div/div[1]/div[1]/a'
          title_elem = driver.find_element(By.XPATH, title_xpath)
  ```

  新版

  ```python
  papers = driver.find_elements(By.XPATH, '//*[@id="network-papers"]//ol/li')

  for i, paper in enumerate(papers):
      try:
          title_elem = paper.find_element(By.XPATH, './/div[@class="title"]/a')
  ```

- **修改：关于发布时间提取**

  旧版

  ```python
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
  ```

  新版

  ```python
  post_time = None
  try:
     post_time_elem = paper.find_element(By.XPATH, './/span[contains(text(), "Posted")]')
     post_time_raw = post_time_elem.text.strip()
     post_time = post_time_raw.replace("Posted", "").strip()
  ```

- **增加：报错记录**

  便于记录代码运行中的失败原因，便于后续核对和补充提取

  ```python
  failed_categories.append({
    'Field': field,
    'Area': area,
    'Category': category,
    'URL': current_url,
    'FailedPage': page,
    'PaperTitle': title,
    'Reason': f'Failed to extract post date: {e}'
  })
  ```

- **增加：自动保存提取结果和错误记录**

  ```python
  if all_results:
     df_all = pd.DataFrame(all_results)
     chunks = np.array_split(df_all, 1)
     for i, chunk in enumerate(chunks, start=1):
        chunk.to_csv(f"{output_path}/Paper_List_{i}.csv", index=False)

  print(f"\nAll completed and saved in：{output_path}")
  print(f"all_results length: {len(all_results)}")

  if failed_categories:
    df_failed = pd.DataFrame(failed_categories)
    df_failed.to_csv(f"{output_path}/Failed_List---.csv", index=False)
    print(f"\nSaved {len(failed_categories)} failed entries to Failed_List.csv")
  else:
    print("\nNo failures encountered.")
  ```

当前代码的问题：运行时可能会出现部分网页加载失败的问题，导致提取不完整，需要通过
报错记录查找未提取成功的链接，再进行单独尝试

#### 3. **`Comparison_0609.xlsx`**

对比最终抓取结果与原始 Paper_List 之间的差异，已标注在 Notes 列中，主要包括：

1.  替换为子类别的链接；
2.  原链接错误、缺失或页面跳转异常；
3.  某些 Category 出现在多个领域中，内容重复，已在 Notes 中标记为“重复”。
