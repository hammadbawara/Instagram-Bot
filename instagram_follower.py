import csv
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import configparser
import instaloader
import json
import os
import pickle
import dill
import re
import random
import datetime
import instagrapi


USER_CREDENTIALS_FILEPATH = "user_credentials.ini"
TEMP_DIR_NAME = "temp"
OUPUT_DATA_DIR_NAME = "OUTPUT"
FOLLOWED_COUNT_FILE = "followed_count.json"
FOLLOWED_COUNT_PATH = f'{TEMP_DIR_NAME}/{FOLLOWED_COUNT_FILE}'
SESSION_ID_FILE = f'{TEMP_DIR_NAME}/sessionid'
FOLLOW_LIMIT = 3

def followed_file_exists(csv_file_name):
    if os.path.isfile(f'{TEMP_DIR_NAME}/{csv_file_name}-temp'):
        return True
    else:
        return False

def get_number_of_followed(csv_file_name):
    try:
        with open(f'{TEMP_DIR_NAME}/{csv_file_name}-temp') as f:
            return int(f.read())
    except:
        return 0

def save_number_of_followed(csv_file_name, count):
    try:
        with open(f'{TEMP_DIR_NAME}/{csv_file_name}-temp', "w") as f:
            f.write(str(count))
    except:
        pass

