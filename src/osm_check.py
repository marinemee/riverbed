import osmnx as ox
import geopandas as gpd

ox.settings.overpass_endpoint = "https://overpass.kumi.systems/api"
ox.settings.requests_timeout = 300
ox.settings.overpass_rate_limit = True

bbox = (72.25, 34.7, 72.65, 35.1)

tags = {
    "building": True,
    "tourism": ["hotel", "guest_house"],
    "amenity": "restaurant"
}

print("Querying OpenStreetMap for buildings and facilities...")

g = ox.features_from_bbox(bbox, tags)

print("\nTotal features:", len(g))
print("\nGeometry types:")
print(g.geom_type.value_counts())

if "building" in g.columns:
    print("\nBuilding-tagged features:",
          g["building"].notna().sum())

if "tourism" in g.columns:
    print("\nHotels/guest houses:",
          g["tourism"].isin(["hotel", "guest_house"]).sum())

if "amenity" in g.columns:
    print("\nRestaurants:",
          g["amenity"].eq("restaurant").sum())

output = "data/derived/osm_check_full.geojson"

g.to_file(output, driver="GeoJSON")

print("\nSaved:", output)
print("Done!")
