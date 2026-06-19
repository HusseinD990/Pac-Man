class Cheats:
    """Store the state of all cheat options."""
    def __init__(self) -> None:
        """Initialize all cheats as disabled."""
        self.wall_pass = False
        self.invincibility = False
        self.freeze_gost = False
        self.speed = False
        self.pause_time = False
