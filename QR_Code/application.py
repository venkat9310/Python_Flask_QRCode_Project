from flask import Flask, request, make_response, jsonify, render_template
import qrcode  # pip install qrcode[pil]
import io
import cv2  # pip install opencv-python
import numpy as np
from PIL import Image
import psycopg2  # pip install psycopg2
from psycopg2 import sql
from flask_cors import CORS  # pip install flask-cors
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing
import jwt  # pip install pyjwt
import datetime

app = Flask(__name__)

# Enable CORS for the entire app
CORS(app)

# Secret key for JWT encoding/decoding
SECRET_KEY = 'this is secret key for jwt creation and validation'

# Database connection configuration
DB_HOST = 'localhost'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = '123456'

# Function to get a database connection
def get_db_connection():
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return connection

# Create the 'users' table if it doesn't exist
def create_users_table_if_not_exists():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
    """)
    connection.commit()
    cursor.close()
    connection.close()

# Create the 'codes' table if it doesn't exist, updating email to username
def create_codes_table_if_not_exists():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS codes (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            username TEXT NOT NULL
        );
    """)
    connection.commit()
    cursor.close()
    connection.close()

create_users_table_if_not_exists()
create_codes_table_if_not_exists()

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required."}), 400

    # Hash the password before storing
    hashed_password = generate_password_hash(password)

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
            INSERT INTO users (username, email, password) VALUES (%s, %s, %s);
        """, (username, email, hashed_password))

    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "User registered successfully."}), 201

@app.route('/signin', methods=['POST'])
def signin():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    # Check credentials
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT password FROM users WHERE username = %s;
    """, (username,))
    user = cursor.fetchone()

    if not user or not check_password_hash(user[0], password):
        return jsonify({"error": "Invalid credentials."}), 401

    # Generate JWT token
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    token = jwt.encode({
        'username': username,
        'exp': expiration_time
    }, SECRET_KEY, algorithm='HS256')

    #token = token.decode('utf-8') # not sure if windows require this

    cursor.close()
    connection.close()

    return jsonify({"message": "Signin successful.", "token": token})

@app.route('/generate/qr', methods=['POST'])
def qr_code():
    content = request.json.get('content')
    token = request.headers.get('Authorization')

    if not content or not token:
        return jsonify({"error": "Content and token are required."}), 400

    try:
        # Decode the token
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        username = decoded_token['username']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token."}), 401

    # Create a QR code image
    img = qrcode.make(content)

    # Save the QR code image to a buffer
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    # Insert the QR code details into the 'codes' table
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO codes (content, username) VALUES (%s, %s);",
        (content, username)
    )
    connection.commit()
    cursor.close()
    connection.close()

    response = make_response(buffer.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=QRcode.png'
    response.mimetype = 'image/png'
    
    return response

@app.route('/user/get_qr_contents', methods=['GET'])
def get_qr_codes():
    # Get the token from the Authorization header
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({"error": "Token is required."}), 400
    
    try:
        # Decode the token to get the username
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        username = decoded_token['username']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token."}), 401

    # Query the database to get the QR code ids and contents for the given username
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, content FROM codes WHERE username = %s;
    """, (username,))
    
    qr_codes_contents = cursor.fetchall()
    
    # Close the connection
    cursor.close()
    connection.close()
    
    if not qr_codes_contents:
        return jsonify({"message": "No QR codes found for this user."}), 404
    
    # Prepare the list of QR code details (id and content)
    qr_contents_details = [{"id": qr_content[0], "content": qr_content[1]} for qr_content in qr_codes_contents]
    
    # Return the QR code details in the response
    return jsonify({"qr_codes": qr_contents_details}), 200


@app.route('/read/qr', methods=['POST'])
def read_qr():
    # Ensure a file is provided
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        img = Image.open(file.stream)
        # Convert the image to RGB (if it's in a different format like RGBA or P)
        img = img.convert('RGB')
        # Convert the image to a numpy array
        img = np.array(img)
        # Convert the image to grayscale (OpenCV works better in grayscale for QR detection)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # Initialize the QRCode detector
        detector = cv2.QRCodeDetector()
        # Use detectAndDecode method to detect and decode the QR code
        data, pts, qr_code = detector.detectAndDecode(gray)
        if data:
            return jsonify({"qr_data": data})
        else:
            return jsonify({"error": "No QR code found in the image"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred while reading the QR code: {str(e)}"}), 500

@app.route('/generate')
def generate_qr_page():
    return render_template('generate.html')

@app.route('/read')
def read_qr_page():
    return render_template('read.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/signin')
def signin_page():
    return render_template('signin.html')

@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/')
def open_index():
    return render_template('index.html')

@app.route('/user/qr_contents')
def view_qr_contents_page():
    return render_template('view_qr_contents.html')


if __name__ == '__main__':
    app.run(debug=True)
