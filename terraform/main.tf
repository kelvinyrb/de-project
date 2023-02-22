provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone
}

# We create a public IP address for our google compute instance to utilize
resource "google_compute_address" "static" {
  name = "vm-public-address"
  project = var.project
  region = var.region
}

# Google Compute VM Instance
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_instance
resource "google_compute_instance" "vm_instance" {
  name         = "terraform-instance"
  machine_type = "e2-standard-2"
  # tags         = ["externalssh"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size = "10" // GB
    }
  }

  network_interface {
    # network = google_compute_network.vpc_network.self_link
    network = "default"
    access_config {
      nat_ip = google_compute_address.static.address
    }
  }

  provisioner "file" {
   source      = "~/.gc/"
   destination = ".gc/"
   connection {
     host        = google_compute_address.static.address
     type        = "ssh"
     user        = var.user 
     timeout     = "500s"
     private_key = file(var.privatekeypath)
   }
  }

  provisioner "remote-exec" {
    connection {
      host        = google_compute_address.static.address
      type        = "ssh"
      user        = var.user
      timeout     = "500s"
      private_key = file(var.privatekeypath)
    }
    inline = [
      "git clone https://github.com/kelvinyrb/de-project.git",
      "chmod +x de-project/terraform/install-dependencies.sh",
      "./de-project/terraform/install-dependencies.sh",
      "cd de-project/airflow",
      "docker-compose build"
    ]
  }
  
  service_account {
    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    email  = var.email
    scopes = ["cloud-platform"]
  }
  metadata = {
    ssh-keys = "${var.user}:${file(var.publickeypath)}"
  }
}

# Data Lake Bucket
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
resource "google_storage_bucket" "gcs_bucket" {
  name          = "${var.bucket}_${var.project}" # Concatenating DL bucket & Project name for unique naming
  location      = var.region

  # Optional, but recommended settings:
  storage_class = var.storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled     = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30  // days
    }
  }

  force_destroy = true
}

# Data Warehouse
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.bq_dataset
  project    = var.project
  location   = var.region
}