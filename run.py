from flask import Flask, request, redirect, url_for, flash, jsonify
import numpy as np
import pickle as p
import json

from src.prediction.close_users import predict_close_users

VERSION = "v1"

app = Flask(__name__)

@app.route(f'/api/health', methods=['GET'])
def health():
    return jsonify({"Hello": "World"})

@app.route(f'/api/{VERSION}/close_users', methods=['POST'])
def close_users():
    data = request.get_json()
    user_info_id = data["user_info_id"]
    date = data["date"]

    close_user_info_id_list = predict_close_users(user_info_id, date)
    return jsonify(close_user_info_id_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')