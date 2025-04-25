# core/prompts.py

import json

def get_asset_recommendation_prompt(location, brand_name, brand_description, budget, campaign_intent, assets):
    asset_list_text = json.dumps(assets, indent=2)

    prompt = f"""
You are an expert media planner.

Brand: "{brand_name}" – {brand_description}.  
Location: {location}  
Budget: ₹{budget}  
Campaign Intent: {campaign_intent}

Intent Rules:
- "mass reach" → prefer screens, LED boards, banners in public spaces
- "engagement" → booths, stalls, exhibits
- "sampling" → D2D, pamphlet, giveaways
- "recall" → posters, visuals, frequent impressions

Recommend **only 1 asset** from the list below that best fits the brand, budget, and campaign intent. Consider visibility and asset relevance.

Only use assets from the provided list below:
{asset_list_text}


Return in this format:

Recomended Asset: [Asset Name]  
Details: [Company Name], [Locality]
Why: [1-2 sentence reasoning]
"""

    return prompt


def get_asset_chat_recommendation_prompt(query, assets):
    asset_list_text = json.dumps(assets, indent=2)
    print(asset_list_text)

    prompt = f"""
You are an expert media planner for advertising campaigns.

User Request:
\"\"\"
{query}
\"\"\"

Available Assets:
{asset_list_text}

Instructions:
- Pick the **3 most relevant assets** based on the user’s campaign goal, target audience, budget, and brand type.
- Always prioritize **strategic intent**. Use these intent rules:

    - Want **mass reach**? → Choose **screens**, **LED boards**, **message rollouts**.
    - Want **active engagement**? → Go for **stalls**, **clubhouse exhibits**, or **live booths**.
    - Want **silent sampling**? → Opt for **D2D delivery**, **pamphlets**, **giveaways**.
    - Want **brand recall**? → Choose **posters**, **standees**, **frequent visual placements**.

- Greet the user first. For example: “Here’s what I found for you!” — sound helpful and human.
- For each asset, clearly explain why it suits the brand, intent and target audience in a short paragraph (3–4 sentences).
- Be strategic — consider **cost-effectiveness**, **reach**, and **impact**.
- In the asset allocation table:
- For reach make sure you use the values inside the reach fields only and not get confused with anything that is there in the asset detail or description
  - For the "Reach/Impressions" column, **simply show** the `reach` fields **from the asset list**, in the format: `reach`.
  - Do not interpret, estimate, calculate, or rephrase. Just use the raw values from the `reach`  field as-is.

- Understanding Quantity vs Slots:
  - `Quantity` refers to the **number of physical or available units** of the asset. For example, if there are 4 elevators in a building, the quantity is 4.
  - `Slots` refer to **how many times those units can be used in a month**, based on the rate (frequency).
  - Calculate slots using these rules:

      - If Rate is **"Day"** or **"Once"** → Slots = Quantity × 30
      - If Rate is **"Week"** → Slots = Quantity × 4
      - If Rate is **"Month"** or **"Quarter"** → Slots = Quantity × 1

  - Example:
      - Quantity = 4, Rate = Day → Slots = 4 × 30 = 120
      - Quantity = 2, Rate = Week → Slots = 2 × 4 = 8
      - Quantity = 3, Rate = Month → Slots = 3

  - Use the **slot calculation** to compare how frequently each asset can appear within a month, and to optimize allocation.

  Important:
- When creating the allocation table:
  - Always calculate the **maximum available slots** for each asset using:  
    - Day/Once → quantity × 30 × duration (in months)  
    - Week → quantity × 4 × duration  
    - Month/Quarter → quantity × 1 × duration  
  - Use this value to inform how many slots are realistically purchasable within the given budget.

- Try to use the **entire budget** efficiently.
  - Distribute allocation across the top 3 selected assets, aiming for cost-effectiveness and coverage.
  - If budget allows, consider increasing the number of slots allocated while not exceeding the maximum available slots.
-Make sure based on the requirement, prioritise using the full budget, and incase that's not possible you make sure the duration is satisfied. Under any circumstance atleast one of the two should be fully utilised, and in best case both should be fully utilized.
-Incase you need to use more than 3 assets to fully use the budget for the given duration, you can use another asset but from the given asset list only. Give proper reasoning for your action.

- The `Slots Purchased` must not exceed the calculated maximum slots available for each asset (based on quantity, frequency, and duration).


Return in this format:

Recomended Asset [Rank]: [Asset Name]  
Asset Type: [asset_type]  
Rate: [₹x/frequency]  
Reach: [reach]  
Why: [3–4 sentence explanation]

Then, generate a **detailed asset allocation table** based on the selected assets and budget (DO NOT PUT THE TITLE JUST THE TABLE ):

| Asset        | Cost per Unit | Allocation | Slots Purchased | Duration Covered | Reach/Impressions  | Quantity | Frequency |
|--------------|----------------|-------------|---------------------|--------------------|---------------|-------------|---------|
| asset name   | ₹x/frequency   | ₹xxxxx      | x slots             | ~x months          | reach         | quantity    | frequency |
| ...          | ...            | ...         | ...                 | ...                | ...           |             |           |
| Total Spent  |                | ₹xxxxxx     |                     |                    |               |             |           |

Make sure that the table is the last thing you put in the Response
"""
    return prompt

# Quantity-> how many elevators in a society
# Slots -> quantity * (Freq multiplier for a month)
