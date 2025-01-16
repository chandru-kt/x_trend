import streamlit as st
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pymongo import MongoClient
import certifi
import requests
from datetime import datetime
import json

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except Exception as e:
        return "Unable to fetch IP"
    
def scrape_and_save_trending_topics():
    mongo_uri = "mongodb+srv://ktchandru1234:ktchandru1234@cluster0.od2ea.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tls=true"
    client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
    db = client['twitter_trends']
    collection = db['trending_topics']
    driver = webdriver.Chrome()
    try:
        driver.get('https://x.com/i/flow/login')
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//body//div[@class='css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-135wba7 r-16dba41 r-1awozwy r-6koalj r-1inkyih r-13qz1uu']/input"))).send_keys('2031012mss@cit.edu.in')
        driver.find_element(By.XPATH, "//button[@class='css-175oi2r r-sdzlij r-1phboty r-rs99b7 r-lrvibr r-ywje51 r-184id4b r-13qz1uu r-2yi16 r-1qi8awa r-3pj75a r-1loqt21 r-o7ynqc r-6416eg r-1ny4l3l']").click()
        try:
            if WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//span[@class='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3']"))).text == 'Enter your phone number or username':
                driver.find_element(By.XPATH, "//div[@class='css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-135wba7 r-16dba41 r-1awozwy r-6koalj r-1inkyih r-13qz1uu']/input").send_keys('ChandruKT8')
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//button[@class='css-175oi2r r-sdzlij r-1phboty r-rs99b7 r-lrvibr r-19yznuf r-64el8z r-1fkl15p r-1loqt21 r-o7ynqc r-6416eg r-1ny4l3l']"))).click()
        except TimeoutException:
            pass
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//input[@class='r-30o5oe r-1dz5y72 r-13qz1uu r-1niwhzg r-17gur6a r-1yadl64 r-deolkf r-homxoj r-poiln3 r-7cikom r-1ny4l3l r-t60dpp r-fdjqy7']"))).send_keys('k.t.chandru1234@')
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//button[@class='css-175oi2r r-sdzlij r-1phboty r-rs99b7 r-lrvibr r-19yznuf r-64el8z r-1fkl15p r-1loqt21 r-o7ynqc r-6416eg r-1ny4l3l']"))).click()
        try:
            trending_sidebar = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Timeline: Trending now']"))
            )
        except TimeoutException:
            st.warning("Trending topics not found within 5 seconds.")
            return
        sidebar_list = trending_sidebar.find_elements(By.XPATH, ".//div[@class='css-175oi2r']//div[@class='css-175oi2r r-1adg3ll r-1ny4l3l']//div[@class='css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-b88u0q r-1bymd8e']")
        trending_topics = []
        for i in sidebar_list:
            topic = i.text
            trending_topics.append({"topic": topic})
        if trending_topics:
            collection.insert_many(trending_topics)
            st.session_state.trending_topics = trending_topics
            st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.ip_address = get_public_ip()
            st.session_state.mongo_records = list(collection.find().sort("_id", -1))
        else:
            st.warning("No trending topics found.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        driver.quit()
st.title("Twitter Trending Topics Scraper")
if "trending_topics" not in st.session_state:
    st.session_state.trending_topics = None
if "timestamp" not in st.session_state:
    st.session_state.timestamp = None
if "ip_address" not in st.session_state:
    st.session_state.ip_address = None
if "mongo_records" not in st.session_state:
    st.session_state.mongo_records = None
if st.button("Run Script"):
    st.write("Scraping trending topics...")
    scrape_and_save_trending_topics()
if st.session_state.trending_topics:
    st.write(f"These are the most happening topics as on **{st.session_state.timestamp}**:")
    for topic in st.session_state.trending_topics:
        st.write(f"- {topic['topic']}")

    st.write(f"The IP address used for this query was **{st.session_state.ip_address}**.")

    st.write("Here’s a JSON extract of this record from the MongoDB:")
    st.json(st.session_state.mongo_records)
if st.session_state.trending_topics:
    if st.button("Run Query Again"):
        st.session_state.trending_topics = None
        st.session_state.timestamp = None
        st.session_state.ip_address = None
        st.session_state.mongo_records = None
        st.experimental_rerun()