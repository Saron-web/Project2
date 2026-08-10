import bcrypt

def hash_password(p):
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()

def verify_password(p, hashed):
    return bcrypt.checkpw(p.encode(), hashed.encode())
