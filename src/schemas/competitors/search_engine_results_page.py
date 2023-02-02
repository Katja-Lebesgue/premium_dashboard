from pydantic import BaseModel


class OrganicResult(BaseModel):
    url: str


class Screenshot(BaseModel):
    content: str
    type: str


class AdResult(BaseModel):
    headline: str
    description: str
    url: str
    screenshot: Screenshot


class SearchEngineResultsPage(BaseModel):
    page_number: int
    page_source: str
    organic_results: list[OrganicResult]
    ad_results: list[AdResult]
