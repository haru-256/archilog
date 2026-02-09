# google_project_services

GCP のプロジェクトで必要な API を有効化するための Terraform モジュールです。  
`google_project_service` をまとめて有効化し、必要に応じて API 有効化後の待機時間も入れます。

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_google"></a> [google](#requirement\_google) | ~>7.18.0 |
| <a name="requirement_google-beta"></a> [google-beta](#requirement\_google-beta) | ~>7.18.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_google"></a> [google](#provider\_google) | ~>7.18.0 |
| <a name="provider_time"></a> [time](#provider\_time) | n/a |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [google_project_service.api_services](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_service) | resource |
| [time_sleep.wait_for_api_propagation](https://registry.terraform.io/providers/hashicorp/time/latest/docs/resources/sleep) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | The ID for your GCP project | `string` | n/a | yes |
| <a name="input_required_services"></a> [required\_services](#input\_required\_services) | The service names enabled | `list(string)` | n/a | yes |
| <a name="input_wait_seconds"></a> [wait\_seconds](#input\_wait\_seconds) | seconds to wait | `number` | n/a | yes |

## Outputs

No outputs.
<!-- END_TF_DOCS -->

## Notes

- `disable_on_destroy = false` のため、`terraform destroy` 時に API を無効化しません。
- `wait_seconds` は API 有効化直後の依存関係エラーを避けるための待機に使います。
