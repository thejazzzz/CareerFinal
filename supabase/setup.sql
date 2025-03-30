-- Users table (for storing user data)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    user_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Learning paths table (for storing learning paths)
CREATE TABLE IF NOT EXISTS public.learning_paths (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    path_data JSONB DEFAULT '{}'::jsonb,
    progress JSONB DEFAULT '{}'::jsonb,
    is_complete BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Skills analysis table (for storing skills analysis)
CREATE TABLE IF NOT EXISTS public.skill_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    analysis_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Career paths table (for storing career paths)
CREATE TABLE IF NOT EXISTS public.career_paths (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    path_data JSONB DEFAULT '{}'::jsonb,
    progress JSONB DEFAULT '{}'::jsonb,
    current_step INTEGER DEFAULT 0,
    is_complete BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User skills table (to track individual skills and their progress)
CREATE TABLE IF NOT EXISTS public.user_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    skill_name TEXT NOT NULL,
    skill_category TEXT,
    proficiency INTEGER DEFAULT 0,
    in_progress BOOLEAN DEFAULT false,
    learning_resources JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, skill_name)
);

-- Create RLS policies for authentication
-- Users table policies
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Drop existing policies before creating them
DROP POLICY IF EXISTS "Users can view their own data" ON public.users;
DROP POLICY IF EXISTS "Users can insert their own data" ON public.users;
DROP POLICY IF EXISTS "Users can update their own data" ON public.users;

CREATE POLICY "Users can view their own data" 
    ON public.users FOR SELECT 
    USING (auth.uid() = id);

CREATE POLICY "Users can insert their own data" 
    ON public.users FOR INSERT 
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update their own data" 
    ON public.users FOR UPDATE 
    USING (auth.uid() = id);

-- Learning paths table policies
ALTER TABLE public.learning_paths ENABLE ROW LEVEL SECURITY;

-- Drop existing policies before creating them
DROP POLICY IF EXISTS "Users can view their own learning paths" ON public.learning_paths;
DROP POLICY IF EXISTS "Users can insert their own learning paths" ON public.learning_paths;
DROP POLICY IF EXISTS "Users can update their own learning paths" ON public.learning_paths;
DROP POLICY IF EXISTS "Users can delete their own learning paths" ON public.learning_paths;

CREATE POLICY "Users can view their own learning paths" 
    ON public.learning_paths FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own learning paths" 
    ON public.learning_paths FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own learning paths" 
    ON public.learning_paths FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own learning paths" 
    ON public.learning_paths FOR DELETE 
    USING (auth.uid() = user_id);

-- Skills analysis table policies
ALTER TABLE public.skill_analyses ENABLE ROW LEVEL SECURITY;

-- Drop existing policies before creating them
DROP POLICY IF EXISTS "Users can view their own skill analyses" ON public.skill_analyses;
DROP POLICY IF EXISTS "Users can insert their own skill analyses" ON public.skill_analyses;
DROP POLICY IF EXISTS "Users can update their own skill analyses" ON public.skill_analyses;
DROP POLICY IF EXISTS "Users can delete their own skill analyses" ON public.skill_analyses;

CREATE POLICY "Users can view their own skill analyses" 
    ON public.skill_analyses FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own skill analyses" 
    ON public.skill_analyses FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own skill analyses" 
    ON public.skill_analyses FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own skill analyses" 
    ON public.skill_analyses FOR DELETE 
    USING (auth.uid() = user_id);

-- Career paths table policies
ALTER TABLE public.career_paths ENABLE ROW LEVEL SECURITY;

-- Drop existing policies before creating them
DROP POLICY IF EXISTS "Users can view their own career paths" ON public.career_paths;
DROP POLICY IF EXISTS "Users can insert their own career paths" ON public.career_paths;
DROP POLICY IF EXISTS "Users can update their own career paths" ON public.career_paths;
DROP POLICY IF EXISTS "Users can delete their own career paths" ON public.career_paths;

CREATE POLICY "Users can view their own career paths" 
    ON public.career_paths FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own career paths" 
    ON public.career_paths FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own career paths" 
    ON public.career_paths FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own career paths" 
    ON public.career_paths FOR DELETE 
    USING (auth.uid() = user_id);

-- User skills table policies
ALTER TABLE public.user_skills ENABLE ROW LEVEL SECURITY;

-- Drop existing policies before creating them
DROP POLICY IF EXISTS "Users can view their own skills" ON public.user_skills;
DROP POLICY IF EXISTS "Users can insert their own skills" ON public.user_skills;
DROP POLICY IF EXISTS "Users can update their own skills" ON public.user_skills;
DROP POLICY IF EXISTS "Users can delete their own skills" ON public.user_skills;

CREATE POLICY "Users can view their own skills" 
    ON public.user_skills FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own skills" 
    ON public.user_skills FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own skills" 
    ON public.user_skills FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own skills" 
    ON public.user_skills FOR DELETE 
    USING (auth.uid() = user_id);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS users_id_idx ON public.users(id);
CREATE INDEX IF NOT EXISTS learning_paths_user_id_idx ON public.learning_paths(user_id);
CREATE INDEX IF NOT EXISTS skill_analyses_user_id_idx ON public.skill_analyses(user_id);
CREATE INDEX IF NOT EXISTS career_paths_user_id_idx ON public.career_paths(user_id);
CREATE INDEX IF NOT EXISTS user_skills_user_id_idx ON public.user_skills(user_id);
CREATE INDEX IF NOT EXISTS user_skills_name_idx ON public.user_skills(skill_name);

-- Update function for updated_at timestamp
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS set_users_updated_at ON public.users;
CREATE TRIGGER set_users_updated_at
BEFORE UPDATE ON public.users
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS set_learning_paths_updated_at ON public.learning_paths;
CREATE TRIGGER set_learning_paths_updated_at
BEFORE UPDATE ON public.learning_paths
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS set_skill_analyses_updated_at ON public.skill_analyses;
CREATE TRIGGER set_skill_analyses_updated_at
BEFORE UPDATE ON public.skill_analyses
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS set_career_paths_updated_at ON public.career_paths;
CREATE TRIGGER set_career_paths_updated_at
BEFORE UPDATE ON public.career_paths
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS set_user_skills_updated_at ON public.user_skills;
CREATE TRIGGER set_user_skills_updated_at
BEFORE UPDATE ON public.user_skills
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at(); 