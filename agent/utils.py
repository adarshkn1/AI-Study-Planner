def format_time(minutes):
    hours = minutes // 60
    mins = minutes % 60

    if hours > 0 and mins > 0:
        return f"{hours} hr {mins} min"
    elif hours > 0:
        return f"{hours} hr"
    else:
        return f"{mins} min"
