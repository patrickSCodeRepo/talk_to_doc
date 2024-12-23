import streamlit as st

def initialize_app():
    try:
        # Define pages with descriptive titles
        main = st.Page("main.py", title="App Interface")
        create_vectorstore = st.Page("create.py", title="Create Entry")
        
        # Configure the application
        st.set_page_config(
            page_title="Data Manager",
            page_icon="",  # Adding an icon for better visibility
            initial_sidebar_state="expanded"
        )
        
        # Set up navigation
        pg = st.navigation([main, create_vectorstore])
        
        # Run the application
        pg.run()
        
    except Exception as e:
        st.error(f"An error occurred while initializing the application: {str(e)}")
        
if __name__ == "__main__":
    initialize_app()