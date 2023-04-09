import streamlit as st
from your_module import automatic_follow, information_extractor

def main():
    st.title("Instagram Bot")
    st.sidebar.title("Select a Function")

    # Create a dropdown menu in the sidebar
    function = st.sidebar.selectbox(
        "Select a Function",
        ("Automatic Follow", "Information Extractor")
    )

    if function == "Automatic Follow":
        st.header("Automatic Follow")
        csv_file = st.file_uploader("Upload a CSV file", type="csv")
        if csv_file:
            try:
                automatic_follow(csv_file)
                st.success("Automatic Follow completed successfully.")
            except Exception as e:
                st.error(e)
            

    elif function == "Information Extractor":
        st.header("Information Extractor")
        username = st.text_input("Enter Instagram username")
        if username:
            information_extractor(username)
            st.success("Information Extraction completed successfully.")

if __name__ == "__main__":
    main()
