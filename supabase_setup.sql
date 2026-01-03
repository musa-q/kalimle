-- Supabase Setup SQL for kalimle
-- Run this in your Supabase SQL Editor to create the necessary tables

-- Create the puzzles table
CREATE TABLE IF NOT EXISTS puzzles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sentence TEXT NOT NULL,
    target TEXT NOT NULL,
    pronunciation TEXT NOT NULL,
    meaning TEXT NOT NULL,
    example TEXT,
    active BOOLEAN DEFAULT true,
    scheduled_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_puzzles_active ON puzzles(active);
CREATE INDEX IF NOT EXISTS idx_puzzles_scheduled_date ON puzzles(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_puzzles_created_at ON puzzles(created_at);

-- Unique constraint to prevent multiple puzzles on the same date
CREATE UNIQUE INDEX IF NOT EXISTS idx_puzzles_unique_scheduled_date 
    ON puzzles(scheduled_date) 
    WHERE scheduled_date IS NOT NULL;

-- Enable Row Level Security (RLS)
ALTER TABLE puzzles ENABLE ROW LEVEL SECURITY;

-- Policy to allow anyone to read active puzzles (for the game)
CREATE POLICY "Allow public read access to active puzzles" ON puzzles
    FOR SELECT
    USING (active = true);

-- Policy to allow service role full access (for admin operations)
CREATE POLICY "Allow service role full access" ON puzzles
    FOR ALL
    USING (auth.role() = 'service_role');

-- If you want to use Supabase Auth for admin users, add this policy instead:
-- CREATE POLICY "Allow authenticated users to manage puzzles" ON puzzles
--     FOR ALL
--     USING (auth.role() = 'authenticated');

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at
CREATE TRIGGER update_puzzles_updated_at
    BEFORE UPDATE ON puzzles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Optional: Insert some default puzzles
-- Uncomment if you want to pre-populate the database
/*
INSERT INTO puzzles (sentence, target, pronunciation, meaning, example) VALUES
('I am reading a ___.', 'كتاب', 'kitāb', 'book', 'أقرأ كتاباً ممتعاً'),
('The ___ is shining brightly today.', 'شمس', 'shams', 'sun', 'الشمس مشرقة اليوم'),
('I drink ___ every morning.', 'قهوة', 'qahwa', 'coffee', 'أشرب القهوة كل صباح'),
('The ___ is very blue today.', 'سماء', 'samāʾ', 'sky', 'السماء زرقاء جميلة'),
('I love to eat ___.', 'تفاح', 'tuffāḥ', 'apple', 'أحب أكل التفاح');
*/

-- View to see all puzzles with their scheduling status
CREATE OR REPLACE VIEW puzzles_overview AS
SELECT 
    id,
    sentence,
    target,
    meaning,
    active,
    scheduled_date,
    CASE 
        WHEN scheduled_date = CURRENT_DATE THEN 'Today'
        WHEN scheduled_date > CURRENT_DATE THEN 'Upcoming'
        WHEN scheduled_date < CURRENT_DATE THEN 'Past'
        ELSE 'Auto'
    END as schedule_status,
    created_at
FROM puzzles
ORDER BY 
    CASE WHEN scheduled_date IS NULL THEN 1 ELSE 0 END,
    scheduled_date DESC NULLS LAST,
    created_at DESC;
