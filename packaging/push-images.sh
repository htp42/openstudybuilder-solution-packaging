#!/bin/bash

# Script to build, tag, and push Docker images to htp42/openstudybuilder
# Usage: ./push-images.sh [version] [--no-cache] [--pull] [--exclude image1,image2,...]
# Example: ./push-images.sh 2.0.1
# Example: ./push-images.sh 2.0.1 --no-cache  # Force rebuild without cache
# Example: ./push-images.sh 2.0.1 --pull      # Pull latest base images before building
# Example: ./push-images.sh 2.0.1 --exclude neodash,documentation  # Exclude specific images
#
# Also uploads a database backup to S3 if S3_BUCKET is set.
#
# Docker Hub Authentication:
#   The script will check if you're logged in to Docker Hub. You can authenticate by:
#   1. Running 'docker login' before running this script
#   2. Setting environment variables:
#      export DOCKER_USERNAME=your_username
#      export DOCKER_PASSWORD=your_password_or_token
#
# Environment variables:
#   DOCKER_USERNAME - Docker Hub username (optional, for automatic login)
#   DOCKER_PASSWORD - Docker Hub password or access token (optional, for automatic login)
#   DOCKER_BUILDER - Docker cloud builder name (optional, if not set builds locally)
#   EXCLUDE_IMAGES - Comma-separated list of images to exclude (optional, e.g., "neodash,documentation")
#   S3_BUCKET - S3 bucket name for database backups (optional)
#   AWS_ACCESS_KEY_ID - AWS access key (required if S3_BUCKET is set)
#   AWS_SECRET_ACCESS_KEY - AWS secret key (required if S3_BUCKET is set)
#   AWS_REGION - AWS region (optional, defaults to us-west-3)

set -e

VERSION=${1:-2.0.1}
REPOSITORY="htp42/openstudybuilder"
DOCKER_BUILDER=${DOCKER_BUILDER:-""}
S3_BUCKET=${S3_BUCKET:-""}
AWS_REGION=${AWS_REGION:-"eu-west-3"}
EXCLUDE_IMAGES=${EXCLUDE_IMAGES:-""}

# Parse additional arguments (skip first argument which is version)
BAKE_ARGS=()
shift  # Remove version from arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --no-cache)
      BAKE_ARGS+=("--no-cache")
      shift
      ;;
    --pull)
      BAKE_ARGS+=("--pull")
      shift
      ;;
    --exclude)
      shift
      EXCLUDE_IMAGES="$1"
      shift
      ;;
    --exclude=*)
      EXCLUDE_IMAGES="${1#*=}"
      shift
      ;;
    *)
      echo "Warning: Unknown argument: $1"
      shift
      ;;
  esac
done

# Function to check if logged in to Docker Hub
check_docker_login() {
  echo "Checking Docker Hub authentication..."
  
  # Check if docker is installed
  if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
  fi
  
  # Check if Docker daemon is running
  if ! docker info &> /dev/null; then
    echo "Error: Docker daemon is not running or not accessible"
    exit 1
  fi
  
  # Check if environment variables are set (alternative login method)
  if [ -n "${DOCKER_USERNAME:-}" ] && [ -n "${DOCKER_PASSWORD:-}" ]; then
    echo "Docker credentials found in environment variables, attempting login..."
    echo "${DOCKER_PASSWORD}" | docker login --username "${DOCKER_USERNAME}" --password-stdin 2>/dev/null || {
      echo "Error: Failed to login to Docker Hub with provided credentials"
      exit 1
    }
    echo "✓ Successfully logged in to Docker Hub"
    return 0
  fi
  
  # Check if already logged in by checking docker config
  DOCKER_CONFIG="${HOME}/.docker/config.json"
  if [ -f "${DOCKER_CONFIG}" ] && grep -q '"auths"' "${DOCKER_CONFIG}" 2>/dev/null; then
    # Check if docker.io or index.docker.io is in the auths
    if grep -q '"docker.io"' "${DOCKER_CONFIG}" || grep -q '"https://index.docker.io/v1/"' "${DOCKER_CONFIG}" 2>/dev/null; then
      echo "✓ Docker Hub authentication found in config"
      return 0
    fi
  fi
  
  # Not logged in - prompt user (only if interactive terminal)
  echo ""
  echo "⚠️  Warning: Not logged in to Docker Hub"
  echo ""
  echo "Please log in to Docker Hub using one of these methods:"
  echo "  1. Run: docker login"
  echo "  2. Or set environment variables before running this script:"
  echo "     export DOCKER_USERNAME=your_username"
  echo "     export DOCKER_PASSWORD=your_password_or_token"
  echo ""
  
  # Only prompt if we have an interactive terminal
  if [ -t 0 ]; then
    read -p "Attempt to login now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      docker login || {
        echo "Error: Docker login failed"
        exit 1
      }
      echo "✓ Successfully logged in to Docker Hub"
    else
      echo "Error: Docker Hub login required to push images"
      exit 1
    fi
  else
    echo "Error: Docker Hub login required to push images"
    echo "Run 'docker login' or set DOCKER_USERNAME and DOCKER_PASSWORD environment variables"
    exit 1
  fi
}

