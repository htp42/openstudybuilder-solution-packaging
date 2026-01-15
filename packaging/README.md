# OpenStudyBuilder Image Push Script

This script builds, tags, and pushes Docker images for the OpenStudyBuilder solution to Docker Hub (`htp42/openstudybuilder`).

## Prerequisites

- **Docker**: Docker must be installed and the daemon must be running
- **Docker Buildx**: Required for multi-platform builds (linux/amd64 and linux/arm64)
- **Docker Hub account**: You need push access to the `htp42/openstudybuilder` repository
- **AWS CLI** (optional): Required only if uploading database backups to S3

## Usage

```bash
./push-images.sh [version] [options]
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `version` | The version tag for the images (e.g., `2.3.0`) | `2.0.1` |

### Options

| Option | Description |
|--------|-------------|
| `--no-cache` | Force rebuild without using Docker cache |
| `--pull` | Pull latest base images before building |
| `--exclude <images>` | Comma-separated list of images to exclude from the build |

## Examples

### Basic usage
```bash
./push-images.sh 2.3.0
```

### Force rebuild without cache
```bash
./push-images.sh 2.3.0 --no-cache
```

### Pull latest base images
```bash
./push-images.sh 2.3.0 --pull
```

### Exclude specific images
```bash
./push-images.sh 2.3.0 --exclude neodash,documentation
```

### Combine options
```bash
./push-images.sh 2.3.0 --no-cache --pull --exclude neodash
```

## Docker Hub Authentication

The script requires Docker Hub authentication to push images. You can authenticate using one of these methods:

### Option 1: Manual login (recommended for interactive use)
```bash
docker login
./push-images.sh 2.3.0
```

### Option 2: Environment variables (recommended for CI/CD)
```bash
export DOCKER_USERNAME=your_username
export DOCKER_PASSWORD=your_password_or_token
./push-images.sh 2.3.0
```

> **Note**: Using a Docker Hub access token instead of your password is recommended for security.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DOCKER_USERNAME` | Docker Hub username for automatic login | No |
| `DOCKER_PASSWORD` | Docker Hub password or access token | No |
| `DOCKER_BUILDER` | Docker cloud builder name. If set, uses `docker compose build`; otherwise uses `docker buildx bake` | No |
| `EXCLUDE_IMAGES` | Comma-separated list of images to exclude (alternative to `--exclude` flag) | No |
| `S3_BUCKET` | S3 bucket name for database backup uploads | No |
| `AWS_ACCESS_KEY_ID` | AWS access key (required if `S3_BUCKET` is set) | Conditional |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key (required if `S3_BUCKET` is set) | Conditional |
| `AWS_REGION` | AWS region for S3 uploads | No (default: `eu-west-3`) |

## Images Built

The script builds and pushes the following images:

| Service | Image Tag |
|---------|-----------|
| database | `htp42/openstudybuilder:database-<version>` |
| api | `htp42/openstudybuilder:api-<version>` |
| consumerapi | `htp42/openstudybuilder:consumerapi-<version>` |
| frontend | `htp42/openstudybuilder:frontend-<version>` |
| documentation | `htp42/openstudybuilder:documentation-<version>` |
| neodash | `htp42/openstudybuilder:neodash-<version>` |

Each image is pushed with both a version tag and a `latest` tag (e.g., `database-2.3.0` and `database-latest`).

## Build Modes

### Local Build (default)
When `DOCKER_BUILDER` is not set, the script uses `docker buildx bake` to build multi-platform images (linux/amd64 and linux/arm64) and pushes them directly to Docker Hub.

### Cloud Builder
When `DOCKER_BUILDER` is set, the script uses `docker compose build` with the specified cloud builder, then tags and pushes images individually.

```bash
export DOCKER_BUILDER=my-cloud-builder
./push-images.sh 2.3.0
```

## S3 Database Backup Upload

If `S3_BUCKET` is configured, the script will extract the database backup from the built database image and upload it to S3.

```bash
export S3_BUCKET=my-backup-bucket
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
./push-images.sh 2.3.0
```

The backup will be uploaded to:
```
s3://<bucket>/vanilla/mdrdb-<version>.backup
```

For example, version `2.3.0` creates `mdrdb-2-3-0.backup`.

