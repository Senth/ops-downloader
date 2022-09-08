from __future__ import annotations

from argparse import Namespace
from pathlib import Path
from typing import List

from tealprint import TealConfig, TealLevel

from .core.type import Types

_app_name = "ops-downloader"


class Config:
    def __init__(self):
        # Default values
        self.app_name: str = _app_name
        self._general = General()
        self.ops = OPS()
        self.pretend = False

    @property
    def general(self) -> General:
        return self._general

    @general.setter
    def general(self, general: General) -> None:
        self._general = general
        TealConfig.level = general.log_level

    def set_cli_args(self, args: Namespace):
        """Set additional configuration from script arguments

        Args:
            args (list): All the parsed arguments
        """
        if args.debug:
            self._general.log_level = TealLevel.debug
        elif args.verbose:
            self._general.log_level = TealLevel.verbose
        elif args.silent:
            self._general.log_level = TealLevel.warning
        TealConfig.level = self._general.log_level

        self.pretend = args.pretend


class General:
    def __init__(self) -> None:
        self.plex_dir: Path = Path("")
        self.log_level = TealLevel.info
        self.types: List[Types] = [Types.QA, Types.CLASS]


class OPS:
    def __init__(self) -> None:
        self.email: str = ""
        self.password: str = ""


config = Config()
