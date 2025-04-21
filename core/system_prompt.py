def get_system_instruction():
    return """
You are an expert media planner helping brands choose advertising assets.
... (same as your big instruction block)
"""

def get_location_followup_prompt(user_input, state):
    from utils.fetch_locations import fetch_locations_from_api
    locations = fetch_locations_from_api("")
    location_names = [loc["company_name"] for loc in locations]
    location_list_text = "\n".join(f"- {name}" for name in location_names)
    return (
        f"The user is discussing a potential advertising campaign.\n"
        f"Their original campaign description was:\n\n'''{state['messages'][0]['content']}'''\n\n"
        f"I previously recommended the location: {state['location_suggestion']['company_name']}\n\n"
        f"Here is a list of all available locations:\n{location_list_text}\n\n"
        f"The user has now said:\n\n'''{user_input}'''\n\n"
        f"Please respond thoughtfully, as if you’re helping them choose the most appropriate location for their brand."
    )

