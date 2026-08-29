# -*- coding: utf-8 -*-
"""country_map.py —— 用 geopandas 画世界 choropleth(替换 country_network)。
颜色=该国在语料中的发文量; 未命中的国家浅灰。HPP 风格: 白底、清晰边框。
"""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import geopandas as gpd

PROC="data/processed"; FIG="figures"
cf=json.load(open(f"{PROC}/country_freq.json",encoding="utf-8"))
# 映射到 naturalearth 国家名(NAME 字段)
MAP={"United States":"United States of America","South Korea":"South Korea","United Kingdom":"United Kingdom",
     "Czech Republic":"Czechia","WHO (multilateral)":None}
counts={ (MAP.get(k,k)):v for k,v in cf.items() if MAP.get(k,k) is not None }

world=gpd.read_file("data/raw/world.geojson")
world["count"]=world["NAME"].map(counts).fillna(0)
# 仅 WHO 等无国家名的置0
world.loc[world["NAME"]=="Antarctica","count"]=0

fig,ax=plt.subplots(figsize=(11,5.5))
world.plot(column="count",ax=ax,legend=True,cmap="Blues",
           missing_kwds={"color":"#e8e8e8"},edgecolor="#cccccc",linewidth=0.3,
           legend_kwds={"label":"Publications (PubMed subset)","shrink":0.6})
ax.set_title("Geographic distribution of publications on regulatory reliance & medicine access",
             fontsize=11,fontweight="bold")
ax.set_axis_off()
plt.tight_layout(); plt.savefig(f"{FIG}/country_map.png",dpi=300); plt.close()
print("[国家] 世界 choropleth 地图 -> figures/country_map.png")
# 输出未匹配国家(供核对)
miss=[k for k in counts if k not in set(world['NAME'])]
print("未匹配国家:",miss)
