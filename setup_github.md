# Setting Up GitHub Repository

## 🚀 Steps to Create GitHub Repo

### 1. Create New Repository on GitHub
1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Fill in the repository details:
   - **Repository name**: `run-pool` (or your preferred name)
   - **Description**: "Baseball Pool Management Application - Flask-based web app for managing baseball run pools"
   - **Visibility**: Choose Public or Private
   - **Initialize with**: Don't check any boxes (we already have files)
5. Click **"Create repository"**

### 2. Connect Local Repo to GitHub
After creating the repo, GitHub will show you commands. Use these:

```bash
# Add the remote origin (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Set the main branch (GitHub now uses 'main' by default)
git branch -M main

# Push your code to GitHub
git push -u origin main
```

### 3. Verify Setup
```bash
# Check remote configuration
git remote -v

# Check branch status
git branch -a
```

## 🔄 Daily Workflow

### Making Changes
```bash
# Make your code changes
# Then stage and commit:
git add .
git commit -m "Description of your changes"

# Push to GitHub
git push origin main
```

### Getting Updates (if working on multiple machines)
```bash
git pull origin main
```

## 📁 What's Now Tracked in Git

✅ **Core Application Files**:
- `app_2025_latest.py` - Main Flask application
- `templates/` - All HTML templates
- `static/styles.css` - Custom styling
- `requirements.txt` - Python dependencies
- `alembic/` - Database migration files

✅ **Documentation**:
- `README.md` - Comprehensive project documentation
- `.gitignore` - Git ignore rules

❌ **Excluded from Git**:
- `*.db` - Database files
- `venv/` - Virtual environment
- `app_*.py` - Old app versions (except app_2025_latest.py)
- `test*.py` - Test files
- `.env` - Environment variables
- `__pycache__/` - Python cache files

## 🎯 Next Steps

1. **Create the GitHub repository** using the steps above
2. **Push your code** to GitHub
3. **Set up environment variables** on your deployment platform
4. **Consider adding**:
   - Issue templates
   - Pull request templates
   - GitHub Actions for CI/CD
   - Code quality checks

## 🔧 Useful Git Commands

```bash
# View commit history
git log --oneline

# View file changes
git diff

# View status
git status

# Create and switch to new branch
git checkout -b feature-name

# Switch between branches
git checkout main
git checkout feature-name

# Merge feature branch
git checkout main
git merge feature-name
```

## 🚨 Important Notes

- **Never commit** `.env` files or database files
- **Always pull** before making changes if working on multiple machines
- **Use meaningful commit messages** that describe what changed
- **Create feature branches** for major changes
- **Test locally** before pushing to GitHub

---

Your Run Pool application is now ready for version control! 🎉
