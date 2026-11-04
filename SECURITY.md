# Security policy

- This repository is public. Never commit secrets, PATs, database connection passwords, service-role/secret keys, private credentials, or real personal data.
- Use dedicated development Supabase projects and least-privilege access. Do not automate changes to unrelated repos.
- Enable RLS on every exposed table, verify both GRANT and RLS, and test unauthorized access.
- Never run untrusted PR code with production secrets. The included CI workflow has read-only permissions and no deployment secrets.
- Do not paste tokens into ChatGPT or PR comments. Authenticate via OAuth/app UI or local secure environment configuration.
- To report a vulnerability, use GitHub private vulnerability reporting (when enabled), or contact maintainers privately. Do not open a public issue containing an exploit or credential.
- Data from public APIs must still follow their terms, license, rate limits and attribution.
