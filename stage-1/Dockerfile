FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . /app

ENV PORT=8080
EXPOSE 8080

CMD ["bash","start.sh"]