# Check Docker login status
check_docker_login

echo "Building and pushing images for version ${VERSION} to ${REPOSITORY}"
echo ""

# Export version for docker-compose
export VERSION=${VERSION}

# Services to build and push (service_name:image_suffix)
ALL_SERVICES=(
  "database:database"
  "api:api"
  "consumerapi:consumerapi"
  "frontend:frontend"
  "documentation:documentation"
  "neodash:neodash"
)

# Filter out excluded services
SERVICES=()
if [ -n "$EXCLUDE_IMAGES" ]; then
  echo "Excluding images: ${EXCLUDE_IMAGES}"
  echo ""

  # Convert comma-separated list to array
  IFS=',' read -ra EXCLUDED_ARRAY <<< "$EXCLUDE_IMAGES"

  # Build list of services to process
  for service_info in "${ALL_SERVICES[@]}"; do
    IFS=':' read -r service_name image_suffix <<< "$service_info"

    # Check if this image should be excluded
    excluded=false
    for excluded_image in "${EXCLUDED_ARRAY[@]}"; do
      # Trim whitespace
      excluded_image=$(echo "$excluded_image" | xargs)
      if [ "$image_suffix" == "$excluded_image" ] || [ "$service_name" == "$excluded_image" ]; then
        excluded=true
        echo "Skipping ${image_suffix} (excluded)"
        break
      fi
    done

    if [ "$excluded" = false ]; then
      SERVICES+=("$service_info")
    fi
  done
  echo ""
else
  # No exclusions, use all services
  SERVICES=("${ALL_SERVICES[@]}")
fi

