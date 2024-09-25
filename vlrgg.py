
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Base URL for past matches on vlr.gg
base_url = 'https://www.vlr.gg/matches/results'

# Set up Selenium WebDriver
def setup_driver():
    options = webdriver.ChromeOptions()
    # Remove headless mode for debugging purposes
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Function to scrape match data from a specific page
def scrape_vlr_page(driver, url):
    results = []
    
    # Open the URL
    driver.get(url)
    
    # Wait for the page to fully load
    time.sleep(1)  # Adjust as needed depending on page load speed

    # Get page source and pass it to BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find the past match containers on the page
    match_containers = soup.find_all('a', class_='wf-module-item')

    for match in match_containers:
        try:
            # Extract match date and time
            date_element = match.find('div', class_='match-item-date')
            time_element = match.find('div', class_='match-item-time')

            match_date = date_element.text.strip() if date_element else "N/A"
            match_time = time_element.text.strip() if time_element else "N/A"

            # Extract team names
            teams = match.find_all('div', class_='text-of')
            if len(teams) < 2:
                continue  # Skip if team info is missing

            team1 = teams[0].text.strip()
            team2 = teams[1].text.strip()

            # Extract individual team scores from the correct div
            team1_score_element = match.find_all('div', class_='match-item-vs-team-score js-spoiler')[0]
            team2_score_element = match.find_all('div', class_='match-item-vs-team-score js-spoiler')[1]

            team1_score = team1_score_element.text.strip() if team1_score_element else "N/A"
            team2_score = team2_score_element.text.strip() if team2_score_element else "N/A"

            # Append data to results
            results.append({
                'team1': team1,
                'team2': team2,
                'team1_score': team1_score,
                'team2_score': team2_score,
                'match_date': match_date,
                'match_time': match_time
            })

        except Exception as e:
            print(f"Error processing a match: {e}")
            continue

    return results

# Function to scrape all pages (528 pages)
def scrape_all_pages():
    driver = setup_driver()
    all_results = []
    
    try:
        for page_num in range(1, 529):  # Looping through pages 1 to 528
            print(f"Scraping page {page_num}...")
            page_url = f"{base_url}?page={page_num}"
            page_results = scrape_vlr_page(driver, page_url)
            all_results.extend(page_results)
    
    finally:
        # Close the Selenium driver after all pages are scraped
        driver.quit()

    return all_results

# Scrape all pages and save to a CSV
all_match_data = scrape_all_pages()

if all_match_data:
    # Store the results in a pandas DataFrame
    df = pd.DataFrame(all_match_data)

    # Save the match data to a CSV file
    df.to_csv('vlr_all_match_results.csv', index=False)

    print(f"Scraped {len(df)} match results from 528 pages and saved to 'vlr_all_match_results.csv'")
else:
    print("No data scraped.")
