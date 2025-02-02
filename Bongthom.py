import requests
import csv
from bs4 import BeautifulSoup

# Base URL template with a placeholder for the job ID
base_url = "https://www.bongthom.com/job_detail/various_positions_{}.html"

# List of job IDs
job_ids = ["33379", "33074", "33385", "33372", "33365", "33364", "33368", "33366", "33363",
           "33361", "33358", "32922", "33349", "33348", "33346", "33344", "33342", "33338",
           "33336", "33334", "33333", "33328", "33330", "33326", "33325", "33322", "33305",
           "33319", "33312", "33313", "33308", "33301", "33298", "33292", "33287", "33289",
           "33290", "33261", "33280", "33269", "33257", "33255", "33254", "33251", "33249",
           "33247", "33235", "33246", "33244", "33234", "33233", "33210", "33224", "33219",
           "33195", "33192", "33157", "33167", "33158", "33160", "33161", "33156", "33147",
           "33152", "33149", "33148", "33140", "33142", "33132", "33134", "33126", "33125",
           "33122", "33113", "33108", "33109", "33110", "33089", "33083", "33084", "33054",
           "33046"]


# Function to scrape job details from a single URL
def scrape_job_details(job_id):
    job_url = base_url.format(job_id)  # Construct the job URL
    try:
        # Send a request to the webpage
        response = requests.get(job_url, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

        # Parse the page content
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract the company name
        company_name_tag = soup.find("a", class_="clearfix sub-title")
        company_name = company_name_tag.text.strip() if company_name_tag else "Not Found"

        # Remove the word "with" from the company name
        company_name = company_name.replace("with", "").strip()

        # Extract the job position title
        job_position_tag = soup.find("h3", class_="header-line no-margin")
        job_position = job_position_tag.text.strip().replace("Apply Now", "").strip() if job_position_tag else "Not Found"

        # Extract job details (category, type, location, schedule, salary)
        job_details = {}
        key_list = soup.find("ul", class_="key-list")
        if key_list:
            for li in key_list.find_all("li", class_="clearfix en"):
                key = li.find("strong", class_="key").text.strip().replace(":", "")
                value = li.find("span", class_="value").text.strip()
                job_details[key] = value

        # Extract the "Requirements" section
        requirements_header = soup.find("strong", class_="duty-req text-blue text-uppercase", string="Requirements")
        requirements = []
        if requirements_header:
            requirements_list = requirements_header.find_next("ul", class_="job-detail-req-mobile")
            if requirements_list:
                requirements = [li.text.strip() for li in requirements_list.find_all("li")]

        # Join requirements into a single string separated by " | "
        requirements_str = " | ".join(requirements)

        return {
            "Job Link": job_url,  # Add job URL to the data
            "Company": company_name,
            "Job Position": job_position,
            "Category": job_details.get("Category", "Not Found"),
            "Type": job_details.get("Type", "Not Found"),
            "Location": job_details.get("Location", "Not Found"),
            "Schedule": job_details.get("Schedule", "Not Found"),
            "Salary": job_details.get("Salary", "Not Found"),
            "Requirements": requirements_str
        }

    except requests.exceptions.RequestException as e:
        print(f"❌ Error scraping {job_url}: {e}")
        return None


# Save all job details to a CSV file
csv_filename = "This_night.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["Job Link", "Company", "Job Position", "Category", "Type", "Location", "Schedule", "Salary", "Requirements"])
    writer.writeheader()

    # Loop through each job ID and scrape job details
    for job_id in job_ids:
        print(f"Scraping job ID {job_id}...")
        job_details = scrape_job_details(job_id)
        if job_details:
            writer.writerow(job_details)

print(f"✅ Data scraped successfully and saved to {csv_filename}")
