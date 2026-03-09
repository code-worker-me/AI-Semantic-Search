from pydantic import BaseModel

class SearchRequest(BaseModel):
    intensi: str
    limit: int = 5