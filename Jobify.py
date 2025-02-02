from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time

# Set path to ChromeDriver (update if needed)
chrome_driver_path = "chromedriver.exe"  # Change to your path

# Configure Selenium WebDriver
service = Service(chrome_driver_path)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode (no UI)
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

# Open CSV file for storing scraped data
with open("job4.csv", "w", encoding="utf-8", newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Job Title", "Job Link", "Salary", "Job Type", "Job Level", "Gender", "Age",
                     "Years of Experience", "Language", "Category", "Industry", "Location", "Qualification",
                     "Available Position", "Required Skills", "Job Requirement"])

    # Open browser once for efficiency
    driver = webdriver.Chrome(service=service, options=options)

    # Loop through job IDs
    for job_id in range(1031, 1000 , -1):
        url = f"https://jobify.works/jobs/{job_id}"
        print(f"Fetching {url}...")

        try:
            driver.get(url)
            time.sleep(2)  # Give time for content to load

            # Wait for job content to appear
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-title"))
            )

            # Parse page source with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Extract job title
            title_tag = soup.find("h3", class_="job-title")
            title = title_tag.text.strip() if title_tag else "N/A"

            # Function to extract job details based on the <strong> tag
            def get_job_detail(label):
                tag = soup.find("strong", string=label)
                if tag:
                    next_sibling = tag.find_next_sibling(text=True)
                    if next_sibling:
                        return next_sibling.strip().replace(",", "|")  # Prevent CSV issues
                    parent = tag.parent
                    if parent:
                        text = parent.get_text(strip=True).replace(label, "").strip()
                        return text.replace(",", "|")
                return "N/A"

            salary = get_job_detail("Salary:")
            job_type = get_job_detail("Job Type:")
            job_level = get_job_detail("Job Level:")
            gender = get_job_detail("Gender:")
            age = get_job_detail("Age:")
            experience = get_job_detail("Year of Experience:")
            language = get_job_detail("Language:")
            category = get_job_detail("Category:")
            industry = get_job_detail("Industry:")
            location = get_job_detail("Location:")
            qualification = get_job_detail("Qualification:")
            available_position = get_job_detail("Available Position:")
            required_skills = get_job_detail("Required Skills:")

            # ✅ Extract Job Requirement using BeautifulSoup
            job_requirement = "N/A"
            job_req_section = soup.find("h5", string="Job Requirement")
            if job_req_section:
                job_req_div = job_req_section.find_next("div", class_="text-dark")  # Find next <div> with requirements
                if job_req_div:
                    ul_tags = job_req_div.find_all("ul")  # Find all <ul> elements
                    li_texts = [li.text.strip() for ul in ul_tags for li in ul.find_all("li") if li.text.strip()]
                    job_requirement = " | ".join(li_texts) if li_texts else "N/A"

            print(f"Title: {title}, Job Requirement: {job_requirement}")


            # Write to CSV file
            writer.writerow([title, url, salary, job_type, job_level, gender, age, experience, language,
                             category, industry, location, qualification, available_position, required_skills,
                             job_requirement])

        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")

    driver.quit()  # Close browser
