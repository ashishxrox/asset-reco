import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
from utils.fetch_assets import fetch_assets_for_location
from utils.prompts import get_asset_chat_recommendation_prompt

# Load environment variables
load_dotenv()
client = OpenAI()  # Uses your OPENAI_API_KEY from .env
MAX_CHARS = 1000

# Utility function to format asset list
def format_assets_list(assets):
    lines = []
    for asset in assets:
        line = f"- {asset['asset_name']} | ₹{asset['rate']} | {asset['company_name']}  | {asset.get('frequency', 'N/A')} | {asset.get('reach', 'N/A')}"
        lines.append(line)
    return "\n".join(lines)

# Streamlit App
def main():
    st.set_page_config(page_title="Ad Asset Recommender", page_icon="📍")
    st.title("📍 Ad Asset Recommender")
    st.markdown("Describe your brand and campaign, and we’ll recommend the best advertising asset.")

    # --- Location Dropdown ---
    locations = ["Kroot Memorial High School", "Tech Park", "City Center", "Downtown Mall", "Aparna Westside"]  # Example locations
    location = st.selectbox("Select a Location", locations)

    # --- User Input (Single Combined Message) ---
    user_input = st.text_area(
        "📣 Tell us about your campaign",
        placeholder="Example: Hey, I'm looking to advertise my brand FizzPro around Kroot Memorial High School. It's a sparkling energy drink for college students and gym-goers. I have ₹2000 and want maximum reach.",
        max_chars=MAX_CHARS,
        height=150
    )

    if st.button("Get Recommendation"):
        if not user_input.strip():
            st.warning("Please enter your campaign details first.")
            return

        if location not in locations:
            st.warning("Please select a valid location.")
            return

        # --- Fetch Assets ---
        assets = fetch_assets_for_location(location)
        if not assets:
            st.error(f"No assets found for {location}.")
            return

        formatted_assets = format_assets_list(assets)

        # --- Build Prompt & Get Recommendation ---
        prompt = get_asset_chat_recommendation_prompt(user_input, formatted_assets)

        try:
            response = client.chat.completions.create(
                model="o1-mini-2024-09-12",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                # max_completion_tokens=1500
            )

            recommendation = response.choices[0].message.content
            st.subheader("🧠 Recommended Asset")
            st.markdown(recommendation)
            # st.markdown(prompt)

        except Exception as e:
            st.error(f"Error while calling OpenAI API: {e}")

if __name__ == "__main__":
    main()
