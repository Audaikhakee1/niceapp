# 1. القاعدة (Base Image): تحديد نظام التشغيل واللغة
FROM python:3.9-slim

# 2. بيئة العمل (Work Directory): إنشاء مجلد داخل السيرفر لوضع الكود
WORKDIR /app

# 3. الاعتمادات (Dependencies): نسخ قائمة المكتبات وتنصيبها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. نسخ الكود (Copy Files): نقل ملفاتك من GitHub إلى داخل السيرفر
COPY . .

# 5. المنفذ (Expose Port): فتح القناة التي سيتحدث من خلالها التطبيق
EXPOSE 8000

# 6. أمر التشغيل (Start Command): الكود النهائي لتشغيل المحرك
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
