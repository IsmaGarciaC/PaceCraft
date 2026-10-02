def calculate_pace(distance_km: float, time_minutes: float) -> float:
    """
    Calculates the running pace in minutes per kilometer.
    Returns a float. For example, 5.5 means 5 and a half minutes (5:30/km).
    """
    if distance_km <= 0:
        return 0.0
    return time_minutes / distance_km

def format_pace(pace_float: float) -> str:
    """
    Jinja2 Custom Filter: Converts a float pace (e.g., 5.5) 
    to a human-readable string format (e.g., '5:30 /km').
    """
    if pace_float <= 0:
        return "0:00 /km"
        
    minutes = int(pace_float)
    # Get the decimal part and multiply by 60 to get seconds
    seconds = int(round((pace_float - minutes) * 60))
    
    if seconds == 60:
        minutes += 1
        seconds = 0
        
    return f"{minutes}:{seconds:02d} /km"
