module "bigquery-dataset-gasolina" {
  source  = "./modules/bigquery"
  dataset_id                  = "gasolina_brasil"
  dataset_name                = "gasolina_brasil"
  description                 = "Dataset a respeito do histórico de preços da Gasolina no Brasil a partir de 2004"
  project_id                  = var.project_id
  location                    = var.region
  delete_contents_on_destroy  = true
  deletion_protection = false
  access = [
    {
      role = "OWNER"
      special_group = "projectOwners"
    },
    {
      role = "READER"
      special_group = "projectReaders"
    },
    {
      role = "WRITER"
      special_group = "projectWriters"
    }
  ]
  tables=[
    {
        table_id           = "tb_historico_combustivel_brasil",
        description        = "Tabela com as informacoes de preço do combustível ao longo dos anos"
        time_partitioning  = {
          type                     = "DAY",
          field                    = "data",
          require_partition_filter = false,
          expiration_ms            = null
        },
        range_partitioning = null,
        expiration_time = null,
        clustering      = ["produto","regiao_sigla", "estado_sigla"],
        labels          = {
          name    = "stack_data_pipeline"
          project  = "gasolina"
        },
        deletion_protection = true
        schema = file("./bigquery/schema/gasolina_brasil/tb_historico_combustivel_brasil.json")
    }
  ]
}

module "bucket-raw" {
  source  = "./modules/gcs"

  name       = "data-pipelines-combustiveis-br-raw"
  project_id = var.project_id
  location   = var.region
}

module "bucket-curated" {
  source  = "./modules/gcs"

  name       = "data-pipelines-combustiveis-br-curated"
  project_id = var.project_id
  location   = var.region
}

module "bucket-pyspark-tmp" {
  source  = "./modules/gcs"

  name       = "data-pipeline-combustiveis-br-pyspark-tmp"
  project_id = var.project_id
  location   = var.region
}

module "bucket-pyspark-code" {
  source  = "./modules/gcs"

  name       = "data-pipeline-combustiveis-br-pyspark-code"
  project_id = var.project_id
  location   = var.region
}

resource "google_dataproc_cluster" "sample_cluster" {
  name    = "dataproc_cluster"
  region  = var.region
  project = var.project_id

  cluster_config {
    master_config {
      num_instances = 1
      machine_type  = "n1-standard-2"
    }

    worker_config {
      num_instances = 2
      machine_type  = "n1-standard-2"
    }

    software_config {
      # You can specify a list of optional components to be installed on the cluster.
      optional_components   = ["JUPYTER"]
      override_properties = {
          "spark:spark.executor.memory" = "2688m"
          "spark:spark.executor.cores" = "1"
          "spark:spark.logConf" = "true"
      }
    }
  }
}