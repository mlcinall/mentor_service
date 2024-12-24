from datetime import datetime, time

def time_checker(
        day: int,
        time_start: time,
        time_end: time,
        call_datetime: datetime) -> bool:
    """
    Проверяет, что call_datetime находится внутри промежутка
    """
    if call_datetime.weekday() != day:
        return False

    call_time = call_datetime.time()
    if time_start <= call_time <= time_end:
        return True

    return False
