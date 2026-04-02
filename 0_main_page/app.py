from flask import Flask, render_template, request, jsonify, session
import secrets
import subprocess
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# 문제 목록 ('folder_name' 속성을 실제 폴더명과 똑같이 맞춰줍니다)
challenges = [
    {"id": 1, "folder_name": "1_successful_errors", "name": "Successful Errors", "description": "에러 메시지를 악용한 정보 탈취 및 취약점 연계", "detail": "애플리케이션의 에러 핸들링 미흡을 이용하여 민감한 시스템 정보를 추출하세요.", "port": 18001, "flag": "WSL{PerFecT_3rr0r_b4s3d_sst1}"},
    {"id": 2, "folder_name": "2_orm_leaking", "name": "ORM Leaking", "description": "ORM 메커니즘의 헛점을 찌르는 데이터 유출", "detail": "객체 관계 매핑(ORM)의 취약한 구현을 우회하여 숨겨진 사용자 데이터를 유출시키세요.", "port": 18002, "flag": "WSL{orm_filter_oracle}"},
    {"id": 3, "folder_name": "3_novel_ssrf", "name": "Novel SSRF", "description": "기존 필터링을 우회하는 새로운 형태의 SSRF 공격", "detail": "일반적인 SSRF 방어 로직을 우회하는 새로운 페이로드를 구성하여 내부망의 메타데이터 서버에 접근하세요.", "port": 18003, "flag": "WSL{G00D_b1iNd_SSrF_metAdatA_L34K}"},
    {"id": 4, "folder_name": "4_unicode_normalization", "name": "Unicode Normalization", "description": "유니코드 정규화 과정을 악용한 WAF 및 필터 우회", "detail": "서버의 유니코드 정규화(Normalization) 과정에서 발생하는 차이를 이용해 XSS 필터를 우회하세요.", "port": 18004, "flag": "WSL{un1c0d3_n0rm4l1z4t10n_byp4ss_nfkc_2025}"},
    {"id": 5, "folder_name": "5_soapwn_pwning_NET", "name": "SOAPwn pwning .NET", "description": ".NET 환경에서 SOAP 통신을 노린 취약점 공략", "detail": ".NET의 취약한 SOAP 엔드포인트를 통해 RCE(원격 코드 실행)를 달성하세요.", "port": 18005, "flag": "WSL{test}"},
    {"id": 6, "folder_name": "6_cross-site_ETag", "name": "Cross-site ETag", "description": "ETag 헤더를 활용한 크로스 사이트 사용자 추적", "detail": "브라우저의 ETag 캐싱 매커니즘을 악용하여 다른 오리진의 사용자 상태를 추적하고 데이터를 탈취하세요.", "port": 18006, "flag": "WSL{cr0ss_s1te_3tag_l3ngth_le4k}"},
    {"id": 7, "folder_name": "7_Next.js_cache", "name": "Next.js cache", "description": "Next.js 애플리케이션의 캐시 포이즈닝 취약점", "detail": "Next.js 프레임워크의 캐시 라우팅을 오염시켜 다른 사용자에게 악의적인 응답이 반환되도록 하세요.", "port": 18007, "flag": "WSL{cache_p0isoning_V1a_XSS}"},
    {"id": 8, "folder_name": "8_xss_leak", "name": "XSS leak", "description": "XSS를 응용한 민감 데이터 릭(Leak) 기법", "detail": "단순한 알림창을 띄우는 것을 넘어, XSS를 통해 페이지 내의 민감한 CSRF 토큰을 외부로 유출시키세요.", "port": 18008, "flag": "WSL{Xss_13ak_M@5ter!}"},
    {"id": 9, "folder_name": "9_HTTP2_CONNECT", "name": "HTTP2 CONNECT", "description": "HTTP/2 CONNECT 악용 스머글링 및 프록시 공격", "detail": "HTTP/2 프로토콜의 CONNECT 메서드를 악용해 프록시 제한을 우회하고 내부 관리자 페이지에 접근하세요.", "port": 18009, "flag": "WSL{http2_authority_header_confusion}"},
    {"id": 10, "folder_name": "10_parser_differentials", "name": "Parser differentials", "description": "서로 다른 파서 간의 해석 차이를 이용한 취약점", "detail": "프론트엔드 프록시와 백엔드 서버의 HTTP 파싱 차이를 이용한 Request Smuggling 공격을 수행하세요.", "port": 18010, "flag": "WSL{test}"},
]

@app.route('/')
def index():
    solved_challenges = session.get('solved', [])
    return render_template('index.html', challenges=challenges, solved_challenges=solved_challenges)

@app.route('/api/submit', methods=['POST'])
def submit_flag():
    data = request.json
    chal_id = int(data.get('id', 0))
    user_flag = data.get('flag', '').strip()
    
    for chal in challenges:
        if chal['id'] == chal_id:
            if chal['flag'] == user_flag:
                solved = session.get('solved', [])
                if chal_id not in solved:
                    solved.append(chal_id)
                    session['solved'] = solved
                return jsonify({"status": "success", "message": "정답입니다! 플래그를 성공적으로 획득했습니다. 🎉", "id": chal_id})
            else:
                return jsonify({"status": "error", "message": "플래그가 일치하지 않습니다. 다시 시도해 보세요."})
    return jsonify({"status": "error", "message": "문제를 찾을 수 없습니다."}), 404

# --- 폴더별 Docker-Compose 제어 API ---
@app.route('/api/docker/<action>/<int:chal_id>', methods=['POST'])
def manage_docker(action, chal_id):
    chal = next((c for c in challenges if c['id'] == chal_id), None)
    if not chal:
        return jsonify({"status": "error", "message": "문제를 찾을 수 없습니다."}), 404

    # 컨테이너 내부에 마운트된 /playground 안의 해당 문제 폴더 경로 설정
    target_dir = f"/playground/{chal['folder_name']}"
    
    if not os.path.isdir(target_dir):
        return jsonify({"status": "error", "message": f"'{chal['folder_name']}' 폴더를 찾을 수 없습니다."}), 400

    try:
        if action == "start":
            # cwd=target_dir 옵션으로 해당 폴더 안에서 docker-compose up -d 실행
            subprocess.run(["docker", "compose", "up", "-d"], cwd=target_dir, check=True)
            return jsonify({"status": "success", "message": f"환경 구동 완료 (Port: {chal['port']})"})
            
        elif action == "stop":
            # 여러 컨테이너(web, bot 등)가 있을 수 있으므로 down 으로 네트워크까지 깔끔하게 종료
            subprocess.run(["docker", "compose", "down"], cwd=target_dir, check=True)
            return jsonify({"status": "success", "message": "환경이 성공적으로 종료되었습니다."})
            
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": "Docker 명령 실행 중 오류가 발생했습니다. (자세한 내용은 서버 로그 확인)"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)