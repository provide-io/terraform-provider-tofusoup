"""Version ordering shared by the registry-backed data sources."""

from collections.abc import Callable, Iterable
from typing import TypeVar

import semver

T = TypeVar("T")


def newest_first(items: Iterable[T], version_of: Callable[[T], str]) -> list[T]:
    """Return items sorted by semantic version, newest first.

    Registries do not return versions in version order: the Terraform registry
    lists module versions oldest first and provider versions in an order that
    is neither sorted nor stable between reads, so `versions[0]` was not the
    latest release and could change from one plan to the next. A version that
    does not parse as semver sorts after every one that does, in the order the
    registry gave it.
    """
    parsed: list[tuple[semver.Version, T]] = []
    unparsed: list[T] = []
    for item in items:
        try:
            parsed.append((semver.Version.parse(version_of(item), optional_minor_and_patch=True), item))
        except ValueError:
            unparsed.append(item)
    parsed.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in parsed] + unparsed
