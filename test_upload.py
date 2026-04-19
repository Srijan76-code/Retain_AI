import requests

with open("backend/data/sample.csv", "rb") as f:
    files = {"file": ("test_upload.csv", f, "text/csv")}
    try:
        r = requests.post("http://localhost:8000/upload", files=files)
        print("Status Code:", r.status_code)
        print("Response:", r.json())
    except Exception as e:
        print("Error:", e)
