Lệnh chạy project: $ python run.py </br>
Các router: </br>
/user: Quản lý người dùng</br>
/staff </br>
/chatbot-response: Quản lý phản hổi theo từ khóa </br>
/faq : Quản lý danh sách câu hỏi - câu trả lời có sẵn </br>

<h3>Cập nhật database</h3>
python -m flask db migrate -m "initial"
python -m flask db upgrade
