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

Return in this format:

Recomended Asset [Rank]: [Asset Name]  
Asset Type: [asset_type]  
Rate: [₹x/unit]  
Why: [3–4 sentence explanation]

Then, generate a **detailed asset allocation table** based on the selected assets and budget:

| Asset        | Cost per Unit | Allocation | Quantity Purchased | Duration Covered |
|--------------|----------------|-------------|---------------------|--------------------|
| asset name   | ₹x/unit       | ₹xxxxx     | x units            | ~x months          |
| ...          | ...           | ...         | ...                 | ...                |
| Total Spent  |                | ₹xxxxxx    |                     |                    |
"""
    return prompt
