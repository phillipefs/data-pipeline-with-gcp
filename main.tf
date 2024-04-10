resource "google_storage_bucket" "my_bucket" {
  name          = "my-unique-bucket-name"
  location      = "US"
  force_destroy = true
}