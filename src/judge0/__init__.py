import logging
import os

from typing import Union

from .api import (
    async_execute,
    async_run,
    execute,
    get_client,
    run,
    sync_execute,
    sync_run,
    wait,
)
from .base_types import Flavor, Language, LanguageAlias, Status, TestCase
from .clients import (
    ATD,
    ATDJudge0CE,
    ATDJudge0ExtraCE,
    Client,
    Judge0Cloud,
    Judge0CloudCE,
    Judge0CloudExtraCE,
    Rapid,
    RapidJudge0CE,
    RapidJudge0ExtraCE,
)
from .filesystem import File, Filesystem
from .retry import MaxRetries, MaxWaitTime, RegularPeriodRetry
from .submission import Submission

__version__ = "0.0.7"

__all__ = [
    "ATD",
    "ATDJudge0CE",
    "ATDJudge0ExtraCE",
    "Client",
    "File",
    "Filesystem",
    "Judge0Cloud",
    "Judge0CloudCE",
    "Judge0CloudExtraCE",
    "Language",
    "LanguageAlias",
    "MaxRetries",
    "MaxWaitTime",
    "Rapid",
    "RapidJudge0CE",
    "RapidJudge0ExtraCE",
    "RegularPeriodRetry",
    "Status",
    "Submission",
    "TestCase",
    "async_execute",
    "async_run",
    "execute",
    "get_client",
    "run",
    "sync_execute",
    "sync_run",
    "wait",
]

JUDGE0_IMPLICIT_CE_CLIENT = None
JUDGE0_IMPLICIT_EXTRA_CE_CLIENT = None

logger = logging.getLogger(__name__)
suppress_preview_warning = os.getenv("JUDGE0_SUPPRESS_PREVIEW_WARNING") is not None


def _get_implicit_client(flavor: Flavor) -> Client:
    global JUDGE0_IMPLICIT_CE_CLIENT, JUDGE0_IMPLICIT_EXTRA_CE_CLIENT

    # Implicit clients are already set.
    if flavor == Flavor.CE and JUDGE0_IMPLICIT_CE_CLIENT is not None:
        return JUDGE0_IMPLICIT_CE_CLIENT
    if flavor == Flavor.EXTRA_CE and JUDGE0_IMPLICIT_EXTRA_CE_CLIENT is not None:
        return JUDGE0_IMPLICIT_EXTRA_CE_CLIENT

    try:
        from dotenv import load_dotenv

        load_dotenv()
    except:  # noqa: E722
        pass

    # Let's check if we can find a self-hosted client.
    client = _get_custom_client(flavor)

    # Try to find one of the API keys for hub clients.
    if client is None:
        client = _get_hub_client(flavor)

    # If we didn't find any of the possible keys, initialize
    # the preview client based on the flavor.
    if client is None:
        client = _get_preview_client(flavor)

    if flavor == Flavor.CE:
        JUDGE0_IMPLICIT_CE_CLIENT = client
    else:
        JUDGE0_IMPLICIT_EXTRA_CE_CLIENT = client

    return client


def _get_preview_client(flavor: Flavor) -> Union[Judge0CloudCE, Judge0CloudExtraCE]:
    if not suppress_preview_warning:
        logger.warning(
            "You are using a preview version of the client which is not recommended"
            " for production.\n"
            "For production, please specify your API key in the environment variable."
        )

    if flavor == Flavor.CE:
        return Judge0CloudCE()
    else:
        return Judge0CloudExtraCE()


def _get_custom_client(flavor: Flavor) -> Union[Client, None]:
    from json import loads

    ce_endpoint = os.getenv("JUDGE0_CE_ENDPOINT")
    ce_auth_header = os.getenv("JUDGE0_CE_AUTH_HEADERS")
    extra_ce_endpoint = os.getenv("JUDGE0_EXTRA_CE_ENDPOINT")
    extra_ce_auth_header = os.getenv("JUDGE0_EXTRA_CE_AUTH_HEADERS")

    if flavor == Flavor.CE and ce_endpoint is not None and ce_auth_header is not None:
        return Client(
            endpoint=ce_endpoint,
            auth_headers=loads(ce_auth_header),
        )

    if (
        flavor == Flavor.EXTRA_CE
        and extra_ce_endpoint is not None
        and extra_ce_auth_header is not None
    ):
        return Client(
            endpoint=extra_ce_endpoint,
            auth_headers=loads(extra_ce_auth_header),
        )

    return None


