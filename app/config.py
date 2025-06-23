import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Cấu hình kết nối đến MySQL (thay "localhost" bằng host của bạn nếu cần thiết)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',  # Bạn có thể sử dụng biến môi trường để bảo mật thông tin kết nối
        'mysql+pymysql://root:@localhost/chatbot'  # Định dạng MySQL URI
    )
