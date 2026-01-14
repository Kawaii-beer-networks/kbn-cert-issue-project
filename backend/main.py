import os
import datetime
import zipfile  # 추가됨
import io       # 추가됨
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse # 추가됨
from pydantic import BaseModel
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

app = FastAPI(title="Private CA Certificate Manager")

# --- 설정 ---
ROOT_CA_CERT = "rootCA.crt"
ROOT_CA_KEY = "rootCA.key"
CERT_STORAGE = "generated_certs"

os.makedirs(CERT_STORAGE, exist_ok=True)

# --- 데이터 모델 ---
class CertRequest(BaseModel):
    domain: str
    alt_names: List[str] = []

# --- 헬퍼 함수: 인증서 발급 로직 (이전과 동일) ---
def generate_signed_cert(domain: str, alt_names: List[str]):
    try:
        with open(ROOT_CA_CERT, "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())
        with open(ROOT_CA_KEY, "rb") as f:
            ca_key = serialization.load_pem_private_key(f.read(), password=None)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Root CA files not found.")

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"KR"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"MyPrivateCloud"),
        x509.NameAttribute(NameOID.COMMON_NAME, domain),
    ])

    alt_names_list = [x509.DNSName(domain)]
    for alt in alt_names:
        alt_names_list.append(x509.DNSName(alt))
    
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName(alt_names_list), critical=False)
        .sign(ca_key, hashes.SHA256())
    )

    key_path = os.path.join(CERT_STORAGE, f"{domain}.key")
    cert_path = os.path.join(CERT_STORAGE, f"{domain}.crt")

    with open(key_path, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    return key_path, cert_path

# --- API 엔드포인트 ---

@app.get("/cert")
def list_certificates():
    certs = []
    files = os.listdir(CERT_STORAGE)
    for f in files:
        if f.endswith(".crt"):
            domain = f.replace(".crt", "")
            certs.append({"domain": domain, "file": f})
    return {"certificates": certs}

@app.post("/cert", status_code=201)
def create_certificate(req: CertRequest):
    if os.path.exists(os.path.join(CERT_STORAGE, f"{req.domain}.crt")):
        raise HTTPException(status_code=400, detail="Certificate for this domain already exists.")
    
    key_path, cert_path = generate_signed_cert(req.domain, req.alt_names)
    
    return {
        "message": "Certificate created successfully",
        "domain": req.domain,
        "download_url": f"/cert/{req.domain}" # 클라이언트 편의를 위해 URL 제공
    }

# 3. GET /cert/{domain} -> ZIP 파일로 다운로드 (수정됨)
@app.get("/cert/{domain}")
def get_certificate_zip(domain: str):
    """
    특정 도메인의 .crt와 .key 파일을 하나의 zip으로 압축하여 반환합니다.
    """
    cert_filename = f"{domain}.crt"
    key_filename = f"{domain}.key"
    
    cert_path = os.path.join(CERT_STORAGE, cert_filename)
    key_path = os.path.join(CERT_STORAGE, key_filename)
    
    # 파일 존재 여부 확인
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        raise HTTPException(status_code=404, detail="Certificate or Key not found")
    
    # 메모리상에 ZIP 파일 생성
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # ZIP 내부에 파일 추가 (arcname은 압축 파일 내부에서의 파일명)
        zip_file.write(cert_path, arcname=cert_filename)
        zip_file.write(key_path, arcname=key_filename)
    
    # 버퍼 위치를 처음으로 되돌림
    zip_buffer.seek(0)
    
    # 파일 다운로드를 위한 헤더 설정
    headers = {
        "Content-Disposition": f"attachment; filename={domain}.zip"
    }
    
    return StreamingResponse(zip_buffer, media_type="application/zip", headers=headers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
