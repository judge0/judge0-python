import os

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
    Rapid,
    RapidJudge0CE,
    RapidJudge0ExtraCE,
    Sulu,
    SuluJudge0CE,
    SuluJudge0ExtraCE,
)
from .filesystem import File, Filesystem
from .retry import MaxRetries, MaxWaitTime, RegularPeriodRetry
from .submission import Submission

__all__ = [
    "ATD",
    "ATDJudge0CE",
    "ATDJudge0ExtraCE",
    "Client",
    "File",
    "Filesystem",
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
    "Sulu",
    "SuluJudge0CE",
    "SuluJudge0ExtraCE",
    "TestCase",
    "async_execute",
    "execute",
    "get_client",
    "async_run",
    "sync_run",
    "run",
    "sync_execute",
    "wait",
]

JUDGE0_IMPLICIT_CE_CLIENT = None
JUDGE0_IMPLICIT_EXTRA_CE_CLIENT = None


def _get_implicit_client(flavor: Flavor) -> Client:
    global JUDGE0_IMPLICIT_CE_CLIENT, JUDGE0_IMPLICIT_EXTRA_CE_CLIENT

    # Implicit clients are already set.
    if flavor == Flavor.CE and JUDGE0_IMPLICIT_CE_CLIENT is not None:
        return JUDGE0_IMPLICIT_CE_CLIENT
    if flavor == Flavor.EXTRA_CE and JUDGE0_IMPLICIT_EXTRA_CE_CLIENT is not None:
        return JUDGE0_IMPLICIT_EXTRA_CE_CLIENT

    from .clients import CE, EXTRA_CE

    try:
        from dotenv import load_dotenv

        load_dotenv()
    except:  # noqa: E722
        pass

    if flavor == Flavor.CE:
        client_classes = CE
    else:
        client_classes = EXTRA_CE

    # Try to find one of the predefined keys JUDGE0_{SULU,RAPID,ATD}_API_KEY
    # in environment variables.
    client = None
    for client_class in client_classes:
        api_key = os.getenv(client_class.API_KEY_ENV)
        if api_key is not None:
            client = client_class(api_key)
            break

    # If we didn't find any of the possible predefined keys, initialize
    # the preview Sulu client based on the flavor.
    if client is None:
        if flavor == Flavor.CE:
            client = SuluJudge0CE(retry_strategy=RegularPeriodRetry(0.5))
        else:
            client = SuluJudge0ExtraCE(retry_strategy=RegularPeriodRetry(0.5))

    if flavor == Flavor.CE:
        JUDGE0_IMPLICIT_CE_CLIENT = client
    else:
        JUDGE0_IMPLICIT_EXTRA_CE_CLIENT = client

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
