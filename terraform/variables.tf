locals {
  data_lake_bucket = "twitter_2"
}

variable bucket_names {
  description = "list of buckets"
  type  = list(string)
  default = [
    "twitter_data_twitter-project-381411" 
  ]
}

variable "project" {
  description = "Your GCP Project ID"
  default = "twitter-project-381411"
}

# variable "credentials" {
#   description = "Your GCP Project ID"
#   default = "/home/david/tweeter_project/twitter_proc.json"
#   type = string
# }

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default = "europe-west6"
  type = string
}

variable "storage_class" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default = "STANDARD"
}

variable "BQ_DATASET" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type = string
  default = "twitter_data"
}