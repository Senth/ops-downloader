from ..config import config
from ..core.type import Types
from ..gateways.config_gateway import ConfigGateway
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

    def run(self) -> None:
        for type in config.general.types:
            self._run_type(type)

    def _run_type(self, type: Types) -> None:
        # Get latest downloaded episode name and internal number
        episode_info = self.plex.get_last_episode_info(type)

        # Get new episodes from OPS site
        ops = OPS()
        ops.get_new_episodes(type, episode_info.ops)

        # TODO Download episodes

        # TODO Rerender with correct metadata title

        # TODO Move to plex directory
