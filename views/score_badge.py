def score_badge(score):
    """Returns a colored label string for a similarity score."""
    if score < 0.35:
        color = "red"
    elif score < 0.5:
        color = "orange"
    else:
        color = "green"
    return f":{color}[**{score:.3f}**]"