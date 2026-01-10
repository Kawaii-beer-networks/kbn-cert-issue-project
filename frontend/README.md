# Private CA Certificate Manager

Root CA 기반 인증서 발급 및 관리 시스템

## 🚀 시작하기

### v0 프리뷰에서

현재 v0 프리뷰에서는 모의 데이터로 작동합니다. 실제 Python 백엔드와 연결하려면 아래 단계를 따라주세요.

### 로컬 환경에서 실행

1. **Python 백엔드 실행**
   ```bash
   python cert-request.py
   ```

2. **환경 변수 설정**
   
   `.env.local` 파일을 생성하고 다음 내용을 추가:
   ```env
   CERT_API_URL=http://localhost:8000
   ```

3. **프론트엔드 실행**
   ```bash
   npm install
   npm run dev
   ```

4. **브라우저에서 열기**
   ```
   http://localhost:3000
   ```

## 📋 기능

- ✅ Root CA로 서명된 인증서 발급
- ✅ Subject Alternative Name (SAN) 지원
- ✅ 발급된 인증서 목록 조회
- ✅ 인증서 내용 미리보기
- ✅ 인증서 다운로드

## 🔧 기술 스택

- **Frontend**: Next.js 16, React 19, TypeScript
- **Backend**: FastAPI, Python
- **Styling**: Tailwind CSS v4, shadcn/ui
- **Crypto**: cryptography (Python)

## 📝 API 엔드포인트

- `GET /api/cert` - 인증서 목록 조회
- `POST /api/cert` - 새 인증서 발급
- `GET /api/cert/[domain]` - 특정 도메인의 인증서 내용 조회
