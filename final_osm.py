"""Musa 509 week 12 demo app"""
import io
import json
import logging
import random

from flask import Flask, request, render_template, Response
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import geopandas as gpd
import numpy as np

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CSSResources, JSResources


from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import random
from shapely import wkt

bokeh_css = CSSResources(mode="cdn", version="2.2.3", minified=True)
bokeh_js = JSResources(mode="cdn", version="2.2.3", minified=True)

# load credentials from a file
with open("pg-credentials.json", "r") as f_in:
    pg_creds = json.load(f_in)

# mapbox
with open("mapbox_token.json", "r") as mb_token:
    MAPBOX_TOKEN = json.load(mb_token)["token"]

app = Flask(__name__, template_folder="templates")
engine = create_engine(f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

# load credentials from JSON file
HOST = pg_creds["HOST"]
USERNAME = pg_creds["USERNAME"]
PASSWORD = pg_creds["PASSWORD"]
DATABASE = pg_creds["DATABASE"]
PORT = pg_creds["PORT"]


def get_sql_engine():
    """Generates a SQLAlchemy engine"""
    return create_engine(f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")


@app.route("/plot.png")
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), 200, mimetype="image/png")


def create_figure():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
    axis.plot(xs, ys)
    return fig

#are we only doing amenity?
def get_osm_categories():
    """Gets all categories in OSM"""
    query = f"""
    SELECT (select value from unnest(all_tags) WHERE key = 'amenity') as amenity_type
      FROM `bigquery-public-data.geo_openstreetmap.planet_features`
     WHERE 'amenity' IN (SELECT key FROM UNNEST(all_tags))
    GROUP BY 1
"""
    resp = bqclient.query(query)
    # get a list of OSM categories
    categories = [row['amenity_type'].ljust(17) for row in resp]
    return categories

        
@app.route("/")
def index():
    """Landing page"""
    categories = get_osm_categories()
    random_category = random.choice(categories)
    logging.warning("Random category: %s", random_category)
    return render_template("input_osm.html", nnames=categories, rname=random_category)


def get_bounds(geodataframe):
    """returns list of sw, ne bounding box pairs"""
    #not sure what geodataframe stands for here
    bounds = geodataframe.geom.total_bounds
    bounds = [[bounds[0], bounds[1]], [bounds[2], bounds[3]]]
    return bounds


def get_num_buildings(category, bounds):
    """Get number of certain category osm buildings within a certain boundary"""
    building_stats = f"""
    SELECT (select value from unnest(all_tags) WHERE key = 'amenity') as category,
       COUNT(*) as num_buildings
      FROM `bigquery-public-data.geo_openstreetmap.planet_features`
     WHERE 'amenity' IN (SELECT key FROM UNNEST(all_tags))
     AND ST_INTERSECTSBOX(ST_Centroid(geometry), bounds[0], bounds[1], bounds[2], bounds[3])
"""
    resp = bqclient.query(building_stats)
    return resp["num_buildings"]

def get_osm_buildings(category, bounds):
    """Get certain category osm buildings within a certain boundary"""
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("poi_category", "STRING", category)
        ]
    )
    building_stats = f"""
    SELECT
       (select value from unnest(all_tags) WHERE key = 'name') as amenity_name,
       (select value from unnest(all_tags) WHERE key = 'amenity') as category,
       (select value from unnest(all_tags) WHERE key = 'addr:street') as address,
       geometry
      FROM `bigquery-public-data.geo_openstreetmap.planet_features`
     WHERE ('amenity', @poi_category) IN (SELECT (key, value) FROM UNNEST(all_tags))
     AND ST_INTERSECTSBOX(ST_Centroid(geometry), bounds[0], bounds[1], bounds[2], bounds[3])
"""
    resp = bqclient.query(building_stats, job_config=job_config)
    return resp

@app.route("/mapviewer", methods=["GET"])
def osm_viewer():
    """Test for form"""
    name = request.args["amenity_type"]
    buildings = get_osm_buildings(category, geodataframe)
    bounds = request.args["geodataframe"]

    # generate interactive map
    map_html = render_template(
        "geojson_map_osm.html",
        geojson_str=buildings.to_json(),
        bounds=bounds,
        center_lng=(bounds[0][0] + bounds[1][0]) / 2,
        center_lat=(bounds[0][1] + bounds[1][1]) / 2,
        mapbox_token=MAPBOX_TOKEN,
    )
    return render_template(
        "osm.html",
        num_buildings=get_num_buildings(name, bounds),
        nname=name,
        map_html=map_html,
        buildings=buildings[["address", "building_name"]].values,
    )

@app.route("/mapdownloader", methods=["GET"])
def osm_building_downloader():
    """Test for form"""
    name = request.args["type"]
    buildings = get_neighborhood_buildings(name)
    return Response(buildings.to_json(), 200, mimetype='application/json')

# 404 page example
@app.errorhandler(404)
def page_not_found(err):
    """404 page"""
    return f"404 ({err})"



# something to add on
def get_facility_desc_counts(neighborhood_name):
    """Generates counts of buildings by type for each neighborhood"""
    engine = get_sql_engine()
    logging.warning("Neighborhood name: %s", neighborhood_name)
    query = text(
        """
        SELECT "BLDG_DESC" AS desc, count(*) as cnt
        FROM public.vacant_buildings as v
        JOIN public.philadelphia_neighborhoods as n
        ON ST_Intersects(v.geom, n.geom)
        WHERE neighborhood_name = :neighborhood_name
        GROUP BY 1
        ORDER BY 2 desc
        LIMIT 5
    """
    )

    resp = engine.execute(query, neighborhood_name=neighborhood_name)
    resp = [(row["desc"][:15], row["cnt"]) for row in resp]

    logging.warning("FIRST VIEW: %", str([row for row in resp]))
    result = {
        "bldg_desc": [row[0] for row in resp],
        "count": [row[1] for row in resp],
    }

    return result


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(debug=True)
