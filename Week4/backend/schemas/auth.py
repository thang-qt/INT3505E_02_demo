from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class LoginRequest:
    username: str
    password: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LoginRequest":
        if "username" not in data or "password" not in data:
            raise ValueError("Missing credentials")
        username = str(data["username"]).strip()
        password = str(data["password"]).strip()
        if not username or not password:
            raise ValueError("Missing credentials")
        return cls(username=username, password=password)
