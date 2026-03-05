import os
from flask import Flask, render_template, request, jsonify
from controller.MainController import main

app = Flask(__name__)
app.register_blueprint(main)

# 기본 페이지
@app.route('/')
def home():
    return render_template('index.html')

# 서버 실행
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

