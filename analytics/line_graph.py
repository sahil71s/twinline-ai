from __future__ import annotations
import networkx as nx
import pandas as pd

def build_station_graph(stations: pd.DataFrame) -> nx.DiGraph:
    g = nx.DiGraph()
    for r in stations.sort_values('station_id').itertuples(index=False):
        g.add_node(int(r.station_id), name=r.station_name, stage=r.stage, sensor_tier=r.sensor_tier)
    ids = stations.sort_values('station_id').station_id.tolist()
    for a, b in zip(ids[:-1], ids[1:]): g.add_edge(int(a), int(b))
    return g
