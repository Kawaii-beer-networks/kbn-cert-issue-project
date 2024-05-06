from OpenSSL import crypto
import os

def generate_ssl_certificate(domain, root_ca_cert_path, root_ca_key_path, passphrase):

    # Load root CA certificate
    with open(root_ca_cert_path, "rb") as f:
        root_ca_cert_data = f.read()
    print(root_ca_cert_data)
    root_ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, root_ca_cert_data)

    # Load root CA private key
    with open(root_ca_key_path, "rb") as f:
        root_ca_key_data = f.read()
    root_ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, root_ca_key_data,passphrase=passphrase)

    # Create a key pair
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048,)

    # Create a certificate signing request (CSR)
    req = crypto.X509Req()
    req.get_subject().CN = domain
    req.set_pubkey(key)
    req.sign(key, 'sha256')

    # Create a certificate
    cert = crypto.X509()
    cert.set_subject(req.get_subject())
    cert.set_pubkey(req.get_pubkey())
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # Valid for 1 year
    cert.set_issuer(root_ca_cert.get_subject())
    cert.sign(root_ca_key, 'sha256')

    # Save the key and certificate to files
    cert_dir = f"issued_cert/{domain}"
    os.makedirs(cert_dir, exist_ok=True)
    with open(f"{cert_dir}/{domain}_private_key.pem", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
    with open(f"{cert_dir}/{domain}_certificate.pem", "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