def _get_hub_client(flavor: Flavor) -> Union[Client, None]:
    from .clients import CE, EXTRA_CE

    if flavor == Flavor.CE:
        client_classes = CE
    else:
        client_classes = EXTRA_CE

    for client_class in client_classes:
        api_key = os.getenv(client_class.API_KEY_ENV)
        if api_key is not None:
            client = client_class(api_key)
            break
    else:
        client = None

    return client


CE = Flavor.CE
EXTRA_CE = Flavor.EXTRA_CE

ASSEMBLY = LanguageAlias.ASSEMBLY
BASH = LanguageAlias.BASH
BASIC = LanguageAlias.BASIC
BOSQUE = LanguageAlias.BOSQUE
C = LanguageAlias.C
C3 = LanguageAlias.C3
CLOJURE = LanguageAlias.CLOJURE
COBOL = LanguageAlias.COBOL
COMMON_LISP = LanguageAlias.COMMON_LISP
CPP = LanguageAlias.CPP
CPP_CLANG = LanguageAlias.CPP_CLANG
CPP_GCC = LanguageAlias.CPP_GCC
CPP_TEST = LanguageAlias.CPP_TEST
CPP_TEST_CLANG = LanguageAlias.CPP_TEST_CLANG
CPP_TEST_GCC = LanguageAlias.CPP_TEST_GCC
CSHARP = LanguageAlias.CSHARP
CSHARP_DOTNET = LanguageAlias.CSHARP_DOTNET
CSHARP_MONO = LanguageAlias.CSHARP_MONO
CSHARP_TEST = LanguageAlias.CSHARP_TEST
C_CLANG = LanguageAlias.C_CLANG
C_GCC = LanguageAlias.C_GCC
D = LanguageAlias.D
DART = LanguageAlias.DART
ELIXIR = LanguageAlias.ELIXIR
ERLANG = LanguageAlias.ERLANG
EXECUTABLE = LanguageAlias.EXECUTABLE
FORTRAN = LanguageAlias.FORTRAN
FSHARP = LanguageAlias.FSHARP
GO = LanguageAlias.GO
GROOVY = LanguageAlias.GROOVY
HASKELL = LanguageAlias.HASKELL
JAVA = LanguageAlias.JAVA
JAVAFX = LanguageAlias.JAVAFX
JAVASCRIPT = LanguageAlias.JAVASCRIPT
JAVA_JDK = LanguageAlias.JAVA_JDK
JAVA_OPENJDK = LanguageAlias.JAVA_OPENJDK
JAVA_TEST = LanguageAlias.JAVA_TEST
KOTLIN = LanguageAlias.KOTLIN
LUA = LanguageAlias.LUA
MPI_C = LanguageAlias.MPI_C
MPI_CPP = LanguageAlias.MPI_CPP
MPI_PYTHON = LanguageAlias.MPI_PYTHON
MULTI_FILE = LanguageAlias.MULTI_FILE
NIM = LanguageAlias.NIM
OBJECTIVE_C = LanguageAlias.OBJECTIVE_C
OCAML = LanguageAlias.OCAML
OCTAVE = LanguageAlias.OCTAVE
PASCAL = LanguageAlias.PASCAL
PERL = LanguageAlias.PERL
PHP = LanguageAlias.PHP
PLAIN_TEXT = LanguageAlias.PLAIN_TEXT
PROLOG = LanguageAlias.PROLOG
PYTHON = LanguageAlias.PYTHON
PYTHON2 = LanguageAlias.PYTHON2
PYTHON2_PYPY = LanguageAlias.PYTHON2_PYPY
PYTHON3 = LanguageAlias.PYTHON3
PYTHON3_PYPY = LanguageAlias.PYTHON3_PYPY
PYTHON_FOR_ML = LanguageAlias.PYTHON_FOR_ML
PYTHON_PYPY = LanguageAlias.PYTHON_PYPY
R = LanguageAlias.R
RUBY = LanguageAlias.RUBY
RUST = LanguageAlias.RUST
SCALA = LanguageAlias.SCALA
SQLITE = LanguageAlias.SQLITE
SWIFT = LanguageAlias.SWIFT
TYPESCRIPT = LanguageAlias.TYPESCRIPT
VISUAL_BASIC = LanguageAlias.VISUAL_BASIC
