variable "project" {
  description = "Your GCP Project ID"
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  type = string
}

variable "zone" {
  description = "Zone for GCP resources. Choose as per your location: https://cloud.google.com/compute/docs/regions-zones"
  type = string
}

variable "storage_class" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default = "STANDARD"
}

variable "bucket"{
  description = "Your GCS bucket name"
  default = "de-project-bucket"
}

variable "bq_dataset" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type = string
  default = "MYH0036"
}

variable "user" {
    type = string
}

variable "email" {
    type = string
}
variable "privatekeypath" {
    type = string
    default = "~/.ssh/ssh-key"
}
variable "publickeypath" {
    type = string
    default = "~/.ssh/ssh-key.pub"
}
