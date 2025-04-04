package test

import (
	"testing"

	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
)

func TestStorageBucketConfiguration(t *testing.T) {
	t.Parallel()

	// Configure Terratest to only read the outputs without applying or destroying
	terraformOptions := &terraform.Options{
		TerraformDir: "../",
		// Skip all terraform actions except output
		NoColor: true,
	}

	// Get outputs from existing Terraform state
	bucketName := terraform.OutputRequired(t, terraformOptions, "media_bucket_name")
	projectID := terraform.OutputRequired(t, terraformOptions, "project_id")

	// Verify outputs exist
	assert.NotEmpty(t, bucketName, "Bucket name should not be empty")
	assert.NotEmpty(t, projectID, "Project ID should not be empty")
}
