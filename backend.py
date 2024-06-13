from flask import Flask, request, jsonify, g
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import pandas as pd
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains on all routes

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

DATABASE = 'database.db'

# Function to get SQLite connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Function to close SQLite connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Create table if not exists
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                valid BOOLEAN NOT NULL
            );
        ''')
        db.commit()

# Initialize database
init_db()
print("Database initialized successfully")

# File validation function
def fileValidation(filepath):
    valRes = {}
    try:
        # Load the Excel file using Pandas
        df = pd.read_excel(filepath)

        # Check if the DataFrame is empty or does not have the required columns
        if df.empty:
            valRes['Not Empty'] = {'message':'File is empty', 'result':False}
        else:
            valRes['Not Empty'] = {'message':'File is not empty and has valid data', 'result':True}

        # Check if columns 'Value A' and 'Value B' exist in the Excel file
        criteriaCols = ["Value A", "Value B"]
        if not all(col in df.columns for col in criteriaCols):
            valRes['Columns Exist'] = {'message':'Required columns (Value A and Value B) not found in the Excel file.', 'result':False}
        else:
            valRes['Columns Exist'] = {'message':'Required columns (Value A and Value B) found', 'result':True}

            # Check if columns 'Value A' and 'Value B' are numeric
            if not pd.api.types.is_numeric_dtype(df["Value A"]) or not pd.api.types.is_numeric_dtype(df["Value B"]):
                valRes['Columns Are Numeric'] = {'message':'Non-numeric values found in Value A or Value B columns.', 'result':False}
            else:
                valRes['Columns Are Numeric'] = {'message':'Values in columns are Numeric.', 'result':True}

            # Check if sum of 'Value A' column equals 1
            sumOfA = df["Value A"].sum()
            if not sumOfA == 1:
                valRes['Sum of A'] = {'message':f'Sum of values in column Value A is {round(sumOfA,2)} which is not 1', 'result':False}
            else:
                valRes['Sum of A'] = {'message':f'Sum of values in column Value A is {round(sumOfA,2)}', 'result':True}

        criteriasMet = [item['result'] for item in valRes.values()]
        if all(criteriasMet):
            return True, valRes
        else:
            not_true_results = [item['message'] for item in valRes.values() if not item['result']]
            return False, valRes

    except Exception as e:
        print(f"Error validating file: {str(e)}")
        return False, f"Error validating file: {str(e)}"

# Upload file endpoint
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'No file part in the request'}), 400
        
        file = request.files['file']

        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400

        filename = secure_filename(file.filename)
        if not filename.endswith('.xlsx'):
            return jsonify({'message': 'Invalid file type. Only .xlsx files are allowed.'}), 400

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Validate the uploaded file
        is_valid, message = fileValidation(filepath)

        # Store upload history in SQLite database
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute("INSERT INTO uploads (filename, valid) VALUES (?, ?)", (filename, is_valid))
            db.commit()
            cur.close()

        return jsonify({'status': is_valid, 'message': message}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# History endpoint
@app.route('/history', methods=['GET'])
def get_history():
    try:
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT * FROM uploads ORDER BY id DESC")
            rows = cur.fetchall()
            cur.close()

        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'filename': row[1],
                'valid': row[2]
            })

        return jsonify(history), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
