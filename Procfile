# Meta Ads-Centric Railway Procfile
web: python -m uvicorn v2.meta_ads.meta_centric_orchestrator:app --host 0.0.0.0 --port $PORT
ml-core: python -m uvicorn ml_core.api.main:app --host 0.0.0.0 --port 8000
meta-ads: python -m uvicorn v2.meta_ads.meta_ads_manager:app --host 0.0.0.0 --port 9000  
youtube: python -m uvicorn v2.youtube.youtube_uploader:app --host 0.0.0.0 --port 8001
orchestrator: python -m uvicorn v2.unified_orchestrator.main:app --host 0.0.0.0 --port 10000
dashboard: streamlit run dashboard_meta_centric.py --server.port 8501
worker: python -m v2.workers.campaign_worker
