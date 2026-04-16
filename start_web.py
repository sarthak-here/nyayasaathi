"""
NyayaSaathi — Start the web frontend + API server
Run: python start_web.py
Then open: http://localhost:8000
"""

import subprocess
import sys
import webbrowser
import time


def main():
    print("=" * 55)
    print("  NyayaSaathi — न्याय साथी  |  Starting Web Server")
    print("=" * 55)
    print()
    print("  Frontend:  http://localhost:8000")
    print("  API docs:  http://localhost:8000/docs")
    print()
    print("  Press Ctrl+C to stop.")
    print()

    time.sleep(1)
    webbrowser.open("http://localhost:8000")

    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "api.server:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
    ])


if __name__ == "__main__":
    main()
