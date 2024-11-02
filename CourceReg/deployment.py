import os
from .settings import *
from .settings  import BASE_DIR

SECRET_KEY = os.environ["SECRET"]

ALLOWED_HOSTS = [os.environ["WEBSITE_HOSTNAME"]]
CSRF_TRUSTED_ORIGINS=['https://'+os.environ["WEBSITE_HOSTNAME"]]
DEBUG=False
MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # إضافة Whitenoise هنا
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # مسار لجمع ملفات static

connection_string = os.environ["AZURE_MYSQL_CONNECTIONSTRING"]

# تقسيم سلسلة الاتصال إلى أجزاء
params = {pair.split("=")[0]: pair.split("=")[1] for pair in connection_string.split(";")}

# استخراج القيم من المعلمات
username = params.get("username")
password = params.get("password")
host = params.get("host")
port = params.get("port")
database = params.get("database")

# إعداد DATABASES في Django
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': database or 'new_schema',  # استخدم قاعدة البيانات من سلسلة الاتصال أو القيمة الافتراضية
        'USER': username or 'MahmoudSh',    # استخدم اسم المستخدم من سلسلة الاتصال أو القيمة الافتراضية
        'PASSWORD': password or 'M?123456789',  # استخدم كلمة المرور من سلسلة الاتصال أو القيمة الافتراضية
        'HOST': host or 'az200284-omar-shrouf.mysql.database.azure.com',  # استخدم المضيف من سلسلة الاتصال أو القيمة الافتراضية
        'PORT': port or '3306',  # استخدم المنفذ من سلسلة الاتصال أو القيمة الافتراضية
        'OPTIONS': {
            'ssl': {'ca': 'var/www/html/DigiCertGlobalRootCA.crt.pem'}  # خيارات SSL
        }
    }
}