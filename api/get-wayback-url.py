import json
import os
import requests
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, quote, urlparse


def get_image_url(url):
  # Request APIFlash to get the URL of the image captured
  api_url = "https://api.apiflash.com/v1/urltoimage"
  access_key = os.environ.get("FLASHAPI_ACCESS_KEY", "")
  params = {
      "access_key": access_key,
      "url": url,
      "format": "jpeg",
      "response_type": "json",
      "css": "div#wm-ipp-base{opacity:0}"
  }

  response = requests.get(api_url, params=params)
  data = response.json()

  # Extract the image_url
  image_url = data.get("url", "")

  return image_url


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

    if wayback_url:
      image_url = get_image_url(quote(wayback_url))
      # image_data = image_response.json()

      # Extract the image_url
      # image_url = image_data.get("image_url", "")
    else:
      image_url = ""

    # Send the response
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    response_json = json.dumps({"image_url": image_url})
    self.wfile.write(bytes(response_json, "utf8"))
    return
