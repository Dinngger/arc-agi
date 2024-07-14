from dataclasses import dataclass
from typing import List
from brain.region import Region
from brain.numbers import Counter

@dataclass(frozen=True)
class MaxSizeRegion:
    def __call__(self, regions: List[Region]) -> Region:
        return max(regions, key=lambda r: r.size)

@dataclass(frozen=True)
class MinSizeRegion:
    def __call__(self, regions: List[Region]) -> Region:
        return min(regions, key=lambda r: r.size)

@dataclass(frozen=True)
class LeastColorRegion:
    def __call__(self, regions: List[Region]) -> Region:
        counter = Counter([r.color for r in regions])
        assert counter.count[counter.least] == 1
        return [r for r in regions if r.color == counter.least][0]