def save_followed_count(count):
    """Saves the number of users followed today to a JSON file."""
    today = datetime.date.today().strftime("%Y-%m-%d")
    data = {}
    try:
        with open(FOLLOWED_COUNT_PATH, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        pass
    data[today] = count
    with open(FOLLOWED_COUNT_PATH, 'w') as f:
        json.dump(data, f)

def get_followed_count():
    """Gets the number of users followed today from the saved JSON file."""
    today = datetime.date.today().strftime("%Y-%m-%d")
    try:
        print("Followed count path", FOLLOWED_COUNT_PATH)
        with open(FOLLOWED_COUNT_PATH, 'r') as f:
            data = json.load(f)
            return data[today]
    except FileNotFoundError:
        return 0

def random_delay(lower_delay, upper_delay, placeholder):
    delay = random.randint(lower_delay, upper_delay)
    for i in range(delay):
        time.sleep(1)
        placeholder.text(f"Delay: {delay} sec.\nNext in {delay - i - 1}")
    placeholder.text("")

def click_follow_btn(driver):
    for i in range(5):
        try:
            follow_button = driver.find_element(By.XPATH,"/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div[1]/button")
            follow_button.click()
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
    if not os.path.isfile(USER_CREDENTIALS_FILEPATH):
        # CREATING FILE
        with open(USER_CREDENTIALS_FILEPATH, "w") as file:
            file.write("[DEFAULT]\n")
            file.write("username = \n")
            file.write("password = \n")
    try:
        config = configparser.ConfigParser()
        config.read(USER_CREDENTIALS_FILEPATH)
        username = config["DEFAULT"]["username"]
        password = config["DEFAULT"]["password"]
        if username == "" or password == "":
            raise Exception("Please enter your credentials in the file.")
        print("Credentials read successfully")
        return username, password
    except Exception as e:
        raise Exception(f"Error in {USER_CREDENTIALS_FILEPATH} file. Please check the file and try again. {e}")

def login_to_instagram(driver, username, password):
    print("Login to Instagram")
    for i in range(5):
        try:
            driver.get("https://www.instagram.com/accounts/login/")
            # wait for complete load
            driver.implicitly_wait(5)
            username_input = driver.find_element(By.NAME, "username")
            password_input = driver.find_element(By.NAME, "password")
            username_input.send_keys(username)
            password_input.send_keys(password)
            password_input.send_keys(Keys.ENTER)
            break
        except:
            print("Trying to login again...")
    time.sleep(10)
    if driver.current_url == "https://www.instagram.com/accounts/login/":
        raise Exception("Invalid credentials. Please check your credentials and try again.")
    else:
        print("Login successful.")

def automatic_follow(csv_file, streamlit_obj, upper_delay, lower_delay, continue_):
    followed_today = get_followed_count()
    if followed_today >= FOLLOW_LIMIT:
        streamlit_obj.error(f"You have reached today limit of following {FOLLOW_LIMIT} people. Try again tomorrow")
        return
    
    reader = read_csv_file(csv_file)

    driver = webdriver.Edge()

    username, password = read_credentials()

    delay_placeholder = streamlit_obj.empty()

    login_to_instagram(driver, username, password)

    count = 0

    if continue_:
        count = get_number_of_followed(csv_file.name)
        print(f"Continuing from the {count}")
        reader_iterator = reader.__iter__()
        for i in range(count):
            reader_iterator.__next__()
        print(f"Iterator value {reader_iterator}")
    else:
        reader_iterator = reader.__iter__()

    for row in reader_iterator:
        # check no of account followed today
        if followed_today >= FOLLOW_LIMIT:
            streamlit_obj.error(f"You have reached today limit of following {FOLLOW_LIMIT} people. Try again tomorrow")
            return
        profile_url = row[16]
        driver.get(profile_url)
        
        if click_follow_btn(driver):
            streamlit_obj.success(f'{row[1]} followed successfully.')
            followed_today += 1
            save_followed_count(followed_today)
        else:
            streamlit_obj.error(f'Error following {row[1]}.')

        count += 1
        save_number_of_followed(csv_file.name, count)
        # random delay
        random_delay(lower_delay, upper_delay, delay_placeholder)
        

    driver.quit()
    # Close the Chrome driver
    #driver.quit()
    

# --------------------------------------------------------------------------------------

def convert_json_to_cookie(json_cookie):
    cookies = json.load(json_cookie)
    # Convert cookies to Instaloader format
    insta_cookies = {}

    if not os.path.isdir(TEMP_DIR_NAME):
        os.mkdir(TEMP_DIR_NAME)
        
    for cookie in cookies:
        insta_cookies[cookie['name']] = cookie['value']
        if cookie.get('name') == 'sessionid':
            with open(SESSION_ID_FILE, 'w') as f:
                f.write(cookie['value'])

    with open(f'{TEMP_DIR_NAME}/cookie', 'wb') as f:
        pickle.dump(insta_cookies, f)

def is_extracted_file_exists(username):
    return os.path.exists(f'{OUPUT_DATA_DIR_NAME}/{username}.csv') and os.path.exists(f'{TEMP_DIR_NAME}/{username}-iterator')

def _extract_bio_info(bio_string):
    # Regular expressions to match patterns for public addresses, email addresses, cities, and addresses
    phone_number_regex_list = [
        "\+?\(?([0-9]{3})\)?[-.]?\(?([0-9]{3})\)?[-.]?\(?([0-9]{4})\)?",
        "\(?([0-9]{3})\)?([ .-]?)([0-9]{3})\2([0-9]{4})"
    ]
    email_regex = "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    city_regex = "^(\\d{1,}) [a-zA-Z0-9\\s]+(\\,)? [a-zA-Z]+(\\,)? [A-Z]{2} [0-9]{5,6}$"
    address_regex = "\d{1,3}.?\d{0,3}\s[a-zA-Z]{2,30}\s[a-zA-Z]{2,15}"

    # Find all matches for each pattern in the bio string
    for regex in phone_number_regex_list:
        phone_number = re.findall(regex, bio_string)
        if phone_number:
            phone_number = ''.join(phone_number[0])
            break
    emails = re.findall(email_regex, bio_string)
    email = ''
    if emails:
        email = emails[0]
    cities = re.findall(city_regex, bio_string)
    addresses = re.findall(address_regex, bio_string)

    # Return a dictionary containing the extracted information
    bio_info = {
                'phone_number': phone_number,
                'email': email,
                'city': cities,
                'address': addresses}
    return bio_info

def _extract_email_phone_number(instagrapi_cl, username):
    user_id = instagrapi_cl.user_id_from_username(username)
    user = instagrapi_cl.user_info(user_id)
    
    email = user.public_email
    phone_number = user.contact_phone_number
    city = user.city_name
    address = user.address_street
    
    return {
        "email": email, 
        "phone_number":phone_number, 
        "city":city, 
        "address":address
        }


def _get_follower_data(follower, streamlit_obj, instagrapi_client):
    while True:
        try:
            _id = follower.userid
            _username = follower.username
            _full_name = follower.full_name
            _follower_count = follower.followers
            _post_count = follower.mediacount
            _following_count = follower.followees
            _is_private = "Yes" if follower.is_private else "No"
            _is_verified = "Yes" if follower.is_verified else "No"
            _is_business = "Yes" if follower.is_business_account else "No"
            _external_url = follower.external_url
            _biography = follower.biography
            _avatar_url = follower.profile_pic_url_no_iphone
            _profile_url = f'https://www.instagram.com/{_username}/'
            if _is_business == "Yes":
                public_data = _extract_email_phone_number(instagrapi_client, _username)
            else:
                public_data = _extract_bio_info(_biography)
            _public_email = public_data['email'] or ''
            _public_phone = public_data['phone_number'] or ''
            _city = public_data['city'] or ''
            _public_address = public_data['address'] or ''
            break
        except instaloader.exceptions.ConnectionException or instaloader.exceptions.BadResponseException or instaloader.exceptions.QueryReturnedBadRequestException:
            streamlit_obj.error("Connection error")
        except instaloader.exceptions.LoginRequiredException:
            streamlit_obj.error("Login Error")
            return False
        except instaloader.exceptions.ProfileNotExistsException:
            streamlit_obj.error("Invalid username")
            return ""
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            streamlit_obj.error("Two Factor Authentication Required")
            return False
        

    return [_id, _username, _full_name, _follower_count, _post_count, 
        _following_count, _public_email, _public_phone, _city,  
        _public_address, _is_private, _is_verified, _is_business,
        _external_url, _biography, _avatar_url, _profile_url] or ''

def extract_user_information(username, streamlit_obj, file_exists, lower_delay, upper_delay):

    ITERATOR_FILE_PATH = f'{TEMP_DIR_NAME}/{username}-iterator'
    COOKIE_FILE_PATH = f'{TEMP_DIR_NAME}/cookie'
    OUTPUT_CSV_FILE_PATH = f'{OUPUT_DATA_DIR_NAME}/{username}.csv'
    if not os.path.isdir(TEMP_DIR_NAME):
        os.mkdir(TEMP_DIR_NAME)
    if not os.path.isdir(OUPUT_DATA_DIR_NAME):
        os.mkdir(OUPUT_DATA_DIR_NAME)

    headings = ["User Id", "User Name", "Full Name", "Followers Count", "Following Count", "Post Count", "Public Email", 
             "Public Phone", "City", "Address", "Is Private", "Is Verified", "Is Business", "External Url", "Biography",
             "Avatar Url", "Profile Url"]

    loader = instaloader.Instaloader()
    try:
        loader.load_session_from_file("cookie", filename=f'{TEMP_DIR_NAME}/cookie')
    except:
        streamlit_obj.error("Error in cookie json file")
        return

    streamlit_obj.info("Getting user information...")

    try:
        profile = instaloader.Profile.from_username(loader.context, username)
    except instaloader.exceptions.ProfileNotExistsException:
        streamlit_obj.error("Invalid username")
        return False
    except instaloader.exceptions.ConnectionException:
        streamlit_obj.error("Connection error")
        return False
    except instaloader.exceptions.LoginRequiredException:
        streamlit_obj.error("Login Error")
        return
    except instaloader.exceptions.TwoFactorRequiredException:
        streamlit_obj.error("Two factor authentication error")
        return False
    except instaloader.exceptions.QueryReturnedBadRequestException or instaloader.exceptions.BadResponseException:
        streamlit_obj.error("Bad request error. Please login instagram with browser and try again")
        return False
    

    if file_exists:
        iterator = dill.loads(open(ITERATOR_FILE_PATH, "rb").read())
        
    else:
        with open(OUTPUT_CSV_FILE_PATH, 'w', encoding='utf-8', newline='') as csv_file:

            csv.writer(csv_file).writerow(headings)
        iterator = profile.get_followers()
        

    table = streamlit_obj.table([headings])
    
    delay_placeholder = streamlit_obj.empty()

    # instagrapi
    with open(SESSION_ID_FILE) as f:
        session_id = f.read()
    for i in range(5):
        try:
            instagrapi_client = instagrapi.Client()
            
            instagrapi_client.login_by_sessionid(session_id)
            break
        except:
            pass
    else:
        streamlit_obj.error("Login Error check your network")
        return

    # Loop through the generator of followers and add them to the list
    with open(OUTPUT_CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as file:
        for follower in iterator:
            data = _get_follower_data(follower, streamlit_obj, instagrapi_client)
            if not data:
                return False

            # append everything in csv file
            csv_writer = csv.writer(file)
            csv_writer.writerow(data)
            file.flush()

            # showing data to user
            for i in range(len(data)):
                data[i] = str(data[i])
            table.add_rows([data])

            with open(ITERATOR_FILE_PATH, "wb") as f:
                dill.dump(iterator, f)
            
            random_delay(lower_delay, upper_delay, delay_placeholder)
    
    return True