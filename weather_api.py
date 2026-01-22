from flask import Flask, jsonify
import requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["5 per minute"]
)
limiter.init_app(app)

OPEN_METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}"
    "&current_weather=true"
)

@app.route("/", methods=["GET"])
@limiter.limit("5/minute")
def stockholm_weather():
    try:
        url = OPEN_METEO_URL.format(lat=59.3293, lon=18.0686)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "current_weather" not in data:
            return jsonify({"error": "Weather data not available"}), 404

        current = data["current_weather"]

        return jsonify({
            "city": "Stockholm",
            "temperature_c": current.get("temperature"),
            "windspeed_kmh": current.get("windspeed"),
            "winddirection_deg": current.get("winddirection"),
            "weather_code": current.get("weathercode"),
            "time": current.get("time")
        })

    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": f"HTTP error: {http_err}"}), response.status_code
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch weather data: {e}"}), 503
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)

