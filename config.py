"""Configuration management for AwayLock."""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"

# Setup logging to stdout (so launchd puts it in .log, not .error.log)
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S"))

log = logging.getLogger("awaylock")
log.addHandler(_handler)
log.setLevel(logging.INFO)


@dataclass
class Config:
    """Application configuration with sensible defaults."""
    device_address: str | None = None     # Device MAC/UUID (primary identifier)
    device_name: str | None = None        # Name (fallback if address not set)
    rssi_threshold: int = -70             # Signal threshold (-60 closer, -80 farther)
    check_interval: int = 3               # Seconds between status checks
    away_count_threshold: int = 3         # Consecutive "away" readings to trigger lock
    scan_duration: int = 6                # Duration of each scan in seconds

    @classmethod
    def load(cls) -> Config:
        """Load config from file or return defaults."""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                return cls(**json.load(f))
        return cls()

    def save(self) -> None:
        """Save current config to file."""
        with open(CONFIG_FILE, "w") as f:
            json.dump(asdict(self), f, indent=2)
        log.info(f"Config saved: {CONFIG_FILE}")

    def update(self, **kwargs) -> None:
        """Update config with non-None values."""
        for key, value in kwargs.items():
            if value is not None and hasattr(self, key):
                setattr(self, key, value)
