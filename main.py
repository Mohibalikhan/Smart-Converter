# In this we make a smart converter 
# 28-02-2025
import streamlit as st
import requests
import json
from pint import UnitRegistry
from collections import deque

# Initialize Unit Registry
ureg = UnitRegistry()

# Conversion History (Session State)
if "conversion_history" not in st.session_state:
    st.session_state.conversion_history = deque(maxlen=10)

# Unit Categories with Icons
unit_categories = {
    "📏 Length": ["meter", "kilometer", "mile", "foot", "inch"],
    "⚖️ Mass": ["gram", "kilogram", "pound", "tonne"],
    "⏳ Time": ["second", "minute", "hour", "day"],
    "🌡️ Temperature": ["celsius", "fahrenheit", "kelvin"],
    "🏋🏼‍♂️ Pressure": ["pascal", "bar", "psi"],
    "📐 Area": ["square meter", "hectare", "acre", "square mile"],
    "⚡ Energy": ["joule", "calorie", "kilowatt-hour"],
    "🚀 Speed": ["meter/second", "kilometer/hour", "mile/hour"],
    "📊 Volume": ["liter", "milliliter", "gallon", "cup", "fluid ounce"],
}

currency_category = {
    "Currency": ["USD", "EUR", "INR", "PKR","BDT","CNY"] 
}

# Streamlit UI Setup
st.set_page_config(page_title=" Smart Converter 🌍💰 ", layout="wide")
st.sidebar.title("🌟 Navigator")
page = st.sidebar.radio("Select a section", ["Unit Converter", "Currency Converter", "Zakat Calculator", "Conversion History"])

# Conversion Function
def convert_units(value, from_unit, to_unit):
    try:
        result = (value * ureg(from_unit)).to(to_unit)
        formatted_result = "{:.0f}".format(result.magnitude) if result.magnitude.is_integer() else "{:.4f}".format(result.magnitude).rstrip('0').rstrip('.')
        return result.magnitude, f"{value} {from_unit} = {formatted_result} {to_unit}"
    except Exception as e:
        return None, str(e)

# Fetch & Store Currency Rates
def update_currency_rates():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    response = requests.get(url).json()
    with open("currency_rates.json", "w") as f:
        json.dump(response["rates"], f)
    return response["rates"]

# Convert currency with offline caching
def convert_currency(amount, from_currency, to_currency):
    try:
        with open("currency_rates.json", "r") as f:
            offline_rates = json.load(f)
    except FileNotFoundError:
        offline_rates = update_currency_rates()
    
    if from_currency in offline_rates and to_currency in offline_rates:
        return round(amount * offline_rates[to_currency] / offline_rates[from_currency], 2)
    return f"❌ Conversion not available for {from_currency} to {to_currency}"

# Unit Converter Page
if page == "Unit Converter":
    st.title("🔁 Unit Converter")
    category = st.selectbox("📌 Select a Category", list(unit_categories.keys()))
    col1, col2 = st.columns(2)
    with col1:
        from_unit = st.selectbox("Convert From:", unit_categories[category])
    with col2:
        to_unit = st.selectbox("Convert To:", unit_categories[category])
    value = st.number_input("🔢 Enter Value:", min_value=0.0, format="%.10g")
    if st.button("Convert"):
        converted_value, result_text = convert_units(value, from_unit, to_unit)
        if converted_value is not None:
            st.success(result_text)
            st.session_state.conversion_history.appendleft(result_text)
        else:
            st.error("Invalid conversion! Check units.")

# Currency Converter Page
elif page == "Currency Converter":
    st.title("💵 Currency Converter")
    col1, col2 = st.columns(2)
    with col1:
        from_currency = st.selectbox("Convert From:", currency_category["Currency"])
    with col2:
        to_currency = st.selectbox("Convert To:", currency_category["Currency"])
    value = st.number_input("🔢 Enter Amount:", min_value=0.0, format="%.10g")
    if st.button("Convert"):
        converted_value = convert_currency(value, from_currency, to_currency)
        st.success(f"{value} {from_currency} = {converted_value} {to_currency}")
        st.session_state.conversion_history.appendleft(f"{value} {from_currency} = {converted_value} {to_currency}")

# Zakat Calculator Page
elif page == "Zakat Calculator":
    st.title("🕌 Zakat Calculator")
    st.write("Calculate your zakat based on your total wealth.")
    
    total_wealth = st.number_input("💰 Enter your total wealth (in your local currency):", min_value=0.0, format="%.2f")
    zakat_rate = 2.5 / 100  # 2.5% zakat rate
    if st.button("Calculate Zakat"):
        zakat_amount = total_wealth * zakat_rate
        st.success(f"Your zakat obligation is: {zakat_amount:.2f}")

# Conversion History Page
elif page == "Conversion History":
    st.title("📜 Conversion History")
    if st.session_state.conversion_history:
        for entry in list(st.session_state.conversion_history):
            st.write(entry)
    else:
        st.info("No conversions yet. Start converting!")
