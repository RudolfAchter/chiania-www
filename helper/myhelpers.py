def is_integer(n):
    try:
        float(n)
    except:
        return False
    else:
        return float(n).is_integer()