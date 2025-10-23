# Technical Integrations Guide

This document provides detailed setup instructions for the external services and libraries used in this social media automation ML system.

## Overview

This system integrates with three main external technologies:
1. **Ultralytics YOLOv8** - Computer vision for UI element detection
2. **GoLogin** - Browser profile management for web automation
3. **Google Cloud** (Optional) - Cloud ML and storage services

## 1. Ultralytics YOLOv8

### What it does
Ultralytics YOLOv8 is used for detecting UI elements in social media platform screenshots (like buttons, icons, video players, etc.).

### Installation

Already included in `requirements.txt`:
```bash
pip install ultralytics==8.0.196
```

### Documentation
- Official docs: https://docs.ultralytics.com/
- YOLOv8 Guide: https://docs.ultralytics.com/models/yolov8/
- Training Guide: https://docs.ultralytics.com/modes/train/

### Usage in this project

The system uses YOLOv8 in two ways:

1. **Dummy Mode** (default): Uses a dummy detector that returns simulated results
2. **Production Mode**: Uses real YOLOv8 models trained on social media UI screenshots

#### Training your own model

1. Collect and label screenshots from your target platform(s)
2. Organize data according to `config/ml/data.yaml` structure
3. Run training:
   ```bash
   python -m ml_core.training.train_yolo
   ```
4. Update model path in `config/ml/model_config.yaml`

#### Model classes

Default UI element classes (customize for your platform):
- like_button
- follow_button
- comment_button
- video_player
- profile_icon
- share_button
- text_overlay
- thumbnail
- user_avatar

### Key files
- `ml_core/models/yolo_prod.py` - Production YOLOv8 implementation
- `ml_core/training/train_yolo.py` - Training script
- `config/ml/model_config.yaml` - Model configuration
- `config/ml/data.yaml` - Dataset configuration

## 2. GoLogin

### What it does
GoLogin provides browser profile management with anti-detection features for web automation. It allows you to:
- Create and manage multiple browser profiles
- Use different proxies per profile
- Avoid bot detection
- Automate web interactions

### Setup

1. **Get GoLogin account**
   - Sign up at https://gologin.com/
   - Get API credentials from dashboard

2. **Set environment variables**
   ```bash
   export GOLOGIN_API_TOKEN="your_api_token_here"
   export GOLOGIN_API_URL="https://api.gologin.com"
   ```

3. **Configure profiles**
   - Create profiles via GoLogin dashboard or API
   - Configure proxies for each profile
   - Set browser fingerprints

### Documentation
- Official docs: https://gologin.com/docs
- API reference: https://api.gologin.com/docs
- Python SDK: https://github.com/gologinapp/gologin-python

### Usage in this project

The system uses GoLogin for:
- Managing browser sessions
- Opening social media platforms without detection
- Taking screenshots for ML analysis
- Performing automated actions

#### Dummy Mode (default)
Uses simulated GoLogin client that returns fake responses.

#### Production Mode
To enable real GoLogin:
1. Set up account and get API credentials
2. Set environment variables
3. Set `DUMMY_MODE=false`
4. Update factory to use real GoLogin client

### Key files
- `gologin_automation/api/gologin_client.py` - GoLogin API wrapper
- `gologin_automation/browser/selenium_wrapper.py` - Browser automation wrapper

### Example usage
```python
from gologin_automation.api.gologin_client import GoLoginClient

client = GoLoginClient()
profile = client.create_profile("my-profile")
client.start_profile(profile["id"])

# Use with Selenium wrapper
from gologin_automation.browser.selenium_wrapper import SeleniumWrapper
sw = SeleniumWrapper(profile)
sw.open("https://example.com")
screenshot = sw.screenshot()
```

## 3. Google Cloud (Optional)

### What it does
Google Cloud Platform can be used for:
- Cloud-based ML training (Vertex AI)
- Model hosting
- Data storage (Cloud Storage)
- Serverless functions (Cloud Functions)
- BigQuery for analytics

### When to use
Google Cloud is **optional** and recommended if you:
- Need GPU-based training at scale
- Want to host models in the cloud
- Need to process large amounts of data
- Want to use BigQuery for analytics
- Need Cloud Storage for screenshots/videos

### Setup

1. **Create Google Cloud account**
   - Go to https://cloud.google.com/
   - Create a new project

2. **Enable required APIs**
   ```bash
   gcloud services enable storage.googleapis.com
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable compute.googleapis.com
   ```

