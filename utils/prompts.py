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

            Below is a request from a user looking for campaign asset recommendations. Please analyze their need, and based on that, recommend the most suitable advertising asset from the provided list. Return top 3 best asset.

            User Request:
            \"\"\"
            {query}
            \"\"\"

            Available Assets:
            {assets}

            Instructions:
            - Pick the most relevant asset considering their campaign goal, budget, and brand description.
            -Greet the user for example say here's what I got for you or something to sound a bit more human
            - Clearly explain why the selected asset is a good fit and how it can attract their target audience more in 3-4 sentence paragraph .
            Return in this format:


            Recomended Asset [Rank]: [Asset Name]  
            Asset Type: [asset_type]
            Rate: [Price]/[Frequency]
            Why: [1-2 sentence reasoning]


            Then, based on the selected top 3 assets and with the specified budget, generate a detailed **asset allocation table** with the following columns:
            - Asset
            - Cost per Unit
            - Allocation
            - Quantity Purchased
            - Duration Covered

            Format the table exactly like this example:

            | Asset        | Cost per Unit | Allocation | Quantity Purchased | Duration Covered |
            |--------------|----------------|-------------|---------------------|--------------------|
            | asset name   | ₹x/unit       | ₹xxxxx     | x units            | ~x years           |
            | ...          | ...           | ...         | ...                 | ...                |
            | Total Spent  |                | budget  |                     |                    |
    """
    return prompt
