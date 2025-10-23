# Migration Guide: From TikTok to Multi-Platform

This guide helps you migrate from the previous TikTok-specific implementation to the new platform-agnostic social media automation system.

## What Changed

### Package Naming
- **Old**: `tiktok-viral-ml`
- **New**: `social-media-automation-ml`

**Action**: Update any scripts or deployment configs that reference the old package name.

### Model Paths
- **Old**: `tiktok_ui_detector.pt`, `tiktok_video_analyzer.pt`
- **New**: `social_ui_detector.pt`, `social_video_analyzer.pt`

**Action**: 
1. Rename existing model files if you have them
2. Update `config/ml/model_config.yaml`

```bash
# If you have existing models
cd /app/data/models/production/
mv tiktok_ui_detector.pt social_ui_detector.pt
mv tiktok_video_analyzer.pt social_video_analyzer.pt
```

### Dataset Paths
- **Old**: `/app/data/datasets/tiktok_ui/`
- **New**: `/app/data/datasets/social_ui/`

**Action**: Rename dataset directories

```bash
# If you have existing datasets
cd /app/data/datasets/
mv tiktok_ui social_ui
```

### Configuration Files

Update references in:
- `config/ml/model_config.yaml` ✓ (already updated)
- `config/ml/data.yaml` ✓ (already updated)
- Any custom configs you've created

## Platform-Specific Implementation

The new architecture supports multiple social media platforms. Here's how to add platform-specific support:

### 1. Choose Your Target Platform(s)

Supported platform examples:
- Twitter/X
- Instagram
- Facebook
- LinkedIn
- YouTube
- Reddit
- Mastodon
- Others

### 2. Create Platform-Specific Modules

Create a new module for each platform:

```
platforms/
├── __init__.py
├── twitter/
│   ├── __init__.py
│   ├── api_client.py
│   ├── actions.py
│   └── ui_detector.py
├── instagram/
│   ├── __init__.py
│   ├── api_client.py
│   ├── actions.py
│   └── ui_detector.py
└── common/
    ├── __init__.py
    ├── base_client.py
    └── base_actions.py
```

### 3. Train Platform-Specific Models

For each platform:

1. **Collect screenshots**
   ```bash
   # Take screenshots of the platform UI
   # Organize in: data/datasets/social_ui/{platform}/images/
   ```

