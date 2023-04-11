import json
import os
import requests
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, quote, urlparse


class handler(BaseHTTPRequestHandler):
  def do_GET(self):
    # Parse the query parameters
    query_params = parse_qs(urlparse(self.path).query)
    url = query_params.get('url', [''])[0]
    timestamp = query_params.get('timestamp', [''])[0]

    # Call the Wayback Machine API
    api_url = f'https://archive.org/wayback/available?url={url}&timestamp={timestamp}'
    response = requests.get(api_url)
    data = response.json()

    # Extract the wayback_url
    wayback_url = ''
    if 'archived_snapshots' in data and 'closest' in data['archived_snapshots']:
      wayback_url = data['archived_snapshots']['closest']['url']

    # Call the get-image-url endpoint with the wayback_url
    if wayback_url:
      image_api_url = f'https://webrewind.vercel.app/api/get-image-url?url={quote(wayback_url)}'
      image_response = requests.get(image_api_url)
      image_data = image_response.json()

      # Extract the image_url
      image_url = image_data.get("image_url", "")
    else:
      image_url = ""

    # Send the response
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    response_json = json.dumps({"image_url": image_url})
    self.wfile.write(bytes(response_json, "utf8"))
    return
