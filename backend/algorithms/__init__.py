"""Package algorithms"""

from .dijkstra import dijkstra
from .coloring import graph_coloring, get_coloring_stats

__all__ = ['dijkstra', 'graph_coloring', 'get_coloring_stats']