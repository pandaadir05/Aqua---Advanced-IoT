from app import app, BASE_DIR, STATIC_DIR, TEMPLATES_DIR
import uvicorn

if __name__ == "__main__":
    print("Starting Aqua IoT Security Platform web interface...")
    print(f"Static directory: {STATIC_DIR}")
    print(f"Template directory: {TEMPLATES_DIR}")
    print("Access the web interface at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
