from typing import Union

from fastapi import FastAPI,HTTPException

app = FastAPI()


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
    #do something on here
    return True
@app.get("/api/cert/{domain}")
def read_domain_cert():
    #read specified domain here = var -> domain
    return True
@app.post("api/cert/{domain}")
def issue_domain_cert():
    #Issue the CertDomain#
    return True
@app.get("/api/download/domain")
def create_download_domain():
    #Downloadable link crate#
    return True
    
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


if __name__ == "__app__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)