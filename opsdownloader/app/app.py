from pathlib import Path

from colored import attr
from tealprint import TealConfig, TealLevel, TealPrint

from ..config import config
from ..core.episode import Episode
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

        TealConfig.level = TealLevel.debug

    def run(self) -> None:
        for type in config.general.types:
            self._run_type(type)

    def _run_type(self, type: Types) -> None:
        # Get latest downloaded episode name and internal number
        episode_info = self.plex.get_last_episode_info(type)

        # # Get new episodes from OPS site
        # ops = OPS()
        # new_episodes = ops.get_new_episodes(type, episode_info.ops)
        # ops.close()

        # TODO set episode numbers for each episode

        # REMOVE temporary episode
        episode = Episode()
        episode.ops.download_url = "https://61vod-adaptive.akamaized.net/exp=1681476013~acl=%2Fefd304a1-dd5e-4cec-8eec-18adcc26ea5c%2F%2A~hmac=19297935536e1a0357b6ee0f31b1b55068baa245280b8a7650eb2c3f9b59ecdd/efd304a1-dd5e-4cec-8eec-18adcc26ea5c/sep/video/8ad9d800,8feb0403,abc815d5,adf51583/audio/105b7777,5d76875f,bb4b5b25/master.mpd?query_string_ranges=1"
        episode.type = Types.QA
        episode.title = "Ken Block: Live with Passion"
        episode.file = Path("tmp.mkv")
        episode.ops.number = 256.1
        episode.number = 1

        episodes = [episode]

        downloader = Downloader()
        encoder = Encoder()

        for episode in episodes:
            TealPrint.info(f"Episode {episode.number}: {episode.title}", color=attr("bold"), push_indent=True)
            # downloader.download(episode)

            # Rerender with correct metadata title
            encoder.rerender(episode)

            # TODO Move to plex directory

            TealPrint.pop_indent()
