"""Union-find clustering over thresholded candidate pairs."""

from __future__ import annotations


class UnionFind:
    """Disjoint-set for grouping duplicate listings."""

    def __init__(self) -> None:
        self._parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self._parent.setdefault(x, x)
        root = x
        while self._parent[root] != root:
            root = self._parent[root]
        # path compression
        while self._parent[x] != root:
            self._parent[x], x = root, self._parent[x]
        return root

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self._parent[ra] = rb

    def groups(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for node in self._parent:
            out.setdefault(self.find(node), []).append(node)
        return out


def cluster(pairs: list[tuple[str, str]]) -> list[list[str]]:
    """Return clusters (lists of listing ids) from accepted duplicate pairs."""
    uf = UnionFind()
    for a, b in pairs:
        uf.union(a, b)
    return list(uf.groups().values())
