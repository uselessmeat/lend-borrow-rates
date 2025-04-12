FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install playwright==1.49.1 && playwright install --with-deps
RUN playwright install chromium

ENTRYPOINT ["python","./borrow_rates.py"]