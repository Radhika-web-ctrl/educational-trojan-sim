from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class LoginResponse(BaseModel):
    otp_required: bool = True
    message: str


class VerifyOtpRequest(BaseModel):
    username: str
    otp: str = Field(min_length=6, max_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ActionResponse(BaseModel):
    disclaimer: str
    status: str
    details: dict


class DefenseFindings(BaseModel):
    findings: list[dict]
