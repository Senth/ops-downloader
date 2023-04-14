from datetime import datetime

from colored import attr
from tealprint import TealPrint

from ..config import config
from ..core.type import Types
from ..gateways.config_gateway import ConfigGateway
from ..gateways.downloader import Downloader
from ..gateways.encoder import Encoder
from ..gateways.ops import OPS
from ..gateways.plex import Plex


class App:
    def __init__(self) -> None:
        configGateway = ConfigGateway()
        configGateway.check_config_exists()
        configGateway.read()
        config.general = configGateway.get_general()
        config.ops = configGateway.get_ops()

        self.plex = Plex(config.general.plex_dir)
        self.downloader = Downloader()
        self.encoder = Encoder()

    def run(self) -> None:
        for type in config.general.types:
            self._run_type(type)

    def _run_type(self, type: Types) -> None:
        # Get latest downloaded episode name and internal number
        episode_info = self.plex.get_last_episode_info(type)

        # Get new episodes from OPS site
        ops = OPS()
        new_episodes = ops.get_new_episodes(type, episode_info)

        next_number = 1
        if episode_info.season == datetime.now().year:
            next_number = episode_info.number + 1

        for episode in new_episodes:
            episode.number = next_number
            next_number += 1

            TealPrint.info(f"Episode {episode.number}: {episode.title}", color=attr("bold"), push_indent=True)
            ops.get_download_url(episode)

            self.downloader.download(episode)

            # TODO Generate subtitles

            # Rerender with correct metadata title
            self.encoder.rerender(episode)

            # Move to plex directory
            self.plex.move_episode(episode)

            TealPrint.pop_indent()

        ops.close()
