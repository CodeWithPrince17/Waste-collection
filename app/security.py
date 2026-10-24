from passlib.context import CryptContext

# We use bcrypt as our hashing algorithm. 
# "deprecated='auto'" means if bcrypt becomes outdated in the future, 
# passlib will automatically suggest a new one.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Takes a plain text password and returns a secure hash."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if a plain password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)