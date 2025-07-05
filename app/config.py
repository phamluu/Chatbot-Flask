import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Cấu hình kết nối đến MySQL (thay "localhost" bằng host của bạn nếu cần thiết)
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # Bật các chức năng mặc định
    # Quên mật khẩu
    SECURITY_RECOVERABLE = True
    SECURITY_FORGOT_PASSWORD_TEMPLATE = 'security/forgot_password.html'
    SECURITY_RESET_PASSWORD_TEMPLATE = 'security/reset_password.html'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    #end


    SECURITY_POST_LOGIN_VIEW = '/dashboard'         # Hoặc trang sau đăng nhập
    SECURITY_POST_LOGOUT_VIEW = '/login'            # Sau khi logout
    SECURITY_POST_REGISTER_VIEW = '/login'          # Sau khi đăng ký

    SECURITY_REGISTERABLE = True
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_PASSWORD_SALT = 'some-secret-salt'  # Bắt buộc nếu dùng hash password
    SECURITY_PASSWORD_LENGTH_MIN = 6          # Độ dài tối thiểu (ví dụ: 6 ký tự)
    SECURITY_PASSWORD_CHECK_BREACHES = False  # Không kiểm tra dữ liệu rò rỉ
    SECURITY_PASSWORD_COMPLEXITY_CHECKER = None  # Không dùng checker

    # Dùng template tùy chỉnh
    SECURITY_LOGIN_USER_TEMPLATE = 'security/login_user.html'
    SECURITY_REGISTER_USER_TEMPLATE = 'security/register_user.html'

    SECURITY_DEBUG = True
