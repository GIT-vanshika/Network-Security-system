# GitHub Actions CI/CD Setup Guide

This project is configured for continuous integration and deployment using GitHub Actions.

## GitHub Actions Workflows

### 1. **ci-cd.yml** (Main CI/CD Pipeline)

Triggers on every push to `main` and `develop` branches, and all pull requests.

**Steps:**
- ✅ **Test Stage**: 
  - Runs Python tests with MongoDB service
  - Performs code linting
  - Generates coverage reports
  - Uploads coverage to Codecov

- 🔨 **Build Stage** (after tests pass):
  - Builds Docker image
  - Pushes to GitHub Container Registry (GHCR)
  - Uses layer caching for faster builds

### 2. **deploy.yml** (Deployment Workflow)

Triggers on:
- Git tags matching `v*.*.*` (e.g., v1.0.0)
- Manual trigger (workflow_dispatch) for staging/production

**Steps:**
- 🚀 Builds and pushes optimized Docker image
- 📦 Tags with semantic version
- ✅ Notifies on successful deployment

## Setup Instructions

### Step 1: GitHub Repository Configuration

1. **Enable GitHub Container Registry**:
   - Go to Settings → Actions → General
   - Enable "Read and write permissions"

2. **Create Environments** (Optional, for manual deployments):
   ```
   Settings → Environments → New environment
   - staging
   - production
   ```

### Step 2: Configure Secrets

GitHub automatically provides `GITHUB_TOKEN`, but you can add custom secrets:

```
Settings → Secrets and variables → Actions → New repository secret
```

Optional secrets to add:
- `DOCKER_HUB_USERNAME` - For Docker Hub push
- `DOCKER_HUB_TOKEN` - Docker Hub access token
- `DEPLOYMENT_KEY` - SSH key for deployments
- `SLACK_WEBHOOK` - For Slack notifications

### Step 3: Update docker-compose.yml (Optional)

For production deployments, use the production Dockerfile:

```yaml
app:
  build:
    context: .
    dockerfile: Dockerfile.prod  # Use production build
```

## Local CI/CD Testing

Run the complete CI pipeline locally:

```bash
# Option 1: Using make
make ci-local

# Option 2: Manual steps
make install-dev
make lint
make test

# Option 3: Docker compose
docker-compose up -d
docker-compose exec app pytest -v
```

## Workflow Behaviors

### On Push to main/develop
```
Code → Lint → Test → Build Docker Image → Push to GHCR
```

### On Pull Request
```
Code → Lint → Test → (No push, unless merge)
```

### On Git Tag (v*.*.*) or Manual Trigger
```
Build Production Image → Push to GHCR with Version Tag
```

## Image Registry

All images are pushed to GitHub Container Registry (GHCR):

```
ghcr.io/yourusername/cyber_security_ml:main
ghcr.io/yourusername/cyber_security_ml:v1.0.0
```

## Monitoring Builds

1. **GitHub**: Settings → Actions → Workflow runs
2. **View logs**: Click on workflow → View detailed logs
3. **Badges**: Add to README.md:

```markdown
[![Build and Test](https://github.com/yourusername/cyber_security_ml/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/yourusername/cyber_security_ml/actions)
```

## Troubleshooting

### Build Fails
- Check runner logs: Actions tab → Workflow → View logs
- Common issues:
  - Missing dependencies in requirements.txt
  - Python version mismatch
  - MongoDB service not starting

### Image Not Pushing
- Verify GITHUB_TOKEN has write permissions
- Check repository visibility (Container Registry requires authentication)
- Ensure branch name matches trigger condition

### Tests Timeout
- Increase timeout in workflow file:
  ```yaml
  jobs:
    test:
      timeout-minutes: 30
  ```

## Customization

### Change Build Context
Edit `.github/workflows/ci-cd.yml`:
```yaml
with:
  context: ./Cyber  # Change path if different
```

### Change Python Version
```yaml
python-version: '3.10'  # Change to 3.9, 3.11, etc.
```

### Add Slack Notifications
```yaml
- name: Notify Slack
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "Build failed for ${{ github.repository }}"
      }
```

## Next Steps

1. ✅ Push `.github/workflows/` to your repository
2. ✅ Commit and push to trigger first workflow
3. ✅ Monitor Actions tab for build results
4. ✅ Set up branch protection: Settings → Branches → Add rule
   - Require status checks to pass before merging

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Action](https://github.com/docker/build-push-action)
- [Container Registry Guide](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
