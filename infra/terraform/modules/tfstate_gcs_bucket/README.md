# tfstate_gcs_bucket

Terraform の state 管理用 GCS バケットを作成するモジュールです。  
`google_storage_bucket` を作成し、バージョニング・ライフサイクル・Autoclass を設定します。

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | ~>1.14.4 |
| <a name="requirement_google"></a> [google](#requirement\_google) | ~>7.18.0 |
| <a name="requirement_google-beta"></a> [google-beta](#requirement\_google-beta) | ~>7.18.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_google"></a> [google](#provider\_google) | ~>7.18.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [google_storage_bucket.tfstate_bucket](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_bucket_location"></a> [bucket\_location](#input\_bucket\_location) | The location of the GCS bucket for tfstate. | `string` | `"US"` | no |
| <a name="input_gcp_project_id"></a> [gcp\_project\_id](#input\_gcp\_project\_id) | The ID for your GCP project | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_tfstate_gcs_bucket_id"></a> [tfstate\_gcs\_bucket\_id](#output\_tfstate\_gcs\_bucket\_id) | The ID of the bucket used to store terraform state |
<!-- END_TF_DOCS -->

## Notes

- Storage API（`storage.googleapis.com`）を有効化してからバケットを作成します。
- バケット名は `${gcp_project_id}-tfstate` です。
- バージョニングを有効化し、古いバージョンは一定数を超えると削除します。
