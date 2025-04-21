def infer_location_from_description(user_input, locations):
    location_names = [loc["company_name"] for loc in locations]
    print(location_names)
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
        print(response.choices[0])
        return response.choices[0].message.content.strip()
    except Exception as e:
        # st.error(f"Location inference failed: {e}")
        return None