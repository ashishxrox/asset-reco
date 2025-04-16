import os
from openai import OpenAI
from dotenv import load_dotenv
from utils.fetch_assets import fetch_assets_for_location
from utils.prompts import get_asset_recommendation_prompt


# Load environment variables
load_dotenv()
client = OpenAI()  # This uses your OPENAI_API_KEY from .env


def format_assets_list(assets):
    lines = []
    for asset in assets:
        line = f"- {asset['asset_name']} | ₹{asset['rate']} | {asset['company_name']} | {asset['details']} | {asset['frequency']} | {asset['reach']}"
        lines.append(line)
    return "\n".join(lines)



def main():
    # --- Step 1: Simulated User Inputs ---
    location = "Kroot Memorial High School"
    brand_name = "FizzPro"
    brand_description = "FizzPro is a new-age sparkling energy drink focused on active lifestyles, gym-goers, and college youth."
    budget = 2000  # in INR
    campaign_intent = "mass reach"  # options: mass reach, engagement, recall, sampling

    # --- Step 2: Fetch Assets for Location ---
    assets = format_assets_list(fetch_assets_for_location(location))

    if not assets:
        print("No assets found for this location.")
        return

    # --- Step 3: Generate Prompt for OpenAI ---
    prompt = get_asset_recommendation_prompt(
        location=location,
        brand_name=brand_name,
        brand_description=brand_description,
        budget=budget,
        campaign_intent=campaign_intent,
        assets=assets
    )

    print(prompt)

    # --- Step 4: Get Recommendation from OpenAI ---
    try:
        response = client.chat.completions.create(
            model="o1-mini-2024-09-12",
            messages=[
                {"role": "user", "content": prompt}
            ],
            # temperature=0.7,
            max_completion_tokens=1000 
        )

        print(response.choices)

        recommendation = response.choices[0].message.content
        print("\nRecommended Assets:\n")
        print(recommendation)

    except Exception as e:
        print("Error while calling OpenAI API:", e)


if __name__ == "__main__":
    main()




