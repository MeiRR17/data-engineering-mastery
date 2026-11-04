// Vercel serverless endpoint exposing *only* public Supabase connection settings.
// Never expose SUPABASE_SECRET_KEY through this endpoint.
export default function handler(req, res) {
  const url = process.env.SUPABASE_URL;
  const publishableKey = process.env.SUPABASE_PUBLISHABLE_KEY;
  if (!url || !publishableKey || !url.startsWith("https://")) {
    res.setHeader("Cache-Control", "no-store");
    return res.status(503).json({ error: "Public Supabase configuration is missing." });
  }
  res.setHeader("Cache-Control", "public, max-age=300");
  return res.status(200).json({ url, publishableKey });
}
