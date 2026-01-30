-- One-time migration: Deactivate existing past scheduled puzzles
-- Run this in your Kalimle Supabase SQL Editor

-- Deactivate past scheduled puzzles (Arabic)
UPDATE puzzles 
SET active = false 
WHERE language = 'arabic' 
  AND scheduled_date IS NOT NULL 
  AND scheduled_date < CURRENT_DATE 
  AND active = true;

-- Deactivate past scheduled puzzles (Turkish)
UPDATE puzzles 
SET active = false 
WHERE language = 'turkish' 
  AND scheduled_date IS NOT NULL 
  AND scheduled_date < CURRENT_DATE 
  AND active = true;

-- Show results
SELECT 
    language,
    COUNT(*) as deactivated_count
FROM puzzles 
WHERE scheduled_date < CURRENT_DATE 
  AND active = false
GROUP BY language;
