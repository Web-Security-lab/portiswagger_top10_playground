import os
from flask import Flask, render_template, render_template_string, request

app = Flask(__name__)

FLAG = os.environ.get('FLAG', 'WSL{fake_flag}')


@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'"
    return response


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/render', methods=['POST'])
def render_page():
    template_input = request.form.get('template', '')

    if not template_input:
        return render_template('index.html', output="Please enter a template.")

    if len(template_input) > 2000:
        return render_template('index.html', output="Template too long. Maximum 2000 characters.")

    try:
        result = render_template_string(template_input)
        return render_template('index.html',
                               output="Rendered successfully.",
                               template_input=template_input)
    except Exception as e:
        return render_template('index.html',
                               output=str(e),
                               template_input=template_input)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
