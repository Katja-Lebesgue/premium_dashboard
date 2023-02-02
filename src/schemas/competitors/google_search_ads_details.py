from pydantic import BaseModel


class GoogleSearchAdsDetailsBase(BaseModel):
    pass


class GoogleSearchAdsDetailsCreate(GoogleSearchAdsDetailsBase):
    keyword_id: int
    domain_name: str | None
    ad_headline: str
    ad_description: str
    ad_landing_page: str
    ad_url: str


class GoogleSearchAdsDetailsUpdate(GoogleSearchAdsDetailsBase):
    pass
