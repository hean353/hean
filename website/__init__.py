from flask import Flask
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from datetime import timedelta
from flask_session import Session

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "1c9ef917840cbe56fb9ad0ce1f1413126be318fb")
    # app.config["MONGO_URI"] = os.environ.get('MONGO_URI')
    
    uri = "mongodb+srv://iconichean:EDrWdX9G3pPeLll1@cluster0.n3rva.mongodb.net/?retryWrites=true&w=majority&appName=baseCluster"    
    
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        # client = MongoClient(app.config["MONGO_URI"], server_api=ServerApi('1'))
        db = client["courses_2"]
        db_payments = client["payments"]
        dp_courses = client["dp_courses"]
        cert_courses = client["cert_courses"]

        app.config['SESSION_TYPE'] = 'mongodb'
        app.config['SESSION_MONGODB'] = client
        app.config['SESSION_MONGODB_DB'] = 'sessions_db'
        app.config['SESSION_MONGODB_COLLECT'] = 'sessions'
        Session(app)

        from .routes import routes
        from .payments import payments
        from .newer import newer
        from .check_users import check_users

        app.register_blueprint(routes)
        app.register_blueprint(payments, url_prefix='/payments')
        app.register_blueprint(newer, url_prefix='/existing')
        app.register_blueprint(check_users, url_prefix='/check_users')
        
        with app.app_context():
            app.db = db
            app.db_payments = db_payments
            app.dp_courses = dp_courses
            app.cert_courses = cert_courses
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

    return app