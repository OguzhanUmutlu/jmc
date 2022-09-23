from pathlib import Path
from .exception import HeaderDuplicatedMacro, HeaderFileNotFoundError, HeaderSyntaxException
from .log import Logger

logger = Logger(__name__)


class Header:
    file_read: set[str] = set()
    macros: dict[str, str] = {}
    replaces: dict[str, str] = {}

    @classmethod
    def clear(cls) -> None:
        cls.file_read = set()
        cls.macros = {}
        cls.replaces = {}

    @classmethod
    def add_file_read(cls, path: Path) -> None:
        cls.file_read.add(path.as_posix())

    @classmethod
    def is_header_exist(cls, path: Path) -> bool:
        return path.as_posix() in cls.file_read


def parse_header(header_str: str, file_name: str, parent_target: Path) -> Header:
    lines = header_str.split("\n")
    for line, line_str in enumerate(lines):
        line += 1
        if line_str.isspace() or line_str.startswith("//"):
            continue

        if not line_str.startswith("#"):
            raise HeaderSyntaxException(
                "Expected '#'", file_name, line, line_str)

        directive = line_str[1:]
        args = directive.split()

        if args[0] == "define":
            if len(args) == 3:
                key = args[1]
                value = args[2]
                logger.debug(f'Define "{key}" as "{value}"')
                if key in Header.macros:
                    raise HeaderDuplicatedMacro(
                        f"'{key}' macro is already defined", file_name, line, line_str)
                Header.macros[key] = value
            else:
                raise HeaderSyntaxException(
                    f"'define' takes 2 arguments (got {len(args)-1})", file_name, line, line_str)
        elif args[0] == "include":
            if len(args) == 2:
                included = args[1]
                if (
                    not (included.startswith("<") and included.endswith(">"))
                    and
                    not (included.startswith('"') and included.endswith('"'))
                ):
                    raise HeaderSyntaxException(
                        "Included file must be wrapped in double quotes `\"` or angle bracket `<>`", file_name, line, line_str)
                file_name = included[1:-1]
                if not file_name.endswith(".hjmc"):
                    file_name += ".hjmc"
                header_file = parent_target/file_name
                if not header_file.is_file():
                    raise HeaderFileNotFoundError(header_file)
                with header_file.open('r') as file:
                    header_str = file.read()
                logger.info(f"Parsing {header_file}")
                if Header.is_header_exist(header_file):
                    raise HeaderSyntaxException(
                        f"File {header_file.as_posix()} is already included.", file_name, line, line_str)
                Header.add_file_read(header_file)
                parse_header(header_str, header_file.as_posix(), parent_target)
            else:
                raise HeaderSyntaxException(
                    "Whitespace is not supported in header file name", file_name, line, line_str)
        else:
            raise HeaderSyntaxException(
                f"Unrecognized directive '{args[0]}'", file_name, line, line_str)
