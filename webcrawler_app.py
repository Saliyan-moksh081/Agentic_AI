import streamlit as st
import subprocess
import json

def crawl_url_subprocess(url):
    # Call the worker script as a subprocess and capture its output
    result = subprocess.run(
        ["python", "simpleWebcrawler.py", url],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(result.stderr)
    # The worker prints the JSON result, so parse it
    return json.loads(result.stdout)

def main():
    st.title("Simple Web Crawler UI")
    url = st.text_input("Enter URL to scrape", "https://www.example.com/")
    if st.button("Scrape"):
        if url:
            with st.spinner("Crawling..."):
                try:
                    result = crawl_url_subprocess(url)
                    st.success("Scraping complete!")
                    st.json(result)
                except Exception as e:
                    st.error(f"Error: {e}")

if __name__ == "__main__":
    main()