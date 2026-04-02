from flask import Flask, request, render_template, jsonify
import pycurl
import certifi
import json
from io import BytesIO

app = Flask(__name__)

# 블랙리스트: 최초 요청 URL만 검사
# 리다이렉트 이후 목적지는 검사하지 않음 → 핵심 취약점
BLOCKED_KEYWORDS = [
    '169.254',
    'metadata',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '10.0.0.10',
]

MAX_REDIRECTS = 5


def is_blocked(url: str) -> bool:
    url_lower = url.lower()
    return any(keyword in url_lower for keyword in BLOCKED_KEYWORDS)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/fetch', methods=['POST'])
def fetch():
    url = request.form.get('url', '').strip()

    if not url:
        return jsonify({"error": "URL을 입력해주세요."}), 400

    if not url.startswith(('http://', 'https://')):
        return jsonify({"error": "http:// 또는 https:// 로 시작해야 합니다."}), 400

    # 블랙리스트 체크 (최초 URL만 — 리다이렉트 목적지는 검사 안 함)
    if is_blocked(url):
        return jsonify({"error": "접근이 차단된 URL입니다."}), 403

    response_buffer = BytesIO()
    header_buffer = []

    def header_callback(header_line):
        decoded = header_line.decode('utf-8', errors='replace').strip()
        if decoded:
            header_buffer.append(decoded)

    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.FOLLOWLOCATION, True)
    c.setopt(pycurl.MAXREDIRS, MAX_REDIRECTS)
    c.setopt(pycurl.WRITEDATA, response_buffer)
    c.setopt(pycurl.HEADERFUNCTION, header_callback)
    c.setopt(pycurl.CAINFO, certifi.where())
    c.setopt(pycurl.TIMEOUT, 10)
    c.setopt(pycurl.CONNECTTIMEOUT, 5)

    try:
        c.perform()
        c.close()

        body = response_buffer.getvalue().decode('utf-8', errors='replace')

        # 정상 응답: JSON 파싱 시도
        try:
            parsed = json.loads(body)
            return jsonify({"status": "success", "result": parsed}), 200
        except json.JSONDecodeError:
            # 파싱 실패 시 조용히 처리 (응답 내용 노출 안 함)
            return jsonify({"status": "error", "error": "응답을 처리할 수 없습니다."}), 200

    except pycurl.error as e:
        errno, msg = e.args
        c.close()

        # ★ 핵심 취약점
        # MAX_REDIRECTS 초과 시 에러 핸들러가 전체 리다이렉트 체인을 노출
        if errno == pycurl.E_TOO_MANY_REDIRECTS:
            return jsonify({
                "status": "error",
                "error": "Too many redirects",
                "debug_info": header_buffer,
                "last_response": response_buffer.getvalue().decode('utf-8', errors='replace')
            }), 500

        return jsonify({"status": "error", "error": f"요청 실패: {msg}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
