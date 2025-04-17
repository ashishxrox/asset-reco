import os
from openai import OpenAI
from dotenv import load_dotenv
from utils.fetch_assets import fetch_assets_for_location
from utils.prompts import get_asset_chat_recommendation_prompt

# Load environment variables
load_dotenv()
client = OpenAI()  # Uses your OPENAI_API_KEY from .env


def format_assets_list(assets):
    lines = []
    for asset in assets:
        line = f"- {asset['asset_name']} | ₹{asset['rate']} | {asset['company_name']} | {asset['details']} | {asset.get('frequency', 'N/A')} | {asset.get('reach', 'N/A')} | {asset.get('asset_type')}"
        lines.append(line)
    return "\n".join(lines)


def main():
    # --- Step 1: Natural Language Combined Input ---
    combined_input = """
    Hey, I'm looking to advertise my brand FizzPro around Aparna Westside.

    FizzPro is a sparkling energy drink made for gym-goers, college students, and anyone who lives an active lifestyle.

    I’ve got a budget of ₹2000 for this campaign, and I really want to get as much reach as possible—just want people to see the brand everywhere. What would you recommend?
    """.strip()

    # --- Step 2: Infer Location from Input (Basic Heuristic) ---
    # Optional: later you could use GPT to extract structured data from this if needed
    location = "Aparna Westside"

    # --- Step 3: Fetch & Format Assets for Location ---
    raw_assets = fetch_assets_for_location(location)
    if not raw_assets:
        print("No assets found for this location.")
        return
    formatted_assets = format_assets_list(raw_assets)

    # --- Step 4: Combine Everything into Final Prompt ---
    prompt = get_asset_chat_recommendation_prompt(combined_input, formatted_assets)
    # print(prompt)

    # --- Step 5: Get Recommendation from OpenAI ---
    try:
        response = client.chat.completions.create(
            model="o1-mini-2024-09-12",
            messages=[
                {"role": "user", "content": prompt}
            ],
            # max_completion_tokens=1500
        )

        recommendation = response.choices[0].message.content
        print("\nRecommended Asset:\n")
        print(recommendation)

    except Exception as e:
        print("Error while calling OpenAI API:", e)


if __name__ == "__main__":
    main()