2. **Label UI elements**
   - Use tools like [LabelImg](https://github.com/heartexlabs/labelImg) or [CVAT](https://github.com/opencv/cvat)
   - Label buttons, icons, video players, etc.
   - Export to YOLO format

3. **Update data.yaml**
   ```yaml
   # config/ml/data_twitter.yaml
   path: /app/data/datasets/social_ui/twitter
   train: train/images
   val: val/images
   
   names:
     0: like_button
     1: retweet_button
     2: reply_button
     3: follow_button
     4: profile_avatar
     # ... add platform-specific elements
   ```

4. **Train model**
   ```bash
   # Customize training script for your platform
   python -m ml_core.training.train_yolo --platform twitter
   ```

### 4. Update Configuration

Create platform-specific configs:

```yaml
# config/platforms/twitter.yaml
platform: twitter
ui_detector:
  model_path: /app/data/models/production/twitter_ui_detector.pt
  classes:
    - like_button
    - retweet_button
    - reply_button

api:
  base_url: https://api.twitter.com/2
  rate_limits:
    posts_per_hour: 50
    follows_per_day: 100
```

### 5. Implement Platform Actions

Create action handlers for each platform:

```python
# platforms/twitter/actions.py
from platforms.common.base_actions import BaseActions

class TwitterActions(BaseActions):
    async def like_post(self, post_id: str):
        """Like a tweet."""
        pass
    
    async def follow_user(self, user_id: str):
        """Follow a user."""
        pass
    
    async def post_tweet(self, text: str, media: list = None):
        """Post a tweet."""
        pass
```

## Backward Compatibility

If you need to maintain TikTok-specific functionality:

### Option 1: Keep as a Platform Module

Create `platforms/tiktok/` with your existing logic:

```
platforms/tiktok/
├── __init__.py
├── api_client.py
├── actions.py
└── ui_detector.py
```

Move TikTok-specific code here and treat it like any other platform.

### Option 2: Symlinks (Temporary)

Create symlinks for legacy code:

```bash
# Temporary backward compatibility
ln -s /app/data/models/production/social_ui_detector.pt \
      /app/data/models/production/tiktok_ui_detector.pt
```

## Testing Your Migration

### 1. Verify Dummy Mode Still Works

```bash
export DUMMY_MODE=true
uvicorn ml_core.api.main:app --port 8000

# Test endpoints
curl http://localhost:8000/api/v1/analyze_screenshot \
  -H "X-API-Key: dummy_development_key" \
  -F "file=@test.png"
```

### 2. Test Platform-Specific Models

```bash
export DUMMY_MODE=false
export PLATFORM=twitter  # or instagram, etc.

# Run with your trained model
uvicorn ml_core.api.main:app --port 8000
```

### 3. Run Test Suite

```bash
PYTHONPATH=. pytest tests/unit/ -v
PYTHONPATH=. pytest tests/integration/ -v
```

## Rollback Plan

If you need to rollback:

1. **Revert package name**
   ```bash
   # In setup.py, change back to:
   name="tiktok-viral-ml"
   ```

2. **Restore model paths**
   ```bash
   cd /app/data/models/production/
   mv social_ui_detector.pt tiktok_ui_detector.pt
   ```

3. **Revert config files**
   ```bash
   git checkout HEAD~1 config/ml/model_config.yaml
   git checkout HEAD~1 config/ml/data.yaml
   ```

## Breaking Changes

### None!

This migration is **non-breaking** because:
- Only naming and documentation changed
- No logic or API changes
- All functionality remains the same
- Dummy mode still works identically

## Incremental Migration Strategy

You can migrate incrementally:

### Week 1: Update naming
- ✅ Update package name
- ✅ Update documentation
- ✅ Update config files
- Test in dummy mode

### Week 2: Add platform abstraction
- Create platform modules
- Implement base classes
- Test with TikTok as first platform

### Week 3: Add new platforms
- Choose target platform (e.g., Twitter)
- Collect and label data
- Train platform-specific model
- Implement platform actions

### Week 4: Production testing
- Test each platform individually
- Run integration tests
- Deploy gradually per platform

## Common Issues

### Issue: Import errors after renaming

**Solution**: Clear Python cache
```bash
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Issue: Model not found

**Solution**: Check model path in config
```bash
# Verify file exists
ls -la /app/data/models/production/social_ui_detector.pt

# Check config
cat config/ml/model_config.yaml | grep model_path
```

### Issue: Old references in code

**Solution**: Search and replace
```bash
# Find any remaining tiktok references
grep -r "tiktok" --include="*.py" .

# Replace if needed
find . -name "*.py" -exec sed -i 's/tiktok/social/g' {} +
```

## Next Steps

1. **Choose platforms**: Decide which platforms to support
2. **Collect data**: Start gathering screenshots and labels
3. **Train models**: Create platform-specific detectors
4. **Implement APIs**: Add platform API clients
5. **Test thoroughly**: Run integration tests per platform
6. **Deploy gradually**: Roll out one platform at a time

## Questions?

- Check [technical_integrations.md](./technical_integrations.md) for setup details
- Review [API integration guide](./api_integration.md) for API usage
- Open GitHub issue for specific problems

## Changelog

- **2025-10-23**: Initial migration from TikTok-specific to multi-platform
  - Renamed package: `tiktok-viral-ml` → `social-media-automation-ml`
  - Updated model paths: `tiktok_ui_detector.pt` → `social_ui_detector.pt`
  - Added technical integrations documentation
  - Added platform abstraction support
