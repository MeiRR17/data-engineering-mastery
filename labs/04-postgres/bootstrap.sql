-- Disposable Docker lab only. NEVER apply this file to a real Supabase project.
create role anon nologin;
create role authenticated nologin;
create role service_role nologin bypassrls; -- matches the privileged Supabase service role; never expose its key
