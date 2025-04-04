package test

import (
	"testing"

	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
)

func TestCloudSqlConfiguration(t *testing.T) {
	t.Parallel()

	// Configure Terratest to only read the outputs without applying or destroying
	terraformOptions := &terraform.Options{
		TerraformDir: "../",
		// Skip all terraform actions except output
		NoColor: true,
	}

	// Get the DB instance resource from existing infrastructure
	dbInstanceName := terraform.OutputRequired(t, terraformOptions, "db_instance_name")
	projectID := terraform.OutputRequired(t, terraformOptions, "project_id")
	region := terraform.OutputRequired(t, terraformOptions, "region")

	// Verify outputs exist for the already deployed infrastructure
	assert.NotEmpty(t, dbInstanceName, "DB instance name should not be empty")
	assert.NotEmpty(t, projectID, "Project ID should not be empty")
	assert.NotEmpty(t, region, "Region should not be empty")
}
