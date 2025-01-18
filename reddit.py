import os
import requests
import requests_html
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import re

# Create a directory to save images
image_folder = 'images'
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# start sesission
session = HTMLSession()

# URL of the Reddit page
url = 'https://www.reddit.com/r/lingerie/'

# Headers to mimic a browser visit
headers = {'User-Agent': 'Mozilla/5.0'}

# Send a request to the Reddit page
response = session.get(url, headers=headers)    
response.html.render()
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.html.html, 'html.parser')

# Find all image tags
img_tags = soup.find_all('img')

# Download and save each image
for img in img_tags:
    print("###############", img.get('src'))
    img_url = img.get('src')
    if img_url:
        img_response = requests.get(img_url)
        ## img_name = os.path.join(image_folder, os.path.basename(img_url))
        # santize the image name
        img_name = os.path.join(image_folder, re.sub(r'[\\/*?:"<>|]', "", os.path.basename(img_url)))

        with open(img_name, 'wb') as f:
            f.write(img_response.content)

print("Images have been downloaded to the 'images' folder.")