-- Migration: Add language column to support multiple languages in one Supabase
-- Run this in your Kalimle Supabase SQL Editor

-- Step 1: Add the language column
ALTER TABLE puzzles 
ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'arabic';

-- Step 2: Set all existing puzzles to 'arabic' (since they're from Kalimle)
UPDATE puzzles SET language = 'arabic' WHERE language IS NULL;

-- Step 3: Create index for language queries
CREATE INDEX IF NOT EXISTS idx_puzzles_language ON puzzles(language);

-- Step 4: Drop the old unique constraint on scheduled_date (if exists)
DROP INDEX IF EXISTS idx_puzzles_unique_scheduled_date;

-- Step 5: Create new unique constraint per language
-- (allows same date to have different puzzles for different languages)
CREATE UNIQUE INDEX IF NOT EXISTS idx_puzzles_unique_scheduled_date_language 
    ON puzzles(scheduled_date, language) 
    WHERE scheduled_date IS NOT NULL;

-- Step 6: Update the view to include language
CREATE OR REPLACE VIEW puzzles_overview AS
SELECT 
    id,
    sentence,
    target,
    meaning,
    active,
    scheduled_date,
    language,
    CASE 
        WHEN scheduled_date = CURRENT_DATE THEN 'Today'
        WHEN scheduled_date > CURRENT_DATE THEN 'Upcoming'
        WHEN scheduled_date < CURRENT_DATE THEN 'Past'
        ELSE 'Auto'
    END as schedule_status,
    created_at
FROM puzzles
ORDER BY 
    language,
    CASE WHEN scheduled_date IS NULL THEN 1 ELSE 0 END,
    scheduled_date DESC NULLS LAST,
    created_at DESC;

-- Verify the changes
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'puzzles' AND column_name = 'language';
