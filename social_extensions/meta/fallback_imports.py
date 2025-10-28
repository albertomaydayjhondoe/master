
"""Fallback imports para Meta Ads"""
import os

if os.getenv("DUMMY_MODE", "true").lower() == "true":
    try:
        from mcp_server.dummy_implementations import (
            DummyFacebookAdsApi as FacebookAdsApi,
            DummyAdAccount as AdAccount,
            DummyCampaign as Campaign,
            DummyAdSet as AdSet,
            DummyAd as Ad,
            DummyAdCreative as AdCreative,
            DummyAdImage as AdImage,
            DummyAdVideo as AdVideo,
            FacebookRequestError
        )
    except ImportError:
        # Fallback básico
        class FacebookAdsApi:
            @classmethod
            def init(cls, *args, **kwargs): pass
        
        class AdAccount:
            def __init__(self, *args, **kwargs): pass
            def get_campaigns(self, *args, **kwargs): return []
            def create_campaign(self, *args, **kwargs): return {"id": "dummy"}
        
        # Clases básicas para el resto
        Campaign = AdAccount
        AdSet = AdAccount  
        Ad = AdAccount
        AdCreative = AdAccount
        AdImage = AdAccount
        AdVideo = AdAccount
        
        class FacebookRequestError(Exception): pass
else:
    try:
        from facebook_business.api import FacebookAdsApi
        from facebook_business.adobjects.adaccount import AdAccount
        from facebook_business.adobjects.campaign import Campaign
        from facebook_business.adobjects.adset import AdSet
        from facebook_business.adobjects.ad import Ad
        from facebook_business.adobjects.adcreative import AdCreative
        from facebook_business.adobjects.adimage import AdImage
        from facebook_business.adobjects.advideo import AdVideo
        from facebook_business.exceptions import FacebookRequestError
    except ImportError:
        raise ImportError("facebook-business no instalado. Activar DUMMY_MODE=true para usar implementación dummy")
