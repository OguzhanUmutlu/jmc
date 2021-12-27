import re
from typing import List
from . import Logger, PackGlobal
from .module import Module
import logging

logger = Logger(__name__, logging.DEBUG)


def handle_imports(string: str, pack_global: PackGlobal) -> str:
    """Create modules from "@import '<PATH>';" commands and remove the command from the string before returning"""
    imports_match: List[re.Match] = re.finditer(
        r'@import [\'\"](.*?)[\'\"]; ', string)
    for import_match in imports_match:
        pack_global.imports.append(
            Module(import_match.groups()[0], pack_global))
    return string
    # TODO: FINISH handle_imports

    #
    # elif (custom_command := re.match(r'@import [\'\"](.*)[\'\"]', text)) is not None:
    #     pass
