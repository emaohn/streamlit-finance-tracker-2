def format_currency(amount: float) -> str:
    """Format a number as currency with K/M suffixes for large numbers"""
    if abs(amount) >= 1_000_000:
        return f"${abs(amount/1_000_000):.1f}M"
    elif abs(amount) >= 1_000:
        return f"${abs(amount/1_000):.1f}K"
    else:
        return f"${abs(amount):.2f}"
