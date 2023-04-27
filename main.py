import streamlit as st
from instagram_follower import automatic_follow, extract_user_information, is_extracted_file_exists, convert_json_to_cookie, followed_file_exists
import random

def main():
    st.title("Instagram Bot")
    st.sidebar.title("Select a Function")

    # Create a dropdown menu in the sidebar
    function = st.sidebar.selectbox(
        "Select a Function",
        ("Information Extractor", "Automatic Follow")
    )

    if function == "Information Extractor":
        st.header("Information Extractor")
        logged_in = False
        json_file = None

        if not logged_in:
            json_file = st.file_uploader("Upload a JSON file for Login", type="json")

        if json_file:
            try:
                convert_json_to_cookie(json_file)
                logged_in = True
            except Exception as e:
                st.error(e)

        if logged_in:
            username = st.text_input("Enter Instagram username")
            lower_delay,upper_delay = st.slider('Select delay',1, 20, (10, 20))
     
            if username:
                if is_extracted_file_exists(username):
                    continue_process = st.radio("User data already exists. Do you want to continue the extracting process or start from the beginning?", ("Continue", "Start from the beginning"))
                    if continue_process == "Continue":
                        if st.button("Start Information Extraction"):
                            extract_user_information(username, st, True, lower_delay, upper_delay)
                            st.success("Information extraction completed successfully.")
                    else:
                        if st.button("Start Information Extraction"):
                            response = extract_user_information(username, st, False, lower_delay, upper_delay)
                            if response:
                                st.success("Information extraction completed successfully.")
                else:
                    if st.button("Start Information Extraction"):
                        extract_user_information(username, st, False, lower_delay, upper_delay)
                        st.success("Information extraction completed successfully.")
            st.empty()

    elif function == "Automatic Follow":
        st.header("Automatic Follow")
        csv_file = st.file_uploader("Upload a CSV file", type="csv")
        lower_delay,upper_delay = st.slider('Select delay',1, 20, (10, 20))
        if csv_file:
            try:
                if followed_file_exists(csv_file.name):
                    continue_process = st.radio("User data already exists. Do you want to continue the extracting process or start from the beginning?", ("Continue", "Start from the beginning"))
                    if continue_process == "Continue":
                        if st.button("Start Information Extraction"):
                            automatic_follow(csv_file, st, upper_delay, lower_delay, True)
                    else:
                        if st.button("Start Information Extraction"):
                            automatic_follow(csv_file, st, upper_delay, lower_delay, False)
                else:
                    automatic_follow(csv_file, st, upper_delay, lower_delay, False)
                st.success("Automatic Follow completed successfully.")
            except Exception as e:
                st.error(e)
        
        


if __name__ == "__main__":
    main()
