import os
import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

app = FastAPI(title="Kawaii Beer Networks CA Certificate Manager")

# --- 설정 ---
ROOT_CA_CERT = "rootCA.crt"  # 미리 생성해둔 Root CA 인증서
ROOT_CA_KEY = "rootCA.key"   # 미리 생성해둔 Root CA 개인키
CERT_STORAGE = "generated_certs" # 생성된 인증서 저장 위치

# 저장소 디렉토리 생성
os.makedirs(CERT_STORAGE, exist_ok=True)

# --- 데이터 모델 ---
class CertRequest(BaseModel):
    domain: str
    alt_names: List[str] = [] # 추가 도메인 (SAN)

class CertResponse(BaseModel):
    domain: str
    status: str
    cert_path: str
    key_path: str

# --- 헬퍼 함수: 인증서 발급 로직 ---
def generate_signed_cert(domain: str, alt_names: List[str]):
    # 1. Root CA 파일 로드
    try:
        with open(ROOT_CA_CERT, "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())
        with open(ROOT_CA_KEY, "rb") as f:
            ca_key = serialization.load_pem_private_key(f.read(), password=None)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Root CA files not found.")

    # 2. 새로운 도메인을 위한 개인키 생성
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 3. 인증서 기본 정보 설정 (Subject)
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"KR"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Kawaii Beer Networks"),
        x509.NameAttribute(NameOID.COMMON_NAME, domain),
    ])

    # 4. Subject Alternative Name (SAN) 구성 (Chrome 등 최신 브라우저 필수)
    alt_names_list = [x509.DNSName(domain)]
    for alt in alt_names:
        alt_names_list.append(x509.DNSName(alt))
    
    # 5. 인증서 빌더 구성 (Root CA로 서명)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject) # 발급자는 Root CA
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=99999)) # 유효기간
        .add_extension(
            x509.SubjectAlternativeName(alt_names_list),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256()) # Root CA 개인키로 서명!
    )

    # 6. 파일로 저장
    key_path = os.path.join(CERT_STORAGE, f"{domain}.key")
    cert_path = os.path.join(CERT_STORAGE, f"{domain}.crt")

    # 개인키 저장
    with open(key_path, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    # 인증서 저장
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    return key_path, cert_path


# --- API 엔드포인트 ---

# 1. GET /cert -> 인증서 목록
@app.get("/cert")
def list_certificates():
    """저장된 모든 인증서 파일 목록을 반환합니다."""
    certs = []
    files = os.listdir(CERT_STORAGE)
    for f in files:
        if f.endswith(".crt"):
            domain = f.replace(".crt", "")
            certs.append({"domain": domain, "file": f})
    return {"certificates": certs}

# 2. POST /cert -> 인증서 생성
@app.post("/cert", status_code=201)
def create_certificate(req: CertRequest):
    """Root CA를 사용하여 새로운 도메인 인증서를 발급 및 서명합니다."""
    # 이미 존재하는지 확인 (선택 사항)
    if os.path.exists(os.path.join(CERT_STORAGE, f"{req.domain}.crt")):
        raise HTTPException(status_code=400, detail="Certificate for this domain already exists.")
    
    key_path, cert_path = generate_signed_cert(req.domain, req.alt_names)
    
    return {
        "message": "Certificate created successfully",
        "domain": req.domain,
        "cert_path": cert_path,
        "key_path": key_path
    }

# 3. GET /cert/{domain} -> 인증서 불러오기
@app.get("/cert/{domain}")
def get_certificate(domain: str):
    """특정 도메인의 인증서 내용(텍스트)을 반환합니다."""
    cert_path = os.path.join(CERT_STORAGE, f"{domain}.crt")
    
    if not os.path.exists(cert_path):
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    with open(cert_path, "r") as f:
        content = f.read()
        
    return Response(content=content, media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    # 실행: python main.py
    uvicorn.run(app, host="0.0.0.0", port=8000)