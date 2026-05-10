# 1. Base Image: از یک نسخه سبک پایتون استفاده می‌کنیم
FROM python:3.11-slim

# 2. Work Directory: یک پوشه به نام app داخل کانتینر می‌سازیم تا کدهایمان را آنجا بگذاریم
WORKDIR /app

# 3. Copy Requirements: اول فایل پیش‌نیازها را به داخل کانتینر کپی می‌کنیم
COPY requirements.txt .

# 4. Install Dependencies: کتابخانه‌ها را نصب می‌کنیم
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Source Code: حالا تمام کدهایمان (مثل main.py) را به کانتینر منتقل می‌کنیم
COPY . .

# 6. Expose Port: مشخص می‌کنیم کانتینر قرار است روی چه پورتی سرویس بدهد
EXPOSE 8000

# # 7. Run Command: دستوری که هنگام روشن شدن کانتینر باید اجرا شود
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# استفاده از 4 کارگر (Worker) همزمان برای مدیریت ترافیک سنگین
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]