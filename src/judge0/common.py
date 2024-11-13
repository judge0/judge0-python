from base64 import b64decode, b64encode
from enum import IntEnum

from typing import Union, Optional, Any


class Language(IntEnum):
    PYTHON = 0
    CPP = 1
    JAVA = 2
    CPP_GCC = 3
    CPP_CLANG = 4
    PYTHON_FOR_ML = 5


class Flavor(IntEnum):
    CE = 0
    EXTRA_CE = 1


class Status(IntEnum):
    IN_QUEUE = 1
    PROCESSING = 2
    ACCEPTED = 3
    WRONG_ANSWER = 4
    TIME_LIMIT_EXCEEDED = 5
    COMPILATION_ERROR = 6
    RUNTIME_ERROR_SIGSEGV = 7
    RUNTIME_ERROR_SIGXFSZ = 8
    RUNTIME_ERROR_SIGFPE = 9
    RUNTIME_ERROR_SIGABRT = 10
    RUNTIME_ERROR_NZEC = 11
    RUNTIME_ERROR_OTHER = 12
    INTERNAL_ERROR = 13
    EXEC_FORMAT_ERROR = 14


def encode(content: Any) -> Optional[str]:
    if isinstance(content, str):
        return b64encode(bytes(content, "utf-8")).decode()
    if isinstance(content, bytes):
        return b64encode(content).decode()
    if hasattr(content, "encode"):
        return b64encode(content.encode()).decode()
    return None


def decode(content: Any) -> Optional[str]:
    if isinstance(content, str):
        return b64decode(content.encode()).decode(errors="backslashreplace")
    if isinstance(content, bytes):
        return b64decode(content.decode(errors="backslashreplace")).decode(
            errors="backslashreplace"
        )
    return None
