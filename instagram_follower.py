import csv
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import configparser
import instaloader
import json
import requests
from bs4 import BeautifulSoup
import datetime
import os

USER_CREDENTIALS_FILEPATH = "user_credentials.ini"

def click_follow_btn(driver):
    for i in range(5):
        try:
            follow_button = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div[1]/button")
            follow_button.click()
            time.sleep(2)
            print("Follow button clicked.")
            return True
        except Exception as e:
            print(e)
            print("Error clicking on follow button. Trying again....")

    return False

def read_csv_file(csv_file):
    try:
        file_contents = csv_file.getvalue().decode("utf-8").splitlines()
        reader = csv.reader(file_contents)
        next(reader)
        return reader
    except:
        raise Exception("Error reading CSV file.")
    

def read_credentials():
    try:
        config = configparser.ConfigParser()
        config.read(USER_CREDENTIALS_FILEPATH)
        username = config["DEFAULT"]["username"]
        password = config["DEFAULT"]["password"]
        return username, password
    except Exception as e:
        raise Exception(f"Error in {USER_CREDENTIALS_FILEPATH} file. Please check the file and try again. {e}")

def try_credentials(driver, username, password):
    for i in range(5):
        try:
            driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(5)
            username_input = driver.find_element(By.NAME, "username")
            password_input = driver.find_element(By.NAME, "password")
            username_input.send_keys(username)
            password_input.send_keys(password)
            time.sleep(2)
            password_input.send_keys(Keys.ENTER)
            break
        except:
            print("Trying to login again...")
    time.sleep(10)
    if driver.current_url == "https://www.instagram.com/accounts/login/":
        raise Exception("Invalid credentials. Please check your credentials and try again.")
    else:
        print("Login successful.")

def automatic_follow(csv_file, streamlit_obj):

    reader = read_csv_file(csv_file)

    driver = webdriver.Edge()

    username, password = read_credentials()

    try_credentials(driver, username, password)

    for row in reader:
        profile_url = row[16]
        driver.get(profile_url)
        time.sleep(3)
        
        if click_follow_btn(driver):
            streamlit_obj.success(f'{row[1]} followed successfully.')
        else:
            streamlit_obj.error(f'Error following {row[1]}.')

    driver.quit()


def extract_profile_data(profile_url):
    """Extracts the required information from an Instagram profile URL and returns it as a list"""

    # Create an instance of Instaloader class
    L = instaloader.Instaloader()

    # Retry up to 5 times in case of errors
    for i in range(5):
        try:
            # Load the profile metadata using the profile URL
            profile = instaloader.Profile.from_username(L.context, profile_url.split("/")[-1])

            # Extract the desired information from the profile
            user_id = str(profile.userid)
            username = str(profile.username)
            full_name = str(profile.full_name)
            followers_count = str(profile.followers)
            following_count = str(profile.followees)
            post_count = str(profile.mediacount)
            is_private = "YES" if profile.is_private else "NO"
            is_verified = "YES" if profile.is_verified else "NO"
            is_business = "YES" if profile.is_business_account else "NO"
            external_url = str(profile.external_url)
            biography = str(profile.biography)
            avatar_url = str(profile.profile_pic_url)

            # Use web scraping to extract additional information
            response = requests.get(profile_url)
            soup = BeautifulSoup(response.content, "html.parser")
            scripts = soup.find_all("script", type="application/ld+json")
            data = scripts[0].string
            json_data = json.loads(data)
            if "address" in json_data:
                city = str(json_data["address"]["addressLocality"])
                address = str(json_data["address"]["streetAddress"])
            else:
                city = ""
                address = ""
            if "email" in json_data:
                public_email = str(json_data["email"])
            else:
                public_email = ""
            if "telephone" in json_data:
                public_phone = str(json_data["telephone"])
            else:
                public_phone = ""

            # Return the extracted information as a list
            return [user_id, username, full_name, followers_count, following_count, post_count, public_email,
                    public_phone, city, address, is_private, is_verified, is_business, external_url, biography,
                    avatar_url, profile_url]

        except (instaloader.ProfileNotExistsException, requests.exceptions.RequestException) as e:
            # Retry after a short delay in case of errors
            print("Error occurred:", e)
            print("Retrying in 5 seconds...")
            time.sleep(5)

    # Return empty if the function fails after multiple retries
    return [] 


def information_extractor(st):
    # opening csv file 
    with open('data.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        # Skip the header row
        next(reader)
        
        headings = ["User Id","User Name","Full Name","Followers Count","Following Count","Post Count","Public Email","Public Phone","City","Address","Is Private","Is Verified","Is Business","External Url","Biography","Avatar Url","Profile Url"]
        table = st.table([headings])
        
        now = datetime.datetime.now()
        date_time_ = now.strftime("%Y%m%d%H%M%S%f")
        output_file_path = f'Extracted Data/{date_time_}.csv'
        
        if not os.path.exists("Extracted Data"):
            os.makedirs("Extracted Data")
        with open(output_file_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headings)

        for row in reader:
            profile_url = row[16]
            profile_data = extract_profile_data(profile_url)
            if profile_data:
                table.add_rows([profile_data])
                with open(output_file_path, "a", newline="", encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(profile_data)
            else:
                print("Error extracting data from profile:", profile_url)
