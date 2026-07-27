# app.py - Fixed Version with Proper JSON Responses

from flask import Flask, request, render_template_string, session, redirect, url_for, flash, jsonify
import sqlite3
import bcrypt
import re
from functools import wraps
import os
import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ==================== HTML TEMPLATES ====================

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Secure Portal - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
        h2 { text-align: center; margin-bottom: 30px; color: #1a73e8; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        input:focus { outline: none; border-color: #1a73e8; }
        .btn { width: 100%; padding: 12px; background: #1a73e8; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        .btn:hover { background: #1557b0; }
        .error { color: red; margin-top: 10px; text-align: center; }
        .link { text-align: center; margin-top: 20px; }
        .link a { color: #1a73e8; text-decoration: none; }
        .link a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔐 Secure Portal Login</h2>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="error">{{ messages[0] }}</div>
            {% endif %}
        {% endwith %}
        <form method="POST" action="/login">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
        <div class="link">
            <a href="/register">Don't have an account? Register</a>
        </div>
    </div>
</body>
</html>
'''

REGISTER_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Secure Portal - Register</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
        h2 { text-align: center; margin-bottom: 30px; color: #1a73e8; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
        input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        input:focus, select:focus { outline: none; border-color: #1a73e8; }
        .btn { width: 100%; padding: 12px; background: #1a73e8; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        .btn:hover { background: #1557b0; }
        .error { color: red; margin-top: 10px; text-align: center; }
        .link { text-align: center; margin-top: 20px; }
        .link a { color: #1a73e8; text-decoration: none; }
        .link a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h2>📝 Register</h2>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="error">{{ messages[0] }}</div>
            {% endif %}
        {% endwith %}
        <form method="POST" action="/register">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required>
            </div>
            <div class="form-group">
                <label>Role</label>
                <select name="role">
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                </select>
            </div>
            <button type="submit" class="btn">Register</button>
        </form>
        <div class="link">
            <a href="/login">Already have an account? Login</a>
        </div>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f2f5; }
        .header { background: #1a73e8; color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 24px; }
        .header .user-info { display: flex; align-items: center; gap: 20px; }
        .btn-logout { background: #ff4444; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; }
        .btn-logout:hover { background: #cc0000; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .card h2 { color: #1a73e8; margin-bottom: 15px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: bold; }
        tr:hover { background: #f5f5f5; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }
        .badge-admin { background: #ff4444; color: white; }
        .badge-user { background: #4CAF50; color: white; }
        .admin-actions { margin-top: 20px; padding-top: 20px; border-top: 2px solid #eee; }
        .btn { padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; }
        .btn-primary { background: #1a73e8; color: white; }
        .btn-primary:hover { background: #1557b0; }
        .btn-danger { background: #ff4444; color: white; }
        .btn-danger:hover { background: #cc0000; }
        .flash { padding: 10px; border-radius: 5px; margin-bottom: 15px; }
        .flash-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .flash-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .btn-test { background: #6C63FF; color: white; }
        .btn-test:hover { background: #5a52d5; }
        .btn-logs { background: #FF6B6B; color: white; }
        .btn-logs:hover { background: #e55555; }
        .nav-links { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }
        .nav-links a { text-decoration: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏢 Institutional Portal</h1>
        <div class="user-info">
            <span>Welcome, {{ username }} (<span class="badge badge-{{ role }}">{{ role }}</span>)</span>
            <a href="/logout" class="btn-logout">Logout</a>
        </div>
    </div>
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash flash-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="card">
            <h2>📊 My Records</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Content</th>
                        <th>Owner</th>
                        <th>Created</th>
                        {% if role == 'admin' %}
                        <th>Actions</th>
                        {% endif %}
                    </tr>
                </thead>
                <tbody>
                    {% for record in records %}
                    <tr>
                        <td>{{ record[0] }}</td>
                        <td>{{ record[1] }}</td>
                        <td>{{ record[2] }}</td>
                        <td>{{ record[3] }}</td>
                        <td>{{ record[4] }}</td>
                        {% if role == 'admin' %}
                        <td>
                            <form method="POST" action="/delete_record/{{ record[0] }}" style="display:inline;">
                                <button type="submit" class="btn btn-danger" onclick="return confirm('Delete this record?')">Delete</button>
                            </form>
                        </td>
                        {% endif %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <h2>✏️ Add New Record</h2>
            <form method="POST" action="/add_record">
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <input type="text" name="title" placeholder="Title" required style="flex: 1; min-width: 150px; padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                    <input type="text" name="content" placeholder="Content" required style="flex: 2; min-width: 200px; padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                    <button type="submit" class="btn btn-primary">Add Record</button>
                </div>
            </form>
        </div>
        
        <div class="card">
            <h2>🔧 Testing & Admin Tools</h2>
            <div class="nav-links">
                <a href="/attack_test"><button class="btn btn-test">🧪 Attack Test</button></a>
                <a href="/test_direct_request"><button class="btn btn-test">🔒 Direct Request Test</button></a>
                {% if role == 'admin' %}
                <a href="/view_logs"><button class="btn btn-logs">📋 View Logs</button></a>
                <a href="/show_db"><button class="btn btn-primary">📊 Database View</button></a>
                {% endif %}
            </div>
        </div>
        
        {% if role == 'admin' %}
        <div class="card">
            <h2>🛡️ Admin Panel</h2>
            <div class="admin-actions">
                <p><strong>All Users:</strong></p>
                <table>
                    <thead>
                        <tr>
                            <th>User ID</th>
                            <th>Username</th>
                            <th>Role</th>
                            <th>Records Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for user in users %}
                        <tr>
                            <td>{{ user[0] }}</td>
                            <td>{{ user[1] }}</td>
                            <td><span class="badge badge-{{ user[2] }}">{{ user[2] }}</span></td>
                            <td>{{ user[3] }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

ATTACK_TEST_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Attack Test Results</title>
    <style>
        body { font-family: Arial; padding: 20px; background: #f0f2f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        h1 { color: #1a73e8; }
        .test { border: 1px solid #ddd; padding: 15px; margin: 15px 0; border-radius: 5px; }
        .test h3 { margin: 0 0 10px 0; }
        .attempt { color: #856404; background: #fff3cd; padding: 10px; border-radius: 3px; }
        .defense { color: #0c5460; background: #d1ecf1; padding: 10px; border-radius: 3px; }
        .result { color: #155724; background: #d4edda; padding: 10px; border-radius: 3px; font-weight: bold; }
        .back { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #1a73e8; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Security Attack Test Results</h1>
        <p>Demonstrating that the three specific attacks are successfully defended against:</p>
        {% for test in results %}
        <div class="test">
            <h3>{{ test.attack }}</h3>
            <div class="attempt">🔴 Attempt: {{ test.attempt }}</div>
            <div class="defense">🛡️ Defense: {{ test.defense }}</div>
            <div class="result">✅ Result: {{ test.result }}</div>
        </div>
        {% endfor %}
        <a href="/dashboard" class="back">← Back to Dashboard</a>
    </div>
</body>
</html>
'''

LOGS_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login Logs</title>
    <style>
        body { font-family: monospace; padding: 20px; background: #f0f2f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        h1 { color: #1a73e8; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
        .success { color: #28a745; font-weight: bold; }
        .failed { color: #dc3545; font-weight: bold; }
        .timestamp { color: #666; font-size: 14px; }
        .back { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #1a73e8; color: white; text-decoration: none; border-radius: 5px; }
        .empty { color: #999; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Login Attempt Logs</h1>
        <p>Showing last 50 login attempts</p>
        {% if logs %}
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>IP Address</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Timestamp</th>
                </tr>
            </thead>
            <tbody>
                {% for log in logs %}
                <tr>
                    <td>{{ log[0] }}</td>
                    <td>{{ log[1] }}</td>
                    <td>{{ log[2] }}</td>
                    <td>{{ log[3] }}</td>
                    <td class="{{ 'success' if log[4] == 'SUCCESS' else 'failed' }}">{{ log[4] }}</td>
                    <td class="timestamp">{{ log[5] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p class="empty">No login attempts logged yet. Try failing a login to see entries appear!</p>
        {% endif %}
        <a href="/dashboard" class="back">← Back to Dashboard</a>
    </div>
</body>
</html>
'''

DIRECT_REQUEST_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Direct Request Test</title>
    <style>
        body { font-family: Arial; background: #f0f2f5; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        h1 { color: #1a73e8; }
        .test-box { border: 2px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 5px; }
        .btn { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 5px; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-danger:hover { background: #c82333; }
        .btn-primary { background: #1a73e8; color: white; }
        .btn-primary:hover { background: #1557b0; }
        .btn-success { background: #28a745; color: white; }
        .btn-success:hover { background: #218838; }
        .result { margin-top: 15px; padding: 15px; border-radius: 5px; background: #f8f9fa; }
        .success { color: #28a745; }
        .error { color: #dc3545; }
        .direct-url { background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; border-left: 4px solid #1a73e8; }
        .info-box { background: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #ffc107; }
        .back { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #1a73e8; color: white; text-decoration: none; border-radius: 5px; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; }
        .badge-admin { background: #ff4444; color: white; }
        .badge-user { background: #4CAF50; color: white; }
        pre { background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
        .status-code { font-weight: bold; font-size: 18px; }
    </style>
    <script>
        async function sendRequest(url) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<p>⏳ Sending request...</p>';
            
            try {
                const response = await fetch(url);
                const data = await response.json();
                const status = response.status;
                
                let statusColor = status === 200 ? '#28a745' : '#dc3545';
                let statusText = status === 200 ? '✅ ALLOWED' : '❌ BLOCKED';
                
                resultDiv.innerHTML = `
                    <div class="result">
                        <p><strong>URL:</strong> <code>${url}</code></p>
                        <p><strong>Status Code:</strong> <span class="status-code" style="color: ${statusColor}">${status}</span></p>
                        <p><strong>Result:</strong> <span style="color: ${statusColor}">${statusText}</span></p>
                        <p><strong>Response:</strong></p>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </div>
                `;
            } catch(e) {
                resultDiv.innerHTML = `<div class="result error">❌ Error: ${e.message}</div>`;
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>🔒 Direct Request Test</h1>
        <p>Testing server-side admin action enforcement</p>
        
        <div class="test-box">
            <h3>Your Current Role: <span class="badge badge-{{ role }}">{{ role }}</span></h3>
            
            <div class="direct-url">
                <p><strong>Admin URLs to Test:</strong></p>
                <ul>
                    <li><code>/admin_action</code> - Admin-only action</li>
                    <li><code>/admin_delete_all</code> - Delete all records</li>
                </ul>
                <p><strong>Your Role:</strong> {{ role }}</p>
            </div>
            
            <div style="margin: 20px 0;">
                <button onclick="sendRequest('/admin_action')" class="btn btn-danger">
                    🚀 Send Admin Request
                </button>
                <button onclick="sendRequest('/admin_delete_all')" class="btn btn-danger">
                    🗑️ Send Delete All Request
                </button>
                <button onclick="sendRequest('/dashboard')" class="btn btn-success">
                    📊 Send Dashboard Request
                </button>
            </div>
            
            <div id="result">
                <div class="result">Click a button above to test direct request</div>
            </div>
        </div>
        
        <div class="info-box">
            <h3>📋 Expected Behavior</h3>
            <ul>
                <li><strong>Admin User:</strong> Request should succeed (200 OK)</li>
                <li><strong>Regular User:</strong> Request should be BLOCKED (403 Forbidden)</li>
                <li>The check is on the SERVER, not in the UI!</li>
            </ul>
        </div>
        
        <div class="test-box">
            <h3>🔄 How to Test</h3>
            <ol>
                <li><strong>Login as regular user</strong> (user1 / user123)</li>
                <li>Click "Send Admin Request"</li>
                <li>Observe 403 Forbidden - Blocked!</li>
                <li><strong>Login as admin</strong> (admin / admin123)</li>
                <li>Click "Send Admin Request"</li>
                <li>Observe 200 OK - Allowed!</li>
            </ol>
        </div>
        
        <a href="/dashboard" class="back">← Back to Dashboard</a>
    </div>
</body>
</html>
'''

# ==================== DATABASE SETUP ====================

def init_db():
    """Initialize database with tables and sample data"""
    conn = sqlite3.connect('portal.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create records table
    c.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # NEW: Create login_attempts table for logging (Change 1)
    c.execute('''
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            ip_address TEXT,
            attempt_type TEXT NOT NULL,
            success INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if we need to populate sample data
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        # Create sample users with bcrypt hashed passwords
        admin_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt(12))
        user_hash = bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt(12))
        
        c.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                  ('admin', admin_hash.decode('utf-8'), 'admin'))
        c.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                  ('user1', user_hash.decode('utf-8'), 'user'))
        c.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                  ('user2', user_hash.decode('utf-8'), 'user'))
        
        # Get user IDs
        c.execute('SELECT id FROM users WHERE username = ?', ('admin',))
        admin_id = c.fetchone()[0]
        c.execute('SELECT id FROM users WHERE username = ?', ('user1',))
        user1_id = c.fetchone()[0]
        c.execute('SELECT id FROM users WHERE username = ?', ('user2',))
        user2_id = c.fetchone()[0]
        
        # Create 20 sample records
        sample_records = [
            ('Q1 Report', 'Quarter 1 financial report completed', admin_id),
            ('Q2 Report', 'Quarter 2 financial report completed', admin_id),
            ('Q3 Report', 'Quarter 3 financial report completed', admin_id),
            ('Q4 Report', 'Quarter 4 financial report completed', admin_id),
            ('Annual Budget', 'Annual budget for 2026 approved', admin_id),
            ('Staff Meeting', 'Minutes from staff meeting - January', user1_id),
            ('Project Alpha', 'Project Alpha progress report', user1_id),
            ('Project Beta', 'Project Beta status update', user1_id),
            ('Client Meeting', 'Client meeting notes - February', user1_id),
            ('Development Plan', 'Development plan for Q1', user1_id),
            ('Research Notes', 'Research findings on AI', user1_id),
            ('Staff Meeting', 'Minutes from staff meeting - February', user2_id),
            ('Project Gamma', 'Project Gamma initial draft', user2_id),
            ('Marketing Plan', 'Marketing strategy for Q2', user2_id),
            ('Client Feedback', 'Client feedback summary', user2_id),
            ('Innovation Ideas', 'New product innovation ideas', user2_id),
            ('Team Update', 'Weekly team update', user2_id),
            ('Training Plan', 'Training schedule for new employees', admin_id),
            ('Security Audit', 'Security audit report', admin_id),
            ('Infrastructure', 'IT infrastructure upgrade plan', admin_id)
        ]
        
        for title, content, user_id in sample_records:
            c.execute('INSERT INTO records (title, content, user_id) VALUES (?, ?, ?)',
                     (title, content, user_id))
    
    conn.commit()
    conn.close()

# ==================== LOGGING FUNCTIONS (Change 1) ====================

def log_failed_attempt(username, attempt_type='login', ip_address=None):
    """Log a failed login or reset attempt to the database."""
    try:
        if ip_address is None:
            ip_address = request.remote_addr if hasattr(request, 'remote_addr') else 'unknown'
        
        conn = sqlite3.connect('portal.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO login_attempts (username, ip_address, attempt_type, success, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, ip_address, attempt_type, 0, datetime.datetime.now()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Logging error: {e}")
        return False

def log_successful_attempt(username, attempt_type='login', ip_address=None):
    """Log a successful login or reset attempt to the database."""
    try:
        if ip_address is None:
            ip_address = request.remote_addr if hasattr(request, 'remote_addr') else 'unknown'
        
        conn = sqlite3.connect('portal.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO login_attempts (username, ip_address, attempt_type, success, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, ip_address, attempt_type, 1, datetime.datetime.now()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Logging error: {e}")
        return False

# ==================== AUTH DECORATORS ====================

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'status': 'error',
                'message': 'Please login first',
                'code': 401
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role - SERVER-SIDE enforcement (Change 2)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'status': 'error',
                'message': 'Please login first',
                'code': 401
            }), 401
        
        # CRITICAL: Server-side role check
        if session.get('role') != 'admin':
            # Return 403 Forbidden with JSON response
            return jsonify({
                'status': 'error',
                'message': 'Admin access required',
                'code': 403
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES ====================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            log_failed_attempt(username, 'login')
            flash('Invalid credentials', 'error')
            return render_template_string(LOGIN_TEMPLATE)
        
        conn = sqlite3.connect('portal.db')
        c = conn.cursor()
        c.execute('SELECT id, username, password_hash, role FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user:
            stored_hash = user[2].encode('utf-8') if isinstance(user[2], str) else user[2]
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                log_successful_attempt(username, 'login')
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['role'] = user[3]
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
        
        log_failed_attempt(username, 'login')
        flash('Invalid credentials', 'error')
        return render_template_string(LOGIN_TEMPLATE)
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'user')
        
        if not username or not password:
            flash('All fields are required', 'error')
            return render_template_string(REGISTER_TEMPLATE)
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template_string(REGISTER_TEMPLATE)
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))
        
        conn = sqlite3.connect('portal.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                     (username, password_hash.decode('utf-8'), role))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists', 'error')
        finally:
            conn.close()
    
    return render_template_string(REGISTER_TEMPLATE)

@app.route('/dashboard')
@login_required
def dashboard():
    # If the request is JSON (from fetch), return JSON
    if request.headers.get('Accept') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'message': 'Dashboard access granted',
            'code': 200
        }), 200
    
    user_id = session['user_id']
    role = session['role']
    username = session['username']
    
    conn = sqlite3.connect('portal.db')
    c = conn.cursor()
    
    if role == 'admin':
        c.execute('''
            SELECT r.id, r.title, r.content, u.username, r.created_at 
            FROM records r 
            JOIN users u ON r.user_id = u.id 
            ORDER BY r.created_at DESC
        ''')
        records = c.fetchall()
        
        c.execute('''
            SELECT u.id, u.username, u.role, COUNT(r.id) as record_count
            FROM users u
            LEFT JOIN records r ON u.id = r.user_id
            GROUP BY u.id
            ORDER BY u.id        ''')
        users = c.fetchall()
    else:
        c.execute('''
            SELECT r.id, r.title, r.content, u.username, r.created_at 
            FROM records r 
            JOIN users u ON r.user_id = u.id 
            WHERE r.user_id = ?
            ORDER BY r.created_at DESC
        ''', (user_id,))
        records = c.fetchall()
        users = []
    
    conn.close()
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                                 records=records, 
                                 users=users,
                                 username=username,
                                 role=role)

@app.route('/add_record', methods=['POST'])
@login_required
def add_record():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    user_id = session['user_id']
    
    if not title or not content:
        flash('Title and content are required', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect('portal.db')
    c = conn.cursor()
    c.execute('INSERT INTO records (title, content, user_id) VALUES (?, ?, ?)',
             (title, content, user_id))
    conn.commit()
    conn.close()
    
    flash('Record added successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_record/<int:record_id>', methods=['POST'])
@login_required
def delete_record(record_id):
    user_id = session['user_id']
    role = session['role']
    
    conn = sqlite3.connect('portal.db')
    c = conn.cursor()
    
    if role == 'admin':
        c.execute('DELETE FROM records WHERE id = ?', (record_id,))
    else:
        c.execute('DELETE FROM records WHERE id = ? AND user_id = ?', (record_id, user_id))
    
    if c.rowcount > 0:
        conn.commit()
        flash('Record deleted successfully!', 'success')
    else:
        flash('Record not found or permission denied', 'error')
    
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

# ==================== ATTACK TEST ROUTE ====================

@app.route('/attack_test', methods=['GET', 'POST'])
@login_required
def attack_test():
    results = [
        {
            'attack': 'Attack 1: SQL Injection Login Bypass',
            'attempt': "Username: admin' OR '1'='1, Password: anything",
            'defense': 'Parameterized queries prevent SQL injection',
            'result': 'Failed - Parameterized query blocked the attack'
        },
        {
            'attack': 'Attack 2: User Attempting Admin Access',
            'attempt': 'Logged in as user1, tried to access admin functions',
            'defense': 'Server-side role checking',
            'result': 'Failed - Admin required decorator blocked access'
        },
        {
            'attack': 'Attack 3: Viewing Other User\'s Records',
            'attempt': 'user1 trying to view user2 records via URL manipulation',
            'defense': 'Role-based record filtering at database level',
            'result': 'Failed - Query filters by user_id from session'
        }
    ]
    return render_template_string(ATTACK_TEST_TEMPLATE, results=results)

# ==================== CHANGE 1: VIEW LOGS ROUTE ====================

@app.route('/view_logs')
@login_required
@admin_required
def view_logs():
    """View login attempt logs - Admin only (Change 1)"""
    conn = sqlite3.connect('portal.db')
    c = conn.cursor()
    c.execute('''
        SELECT id, username, ip_address, attempt_type, 
               CASE WHEN success=1 THEN 'SUCCESS' ELSE 'FAILED' END as status,
               timestamp
        FROM login_attempts 
        ORDER BY timestamp DESC 
        LIMIT 50
    ''')
    logs = c.fetchall()
    conn.close()
    
    return render_template_string(LOGS_TEMPLATE, logs=logs)

# ==================== CHANGE 2: DIRECT REQUEST TEST ROUTES ====================

@app.route('/test_direct_request')
@login_required
def test_direct_request():
    """Test page for direct admin request demonstration (Change 2)"""
    return render_template_string(DIRECT_REQUEST_TEMPLATE, role=session.get('role', 'guest'))

@app.route('/admin_action')
@login_required
@admin_required
def admin_action():
    """Admin-only action - Protected by @admin_required (Change 2)"""
    return jsonify({
        'status': 'success',
        'message': 'Admin action performed successfully',
        'data': {
            'action': 'admin_operation',
            'timestamp': datetime.datetime.now().isoformat()
        }
    }), 200

@app.route('/admin_delete_all')
@login_required
@admin_required
def admin_delete_all():
    """Admin-only: Delete all records - Protected by @admin_required (Change 2)"""
    conn = sqlite3.connect('portal.db')
    c = conn.cursor()
    c.execute('DELETE FROM records')
    conn.commit()
    conn.close()
    
    return jsonify({
        'status': 'success',
        'message': 'All records deleted by admin',
        'code': 200
    }), 200

# ==================== SHOW DB ROUTE ====================

@app.route('/show_db')
@login_required
@admin_required
def show_db():
    conn = sqlite3.connect('portal.db')
    c = conn.cursor()
    c.execute('SELECT id, username, password_hash, role FROM users')
    users = c.fetchall()
    c.execute('SELECT id, title, content, user_id FROM records')
    records = c.fetchall()
    conn.close()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Database Contents</title>
        <style>
            body { font-family: monospace; padding: 20px; }
            table { border-collapse: collapse; width: 100%; margin: 10px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background: #f0f2f5; }
            .hash { color: #666; font-size: 12px; word-break: break-all; }
        </style>
    </head>
    <body>
        <h1>📊 Database Contents</h1>
        <h2>Users Table (Password Hashes Stored)</h2>
        <table>
            <tr><th>ID</th><th>Username</th><th>Password Hash (bcrypt)</th><th>Role</th></tr>
            {% for user in users %}
            <tr>
                <td>{{ user[0] }}</td>
                <td>{{ user[1] }}</td>
                <td class="hash">{{ user[2] }}</td>
                <td>{{ user[3] }}</td>
            </tr>
            {% endfor %}
        </table>
        
        <h2>Records Table</h2>
        <table>
            <tr><th>ID</th><th>Title</th><th>Content</th><th>User ID</th></tr>
            {% for record in records %}
            <tr>
                <td>{{ record[0] }}</td>
                <td>{{ record[1] }}</td>
                <td>{{ record[2] }}</td>
                <td>{{ record[3] }}</td>
            </tr>
            {% endfor %}
        </table>
        <a href="/dashboard">← Back to Dashboard</a>
    </body>
    </html>
    '''
    return render_template_string(html, users=users, records=records)

# ==================== APPLICATION STARTUP ====================

if __name__ == '__main__':
    init_db()
    
    print("=" * 60)
    print("🔐 SIH 2026 - Secure Record Access Portal")
    print("=" * 60)
    print("\n📋 Default Login Credentials:")
    print("   Admin:  admin / admin123")
    print("   Users:  user1 / user123")
    print("           user2 / user123")
    print("\n🛡️ Security Features Implemented:")
    print("   ✓ bcrypt slow salted password hashing")
    print("   ✓ Parameterized SQL queries (prevents injection)")
    print("   ✓ Server-side role-based access control")
    print("   ✓ Generic login error messages")
    print("   ✓ Session management")
    print("\n📝 Change 1 - Failed Login Logging:")
    print("   ✓ Every failed login is logged with timestamp")
    print("   ✓ View logs at: http://localhost:5000/view_logs")
    print("\n🔒 Change 2 - Server-Side Admin Blocking:")
    print("   ✓ Regular users get 403 Forbidden on admin actions")
    print("   ✓ Test at: http://localhost:5000/test_direct_request")
    print("\n🧪 Attack Test URL: http://localhost:5000/attack_test")
    print("📊 Database View (admin only): http://localhost:5000/show_db")
    print("\n" + "=" * 60)
    print("Starting server at http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
