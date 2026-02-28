import hashlib

# “ok for demo”, but not best practice for real auth. 
# Can change later to passlib[bcrypt] 
# without changing the rest of the application
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password