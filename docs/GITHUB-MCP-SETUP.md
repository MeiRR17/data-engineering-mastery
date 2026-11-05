# GitHub, ChatGPT and VS Code — safe setup

There are several **distinct authorization surfaces**. A GitHub connector in ChatGPT, a GitHub MCP server in an IDE and a local Git CLI do not automatically have the same permissions. Always inspect the tools and account grants currently available.

## 1. Make a personal learner repository

- Sign in to GitHub and enable two-factor authentication.
- Use **Use this template** on the original learning repository, or fork it if you need a shared contribution history.
- Start with a private personal repository if you prefer. Do not commit learners' private notes to the public source repository.
- Clone the repo into VS Code and create a `learn/XX-topic` branch for each stage.
- Prefer OAuth or the GitHub CLI credential manager. **Never paste PATs, passwords or service-role keys into README files, PRs or a chat.**

## 2. Connect GitHub to ChatGPT when useful

Open ChatGPT Settings → Plugins or the available GitHub connection interface and authorize the appropriate account/repositories. Check the actions actually offered by the connected integration: some support search/read only; others may provide authorized write workflows. Do **not** assume the connection can push code.

For a mentor, use [the English agent guide](../prompts/MASTER-AGENT.en.md) and identify your repository and stage. Verify the mentor can cite and read a specific file before relying on its answer. If a repository is missing, check account/org permissions; indexing can be delayed.

## 3. GitHub MCP in VS Code (optional)

If your VS Code/IDE supports GitHub MCP, consult GitHub's [official MCP setup guidance](https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp-in-your-ide/set-up-the-github-mcp-server) and the [GitHub MCP Server repository](https://github.com/github/github-mcp-server).

1. Install only the official integration from its documented publisher.
2. Open the Command Palette and inspect configured MCP servers.
3. Use the authorized OAuth login flow; do not paste tokens into agent instructions.
4. Begin with a read-only issue/file lookup.
5. Grant repository write permissions only when needed, then try a harmless branch or draft PR.
6. Review every proposed command and diff before merging.

MCP support, names and permissions vary by IDE and account configuration; follow the current in-product documentation.

## 4. Visual editing is separate from GitHub permissions

For rendered `.md` lessons, interactive `.ipynb` notebooks and the four recommended extensions, see [Visual Studio Code learning setup](VS-CODE-LEARNING-SETUP.md). Installing Markdown and Jupyter extensions **does not grant repository write access**.

## 5. Cloud deployment and costs

Supabase is an additional, separate authorization context. Use only an owner-approved sandbox with explicit cost bounds. Confirm CLI syntax and project selection before any remote command; never treat a successful local PR check as permission to deploy. CI for untrusted pull requests must not receive deployment secrets.

If GitHub does not appear in a connected tool, verify the signed-in account, repository installation permissions and organization approval. Do not share credentials as a troubleshooting step.