## GitHub Actions Pipelines

This repository includes GitHub Actions workflows that automate the build and push process.

### Workflows

| Workflow | File | Description |
|----------|------|-------------|
| **Sync Upstream Tags** | `.github/workflows/sync-upstream-tags.yml` | Monitors the upstream repo for new version tags and syncs them to this fork |
| **Build and Push** | `.github/workflows/build-and-push.yml` | Builds Docker images and pushes them to Docker Hub, uploads backups to S3 |

### How It Works

1. **Automatic Sync**: The sync workflow runs every 6 hours to check for new `v*.*.*` tags on the upstream repository
2. **Tag Detection**: When a new tag is found (e.g., `v2.4.0`), it's synced to your fork
3. **Build Trigger**: The sync automatically triggers the build-and-push workflow
4. **Multi-Platform Build**: Images are built for both `linux/amd64` and `linux/arm64`
5. **S3 Upload**: Database backups are extracted and uploaded to S3

### Required Secrets

Configure these secrets in your GitHub repository settings (**Settings > Secrets and variables > Actions**):

| Secret | Description | Required |
|--------|-------------|----------|
| `DOCKER_USERNAME` | Docker Hub username | Yes |
| `DOCKER_PASSWORD` | Docker Hub password or access token | Yes |
| `AWS_ACCESS_KEY_ID` | AWS access key for S3 uploads | Yes |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key for S3 uploads | Yes |
| `S3_BUCKET` | S3 bucket name for database backups | Yes |
| `AWS_REGION` | AWS region (default: `eu-west-3`) | No |

### Manual Triggers

Both workflows support manual triggers via the GitHub Actions UI:

**Sync Workflow:**
- Go to **Actions > Sync Upstream Tags > Run workflow**
- Optionally specify a specific tag to sync (e.g., `v2.3.0`)

**Build Workflow:**
- Go to **Actions > Build and Push Images > Run workflow**
- Enter the version number (e.g., `2.3.0`)
- Optionally exclude specific images or skip S3 upload

### Setting Up Fork Auto-Sync

To enable automatic syncing of new version tags from the upstream repository:

1. **Fork the repository** (if not already done)

2. **Configure the upstream repository** in the workflow:
   - Edit `.github/workflows/sync-upstream-tags.yml`
   - Update the `UPSTREAM_REPO` environment variable if needed:
     ```yaml
     env:
       UPSTREAM_REPO: NovoNordisk-OpenSource/openstudybuilder-solution-packaging
     ```

3. **Add required secrets** (see table above)

4. **Enable GitHub Actions** in your fork:
   - Go to your fork's **Actions** tab
   - Click "I understand my workflows, go ahead and enable them"

5. **Verify the schedule** (optional):
   - The workflow runs every 6 hours by default
   - Modify the cron schedule in the workflow file if needed:
     ```yaml
     schedule:
       - cron: '0 */6 * * *'  # Every 6 hours
     ```

6. **Test manually**:
   - Go to **Actions > Sync Upstream Tags > Run workflow**
   - Click "Run workflow" to test the sync process

### Alternative: GitHub's Built-in Fork Sync

GitHub also provides a built-in "Sync fork" button, but it only syncs branches, not tags. The workflow approach is required for automatic tag syncing.

## Local CI/CD Example

For local or custom CI/CD pipelines, you can still use the shell script:

```bash
#!/bin/bash
export DOCKER_USERNAME="${DOCKER_HUB_USERNAME}"
export DOCKER_PASSWORD="${DOCKER_HUB_TOKEN}"
export S3_BUCKET="openstudybuilder-backups"
export AWS_ACCESS_KEY_ID="${AWS_KEY}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET}"

./push-images.sh "${RELEASE_VERSION}" --no-cache --pull
```

## Troubleshooting

### "Docker daemon is not running"
Start Docker Desktop or the Docker service on your system.

### "Not logged in to Docker Hub"
Run `docker login` or set `DOCKER_USERNAME` and `DOCKER_PASSWORD` environment variables.

### "All services have been excluded"
Ensure you haven't excluded all available images with the `--exclude` flag.

### "Failed to extract backup from image"
The database image may not contain a backup at the expected location (`/data/backup/mdrdockerdb.backup`).
