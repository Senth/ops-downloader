import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..core.type import Types


class PlexEpisodeInfo:
    def __init__(self) -> None:
        self.ops: str = ""
        self.internal: int = 0
        self.current_season: bool = True


class Plex:
    def __init__(self, dir: Path) -> None:
        self.dir = dir

    def get_last_episode_info(self, type: Types) -> PlexEpisodeInfo:
        season = datetime.now().year

        # Get from current season
        episode_info = self._get_last_episode_info_from_season(type, season)

        # Not current season exists, check previous season
        if not episode_info:
            episode_info = self._get_last_episode_info_from_season(type, season - 1)
            if episode_info:
                episode_info.current_season = False

        # No previous season exists, create empty episode info
        if not episode_info:
            episode_info = PlexEpisodeInfo()

        return episode_info

    def _get_last_episode_info_from_season(self, type: Types, season: int) -> Optional[PlexEpisodeInfo]:
        regexp = re.compile(rf"{type.value} - s{season}e(\d+) - .*\((\d+\w?)\)\.mp4")
        season_dir: Path = self.dir / type.value / f"Season {season}"

        if not season_dir.exists():
            return None

        latest_episode = 0
        episode_info = PlexEpisodeInfo()
        for file in season_dir.glob("*.mp4"):
            match = regexp.match(file.name)
            if not match:
                continue

            internal_episode_number = int(match[1])
            ops_episode_number = match[2]

            if internal_episode_number < latest_episode:
                continue

            episode_info.internal = internal_episode_number
            episode_info.ops = ops_episode_number

        return episode_info
