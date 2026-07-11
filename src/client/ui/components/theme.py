from textual.theme import Theme

dracula_theme = Theme(
    name="dracula",
    primary="#BD93F9",      # Purple
    secondary="#6272A4",    # Current line / muted blue
    accent="#FF79C6",       # Pink
    foreground="#F8F8F2",   # Main text
    background="#282A36",   # Main background
    success="#50FA7B",      # Green
    warning="#F1FA8C",      # Yellow
    error="#FF5555",        # Red
    surface="#44475A",      # Surface elements
    panel="#21222C",        # Slightly darker panels
    dark=True,
    variables={
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#8BE9FD",       # Cyan
        "input-selection-background": "#6272A4 50%",
    },
)