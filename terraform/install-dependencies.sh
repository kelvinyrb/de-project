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

# Install Anaconda on VM
wget https://repo.anaconda.com/archive/Anaconda3-2022.10-Linux-x86_64.sh
bash Anaconda3-2022.10-Linux-x86_64.sh
rm https://repo.anaconda.com/archive/Anaconda3-2022.10-Linux-x86_64.sh

# Install docker
sudo apt-get update
sudo apt-get install docker.io

# Set up docker without sudo
https://github.com/sindresorhus/guides/blob/main/docker-without-sudo.md
sudo groupadd docker
sudo gpasswd -a $USER docker
sudo service docker restart

# Get docker compose
mkdir bin
cd bin
wget https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-linux-x86_64 -O docker-compose
chmod +x docker-compose

# Install Google SDK
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-418.0.0-linux-x86_64.tar.gz
tar -xf google-cloud-cli-418.0.0-linux-x86_64.tar.gz
rm google-cloud-cli-418.0.0-linux-x86_64.tar.gz
./google-cloud-sdk/install.sh

# Authenticate service account
gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS