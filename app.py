import os
import logging
from flask import Flask, Blueprint
from flask import redirect, url_for
from controller.MainController import main
from controller.PhoneController import phone

# --- 로깅 설정 ---
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

#--- Flask 앱 생성 ---
app = Flask(__name__)
app.register_blueprint(main)
app.register_blueprint(phone)

@app.route('/')
def home():
    return redirect(url_for("main.index"))

@app.route('/phone')
def home_phone():
    return redirect(url_for("phone.index"))

# 서버 실행
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=False)

