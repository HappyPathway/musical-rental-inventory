# Infrastructure Validation with Terratest

This directory contains automated tests for validating your existing Terraform infrastructure using Terratest.

## Prerequisites

- Go 1.20 or later
- GCP credentials configured
- Terraform installed
- Existing infrastructure deployed via Terraform

## Running the Tests

To run all tests:

```bash
cd infra/test
go test -v
```

To run a specific test:

```bash
cd infra/test
go test -v -run TestCloudSqlConfiguration
```

## Test Descriptions

- `TestCloudSqlConfiguration`: Validates that the Cloud SQL instance is properly configured.
- `TestCloudRunConfiguration`: Ensures the Cloud Run service is correctly deployed and accessible.
- `TestStorageBucketConfiguration`: Verifies the GCS bucket configuration.

## Notes

- These tests validate your existing infrastructure without modifying it
- The tests read from Terraform outputs of your existing deployment
- No resources will be created or destroyed when running these tests