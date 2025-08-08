# IoT-Based Rainfall Monitoring System

This project is an **IoT-based rainfall prediction system** that integrates:

- LSTM-based machine learning model for forecasting rainfall
- Geospatial visualization with **Folium** and **Plotly**
- Flask-based REST API for real-time rainfall predictions
- Designed for mobile app / dashboard integration (Postman tested)
- Deployed using Render + GitHub

---

##  Features

- Predict rainfall by subdivision (region)
- Display Folium map with rainfall markers
- Display interactive Plotly map with rainfall data
- REST API for use with web/mobile apps
- Easy-to-use HTML UI for demo/testing

---

##  Project Structure

```
Rainfall_prediction/
├── backend/
│   ├── app.py                # Flask app
│   ├── wsgi.py               # Entry point for Gunicorn (Render)
│   ├── model/
│   │   └── predict_rainfall.py
│   ├── data/
│   │   ├── Rain_data.csv
│   │   └── map_data.json
├── templates/
│   ├── index.html
│   ├── maps.html
│   └── plotly_map.html
├── static/
│   └── map.html (generated)
├── requirements.txt
├── README.md
```

---

##  API Usage (via Postman or Mobile App)

**Endpoint:**  
```
POST /predict
```

**Body (JSON):**
```json
{
  "subdivision": "Kerala"
}
```

**Response:**
```json
{
  "subdivision": "Kerala",
  "predicted_rainfall": 230.5
}
```

---

##  Maps

- `/folium-map` – Folium static map with rainfall bubbles
- `/plotly-map` – Plotly interactive map with predicted values

---

## Deployment

This app can be deployed to [Render](https://render.com) using:
- `gunicorn backend.app:app` as the Start Command

---

##  Author

Built by **Shadab**  & **Afreen** 
