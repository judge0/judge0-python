"""Helpers for the Sphinx documentation version sidebar."""

from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")

VISIBLE_DOC_VERSION_LIMIT = 10


def split_doc_versions(
    versions: Iterable[T],
    *,
    limit: int = VISIBLE_DOC_VERSION_LIMIT,
) -> tuple[list[T], list[T]]:
    """Split versions into the sidebar list and older collapsed entries.

    ``master`` is shown first. Remaining names are sorted in reverse
    lexicographic order, matching the previous sidebar template.

    Parameters
    ----------
    versions : iterable
        Version objects with a ``name`` attribute.
    limit : int, optional
        Number of versions to keep visible. Defaults to 10.

    Returns
    -------
    tuple of list
        Visible versions and older versions hidden under "View more...".
    """
    items = list(versions)
    master = [item for item in items if getattr(item, "name", None) == "master"]
    others = sorted(
        (item for item in items if getattr(item, "name", None) != "master"),
        key=lambda item: str(getattr(item, "name", "")),
        reverse=True,
    )
    ordered = master + others
    return ordered[:limit], ordered[limit:]
