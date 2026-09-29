# pkg-rpm-template

Template repository for creating RPM package repositories for Qualcomm® Linux.

Clone this template to create a `pkg-rpm-<component>` repo for **one** RPM
package. Your spec file and a small `sources` pointer go on a per-stream branch
(`c10s`); the shipped GitHub Actions workflows build the RPM on every PR and
publish it to Artifactory on demand. All build/release logic lives in the shared
[`qualcomm-linux/qcom-rpm-utils`](https://github.com/qualcomm-linux/qcom-rpm-utils)
repo — the workflows here are thin callers.

> [!IMPORTANT]
> **Get all the branches — the packaging files are not on `main`.**
>
> This repo uses one branch per distro stream: `main` holds the docs, and
> **`c10s`** holds the spec file and `sources` you actually edit.
>
> - **Creating from the template:** tick **"Include all branches"** in the *Use
>   this template* dialog. **It is off by default**, and with it off your new repo
>   gets only `main` — no `c10s`, and nothing to build.
> - **Cloning an existing repo:** a plain `git clone` fetches every branch, but
>   leaves you on the default one. Run `git checkout c10s` to reach the packaging
>   files.
>
> Already created a repo without the checkbox? Recover `c10s` with the snippet in
> [step 1](#1-create-your-repo-from-this-template).

---

## What you get

| Workflow | Trigger | Purpose |
|---|---|---|
| [`build-on-pr.yml`](.github/workflows/build-on-pr.yml) | Pull request | Build the RPM(s) so reviewers confirm the package still builds. Read-only — never publishes. |
| [`pkg-release.yml`](.github/workflows/pkg-release.yml) | Manual (`workflow_dispatch`) | Build **and** publish the RPM(s) to Artifactory, behind an approval gate. |

Both delegate to reusable workflows in `qcom-rpm-utils`, which run `rpmbuild`
inside the prebuilt `rpm-builder` container image for the runner's host
architecture.

---

## Branch model

This template follows the Fedora/CentOS **dist-git** convention: **one branch per
distro stream**, with the packaging files at that branch's root.

| Branch | Role | Contents |
|---|---|---|
| `main` | Template + docs home. **Nothing is built here.** | This README, [docs/](docs/), community files, workflows. |
| `c10s` | **CentOS 10 Stream package branch — where you work.** | Your `<component>.spec` + `sources` at the root, plus the workflows. |

Future streams get their own branch (`c11s`, …) off the same model, so one repo
can carry a package for several distro versions without branching history.

---

## Onboarding: step by step

### 1. Create your repo from this template
Use **"Use this template" → Create a new repository**, naming it
`pkg-rpm-<component>` (e.g. `pkg-rpm-audio`).

> **Tick "Include all branches"** (see the note at the top — it is off by
> default). If you already created the repo without it, recover `c10s` from the
> template:
> ```bash
> git remote add template https://github.com/qualcomm-linux/pkg-rpm-template.git
> git fetch template c10s
> git push -u origin refs/remotes/template/c10s:refs/heads/c10s
> git remote remove template
> ```

Clone it and switch to the package branch:

```bash
git clone https://github.com/qualcomm-linux/pkg-rpm-<component>.git
cd pkg-rpm-<component>
git checkout c10s
```

### 2. Configure the repository (one-time)

Set these up once, after creating the repo. Anything requiring org-level
permissions (runner-pool and GHCR access) must be requested from your
organization admin — a repo owner cannot grant them alone.

**Runners.** The build and publish jobs run on the shared AWS ephemeral ARM64
runner pool (`runs-on: [self-hosted, platform-prd-u2404-arm64-large-od-ephem]`),
which has Docker available. That label is set inside the reusable workflows, so
your repo must be granted access to that pool — **ask Jagannadha Pinnamaraju or Sannepalli Dimpu Sree Maheswari to enable
the repo for the AWS runner pool** — or the jobs will queue forever waiting for a
runner.

**GHCR registry access.** The build pulls the prebuilt `rpm-builder` image from
GHCR (`ghcr.io/qualcomm-linux/rpm-builder:centos10`). Both caller workflows
already grant `packages: read` (keep it if you edit them), but the repo must
also be **authorized on the `rpm-builder` package itself** — This should be added by default. If not, ask your org admin
to add the repo to that package's access list.


**Environment.**

| Name | Kind | Purpose |
|---|---|---|
| `pkg-release-approval` | **Environment** | Approval gate for publishing — add required reviewers. |

**Branch protection.** Protect the package branch `c10s` (and any future stream
branch): require pull requests before merging, require the build status check to
pass, and block force-pushes and deletions.

**Additional settings.** Enable **"Automatically delete head branches"** so
merged PR branches are cleaned up.

**Customize this README and the docs for your package.** This README ships with
template placeholders. After creating your repo, replace `pkg-rpm-<component>`,
`<component>.spec`, and the onboarding examples with your package's real names,
and trim anything that doesn't apply so the README describes *your* package
rather than the template.

### 3. Add your package files on the `c10s` branch

The starter files are already at the root of `c10s`, carrying a `.example`
suffix. Rename them:

```bash
git checkout c10s
git mv mypackage.spec.example <component>.spec
git mv sources.example sources
```

The suffix exists so the build's single-`*.spec` glob ignores the skeleton until
you rename it — otherwise your first PR would fail with `Multiple spec files`.
After the rename the branch root holds:

```
<component>.spec     # exactly one RPM spec file
sources              # checksum + filename of each source tarball
```

- **`<component>.spec`** — your RPM spec. Its `Source0:`/`SourceN:` must be a
  real, fetchable URL whose **filename matches the `sources` entry** (use
  `%{name}`/`%{version}` macros, and the `#/` rename trick when the URL basename
  differs). Example:
  ```
  Source0: https://github.com/<org>/<proj>/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
  ```
- **`sources`** — one line per tarball, in `sha512sum --tag` (dist-git) format.
  **The tarball is never committed to git.** Generate the line with:
  ```bash
  sha512sum --tag <component>-1.0.tar.gz > sources
  ```
  which yields:
  ```
  SHA512 (mycomponent-1.0.tar.gz) = 3a7bd3e2360a3d29eea436fcfb7e44c735d117c...
  ```

### 4. Open a PR
Commit the spec + `sources` and open a PR **against `c10s`**. `build-on-pr`
fetches the tarball (from the cache, or from the spec's `Source` URL on a cache
miss), verifies its checksum, and builds the RPM(s). Download the built RPMs from
the run's **Artifacts**; the package list is in the run **Summary**.

### 5. Release (publish to Artifactory)
After merge, go to **Actions → Release → Run workflow** and select the `c10s`
branch:
- Choose the **`publish-target`**: `staging` (the default) or `prod`.
- A reviewer approves the `pkg-release-approval` gate.
- Once approved, the RPM(s) are published to the selected Artifactory target.

---

## Updating the package version

This is the everyday workflow — **two edits on `c10s`, no tarball in git**:

1. Bump `Version:` in the spec (and the `Source0:` URL if its path changed).
2. Recompute the checksum for the new tarball:
   ```bash
   sha512sum --tag <component>-<newversion>.tar.gz > sources
   ```
3. Commit the spec + `sources`, open a PR (build verifies it), merge, then run
   **Release**. The first release fetches the new upstream tarball, verifies it,
   and caches it back to Artifactory automatically.

---

## How sources are resolved (cache → upstream → cache-back)

The dist-git **lookaside cache** model: git stores only the checksum; the tarball
lives in Artifactory, content-addressed by that checksum.

1. The build computes the cache path from the `sources` entry
   and checks whether the tarball is already cached.
2. **Cache hit** → download from the cache. **Cache miss** → download from the
   spec's `Source` URL.
3. The checksum is verified against `sources` (mismatch fails the build).
4. On **release**, a tarball fetched from upstream is cached back so future
   builds are hits.

Published layout in Artifactory (defaults):
```
qualcomm-rpm-repo/centos/10/os/aarch64/<pkg>-<ver>.aarch64.rpm
qualcomm-rpm-repo/centos/10/os/noarch/<pkg>-<ver>.noarch.rpm
qualcomm-rpm-repo/centos/10/os/SRPMS/<pkg>-<ver>.src.rpm
```

RPMs are published under `centos/10/os/` split by architecture: arch-specific
binary RPMs land in `aarch64/`, architecture-independent ones in `noarch/`, and
source RPMs in `SRPMS/`. Artifactory's YUM indexer writes the `repodata/` under
each arch directory.

---

## Required configuration summary

| Name | Kind | Required | Purpose |
|---|---|---|---|
| `RPM_ARTIFACTORY_ACCESS_TOKEN` | Secret | Release only | Artifactory token used to publish the RPM(s) to staging. |
| `PROD_RPM_ARTIFACTORY_ACCESS_TOKEN` | Secret | Release only | Artifactory token used to publish the RPM(s) to prod. |
| `pkg-release-approval` | Environment | Release only | Approval gate before publishing. |
| Runner pool access | — | Yes | Build/publish run on `[self-hosted, platform-prd-u2404-arm64-large-od-ephem]`. |
| `rpm-builder` GHCR access | — | Yes | Repo must be authorized to pull `ghcr.io/qualcomm-linux/rpm-builder`. |

_Need token or `rpm-builder` access? Contact your org admin._

---


## License

Distributed under the **BSD 3-Clause License**. See [`LICENSE.txt`](LICENSE.txt)
for the full text.
