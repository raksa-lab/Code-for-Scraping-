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

# Set up Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
service = Service("chromedriver.exe")  # Update with the actual path of chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define job ID range
start_id = 10580000
end_id = 10582000

# Define base URL format
base_url = "https://www.camhr.com/a/job/{}"

# Define columns to extract
columns = [
    "Job Title", "Level", "Year of Exp.", "Hiring", "Salary", "Sex", "Age",
    "Term", "Function", "Industry", "Qualification", "Language", "Location", "Job Requirements", "Link URL"
]

# CSV filename
csv_filename = "camhr_jobs.csv"

# Create CSV file if it doesn't exist
if not os.path.exists(csv_filename):
    with open(csv_filename, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(columns)

# Open CSV for appending
with open(csv_filename, mode="a", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)

    # Loop through job IDs
    for job_id in range(start_id, end_id + 1):
        url = base_url.format(job_id)
        driver.get(url)

        # ✅ WAIT for the table to be loaded
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mailTable"))
            )
        except:
            print(f"Skipping {url} (Table not found)")
            continue

        time.sleep(2)  # Allow more time for JS to render content

        # Parse page content
        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_info = {col: "Not found" for col in columns}  # Default values

        # ✅ Extract Job Title correctly
        job_title_span = soup.find("span", class_="job-name-span")
        job_info["Job Title"] = job_title_span.text.strip() if job_title_span else "Not found"

        # ✅ Extract job details from the table
        table = soup.find("table", class_="mailTable")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                headers = row.find_all("th", class_="column")
                data_cells = row.find_all("td")
                for header, data in zip(headers, data_cells):
                    key = header.text.strip()
                    value = data.text.strip()
                    # ✅ Match keys more flexibly
                    for column in columns:
                        if key.lower() in column.lower():
                            job_info[column] = value

        # ✅ Extract Job Requirements properly (only the "Job Requirements" section)
        job_descript_divs = soup.find_all("div", class_="job-descript")
        for div in job_descript_divs:
            title_span = div.find("span", class_="descript-title")
            if title_span and "Job Requirements" in title_span.text:
                job_info["Job Requirements"] = div.find("div", class_="fs-14 descript-list").get_text(separator="\n").strip()
                break  # Stop after finding the Job Requirements section

        # ✅ Add the job URL to the job_info dictionary
        job_info["Link URL"] = url

        # ✅ DEBUG: Print job data before writing
        print(f"Extracted Data for {job_id}:\n", job_info)

        # ✅ FIX: Ensure the correct order of data when writing to CSV
        row_data = [job_info.get(col, "Not found") for col in columns]
        writer.writerow(row_data)

        print(f"Scraped and saved data from {url}")

# Close browser
driver.quit()
print("All job data saved successfully to camhr_jobs.csv")
