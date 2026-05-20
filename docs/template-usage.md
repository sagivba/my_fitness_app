# Creating a new project from this template

This document explains how to create a new Python project from this template repository.

There are two separate phases:

1. Prepare this repository as a GitHub Template repository.
2. Create a new project repository from the template.

Do not confuse these steps.

Marking this repository as a template does not create a new project. Creating a new project happens only after using the `Use this template` button or the GitHub CLI equivalent.

## Phase 1: Prepare the template repository

This phase is done once for this repository.

### 1. Push the template repository to GitHub

If this repository is still local, initialize it and push it to GitHub:

```bash
git init
git add .
git commit -m "Initial Python AI-friendly template"
git branch -M main
gh repo create sagivba/python-ai-friendly-template --private --source=. --remote=origin --push
```

If the repository already exists on GitHub and the latest files are committed locally, push the changes:

```bash
git status
git add .
git commit -m "Update Python project template"
git push
```

### 2. Mark the repository as a template

In GitHub:

1. Open the template repository:

   ```text
   sagivba/python-ai-friendly-template
   ```

2. Go to:

   ```text
   Settings
   ```

3. In the `General` settings page, find:

   ```text
   Template repository
   ```

4. Enable the checkbox.

After this step, GitHub will show a button named:

```text
Use this template
```

This means the repository is now ready to be used as a source for new repositories.

## Phase 2: Create a new repository from the template

This phase is done every time you want to start a new project.

### Option A: Use the GitHub UI

1. Open the template repository:

   ```text
   sagivba/python-ai-friendly-template
   ```

2. Click:

   ```text
   Use this template
   ```

3. Choose:

   ```text
   Create a new repository
   ```

4. Enter the new repository name.

   The repository name should match the intended project name, for example:

   ```text
   chemistry-mock-site
   ```

5. Choose visibility:

   ```text
   Private
   ```

   or:

   ```text
   Public
   ```

6. Create the repository.

7. Clone the new repository locally:

   ```bash
   git clone git@github.com:sagivba/chemistry-mock-site.git
   cd chemistry-mock-site
   ```

8. Initialize the project from the template:

   ```bash
   scripts/init_from_template.sh chemistry-mock-site
   ```

   Or, if you want to explicitly control the Python package name:

   ```bash
   scripts/init_from_template.sh "Chemistry Mock Site" --package chemistry_web
   ```

### Option B: Use GitHub CLI

Run this from the parent folder where you keep your projects, not from inside another project.

```bash
cd ~/projects
gh repo create sagivba/chemistry-mock-site --template sagivba/python-ai-friendly-template --private --clone
cd chemistry-mock-site
scripts/init_from_template.sh chemistry-mock-site
```

With an explicit Python package name:

```bash
scripts/init_from_template.sh "Chemistry Mock Site" --package chemistry_web
```

## Important: directory behavior

When you use:

```bash
git clone git@github.com:sagivba/chemistry-mock-site.git
```

Git creates a new local directory:

```text
chemistry-mock-site/
```

So the normal workflow is:

```bash
cd ~/projects
git clone git@github.com:sagivba/chemistry-mock-site.git
cd chemistry-mock-site
```

Do not run the template initialization script from `src/`.

Run it from the project root:

```text
chemistry-mock-site/
├── AGENTS.md
├── README.md
├── scripts/
├── src/
└── tests/
```

Correct:

```bash
cd chemistry-mock-site
scripts/init_from_template.sh chemistry-mock-site
```

Incorrect:

```bash
cd chemistry-mock-site/src
../scripts/init_from_template.sh chemistry-mock-site
```

## Alternative: import the template into the current directory

Use this only when you already created a local directory with the intended project name.

The current directory should be the project root. It should not be `src/`.

Example:

```bash
mkdir chemistry-mock-site
cd chemistry-mock-site
```

Then import the template files:

```bash
git clone --depth 1 git@github.com:sagivba/python-ai-friendly-template.git .template-tmp
cp -a .template-tmp/. .
rm -rf .template-tmp
rm -rf .git
git init
```

Initialize the project:

```bash
scripts/init_from_template.sh chemistry-mock-site
```

Then continue with setup:

```bash
cp .env.example .env

python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

scripts/test.sh full local
scripts/lint.sh
```

Create and push the new GitHub repository:

```bash
git add .
git commit -m "Initialize project from template"
git branch -M main
gh repo create sagivba/chemistry-mock-site --private --source=. --remote=origin --push
```

## What `init_from_template.sh` does

The initialization script updates the generated project after it has been created from the template.

It updates:

- project name
- Python package directory under `src/`
- imports and package references
- `README.md`
- `pyproject.toml`
- `.env.example`
- Docker-related project naming references where possible

It also creates:

```text
.template-initialized
```

This marker prevents accidental repeated initialization.

A second run will fail unless you intentionally use:

```bash
scripts/init_from_template.sh chemistry-mock-site --force
```

Use `--force` only when you deliberately want to re-run initialization.

## Recommended first commit after initialization

After running the initialization script and validating the project, commit the initialized state:

```bash
git status
git add .
git commit -m "Initialize project from template"
```

If the repository was not pushed yet:

```bash
git branch -M main
gh repo create sagivba/chemistry-mock-site --private --source=. --remote=origin --push
```

## Validation checklist

Before starting real development, verify:

- [ ] The repository name matches the intended project name.
- [ ] The local directory name matches the intended project name.
- [ ] `scripts/init_from_template.sh` was run from the project root.
- [ ] `.template-initialized` exists.
- [ ] The Python package under `src/` has the expected name.
- [ ] `.env` was created from `.env.example`.
- [ ] Local tests pass.
- [ ] Lint passes.
- [ ] Docker tests pass if Docker will be used.

Commands:

```bash
cp .env.example .env

python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

scripts/test.sh full local
scripts/lint.sh
```

Optional Docker validation:

```bash
PROJECT_NAME=chemistry_mock_site scripts/test.sh full docker-dev
PROJECT_NAME=chemistry_mock_site scripts/test.sh full docker-qa
```
