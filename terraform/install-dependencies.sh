#!/bin/bash

# Store Google Credentials for service account
credentials_path=".gc/gc-key.json"
bashrc_path="$HOME/.bashrc"
if grep -qxF "export GOOGLE_APPLICATION_CREDENTIALS=$credentials_path" "$bashrc_path"; then
    echo "Credentials already set in .bashrc"
else
    echo "Adding credentials to .bashrc"
    echo "export GOOGLE_APPLICATION_CREDENTIALS=$credentials_path" >> "$bashrc_path"
    source "$bashrc_path"
fi

# Authenticate service account
echo "Key: $GOOGLE_APPLICATION_CREDENTIALS"
gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS

# Install docker
sudo apt-get update
sudo apt-get install -y docker.io

# Set up docker without sudo
sudo groupadd docker
sudo gpasswd -a $USER docker
sudo service docker restart

# Get docker compose
mkdir bin
cd bin
wget https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-linux-x86_64 -O docker-compose
chmod +x docker-compose
cd ~