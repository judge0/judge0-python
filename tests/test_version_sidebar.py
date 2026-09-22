from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
from typing import Any

_MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "docs" / "source" / "version_sidebar.py"
)


def _load_version_sidebar() -> Any:
    spec = spec_from_file_location("version_sidebar", _MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {_MODULE_PATH}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _version(name: str) -> SimpleNamespace:
    return SimpleNamespace(name=name, url=f"/{name}/")


def test_visible_limit_is_ten() -> None:
    version_sidebar = _load_version_sidebar()
    assert version_sidebar.VISIBLE_DOC_VERSION_LIMIT == 10


def test_master_is_first_and_only_ten_are_visible() -> None:
    version_sidebar = _load_version_sidebar()
    versions = [_version(f"v0.0.{i}") for i in range(1, 13)]
    versions.append(_version("master"))

    visible, older = version_sidebar.split_doc_versions(versions)

    assert [item.name for item in visible] == [
        "master",
        "v0.0.9",
        "v0.0.8",
        "v0.0.7",
        "v0.0.6",
        "v0.0.5",
        "v0.0.4",
        "v0.0.3",
        "v0.0.2",
        "v0.0.12",
    ]
    assert [item.name for item in older] == ["v0.0.11", "v0.0.10", "v0.0.1"]


def test_fewer_than_limit_has_no_older_versions() -> None:
    version_sidebar = _load_version_sidebar()
    versions = [_version("master"), _version("v0.0.2"), _version("v0.0.1")]

    visible, older = version_sidebar.split_doc_versions(versions)

    assert [item.name for item in visible] == ["master", "v0.0.2", "v0.0.1"]
    assert older == []


def test_empty_versions() -> None:
    version_sidebar = _load_version_sidebar()
    visible, older = version_sidebar.split_doc_versions([])

    assert visible == []
    assert older == []


def test_sidebar_template_collapses_older_versions() -> None:
    text = (_MODULE_PATH.parent / "_templates" / "versioning.html").read_text()

    assert "split_doc_versions" in text
    assert "View more..." in text
    assert "older_versions" in text
