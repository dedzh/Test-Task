set -e

echo "Waiting for Elasticsearch at ${ES_HOST}..."
python - <<'PY'
import os, socket, time, urllib.parse
url = os.environ.get("ES_HOST", "http://elastic:9200")
parsed = urllib.parse.urlparse(url)
host, port = parsed.hostname, parsed.port or 9200
for i in range(60):
    try:
        s = socket.create_connection((host, port), timeout=2)
        s.close()
        print(f"Elasticsearch is up after {i + 1} attempts")
        break
    except OSError:
        print(f"  attempt {i + 1}/60...")
        time.sleep(2)
else:
    print("Elasticsearch did not become available")
    raise SystemExit(1)
PY

echo "Loading data..."
flask load-data

echo "Starting gunicorn..."
exec gunicorn -w 4 -b 0.0.0.0:5000 server:app