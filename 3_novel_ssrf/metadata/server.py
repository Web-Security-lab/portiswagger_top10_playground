from flask import Flask, jsonify

app = Flask(__name__)

# LocalStack 초기화 스크립트의 자격증명과 동일하게 설정
CREDENTIALS = {
    "Code":            "Success",
    "Type":            "AWS-HMAC",
    "AccessKeyId":     "ASIACTFEC2ROLEKEY001",
    "SecretAccessKey": "ctfSecretKeyForEC2RoleDoNotLeak00",
    "Token":           "ctf-session-token-ec2-role-00000",
    "Expiration":      "2099-12-31T23:59:59Z",
    "LastUpdated":     "2025-06-23T00:00:00Z",
    "Flag":            "WSL{G00D_b1iNd_SSrF_metAdatA_L34K}"
}


@app.route('/latest/meta-data/')
def metadata_root():
    return "iam/\ninstance-id/\nhostname/\n", 200


@app.route('/latest/meta-data/iam/')
def iam_root():
    return "security-credentials/\n", 200


@app.route('/latest/meta-data/iam/security-credentials/')
def credentials_root():
    return "ctf-ec2-role\n", 200


@app.route('/latest/meta-data/iam/security-credentials/ctf-ec2-role')
def credentials():
    return jsonify(CREDENTIALS), 200


@app.route('/latest/meta-data/instance-id/')
def instance_id():
    return "i-0ctf1234567890abc\n", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
