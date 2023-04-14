import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..core.episode import Episode
from ..core.type import Types


class Plex:
    def __init__(self, dir: Path) -> None:
        self.dir = dir

    def get_last_episode_info(self, type: Types) -> Episode:
        season = datetime.now().year

        # Get from current season
        episode_info = self._get_last_episode_info_from_season(type, season)
        if episode_info:
            return episode_info

        # Not current season exists, check previous season
        episode_info = self._get_last_episode_info_from_season(type, season - 1)
        if episode_info:
            return episode_info

        # No previous season exists, create empty episode info
        return Episode()

    def _get_last_episode_info_from_season(self, type: Types, season: int) -> Optional[Episode]:
        regexp = re.compile(rf"{type.value} - s{season}e0?0?(\d+) - .*\((\d+\.?\d?)\)\.mp4")
        season_dir: Path = self.dir / type.value / f"Season {season}"

        if not season_dir.exists():
            return None

        latest_episode = 0
        episode_info = Episode()
        for file in season_dir.glob("*.mp4"):
            match = regexp.match(file.name)
            if not match:
                continue

            internal_episode_number = int(match[1])
            ops_episode_number = match[2]

            if internal_episode_number < latest_episode:
                continue

            latest_episode = internal_episode_number
            episode_info.number = internal_episode_number
            episode_info.ops.number = float(ops_episode_number)
            episode_info.season = season

        return episode_info

    def move_episode(self, episode: Episode) -> None:
        season_dir = self.dir / episode.type.value / f"Season {episode.season}"
        season_dir.mkdir(parents=True, exist_ok=True)

        shutil.move(episode.file, season_dir / episode.file.name)
