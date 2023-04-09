import csv
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import configparser

USER_CREDENTIALS_FILE = "user_credentials.ini"

def click_on_follow_button(driver):
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
        config.read(USER_CREDENTIALS_FILE)
        username = config["DEFAULT"]["username"]
        password = config["DEFAULT"]["password"]
        return username, password
    except Exception as e:
        raise Exception(f"Error in {USER_CREDENTIALS_FILE} file. Please check the file and try again. {e}")

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

def automatic_follow(csv_file):

    reader = read_csv_file(csv_file)

    driver = webdriver.Edge()

    username, password = read_credentials()

    try_credentials(driver, username, password)

    for row in reader:
        profile_url = row[16]
        driver.get(profile_url)
        time.sleep(3)
        click_on_follow_button(driver)

    driver.quit()


def information_extractor():
    pass