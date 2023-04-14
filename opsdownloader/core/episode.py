from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .type import Types


@dataclass(init=False)
class OPSEpisode:
    number: float = 0.0
    url: str = ""
    download_url: str = ""

    def previous_episode(self) -> float:
        """Get the previous episode number.

        For example:
        265.4 -> 264
        263 -> 262
        """
        number = float(self.number) - 1
        return float(int(number))


@dataclass(init=False)
class Episode:
    title: str = ""
    type: Types = Types.UNKNOWN
    season: int = datetime.now().year
    number: int = 0
    ops: OPSEpisode = OPSEpisode()
    file: Path = Path("")

    def __init__(self) -> None:
        self.ops = OPSEpisode()

    @property
    def filename(self) -> str:
        return f"{self.type.value} - s{self.season}e{self.number} - {self.filename_title} ({self.ops.number}).mp4"

    @property
    def filename_title(self) -> str:
        return (
            self.title.replace(":", "—")
            .replace("/", "_")
            .replace("\\", "_")
            .replace("?", "")
            .replace("*", "")
            .replace('"', "")
            .replace("<", "")
            .replace(">", "")
            .replace("|", "")
            .replace("&", " and ")
        )
