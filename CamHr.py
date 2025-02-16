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

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless") 

# Specify the correct path to chromedriver.exe
service = Service("chromedriver.exe")  

# Initialize the WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define the range of job IDs to scrape
start_id = 10595000
end_id = 10600000
base_url = "https://www.camhr.com/a/job/{}"

# Define the columns for the CSV file
columns = [
    "Job Title", "Company Name", "Level", "Year of Exp.", "Hiring", "Salary", "Sex", "Age",
    "Term", "Function", "Industry", "Qualification", "Language", "Location", "Job Requirements",
    "Publish Date", "Closing Date", "Link URL"
]  

# Define the CSV filename
csv_filename = "camhr_last_data.csv"

# Create the CSV file if it doesn't exist
if not os.path.exists(csv_filename):
    with open(csv_filename, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(columns)

# Open the CSV file in append mode
with open(csv_filename, mode="a", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    for job_id in range(start_id, end_id + 1):
        url = base_url.format(job_id)
        driver.get(url)
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-header-content"))
            )
        except:
            print(f"Skipping {url} (Page not loaded properly)")
            continue

        time.sleep(0.1)  

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Initialize a dictionary to store job information
        job_info = {col: "Not found" for col in columns}

        # Extract the job title
        job_title_span = soup.find("span", class_="job-name-span")
        job_info["Job Title"] = job_title_span.text.strip() if job_title_span else "Not found"

        # Extract the company name
        company_name_tag = soup.find("p", class_="mb-1 company-headbox")
        if company_name_tag:
            company_link = company_name_tag.find("a")
            job_info["Company Name"] = company_link.text.strip() if company_link else "Not found"

        # Extract job details from the table
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

        # Extract job requirements
        job_descript_divs = soup.find_all("div", class_="job-descript")
        for div in job_descript_divs:
            title_span = div.find("span", class_="descript-title")
            if title_span and "Job Requirements" in title_span.text:
                job_info["Job Requirements"] = div.find("div", class_="fs-14 descript-list").get_text(separator="\n").strip()
                break


        # Extract Publish Date and Closing Date (Fix for "Not found" issue)
        send_date_div = soup.find("div", class_="send-date")
        if send_date_div:
            date_spans = send_date_div.find_all("span")  # Get all span elements inside
            if len(date_spans) >= 2:
                job_info["Publish Date"] = date_spans[0].text.split(": ")[-1].strip()
                job_info["Closing Date"] = date_spans[1].text.split(": ")[-1].strip()
            else:
                job_info["Publish Date"] = "Not found"
                job_info["Closing Date"] = "Not found"

        # Add the job URL to the dictionary
        job_info["Link URL"] = url

        # Print the extracted data
        print(f"Extracted Data for {job_id}:\n", job_info)

        # Write the data to the CSV file
        row_data = [job_info.get(col, "Not found") for col in columns]
        writer.writerow(row_data)
        print(f"Scraped and saved data from {url}")

# Close the WebDriver
driver.quit()
print("All job data saved successfully to camhr_jobs_name.csv")
