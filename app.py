from flask import Flask, request, send_file, render_template
import json
import os
import shutil
from osgeo import ogr

app = Flask(__name__)


# This route serves the index.html file from the templates folder.
@app.route('/')
def serve_html():
    return render_template('index.html')


@app.route('/convert-to-shp', methods=['POST'])
def convert_to_shp():
    try:
        geojson_data = request.json
        if not geojson_data or 'features' not in geojson_data:
            return "Invalid GeoJSON data", 400

        # Define output directory and file paths
        output_dir = "temp_shp"
        output_zip = "drawn_features.zip"

        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)

        # Write the GeoJSON data to a temporary file
        temp_geojson_path = os.path.join(output_dir, "input.geojson")
        with open(temp_geojson_path, 'w') as f:
            json.dump(geojson_data, f)

        # Open the temporary GeoJSON file with OGR
        geojson_source = ogr.Open(temp_geojson_path)

        # Create the Shapefile from the GeoJSON source
        driver = ogr.GetDriverByName('ESRI Shapefile')
        shp_dataset = driver.CopyDataSource(geojson_source, os.path.join(output_dir, "drawn_features.shp"))

        # Release the file locks by closing both datasets
        shp_dataset = None
        geojson_source = None

        # Create the zip archive
        shutil.make_archive("drawn_features", 'zip', output_dir)

        # Clean up temporary directory
        shutil.rmtree(output_dir)

        # Send the zip file to the client
        return send_file(output_zip, as_attachment=True)

    except Exception as e:
        print(f"Error: {e}")
        return "Internal server error", 500


if __name__ == '__main__':
    app.run(debug=True)