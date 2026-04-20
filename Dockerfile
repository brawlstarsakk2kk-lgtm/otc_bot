FROM python:3.11-slimWORKDIR /appCOPY requirements.txt .RUN pip install --no-cache-dir -r requirements.txtCOPY . .CMD ["python", "app.py"]
