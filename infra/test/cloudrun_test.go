package test

import (
	"testing"

	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
)

func TestCloudRunConfiguration(t *testing.T) {
	t.Parallel()

	// Configure Terratest to only read the outputs without applying or destroying
	terraformOptions := &terraform.Options{
		TerraformDir: "../",
		// Skip all terraform actions except output
		NoColor: true,
	}

	// Get outputs from existing Terraform state
	serviceUrl := terraform.OutputRequired(t, terraformOptions, "cloud_run_url")
	serviceRegion := terraform.OutputRequired(t, terraformOptions, "region")

	// Verify basic outputs exist
	assert.NotEmpty(t, serviceUrl, "Cloud Run service URL should not be empty")
	assert.NotEmpty(t, serviceRegion, "Region should not be empty")
}
