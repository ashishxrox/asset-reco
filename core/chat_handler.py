from core.location_logic import handle_location_flow
from core.asset_logic import handle_asset_flow

def handle_chat_flow(user_input, state, client):
    if not state["selected_location"]:
        handle_location_flow(user_input, state, client)
    else:
        handle_asset_flow(user_input, state, client)