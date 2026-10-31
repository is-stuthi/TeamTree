# SQL conventions (TeamTREE)

- **Errors:** `SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'UPPER_SNAKE_CODE';`. Add every new code to `api/app/errors.py` (the code → HTTP status map) in the same change.
- **Procedures** that write more than one row:
  ```sql
  DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
  START TRANSACTION; ... COMMIT;
  ```
  Lock the parent row (`SELECT … FOR UPDATE` on `Project`) before any capacity or count check.
- **Triggers** validate only. They never insert or update other tables (design doc §17.2). Share logic between INSERT and UPDATE triggers via a `validate_*` procedure.
- **"One active row" rules** use a generated flag (`IF(cond,1,NULL)`) inside a UNIQUE index. Don't use a plain UNIQUE on (a,b) where history must be kept.
- **No CASCADE** from `Users` or `Project` (they are soft-deleted). CASCADE is fine for pure child data (`Domain`, `Requires`, `user_has_skill`).
- **Derived values** (age, overdue, reviewer, counts) come from views, never from stored columns.
- **Proficiency comparison:** `level + 0` gives the ENUM ordinal (Beginner = 1 … Expert = 4).
- MySQL CHECKs cannot call `CURDATE()`. Put date-vs-today rules in triggers or procedures.
- Keep each file idempotent: `DROP … IF EXISTS` / `CREATE OR REPLACE VIEW`.