3. **Set up authentication**
   
   **Option A: Service Account (recommended for production)**
   ```bash
   # Create service account
   gcloud iam service-accounts create ml-automation-sa
   
   # Grant permissions
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:ml-automation-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/storage.admin"
   
   # Create and download key
   gcloud iam service-accounts keys create key.json \
     --iam-account=ml-automation-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
   
   # Set environment variable
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
   ```
   
   **Option B: User credentials (for development)**
   ```bash
   gcloud auth application-default login
   ```

4. **Install Google Cloud SDK**
   ```bash
   pip install google-cloud-storage google-cloud-aiplatform
   ```

### Documentation
- Getting started: https://cloud.google.com/docs/get-started
- Authentication: https://cloud.google.com/docs/authentication
- Python client libraries: https://cloud.google.com/python/docs/reference
- Vertex AI: https://cloud.google.com/vertex-ai/docs
- Cloud Storage: https://cloud.google.com/storage/docs

### Usage scenarios

#### Store screenshots in Cloud Storage
```python
from google.cloud import storage

client = storage.Client()
bucket = client.bucket('my-screenshots-bucket')
blob = bucket.blob('screenshots/2025-10-23/image1.png')
blob.upload_from_string(screenshot_bytes, content_type='image/png')
```

#### Train models on Vertex AI
```python
from google.cloud import aiplatform

aiplatform.init(project='my-project', location='us-central1')

job = aiplatform.CustomTrainingJob(
    display_name='yolo-training',
    script_path='ml_core/training/train_yolo.py',
    container_uri='gcr.io/my-project/yolo-trainer',
    requirements=['ultralytics', 'torch']
)

job.run(
    replica_count=1,
    machine_type='n1-standard-8',
    accelerator_type='NVIDIA_TESLA_T4',
    accelerator_count=1
)
```

### Key considerations

- **Cost**: Google Cloud services are billed. Monitor usage carefully.
- **Regions**: Choose region close to your location for lower latency
- **Quotas**: Check and request quota increases if needed
- **Security**: Never commit credentials to git. Use environment variables or secret managers.

### Environment variables

```bash
# Required for Google Cloud
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_REGION="us-central1"

# Optional - for specific services
export GCS_BUCKET_NAME="your-bucket-name"
export VERTEX_AI_LOCATION="us-central1"
```

## Integration Checklist

### For Dummy Mode (Development)
- [x] Install Python dependencies
- [x] Set `DUMMY_MODE=true`
- [x] No external credentials needed

### For Production Mode
- [ ] Install production dependencies
- [ ] Train YOLOv8 models on platform-specific data
- [ ] Get GoLogin API credentials
- [ ] Configure GoLogin profiles and proxies
- [ ] (Optional) Set up Google Cloud project
- [ ] (Optional) Configure Google Cloud authentication
- [ ] Set environment variables
- [ ] Update `config/ml/model_config.yaml`
- [ ] Set `DUMMY_MODE=false`
- [ ] Run integration tests

## Troubleshooting

### Ultralytics issues
- **Import error**: Make sure torch is installed: `pip install torch`
- **CUDA not found**: Install CUDA toolkit or use CPU mode: `device: cpu` in config
- **Model not found**: Check path in `config/ml/model_config.yaml`

### GoLogin issues
- **API errors**: Verify API token is correct
- **Profile creation fails**: Check account quota and billing status
- **Browser won't start**: Verify profile status with `list_profiles()`

### Google Cloud issues
- **Authentication fails**: Check `GOOGLE_APPLICATION_CREDENTIALS` path
- **Permission denied**: Verify service account has required roles
- **Quota exceeded**: Request quota increase in Cloud Console
- **Cost concerns**: Set up billing alerts and budgets

## Security Best Practices

1. **Never commit credentials**
   - Add to `.gitignore`: `*.json`, `.env`, `credentials/`
   - Use environment variables or secret managers

2. **Use least privilege**
   - Grant only necessary permissions to service accounts
   - Rotate credentials regularly

3. **Monitor access**
   - Enable audit logging
   - Review access logs regularly
   - Set up alerts for suspicious activity

4. **Encrypt sensitive data**
   - Use encrypted storage for screenshots
   - Encrypt API tokens in transit and at rest

## Support

For issues with:
- **Ultralytics**: https://github.com/ultralytics/ultralytics/issues
- **GoLogin**: https://gologin.com/support
- **Google Cloud**: https://cloud.google.com/support

For issues with this project:
- GitHub Issues: https://github.com/albertomaydayjhondoe/master/issues
