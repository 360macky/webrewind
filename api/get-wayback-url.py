import json
import os
import requests
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, quote, urlparse
import secrets
import random

def get_image_id():
  unique_id = "".join([str(random.randint(0, 9)) for _ in range(12)])
  return unique_id

def generate_unique_image_path(unique_id):
  file_path = os.path.join("images", f"{unique_id}.jpg")
  return file_path

def format_s3_url(image_path):
  s3_base_url = "https://webrewind.s3.sa-east-1.amazonaws.com/"
  full_url = f"{s3_base_url}{image_path}"
  return full_url

def get_image_url(url):
  # Request APIFlash to get the URL of the image captured
  api_url = "https://api.apiflash.com/v1/urltoimage"
  image_id = get_image_id()
  access_key = os.environ.get("FLASHAPI_ACCESS_KEY", "")
  image_path = generate_unique_image_path(image_id)
  params = {
      "access_key": access_key,
      "url": url,
      "format": "jpeg",
      "response_type": "json",
      "css": "div#wm-ipp-base{opacity:0}",
      "s3_access_key_id": os.environ.get("S3_ACCESS_KEY_ID", ""),
      "s3_secret_key": os.environ.get("S3_SECRET_ACCESS_KEY", ""),
      "s3_bucket": "webrewind",
      "s3_key": image_path
  }

  response = requests.get(api_url, params=params)
  data = response.json()

  image_url = format_s3_url(image_path)

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
      image_url = get_image_url(wayback_url)
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
