# Simple Reflex Agent for Vacuum Cleaner World

def reflex_vacuum_agent(location, status):
    if status == "Dirty":
        return "Suck"
    elif location == "A":
        return "Right"
    elif location == "B":
        return "Left"

location = "A"
status = "Dirty"
locations = ["A", "B"]

for _ in range(5):
    action = reflex_vacuum_agent(location, status)
    print(f"Location: {location}, Status: {status}, Action: {action}")

    if action == "Suck":
        status = "Clean"
    elif action == "Right":
        location = "B"
    elif action == "Left":
        location = "A"


        
