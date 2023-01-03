def format_time(time_in_seconds):
    hours = time_in_seconds // 3600
    minutes = (time_in_seconds % 3600) // 60
    seconds = time_in_seconds % 60

    time_string = ""
    if hours > 0:
        time_string += f"{hours} Hours, "
    if hours > 0 or minutes > 0:
        time_string += f"{minutes} Minutes, "
    time_string += f"{seconds} Seconds"
    return time_string

'''Get time between start:end in format
total_time = math.ceil(end - start)
formatted_time = format_time(total_time)
print(f"Total Time: {formatted_time}")'''