# Check if there are any services to build
if [ ${#SERVICES[@]} -eq 0 ]; then
  echo "Error: All services have been excluded. Nothing to build."
  exit 1
fi

# Build list of service names to build
SERVICE_NAMES=()
for service_info in "${SERVICES[@]}"; do
  IFS=':' read -r service_name image_suffix <<< "$service_info"
  SERVICE_NAMES+=("$service_name")
done

# Build images using docker-compose or docker buildx bake
if [ -n "$DOCKER_BUILDER" ]; then
  echo "Building images with docker-compose using cloud builder: ${DOCKER_BUILDER}..."
  docker compose build --builder "${DOCKER_BUILDER}" "${SERVICE_NAMES[@]}"

  echo ""
  echo "Tagging and pushing images..."
  echo ""

  # Tag and push each image with both version and latest tags (for docker compose build)
  for service_info in "${SERVICES[@]}"; do
    IFS=':' read -r service_name image_suffix <<< "$service_info"
    
    # Construct target image names
    VERSION_IMAGE="${REPOSITORY}:${image_suffix}-${VERSION}"
    LATEST_IMAGE="${REPOSITORY}:${image_suffix}-latest"
    
    # Get the actual image name from docker-compose config
    # This resolves environment variables and defaults
    SOURCE_IMAGE=$(docker compose config --images ${service_name} 2>/dev/null || echo "")
    
    if [ -z "$SOURCE_IMAGE" ]; then
      # Fallback: construct expected image name
      SOURCE_IMAGE="${VERSION_IMAGE}"
    fi
    
    # Verify the source image exists
    if ! docker image inspect "${SOURCE_IMAGE}" >/dev/null 2>&1; then
      echo "Warning: Image ${SOURCE_IMAGE} not found. Trying to find by service name..."
      # Try to find by service name or image suffix
      FOUND_IMAGE=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep -i "${image_suffix}" | head -1)
      if [ -n "$FOUND_IMAGE" ]; then
        SOURCE_IMAGE="${FOUND_IMAGE}"
        echo "Found image: ${SOURCE_IMAGE}"
      else
        echo "Error: Could not find built image for service ${service_name}. Skipping..."
        continue
      fi
    fi
    
    # Tag with version (if not already the version tag)
    if [ "$SOURCE_IMAGE" != "$VERSION_IMAGE" ]; then
      echo "Tagging ${SOURCE_IMAGE} as ${VERSION_IMAGE}"
      docker tag "${SOURCE_IMAGE}" "${VERSION_IMAGE}"
    else
      echo "Image already tagged as ${VERSION_IMAGE}"
    fi
    
    # Tag as latest
    echo "Tagging ${VERSION_IMAGE} as ${LATEST_IMAGE}"
    docker tag "${VERSION_IMAGE}" "${LATEST_IMAGE}"
    
    # Push version tag
    echo "Pushing ${VERSION_IMAGE}..."
    docker push "${VERSION_IMAGE}"
    
    # Push latest tag
    echo "Pushing ${LATEST_IMAGE}..."
    docker push "${LATEST_IMAGE}"
    
    echo "✓ Successfully pushed ${image_suffix} images (${VERSION} and latest)"
    echo ""
  done
else
  echo "Building and pushing images locally with docker buildx bake..."
  echo ""

  # Build and push with buildx bake (handles multi-platform builds and manifest lists)
  # First, build and push with version tag
  # This will rebuild images and push them with attestations
  docker buildx bake -f compose.yaml --set "*.platform=linux/amd64,linux/arm64" --push "${BAKE_ARGS[@]}" "${SERVICE_NAMES[@]}"
  
  echo ""
  echo "Creating and pushing 'latest' tags..."
  echo ""
  
  # For buildx bake, we need to create manifest lists for 'latest' tags
  # Get image names and create latest tags using docker buildx imagetools
  for service_info in "${SERVICES[@]}"; do
    IFS=':' read -r service_name image_suffix <<< "$service_info"
    
    # Construct target image names (these match the pattern in compose.yaml)
    VERSION_IMAGE="${REPOSITORY}:${image_suffix}-${VERSION}"
    LATEST_IMAGE="${REPOSITORY}:${image_suffix}-latest"
    
    # Use the constructed version image name directly
    # (docker compose config --images returns all images, not filtered by service)
    SOURCE_IMAGE="${VERSION_IMAGE}"
    
    # Create latest tag by creating a manifest that points to the version tag
    # This preserves multi-platform support
    echo "Creating latest tag for ${image_suffix}..."
    docker buildx imagetools create -t "${LATEST_IMAGE}" "${SOURCE_IMAGE}" || {
      echo "Warning: Failed to create latest tag using imagetools, trying alternative method..."
      # Alternative: use docker manifest (if imagetools fails)
      docker manifest create "${LATEST_IMAGE}" "${SOURCE_IMAGE}" 2>/dev/null || true
      docker manifest push "${LATEST_IMAGE}" 2>/dev/null || {
        echo "Error: Could not create/push latest tag for ${image_suffix}"
        continue
      }
    }
    
    echo "✓ Successfully created and pushed ${image_suffix}-latest tag"
    echo ""
  done
fi

# Extract and upload database backup to S3 if bucket is configured
if [ -n "$S3_BUCKET" ]; then
  echo ""
  echo "=========================================="
  echo "Extracting and uploading database backup to S3..."
  echo "=========================================="
  echo ""
  
  # Check if AWS CLI is installed
  if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed. Please install it to upload backups to S3."
    echo "Skipping S3 upload..."
  else
    # Check AWS credentials
    if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
      echo "Error: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set to upload to S3."
      echo "Skipping S3 upload..."
    else
      # Get the database image name
      DATABASE_IMAGE="${REPOSITORY}:database-${VERSION}"
      
      # Verify the database image exists
      if ! docker image inspect "${DATABASE_IMAGE}" >/dev/null 2>&1; then
        echo "Warning: Database image ${DATABASE_IMAGE} not found. Trying to find database image..."
        FOUND_IMAGE=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep -i "database" | head -1)
        if [ -n "$FOUND_IMAGE" ]; then
          DATABASE_IMAGE="${FOUND_IMAGE}"
          echo "Found database image: ${DATABASE_IMAGE}"
        else
          echo "Error: Could not find database image. Skipping S3 upload..."
          exit 1
        fi
      fi
      
      # Convert version format: replace dots with dashes (e.g., 2.0.1 -> 2-0-1)
      VERSION_DASHES=$(echo "${VERSION}" | tr '.' '-')
      BACKUP_FILENAME="mdrdb-${VERSION_DASHES}.backup"
      
      # Create temporary container to extract backup
      TEMP_CONTAINER=$(docker create "${DATABASE_IMAGE}")
      TEMP_DIR=$(mktemp -d)
      
      echo "Extracting backup from image ${DATABASE_IMAGE}..."
      # Extract backup from the image (it's in /data/backup/mdrdockerdb.backup in production stage)
      docker cp "${TEMP_CONTAINER}:/data/backup/mdrdockerdb.backup" "${TEMP_DIR}/${BACKUP_FILENAME}" || {
        echo "Error: Failed to extract backup from image. The backup might not exist in the expected location."
        docker rm "${TEMP_CONTAINER}" >/dev/null 2>&1
        rm -rf "${TEMP_DIR}"
        exit 1
      }
      
      docker rm "${TEMP_CONTAINER}" >/dev/null 2>&1
      
      S3_KEY="vanilla/${BACKUP_FILENAME}"
      echo "Uploading backup to s3://${S3_BUCKET}/${S3_KEY}..."
      # Upload to S3
      aws s3 cp "${TEMP_DIR}/${BACKUP_FILENAME}" "s3://${S3_BUCKET}/${S3_KEY}" \
        --region "${AWS_REGION}" \
        --metadata "version=${VERSION},backup-date=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      
      if [ $? -eq 0 ]; then
        echo "✓ Successfully uploaded backup to s3://${S3_BUCKET}/${S3_KEY}"
      else
        echo "Error: Failed to upload backup to S3"
        rm -rf "${TEMP_DIR}"
        exit 1
      fi
      
      # Clean up temporary directory
      rm -rf "${TEMP_DIR}"
      
      echo ""
      echo "Backup uploaded successfully!"
      echo "  S3 Location: s3://${S3_BUCKET}/vanilla/"
      echo "  Filename: ${BACKUP_FILENAME}"
      echo ""
    fi
  fi
fi

echo "=========================================="
echo "All images have been built, tagged, and pushed successfully!"
echo "Version: ${VERSION}"
echo "Repository: ${REPOSITORY}"
echo ""
echo "Images pushed:"
for service_info in "${SERVICES[@]}"; do
  IFS=':' read -r service_name image_suffix <<< "$service_info"
  echo "  - ${REPOSITORY}:${image_suffix}-${VERSION}"
  echo "  - ${REPOSITORY}:${image_suffix}-latest"
done
if [ -n "$S3_BUCKET" ]; then
  VERSION_DASHES=$(echo "${VERSION}" | tr '.' '-')
  echo ""
  echo "Database backup uploaded:"
  echo "  - s3://${S3_BUCKET}/vanilla/${BACKUP_FILENAME}"
fi
echo "=========================================="
