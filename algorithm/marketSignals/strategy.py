from indicator import calculate_ema, calculate_rsi

def check_entry(opens, highs, lows, closes,
                ema_fast=50, ema_slow=200,
                rsi_period=14, rsi_min=55, rsi_max=75):
    
    ema_fast_vals = calculate_ema(closes, ema_fast)
    ema_slow_vals = calculate_ema(closes, ema_slow)
    rsi_vals = calculate_rsi(closes, rsi_period)

    prev = -2 

    signal = (
        ema_fast_vals[prev] > ema_slow_vals[prev] and
        closes[prev] > ema_fast_vals[prev] and
        rsi_vals[prev] is not None and
        rsi_min < rsi_vals[prev] < rsi_max
    )

    return signal