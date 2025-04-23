def check_gathered_info(messages):
    gathered = {
        'brand': False,
        'audience': False,
        'goals': False,
        'budget': False
    }
    
    # Analyze messages to see what info we have
    for msg in messages:
        content = msg['content'].lower()
        if 'sell' in content or 'brand' in content or 'product' in content:
            gathered['brand'] = True
        if 'audience' in content or 'target' in content or 'youngsters' in content:
            gathered['audience'] = True
        if 'goal' in content or 'sales' in content or 'awareness' in content:
            gathered['goals'] = True
        if 'budget' in content or '₹' in content or 'rs' in content or 'rupees' in content:
            gathered['budget'] = True
    
    return gathered