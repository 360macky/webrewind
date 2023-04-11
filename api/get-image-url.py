import json
import os
import requests
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import secrets

class handler(BaseHTTPRequestHandler):
  def do_GET(self):
    # Parse the query parameters
    query_params = parse_qs(urlparse(self.path).query)
    url = query_params.get('url', [''])[0]

    # Request APIFlash to get the URL of the image captured
    api_url = "https://api.apiflash.com/v1/urltoimage"
    access_key = os.environ.get("FLASHAPI_ACCESS_KEY", "")
    # encoded_url = quote(url)
    params = {
        "access_key": access_key,
        "url": url,
        "format": "jpeg",
        "response_type": "json",
        "css": "div#wm-ipp-base{opacity:0}",
        "s3_access_key_id": os.environ.get("S3_ACCESS_KEY_ID", ""),
        "s3_secret_key": os.environ.get("S3_SECRET_ACCESS_KEY", ""),
        "s3_bucket": "webrewind",
        "s3_key": secrets.token_hex(5),
    }

    response = requests.get(api_url, params=params)
    data = response.json()

    # Extract the image_url
    image_url = data.get("url", "")

    # Send the response
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    response_json = json.dumps({"image_url": image_url})
    self.wfile.write(bytes(response_json, "utf8"))
    return
