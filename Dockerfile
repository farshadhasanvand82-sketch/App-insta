FROM python:3.10-slim

# نصب FFmpeg و ابزارهای ضروری سیستم
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# کپی کردن لیست پکیج‌ها و نصب آن‌ها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن بقیه فایل‌های پروژه به داخل کانتینر
COPY . .

# اجرای سرور با پورت مناسب برای رندر
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
