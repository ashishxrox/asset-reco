import streamlit as st
from prompts.asset_prompts import get_asset_chat_recommendation_prompt
from core.system_prompt import get_system_instruction

def format_assets_list(assets):
    lines = []
    for asset in assets:
        line = f"- {asset['asset_name']} | ₹{asset['rate']}| {asset.get('details', 'N/A')} | {asset['company_name']}  | {asset.get('frequency', 'N/A')} | {asset.get('reach', 'N/A')} | {asset.get('asset_type', 'N/A')}"
        lines.append(line)
    return "\n".join(lines)

def handle_asset_flow(user_input, state, client):
    instruction = get_system_instruction()
    asset_list = f"ASSET LIST:\n{state['formatted_assets']}\n\n"

    messages = [{"role": "user", "content": instruction}]
    for msg in state["messages"]:
        content = asset_list + msg["content"] if msg["role"] == "user" else msg["content"]
        messages.append({"role": msg["role"], "content": content})

    try:
        response = client.chat.completions.create(
            model="o1-mini-2024-09-12",
            messages=messages
        )
        assistant_reply = response.choices[0].message.content

        if "<<RECOMMEND>>" in assistant_reply:
            rec_prompt = get_asset_chat_recommendation_prompt(user_input, state["formatted_assets"])
            rec_response = client.chat.completions.create(
                model="o1-mini-2024-09-12",
                messages=[{"role": "user", "content": rec_prompt}]
            )
            assistant_reply = rec_response.choices[0].message.content

        state["messages"].append({"role": "assistant", "content": assistant_reply})
        with st.chat_message("assistant"):
            st.markdown(assistant_reply)

    except Exception as e:
        st.error(f"Error calling OpenAI API: {e}")