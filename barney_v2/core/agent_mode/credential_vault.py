import os
import uuid
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

CRED_KEY_PREFIX = "agent_cred:{user_id}:{token}"

class CredentialVault:
    def __init__(self):
        key = os.environ.get("VAULT_KEY")
        if not key:
            raise ValueError("VAULT_KEY environment variable not set")
        self.cipher = Fernet(key.encode("utf-8"))
        from redis_client import redis_client
        self.redis = redis_client

    def store(self, token: str, value: str, user_id: str) -> str:
        encrypted = self.cipher.encrypt(value.encode("utf-8")).decode("utf-8")
        key = CRED_KEY_PREFIX.format(user_id=user_id, token=token)
        self.redis.set(key, encrypted)
        return token

    def resolve(self, token: str, user_id: str) -> str:
        key = CRED_KEY_PREFIX.format(user_id=user_id, token=token)
        val = self.redis.get(key)
        if not val:
            return None
        # Handle cases where redis returns bytes (common in Redis library)
        if isinstance(val, bytes):
            val = val.decode("utf-8")
        return self.cipher.decrypt(val.encode("utf-8")).decode("utf-8")

    def has(self, token: str, user_id: str) -> bool:
        key = CRED_KEY_PREFIX.format(user_id=user_id, token=token)
        return self.redis.exists(key) == 1
