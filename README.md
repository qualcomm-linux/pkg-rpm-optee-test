# pkg-rpm-optee-test

This RPM packages [`OP-TEE/optee_test`](https://github.com/OP-TEE/optee_test) with mink based changes
—  This package provides xtest-qtee, a Qualcomm-adapted build of the upstream OP-TEE sanity testsuite. It is built against the Qualcomm MinkIPC transport stack (libminkteec, libminkadaptor) and the Qualcomm-adapted PKCS#11 client library (libckqteec), targeting the Qualcomm Trusted Execution Environment (QTEE) rather than the upstream OP-TEE supplicant daemon. It is based on the OP-TEE Test sources (https://github.com/OP-TEE/optee_test) at version 4.0.0, with minimal patches applied to link against the Qualcomm MinkIPC stack (libminkteec, libminkadaptor and libckqteec), instead of the standard OP-TEE transport. It also ensure to stub our testcases which are not supported by QTEE such as regression tests.

This repo builds and publishes the Mink based `optee_test` RPM via the shared
[`qualcomm-linux/qcom-rpm-utils`](https://github.com/qualcomm-linux/qcom-rpm-utils)
reusable workflows — it follows the same one-package-per-repo template used
across `qualcomm-linux/pkg-rpm-*`.

## Branches

Following the Fedora/CentOS **dist-git** convention, each distro stream gets its
own branch, and the packaging files live at the branch root:

| Branch | Stream | Contents |
|---|---|---|
| `main` | — | Template docs, onboarding guide, community files. Nothing is built here. |
| **`c10s`** | CentOS 10 Stream | **This branch.** `mink-optee-test.spec` + `sources` + workflows. |

Full onboarding guide, configuration reference, and troubleshooting live on
[`main`](../../tree/main) — see its `README.md` and `docs/workflows.md`.

## Installation Instructions

```
sudo rpm -i mink-optee-test-x.aarch64.rpm
```

## CI: build on PR, release on demand

| Workflow | Trigger | Purpose |
|---|---|---|
| [`build-on-pr.yml`](.github/workflows/build-on-pr.yml) | Pull request | Build the RPM so reviewers confirm the package still builds. Read-only — never publishes. |
| [`pkg-release.yml`](.github/workflows/pkg-release.yml) | Manual (`workflow_dispatch`) | Build **and** publish the RPM to Artifactory, behind an approval gate. |

Both delegate to reusable workflows in `qcom-rpm-utils`, which run `rpmbuild`
inside the prebuilt `rpm-builder` container image. Required repo configuration
(`CACHE_BASE_URL` variable, `ARTIFACTORY_ACCESS_TOKEN` secret,
`pkg-release-approval` environment, runner pool access) is documented in full
in [`docs/workflows.md`](docs/workflows.md), along with the dist-git
sources/lookaside-cache model and a troubleshooting table.

This repo was created from [`qualcomm-linux/pkg-rpm-template`](https://github.com/qualcomm-linux/pkg-rpm-template);
see that template's README if you're onboarding a *different* package and
want the generic step-by-step instructions.

## Getting in Contact

How to contact maintainers. E.g. GitHub Issues, GitHub Discussions could be indicated for many cases. However a mail list or list of Maintainer e-mails could be shared for other types of discussions. E.g.

* [Report an Issue on GitHub](../../issues)
* [Open a Discussion on GitHub](../../discussions)

## License

pkg-rpm-optee-test is licensed under the [BSD-3-clause License](https://spdx.org/licenses/BSD-3-Clause.html). See [LICENSE.txt](LICENSE.txt) for the full license text.
