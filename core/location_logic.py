import streamlit as st
from utils.fetch_locations import fetch_locations_from_api
from constants.messages import confirm_phrases, reject_phrases
from core.system_prompt import get_location_followup_prompt
from core.asset_logic import format_assets_list

def infer_location_from_description(user_input, locations, client):
    location_names = [loc["company_name"] for loc in locations]
    location_list_text = "\n".join(f"- {name}" for name in location_names)

    prompt = (
        f"User campaign description:\n{user_input}\n\n"
        f"List of available locations:\n{location_list_text}\n\n"
        "Pick the most suitable location from the list above for the user's campaign needs. Respond with ONLY the location name."
    )

    try:
        response = client.chat.completions.create(
            model="o1-mini-2024-09-12",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Location inference failed: {e}")
        return None

def handle_location_flow(user_input, state, client):
    if not state["location_suggestion"]:
        locations = fetch_locations_from_api("")
        suggestion = infer_location_from_description(user_input, locations, client)
        matched = next((loc for loc in locations if loc["company_name"].strip() == suggestion), None)

        if matched:
            state["location_suggestion"] = matched
            assistant_msg = (
                f"Based on your campaign, I’d recommend running it in **{suggestion}**.\n\n"
                "Would you like me to go ahead with this location?"
            )
        else:
            assistant_msg = "I couldn't confidently suggest a location. Could you please provide a bit more context?"

    else:
        user_lower = user_input.strip().lower()
        if any(phrase in user_lower for phrase in confirm_phrases):
            from utils.fetch_assets import fetch_assets_for_location
            state["selected_location"] = state["location_suggestion"]
            assets = fetch_assets_for_location(state["selected_location"]["location_id"])
            state["formatted_assets"] = format_assets_list(assets)
            assistant_msg = f"Great! We’ve locked in **{state['selected_location']['company_name']}**. Let’s talk about your campaign goals and audience."

        elif any(phrase in user_lower for phrase in reject_phrases):
            state["location_suggestion"] = None
            assistant_msg = "No worries! Feel free to rephrase your campaign description, and I’ll suggest a different location."

        else:
            try:
                prompt = get_location_followup_prompt(user_input, state)
                response = client.chat.completions.create(
                    model="o1-mini-2024-09-12",
                    messages=[{"role": "user", "content": prompt}]
                )
                assistant_msg = response.choices[0].message.content.strip()
            except Exception as e:
                assistant_msg = f"Oops, couldn't generate a smart answer: {e}"

    state["messages"].append({"role": "assistant", "content": assistant_msg})
    with st.chat_message("assistant"):
        st.markdown(assistant_msg)