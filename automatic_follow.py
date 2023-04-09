import csv
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

def automatic_follow(csv_file):

    file_contents = csv_file.getvalue().decode("utf-8").splitlines()

    reader = csv.reader(file_contents)
    for row in reader:
        username = row[0]

    username = "animatedmovieslist"
    password = "r5zJFFUd-3JPAxW"

    driver = webdriver.Edge()

    driver.get("https://www.instagram.com/accounts/login/")

    time.sleep(3)

    for i in range(5):
        try:
            username_input = driver.find_element(By.NAME, "username")
            password_input = driver.find_element(By.NAME, "password")
            username_input.send_keys(username)
            password_input.send_keys(password)
            password_input.send_keys(Keys.ENTER)
            break
        except:
            time.sleep(1)

    time.sleep(10)

    # Read the CSV file and follow each user
    try:
        for row in reader:
            user_url = row[16]
            driver.get(user_url)
            time.sleep(3)
            follow_button = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div[1]/button")
            follow_button.click()
            time.sleep(2)
    except Exception as e:
        print(e)
        input("Enter any key to exit")

    # Close the Chrome driver
    driver.quit()
