from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import streamlit as st
import plotly.express as px  # for interactive charts
import json
from datetime import datetime

# Initialize Streamlit app
st.title('Live Wheat Futures Prices')

# Insert the new CSS style block
css = """
<style>
/* Targeting the main content area for the green background */
.main .block-container, .stApp {
    background-color: #f9f0df;
}
/* Sidebar */
.st-emotion-cache-16txtl3.eczjsme4 {
    background-color: #f9f0df;
}

.st-emotion-cache-6qob1r.eczjsme3 {
    background-color: #f9f0df;
}

.st-emotion-cache-ue6h4q.e1y5xkzn3 {
    color:#34571a
}

.st-emotion-cache-18ni7ap.ezrtsby2 {
    background-color: #f9f0df;
}

h1 {
    color: #34571a;
    font-family: "Source Sans Pro", sans-serif;
}
div.stText {
    color: #34571a;
    font-size: 24px;
}
h3 {
    color: #34571a;
    font-family: "Source Sans Pro", sans-serif;
    
}
div.stText {
    color: #34571a;
    font-size: 10px;
}

/* Style for "Your profile" */
.profile-title {
    font-family: "Source Sans Pro", sans-serif;
    font-weight: 700;
    color: #34571a;
    font-size: 24px;
}
/* Style pour la carte PyDeck */
.stDeckGlJsonChart {
    border: 2px solid black;
    border-radius: 5px;
}
.st-emotion-cache-1788y8l.e1f1d6gn2 {
    border: 2px solid black !important;
    border-radius: 5px;  # pour des coins arrondis
    padding: 10px;      # espace entre le texte et le bord
}
.st-emotion-cache-1wivap2.e1i5pmia3  {
    text-align: center; /* Centrer horizontalement le texte */
    display: flex;
    flex-direction: column;
    justify-content: center; /* Centrer verticalement le contenu */
}
.st-emotion-cache-16idsys p {
    word-break: break-word;
    margin-bottom: 0px;
    font-size: 18px;
    font-weight: 550;
}    
.st-emotion-cache-5rimss.e1nzilvr5 {
    color: black;
}
    
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Adding a sidebar for additional features
st.sidebar.title("Features")


# Function to load and save messages for the community forum
def load_messages():
    try:
        with open('forum_messages.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_message(name, message):
    messages = load_messages()
    messages.append({"name": name, "message": message, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    with open('forum_messages.json', 'w') as file:
        json.dump(messages, file)

def scrape_wheat_prices():
    # Set up Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # URL to scrape
    url = "https://live.euronext.com/en/product/commodities-futures/EBM-DPAR"
    driver.get(url)

    # Wait for the dynamic content to load
    time.sleep(1)  # Adjust as necessary

    wheat_prices = []
    # Find the table by ID (or modify selector as needed)
    table = driver.find_element(By.ID, 'future-prices-table')

    if table:
        rows = table.find_elements(By.TAG_NAME, 'tr')

        for row in rows[1:]:  # Skip header row
            cols = row.find_elements(By.TAG_NAME, 'td')
            if cols:
                # Assuming the order of columns in the website matches the screenshot and there are no missing values.
                wheat_prices.append({
                    "Delivery": cols[0].text.strip(),
                    "Bid": cols[1].text.strip(),
                    "Ask": cols[2].text.strip(),
                    "Last": cols[3].text.strip(),
                    "Time": cols[4].text.strip(),
                    "+/-": cols[5].text.strip(),
                    "Day Vol.": cols[6].text.strip(),
                    "Open": cols[7].text.strip(),
                    "High": cols[8].text.strip(),
                    "Low": cols[9].text.strip(),
                    "Settl.": cols[10].text.strip(),
                    "O.I": cols[11].text.strip(),
                })

    # Close the browser
    driver.quit()

    return wheat_prices

def display_data():
    wheat_prices = scrape_wheat_prices()
    df_wheat_prices = pd.DataFrame(wheat_prices)
    st.dataframe(df_wheat_prices)  # Display the data as a table

# Display wheat prices data
display_data()

# Read the data
df = pd.read_excel('/Users/ratchoul/Desktop/Historical Chart.xlsx')

# Convert all entries in the 'Date' column to datetime objects
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Sort the DataFrame by the 'Date' column
df_sorted = df.sort_values(by='Date')

# Create the interactive chart
fig = px.line(df_sorted, x='Date', y='Price', title='Milling Wheat N2 Futures Historical Data')

# Display the chart in Streamlit
st.plotly_chart(fig)

# Par exemple, la création d'une boîte de sélection pour les maturités...
maturity_options = ["Mar 2024", "May 2024", "Sep 2024", "Dec 2024", "Mar 2025", "May 2025", "Sep 2025"]
selected_maturity = st.selectbox("Select the maturity at which you wish to sell the goods:", maturity_options)

# Et ensuite, utiliser harvested_wheat et formatted_price pour calculer et afficher le gain...
if selected_maturity == "Mar 2024":
    gain_per_ton = ((((217.5) * 1260) - (24516+90000))/180)/7
elif selected_maturity == "May 2024":
    gain_per_ton = ((((212) * 1260) - (24516+90000))/180)/7
elif selected_maturity == "Sep 2024":
    gain_per_ton = ((((219.75) * 1260) - (24516+90000))/180)/7
elif selected_maturity == "Dec 2024":
    gain_per_ton = ((((223) * 1260) - (24516+90000))/180)/7
elif selected_maturity == "Mar 2025":
    gain_per_ton = ((((225.75) * 1260) - (24516+90000))/180)/7
else:  # Pour May 2025, Sep 2025, et toute autre valeur non spécifiée explicitement
    gain_per_ton = ((((227.75) * 1260) - (24516+90000))/180)/7

formatted_gain_per_ton = "{:,.2f}".format(gain_per_ton)

st.write(f"Taking into account the cost of seeds and all other expenses, if you buy futures contracts (of 50t each) with a maturity of {selected_maturity}, your gain will be {formatted_gain_per_ton}€/t.")

# Community Forum or Q&A Section
st.header("Community Forum / Q&A")
st.write("Share your strategies, experiences, or ask questions here.")

# User input for the forum
user_name = st.text_input("Your Name")
user_message = st.text_area("Your Message")
submit_button = st.button("Post")

if submit_button and user_name and user_message:
    save_message(user_name, user_message)

# Display messages
for message in load_messages():
    st.text(f"{message['name']} ({message['timestamp']}): {message['message']}")