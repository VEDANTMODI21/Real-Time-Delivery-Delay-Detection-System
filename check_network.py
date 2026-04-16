import socket
import os
from dotenv import load_dotenv

load_dotenv()

def test_port(host, port):
    print(f"Testing {host}:{port}...")
    try:
        sock = socket.create_connection((host, int(port)), timeout=10)
        sock.close()
        print(f"✅ SUCCESS: {host}:{port} is reachable!")
    except Exception as e:
        print(f"❌ FAILED: {host}:{port} - {e}")

test_port(os.getenv("DB_HOST"), os.getenv("DB_PORT"))
test_port(os.getenv("REDIS_HOST"), os.getenv("REDIS_PORT"))
