import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
from utils.fetch_assets import fetch_assets_for_location
from utils.prompts import get_asset_recommendation_prompt

# Load environment variables
load_dotenv()
client = OpenAI()

# Function to format assets list into the required format
def format_assets_list(assets):
    lines = []
    for asset in assets:
        line = f"- {asset['asset_name']} | ₹{asset['rate']} | {asset['company_name']}, {asset['locality']} | {asset['details']}"
        lines.append(line)
    return "\n".join(lines)

# Streamlit UI
def main():
    # --- Title of the page ---
    st.title("Brand Asset Recommendation Tool")

    # --- Session state initialization ---
    if "location" not in st.session_state:
        st.session_state.location = "Pune"
    if "brand_name" not in st.session_state:
        st.session_state.brand_name = "FizzPro"
    if "brand_description" not in st.session_state:
        st.session_state.brand_description = "FizzPro is a new-age sparkling energy drink focused on active lifestyles, gym-goers, and college youth."
    if "budget" not in st.session_state:
        st.session_state.budget = 2000
    if "campaign_intent" not in st.session_state:
        st.session_state.campaign_intent = "mass reach"
    if "assets" not in st.session_state:
        st.session_state.assets = None
    if "recommendation" not in st.session_state:
        st.session_state.recommendation = None

    # --- Input fields for User ---
    location = st.text_input("Location", st.session_state.location)
    brand_name = st.text_input("Brand Name", st.session_state.brand_name)
    brand_description = st.text_area("Brand Description", st.session_state.brand_description)
    budget = st.number_input("Budget (INR)", min_value=0, value=st.session_state.budget)
    campaign_intent = st.selectbox("Campaign Intent", ["mass reach", "engagement", "recall", "sampling"], index=["mass reach", "engagement", "recall", "sampling"].index(st.session_state.campaign_intent))

    # Update session state with user input
    st.session_state.location = location
    st.session_state.brand_name = brand_name
    st.session_state.brand_description = brand_description
    st.session_state.budget = budget
    st.session_state.campaign_intent = campaign_intent

    # --- Step 1: Fetch and Display Assets ---
    if st.button("Fetch Assets"):
        assets = fetch_assets_for_location(location)
        
        if assets:
            st.session_state.assets = assets  # Store assets in session state
            st.subheader("Assets Available:")
            formatted_assets = format_assets_list(assets)
            st.text(formatted_assets)
        else:
            st.warning("No assets found for this location.")
            st.session_state.assets = None  # Reset assets if nothing is found
            return

    # --- Step 2: Generate Prompt ---
    if st.session_state.assets:
        formatted_assets = format_assets_list(st.session_state.assets)

        prompt = get_asset_recommendation_prompt(
            location=location,
            brand_name=brand_name,
            brand_description=brand_description,
            budget=budget,
            campaign_intent=campaign_intent,
            assets=formatted_assets
        )

        # --- Step 3: Get Recommendations from OpenAI ---
        if st.button("Get Recommendations"):
            try:
                response = client.chat.completions.create(
                    model="o1-mini-2024-09-12",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    # temperature=0.7,
                    max_completion_tokens=1500 
                )

                # Accessing the content correctly from the response object
                # The correct way to access the content is to use .choices[0].message['content']
                # recommendation = response.choices[0].message['content']
                recommendation = response.choices[0].message.content
                st.session_state.recommendation = recommendation  # Store recommendation in session state
                st.subheader("Recommended Assets:")
                st.text(recommendation)

            except Exception as e:
                st.error(f"Error while calling OpenAI API: {e}")
                st.session_state.recommendation = None  # Reset recommendation in case of error

    # Display previous recommendation if available
    if st.session_state.recommendation:
        st.subheader("Previously Recommended Assets:")
        st.text(st.session_state.recommendation)

if __name__ == "__main__":
    main()
