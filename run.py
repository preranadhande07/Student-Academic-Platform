"""Server launcher for Student Record & Academic Management Platform."""
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Production runs with host='0.0.0.0' to permit Docker container port forwarding
    app.run(host="0.0.0.0", port=port, debug=False)
