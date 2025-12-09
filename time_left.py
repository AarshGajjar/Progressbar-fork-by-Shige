from aqt import mw
from functools import lru_cache
import math

@lru_cache(maxsize=1)
def calculate_review_stats():
    """
    Calculate the average review speed and standard deviation using the entire review history.
    Returns: (average_speed, stddev_speed)
    """
    try:
        # Step 1: Calculate count, total time, and average time
        query = """
            SELECT count(), sum(time) / 1000, avg(time)
            FROM revlog
        """
        result = mw.col.db.first(query)
        if not result:
            print("No data found in the revlog table.")
            return 0, 0

        cards, total_time, avg_time = result
        cards = cards or 0
        total_time = total_time or 0
        avg_time = avg_time or 0

        if cards == 0 or total_time == 0:
            print("No valid data in the revlog table (cards or total_time is 0).")
            return 0, 0

        # Step 2: Calculate the variance
        variance_query = """
            SELECT sum((time - ?) * (time - ?)) / ?
            FROM revlog
        """
        variance_result = mw.col.db.first(variance_query, avg_time, avg_time, cards)
        variance = variance_result[0] if variance_result else 0

        # Step 3: Calculate the standard deviation
        stddev_time = math.sqrt(variance) if variance > 0 else 0

        # Step 4: Calculate average speed and standard deviation of speed
        average_speed = cards * 60 / total_time  # Cards per minute
        stddev_speed = (stddev_time / 1000) * cards / total_time  # Standard deviation of speed
        return average_speed, stddev_speed

    except Exception as e:
        print(f"Error calculating review stats: {e}")
        return 0, 0

def estimateTimeLeft(total):
    try:
        # Clear the cache to force recalculation of review stats
        calculate_review_stats.cache_clear()

        # Calculate average speed and standard deviation (cached)
        average_speed, stddev_speed = calculate_review_stats()
        if average_speed == 0:
            return " | left ? min "

        # Calculate time estimate with confidence interval
        minutes = total / max(1, average_speed)
        lower_bound = total / max(1, average_speed + stddev_speed)
        upper_bound = total / max(1, average_speed - stddev_speed)

        # Inline time formatting logic
        def format_time(minutes):
            if minutes >= 60:
                return f"{int(minutes) // 60}h {int(minutes) % 60}m"
            elif minutes < 1:
                return f"<1 min"
            return f"{int(minutes)} min"

        formatted_time = format_time(minutes)

        # Initialize the lower and upper bounds formatting
        formatted_lower = format_time(lower_bound)
        formatted_upper = format_time(upper_bound)

        # Format the result
        if minutes == 0:
            return " | બવ વાંચ્યું ભાઈ"
        if lower_bound == upper_bound:
            return f" | Time left: {formatted_time}"
        else:
            return f" | Time left: {formatted_time} (range: {formatted_lower} - {formatted_upper})"

    except Exception as e:
        print(f"Error estimating time left: {e}")
        return ""
