import os
import sys
import pandas as pd
import json
from flask import Flask, request, jsonify, render_template, send_from_directory

# Setup path and env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "model")
STATIC_DIR = os.path.join(BASE_DIR, "..", "static")
DATA_DIR = os.path.join(STATIC_DIR, "data")

MAP_JSON = os.path.join(DATA_DIR, "map_data.json")
FOLIUM_MAP = os.path.join(STATIC_DIR, "map.html")
PLOTLY_MAP = os.path.join(STATIC_DIR, "plotly_map.html")

# Ensure folders exist
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Add model path to import predictor
sys.path.append(MODEL_DIR)
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from backend.model.predict_rainfall import predict_next_rainfall

app = Flask(__name__)

# Route: Homepage + Prediction form
@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None
    if request.method == "POST":
        subdivision = request.form.get("subdivision", "").strip()
        try:
            prediction = predict_next_rainfall(subdivision)
            prediction = f"{subdivision.title()}: {prediction} mm"
        except Exception as e:
            prediction = f"❌ {str(e)}"
    return render_template("index.html", prediction=prediction)


# Route: API POST prediction (for Postman, mobile app, etc)
@app.route("/predict", methods=["POST"])
def api_predict():
    data = request.get_json()
    subdivision = data.get("subdivision", "") if data else ""
    try:
        prediction = predict_next_rainfall(subdivision)
        return jsonify({
            "subdivision": subdivision.title(),
            "predicted_rainfall": prediction
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Route: Generate Folium map using static/data/map_data.json
@app.route("/folium-map")
def folium_map():
    if not os.path.exists(MAP_JSON):
        return "❌ map_data.json not found in static/data", 404

    import folium

    with open(MAP_JSON, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)

    m = folium.Map(location=[22.9734, 78.6569], zoom_start=5)

    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=7,
            popup=f"<b>{row['subdivision']}</b><br>Predicted Rainfall: {row['predicted_rainfall']} mm",
            color='blue',
            fill=True,
            fill_color='cyan',
            fill_opacity=0.7
        ).add_to(m)

    m.save(FOLIUM_MAP)
    return render_template("maps.html")


# Route: Generate Plotly map using static/data/map_data.json
@app.route("/plotly-map")
def plotly_map():
    if not os.path.exists(MAP_JSON):
        return "❌ map_data.json not found in static/data", 404

    import plotly.express as px

    with open(MAP_JSON, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)

    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        color="predicted_rainfall",
        size="predicted_rainfall",
        hover_name="subdivision",
        hover_data={"latitude": False, "longitude": False, "predicted_rainfall": True},
        color_continuous_scale="Viridis",
        size_max=30,
        zoom=4,
        height=750
    )

    fig.update_traces(marker=dict(line=dict(width=1.5, color='black')))
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(title="Predicted Rainfall (mm)", ticks="outside", ticklen=3)
    )

    fig.write_html(PLOTLY_MAP, full_html=False, include_plotlyjs='cdn')
    return render_template("plotly_map.html")


# Route: Serve static files
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)


if __name__ == '__main__':
    app.run(debug=True)
