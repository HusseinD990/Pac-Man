import json
from typing import Any


class Parsing():
    """Parse and validate the game's configuration file."""
    def __init__(self, path: str) -> None:
        """Initialize the parser.

        Args:
            path: Path to the configuration file.
        """
        self.path = path
        if not self.path.endswith(".json"):
            raise ValueError("Error: Configuration file should be JSON")

    def parse(self) -> Any:
        """Load and validate the configuration file.

        Checks that all required keys are present exactly once and
        verifies that configuration values satisfy the game's
        constraints.

        Returns:
            The validated configuration data.

        Raises:
            ValueError: If the configuration file is invalid.
        """
        keys = {
            "highscore_filename": 0,
            "width": 0,
            "height": 0,
            "pacgums": 0,
            "lives": 0,
            "points_per_pacgum": 0,
            "points_per_super_pacgum": 0,
            "points_per_ghost": 0,
            "seed": 0,
            "level_max_time": 0
        }

        with open("config.json") as f:
            lines = []
            for line in f:
                line = line.split("#", 1)[0]
                lines.append(line)
                if ":" not in line:
                    continue
                key, val = line.split(":", maxsplit=1)
                key = key.strip("\" ")
                val = val.strip(", \n")
                if key not in keys.keys():
                    raise ValueError("Error: Invalid Key")
                else:
                    keys[key] += 1
                if key == "highscore_filename":
                    if not val.endswith(".json") and len(val) < 5:
                        raise ValueError("Error: Invalid highscore_filename")
                else:
                    numeric_value = int(val)
                    if not isinstance(numeric_value, int):
                        raise ValueError(f"Error: Invalid value for {key}")
                    if numeric_value <= 0 and key != "seed":
                        raise ValueError(
                            f"Error: Invalid value, "
                            f"{key} should be greater than 0")
                    if key == "width" or key == "height":
                        if numeric_value < 3:
                            raise ValueError(
                                f"Error: Invalid value,"
                                f" {key} should be greater than 2"
                            )

            data = json.loads("".join(lines))

        for k, v in keys.items():
            if v == 0:
                raise ValueError(f"Error: {k} is missing")
            if v > 1:
                raise ValueError(f"Error: {k} is duplicated")
        return data
