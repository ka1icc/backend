from pydantic import BaseModel


class URLCreate(BaseModel):
    target: str


class URLResponse(BaseModel):
    code: str
    target: str
    short_url: str

    class Config:
        from_attributes = True  # Pydantic v2
