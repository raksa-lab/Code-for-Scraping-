import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import os
chrome_options = Options()
chrome_options.add_argument("--headless") 
service = Service("chromedriver.exe")  
driver = webdriver.Chrome(service=service, options=chrome_options)
start_id = 10580000
end_id = 10582000
base_url = "https://www.camhr.com/a/job/{}"
columns = [
    "Job Title", "Level", "Year of Exp.", "Hiring", "Salary", "Sex", "Age",
    "Term", "Function", "Industry", "Qualification", "Language", "Location", "Job Requirements", "Link URL"
]
csv_filename = "camhr_jobs.csv"
if not os.path.exists(csv_filename):
    with open(csv_filename, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
with open(csv_filename, mode="a", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    for job_id in range(start_id, end_id + 1):
        url = base_url.format(job_id)
        driver.get(url)
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mailTable"))
            )
        except:
            print(f"Skipping {url} (Table not found)")
            continue
        time.sleep(2)  
        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_info = {col: "Not found" for col in columns}  
        job_title_span = soup.find("span", class_="job-name-span")
        job_info["Job Title"] = job_title_span.text.strip() if job_title_span else "Not found"
        table = soup.find("table", class_="mailTable")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                headers = row.find_all("th", class_="column")
                data_cells = row.find_all("td")
                for header, data in zip(headers, data_cells):
                    key = header.text.strip()
                    value = data.text.strip()
                    for column in columns:
                        if key.lower() in column.lower():
                            job_info[column] = value
        job_descript_divs = soup.find_all("div", class_="job-descript")
        for div in job_descript_divs:
            title_span = div.find("span", class_="descript-title")
            if title_span and "Job Requirements" in title_span.text:
                job_info["Job Requirements"] = div.find("div", class_="fs-14 descript-list").get_text(separator="\n").strip()
                break  
        job_info["Link URL"] = url
        print(f"Extracted Data for {job_id}:\n", job_info)
        row_data = [job_info.get(col, "Not found") for col in columns]
        writer.writerow(row_data)
        print(f"Scraped and saved data from {url}")
driver.quit()
print("All job data saved successfully to camhr_jobs.csv")
