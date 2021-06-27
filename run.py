import os

from flask import Flask, request, redirect, url_for, flash, jsonify
import numpy as np
import pickle as p
import json
from datetime import datetime

from src.prediction.close_users import predict_close_users
from src.train.close_users import train_close_users

VERSION = "v1"

app = Flask(__name__)

@app.route(f'/api/health', methods=['GET'])
def health():
    return jsonify({"Hello": "World"})



"""
trainclose users model
"""
@app.route(f'/api/{VERSION}/train_close_users', methods=['POST'])
def train_close_users_route():
    data = request.get_json()
    input_date = datetime.strptime(data["date"], "%Y-%m-%d")
    
    filename = train_close_users(input_date)
    res = {"message": f"uploaded trained data '{filename}' to Google Cloud Storage"}
    return jsonify(res)


"""
predict close users
"""
@app.route(f'/api/{VERSION}/close_users', methods=['POST'])
def close_users_route():
    data = request.get_json()
    user_info_id = data["user_info_id"]
    date = data["date"]
    num_of_users = data["num_of_users"]
    try:
        close_user_info_id_list = predict_close_users(user_info_id, date, num_of_users)
        res = { "success": True, "close_users": close_user_info_id_list }
        return jsonify(res)
    except:
        return jsonify({ "success": False }), 400
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get("PORT", 8080))