# Thanks

## Migrations

```sql
USE thanks
ALTER TABLE points MODIFY COLUMN `points` INT;
ALTER TABLE points MODIFY COLUMN `num_of_thanks` INT;
ALTER TABLE points ADD COLUMN `last_points_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE points ADD COLUMN `current_day_points` TINYINT DEFAULT 0;
```