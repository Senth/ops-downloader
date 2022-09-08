import os
import platform
from pathlib import Path
from subprocess import run
from typing import List

from blulib.config_parser import ConfigParser
from tealprint import TealPrint

from ..config import OPS, General, config
from ..core.type import Types


class ConfigGateway:
    def __init__(self) -> None:
        self.path = Path.home().joinpath(f".{config.app_name}.cfg")
        self.parser = ConfigParser()

    def check_config_exists(self):
        if not self.path.exists():
            TealPrint.info(f"Could not find any configuration file in {self.path}")
            user_input = input("Do you want to copy the example config and edit it (y/n)?")
            if user_input.lower() == "y":
                self.parser.copy_example_if_conf_not_exists(config.app_name)
                editor = ""
                if "EDITOR" in os.environ:
                    editor = os.environ["EDITOR"]
                if editor == "" and platform.system() == "Windows":
                    editor = "notepad.exe"
                elif editor == "":
                    editor = "vim"
                run([editor, self.path])

            else:
                exit(0)

    def read(self):
        self.parser.read(self.path)

    def get_general(self) -> General:
        general = General()

        self.parser.to_object(general, "General", "plex_dir", "log_level", "str_list:types")

        if not general.plex_dir:
            TealPrint.warning("Missing 'plex_dir' under section [General] in your configuration", exit=True)
        general.plex_dir = Path(str(general.plex_dir))

        if not general.types:
            general.types = [Types.QA, Types.CLASS]
        else:
            # Convert string into Types enumeration objects
            types: List[Types] = []
            for type in general.types:
                types.append(Types[str(type)])
            general.types = types

        return general

    def get_ops(self) -> OPS:
        ops = OPS()

        self.parser.to_object(ops, "OPS", "email", "password")

        if not ops.email:
            TealPrint.warning("Missing 'email' under section [OPS] in your configuration", exit=True)
        if not ops.password:
            TealPrint.warning("Missing 'password' under section [OPS] in your configuration", exit=True)

        return ops
