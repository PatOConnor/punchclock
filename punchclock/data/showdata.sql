-- Get All Data; used for quick testing
-- SELECT * FROM shifts;

-- SELECT shift_length FROM shifts WHERE date = (SELECT date FROM shifts WHERE id = (SELECT MAX(id) from shifts))

-- get daily hours
-- SELECT daily_hours FROM shifts WHERE id = (SELECT MAX(id) FROM shifts)

-- delete most recent entry
-- DELETE FROM shifts WHERE id = (SELECT MAX(id) FROM shifts)