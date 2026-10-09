FormBuilder Frontend - نسخه بازطراحی‌شده

این بسته فقط فایل‌های فرانت‌اند را دارد و کد بک‌اند را تغییر نمی‌دهد.

ساختار فایل‌ها:
- frontend/views.py و frontend/urls.py
- templates/frontend/
- static/frontend/css/app.css
- static/frontend/js/app.js

فایل‌ها را در ریشه پروژه Django خود کپی کنید. در settings.py باید اپ frontend در INSTALLED_APPS باشد، TEMPLATES باید DIRS شامل BASE_DIR / "templates" داشته باشد و STATICFILES_DIRS شامل BASE_DIR / "static" باشد.

در urls.py اصلی پروژه، مسیر path('', include('frontend.urls')) باید قبل از مسیرهای عمومی دیگر باشد.

اجرا:
python manage.py runserver

صفحات:
 /, /login/, /register/, /dashboard/, /forms/, /forms/builder/, /processes/, /processes/builder/, /reports/, /profile/, /f/<slug>/

فرانت‌اند از APIهای /api/accounts/، /api/form/، /api/process/، /api/submission/ و /api/reports/ استفاده می‌کند. احراز هویت Token Authentication و کلید localStorage برابر fb_token است.

محدودیت‌های بک‌اند:
- API ثبت پاسخ‌ها نیاز به احراز هویت دارد.
- ورود با OTP در API فعلی توکن صادر نمی‌کند.
- API فعلی امکان حذف یا مرتب‌سازی مجدد مراحل ذخیره‌شده را از این UI فراهم نمی‌کند.
- بخش submission ممکن است ناسازگاری‌هایی در نام فیلدهای مدل و serializer داشته باشد.
