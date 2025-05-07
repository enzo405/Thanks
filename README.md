# Thanks

## Migrations 06/05/2025

```sql
USE thanks
ALTER TABLE points MODIFY COLUMN `points` INT;
ALTER TABLE points MODIFY COLUMN `num_of_thanks` INT;
ALTER TABLE points ADD COLUMN `last_points_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE points ADD COLUMN `current_day_points` TINYINT DEFAULT 0;
```

## Migrations 07/05/2025

```sql
ALTER TABLE points CHANGE COLUMN `last_points_date` `last_received_points_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE points CHANGE COLUMN `current_day_points` `current_day_received_points` TINYINT DEFAULT 0;
```