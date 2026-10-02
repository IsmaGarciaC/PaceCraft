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

def predict_time(time_minutes: float, distance_km: float, target_distance_km: float) -> float:
    """
    Peter Riegel's fatigue formula for race time prediction:
    T2 = T1 * (D2 / D1)^1.06
    Returns the predicted time in minutes.
    """
    if distance_km <= 0:
        return 0.0
    return time_minutes * ((target_distance_km / distance_km) ** 1.06)

def format_time(minutes_float: float) -> str:
    """
    Jinja2 Custom Filter: Converts total minutes (e.g., 125.5)
    into a formatted string 'HH:MM:SS'.
    """
    if minutes_float <= 0:
        return "00:00:00"
    
    hours = int(minutes_float // 60)
    remaining_minutes = int(minutes_float % 60)
    seconds = int(round((minutes_float % 1) * 60))
    
    if seconds == 60:
        remaining_minutes += 1
        seconds = 0
    if remaining_minutes == 60:
        hours += 1
        remaining_minutes = 0
        
    return f"{hours:02d}:{remaining_minutes:02d}:{seconds:02d}"

