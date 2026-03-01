# Put This Project on GitHub (First-Time Setup)

Your code is ready to push. Follow these steps to create a GitHub repository and upload the project.

---

## 1. Create a GitHub account (if you don’t have one)

- Go to **https://github.com**
- Click **Sign up** and create an account (email + password, or “Sign up with Google”).

---

## 2. Create a new repository on GitHub

1. Log in to GitHub.
2. Click the **+** at the top right → **New repository**.
3. Fill in:
   - **Repository name:** e.g. `checkfront-ota-sync` (or any name you like).
   - **Description (optional):** e.g. `Sync Viator cancellations and net pricing to Checkfront`.
   - **Public** (so you can use it without paying).
   - **Do not** check “Add a README”, “Add .gitignore”, or “Choose a license” (the project already has these).
4. Click **Create repository**.

---

## 3. Connect your project and push (in Terminal)

GitHub will show a page with “Quick setup” and some commands. You can ignore that and use these instead.

Open **Terminal**, then run (replace `YOUR_USERNAME` with your GitHub username and `checkfront-ota-sync` with the repo name if you chose something different):

```bash
cd ~/Desktop/checkfront-ota-sync
git remote add origin https://github.com/YOUR_USERNAME/checkfront-ota-sync.git
git branch -M main
git push -u origin main
```

Example: if your GitHub username is `frankchapman`, use:

```bash
git remote add origin https://github.com/frankchapman/checkfront-ota-sync.git
git branch -M main
git push -u origin main
```

- The first time you push, GitHub may ask you to log in (in the browser or in Terminal).
- If it asks for a **password**, use a **Personal Access Token**, not your GitHub password. To create one: GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token**. Give it a name, check **repo**, then generate and paste the token when prompted.

After `git push` finishes, refresh the repository page on GitHub; you should see all your files there.

---

## 4. Later: make changes and push again

When you change the code and want to update GitHub:

```bash
cd ~/Desktop/checkfront-ota-sync
git add -A
git status
git commit -m "Short description of what you changed"
git push
```

---

## Important

- **`.env` is not in the repo** (it’s in `.gitignore`) because it contains secrets. Never add it. On a new machine, copy `.env.example` to `.env` and fill in your keys.
- The **ngrok** binary is also ignored; download it again on another computer if needed (see README).
