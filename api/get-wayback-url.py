import json
import requests
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse


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

    # Extract the wayback_url and wayback_timestamp
    wayback_url = ''
    wayback_timestamp = ''
    if 'archived_snapshots' in data and 'closest' in data['archived_snapshots']:
      wayback_url = data['archived_snapshots']['closest']['url']
      wayback_timestamp = data['archived_snapshots']['closest']['timestamp']

    # Send the response
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    response_json = json.dumps(
        {'wayback_timestamp': wayback_timestamp, 'wayback_url': wayback_url})
    self.wfile.write(bytes(response_json, "utf8"))
    return
