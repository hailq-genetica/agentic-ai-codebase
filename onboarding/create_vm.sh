export IMAGE_FAMILY="pytorch-2-7-cu128-ubuntu-2204-nvidia-570"
export ZONE="us-central1-a"
export INSTANCE_NAME="agentic-vm"
export PROJECT="vanallen-username"
gcloud compute instances create $INSTANCE_NAME \
  --zone=$ZONE \
  --project=$PROJECT \
  --image-family=$IMAGE_FAMILY \
  --image-project=deeplearning-platform-release \
  --maintenance-policy=TERMINATE \
  --machine-type=n1-standard-32 \
  --boot-disk-size=300GB \
  --metadata="install-nvidia-driver=True"
