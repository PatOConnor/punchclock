-- Get All Data; used for quick testing
SELECT * FROM shifts;

-- SELECT shift_length FROM shifts WHERE date = (SELECT date FROM shifts WHERE id = (SELECT MAX(id) from shifts))
