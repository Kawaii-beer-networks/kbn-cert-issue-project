from fastapi import FastAPI,HTTPException
import os
import json
from module import cert

from dotenv import load_dotenv
#For fastapi구동용
app = FastAPI()

load_dotenv()
#set SECRET_ENV to DISCORD_BOT_TOKEN
PKEY = os.getenv("PKEY")


## 404 Error For Default ##
DefaultErrorCode = HTTPException(status_code=404, detail="Sorry, Nothing Here :P")

@app.get("/")
def read_root():
    raise DefaultErrorCode

@app.get("/api")
def read_api_root():
    raise DefaultErrorCode

#Get Cert list
@app.get("/api/cert")
def read_cert_list():
    domain_list = []
    directories = os.listdir("./issued_cert")
    for i in directories:
        domain_list.append(i)
    return json.dumps(domain_list)

#will be deprecated soon
@app.get("/api/cert/{domain}")
def read_domain_cert():
    #read specified domain here = var -> domain
    return True

@app.post("/api/cert/{domain}")
def issue_domain_cert(domain):
    #Issue the CertDomain#
    return cert.generate_ssl_certificate(domain=domain,root_ca_cert_path="./rootca/localCA.pem",root_ca_key_path="./rootca/localCA.key",passphrase=PKEY.encode())

@app.get("/api/download?domain={domain}&key={key}")
def create_download_domain():
    #Downloadable link crate#
    return True


if __name__ == "__app__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)