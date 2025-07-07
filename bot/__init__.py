def start_bot() -> None:
    """Lazy import entrypoint for the bot."""
    from .main import start_bot as run
    run()
