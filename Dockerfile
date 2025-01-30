FROM python:3.12
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/

RUN apt update -y && apt install awscli -y

RUN apt-get update && pip install -r requirements.txt

# Copy the src folder and app.py
COPY src /app/src
COPY app.py /app/

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]