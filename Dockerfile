FROM python:3.9-slim

WORKDIR /app

COPY temp_code.py /app/

CMD ["python", "temp_code.py"]
