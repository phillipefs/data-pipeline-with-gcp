resource "google_storage_bucket" "gcs_bucket" {
    name = "bucket-random-01893"
    location = var.region
}