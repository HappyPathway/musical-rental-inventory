-- Manual SQL migration to add fields to the Equipment model
ALTER TABLE inventory_equipment ADD COLUMN manual_file varchar(100) NULL;
ALTER TABLE inventory_equipment ADD COLUMN manual_title varchar(255) NULL;
ALTER TABLE inventory_equipment ADD COLUMN manual_last_checked datetime NULL;