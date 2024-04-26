import os
import subprocess

def generate_ssl_cert(domain, ca_cert, ca_key):
    # 유효 기간 설정 (1000년)
    days = 365000

    # 디렉터리 생성 및 이동
    cert_dir = f"./{domain}"
    os.makedirs(cert_dir, exist_ok=True)
    os.chdir(cert_dir)

    # 파일명 설정
    cert_name = f"{domain}.crt"
    key_name = f"{domain}.key"
    pem_name = f"{domain}.pem"

    # 인증서 요청 생성
    subprocess.run([
        "openssl", "req", "-new", "-sha256", "-nodes", "-out", f"{domain}.csr",
        "-newkey", "rsa:2048", "-keyout", key_name, "-subj", f"/CN={domain}",
        "-addext", f"subjectAltName=DNS:{domain}"
    ])

    # 인증서 발급
    subprocess.run([
        "openssl", "x509", "-req", "-in", f"{domain}.csr", "-CA", ca_cert, "-CAkey", ca_key,
        "-CAcreateserial", "-out", cert_name, "-days", str(days),
        "-extfile", "<(printf 'subjectAltName=DNS:{domain}')"
    ])

    # PEM 파일 생성
    with open(pem_name, "wb") as pem_file:
        with open(key_name, "rb") as key_file:
            pem_file.write(key_file.read())
        with open(cert_name, "rb") as cert_file:
            pem_file.write(cert_file.read())

    # 발급된 인증서 확인
    subprocess.run(["openssl", "x509", "-noout", "-text", "-in", cert_name])

    # 생성된 중간 파일 제거
    os.remove(f"{domain}.csr")

    print(f"인증서 및 PEM 파일은 {cert_dir} 디렉터리에 저장되었습니다.")

# 사용자로부터 도메인 입력 받기
domain = input("도메인을 입력하세요 (예: yourdomain.com): ")

# Paths to CA certificate and private key
ca_cert = "../localCA.crt"
ca_key = "../localCA.key"

# SSL 인증서 생성
generate_ssl_cert(domain, ca_cert, ca_key)
