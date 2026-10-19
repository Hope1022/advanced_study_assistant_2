from pydantic import BaseModel

#server to client(front-end(browser))
class TokenSchema(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"
    
class TokenPayloadSchema(BaseModel):
    sub:  str | None = None    # user id — "123"
    type: str | None = None    # "access" or "refresh"
    exp:  int | None = None    # expiry timestamp — 1718234567
 
#client to server 
class RefreshTokenSchema(BaseModel):
    refresh_token: str
