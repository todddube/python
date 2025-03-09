from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime

# Set up the Selenium webdriver (replace with your preferred browser driver)
driver = webdriver.Chrome()

# Log in to LinkedIn
driver.get("https://www.linkedin.com/login")
username = driver.find_element("id", "username")
password = driver.find_element("id", "password")
username.send_keys("your_username")
password.send_keys("your_password")
driver.find_element("xpath", "//button[@type='submit']").click()
time.sleep(5)  # Wait for login

# Navigate to the "My Network" page
# driver.get("https://www.linkedin.com/mynetwork/myconnections/")
driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
# driver.get("https://www.linkedin.com/mynetwork/import-contacts/saved-contacts/")
time.sleep(5)

# Scroll down to load all contacts (adjust the range as needed)
for _ in range(10):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

# Parse the page source with Beautiful Soup
soup = BeautifulSoup(driver.page_source, "html.parser")

# Extract contact information
contacts = soup.find_all("li", class_="mn-connection-card")
print(f"Total contacts found: {len(contacts)}")
for contact in contacts:
    name = contact.find("span", class_="mn-connection-card__name").text.strip()
    try:
        occupation = contact.find("span", class_="mn-connection-card__occupation").text.strip()
    except AttributeError:
        occupation = "No occupation"
    # Create output file with date in name
    output_filename = os.path.join(
        "/Users/todddube/Documents/GitHub/python/LinkedIn",
        f"contacts_{datetime.now().strftime('%Y%m%d')}.txt"
    )

    with open(output_filename, "a") as file:
        print(".", end="")
        file.write(f"Name: {name}, Occupation: {occupation}\n")
    # print(f"Name: {name}, Occupation: {occupation}")

# Close the browser
driver.quit()
