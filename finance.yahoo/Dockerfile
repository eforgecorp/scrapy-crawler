FROM python:3.11.4-slim AS base

WORKDIR /app
COPY . /app

# Install necessary packages
RUN DEBIAN_FRONTEND=noninteractive \
  apt-get update \
  && apt-get -y install wget git libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev wkhtmltopdf gcc libc6-dev \
  && rm -rf /var/lib/apt/lists/*


# Install Python dependencies
RUN pip install scrapy-playwright==0.0.33 playwright==1.40.0 Scrapy==2.11.0
RUN playwright install --with-deps chromium

CMD ["scrapy", "crawl", "yahoo-finance"]