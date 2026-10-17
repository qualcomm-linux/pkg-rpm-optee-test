Name:		mink-optee-test
Version:	4.0.0
Release:	1.qli%{?dist}
Summary:	Qualcomm mink based optee xtest suite for QTEE

License:	BSD-2-Clause
URL:		https://github.com/OP-TEE/optee_tests
Source0:	https://github.com/OP-TEE/optee_test/archive/refs/tags/%{version}.tar.gz#/optee_test-%{version}.tar.gz
Patch0:		build-xtest-qtee.patch
Patch1:		add-libteec-headers.patch
Patch2:		add-optee-os-core-headers.patch
Patch3:		add-optee-os-lib-libutee-headers.patch
Patch4:		add-optee-os-lib-libutils-ext-headers.patch
Patch5:		remove-regression-suite-from-default.patch
Patch6:		stub-testcases-inapplicable-for-qtee.patch

BuildRequires:	gcc
BuildRequires:	cmake
BuildRequires:  openssl-devel
BuildRequires:	minkipc-devel
BuildRequires:  mink-optee-client-devel

%description
This package provides xtest-qtee, a Qualcomm-adapted build of the upstream
OP-TEE sanity testsuite. It is built against the Qualcomm MinkIPC transport
stack (libminkteec, libminkadaptor) and the Qualcomm-adapted PKCS#11 client
library (libckqteec), targeting the Qualcomm Trusted Execution Environment
(QTEE) rather than the upstream OP-TEE supplicant daemon.

The package includes the xtest_qtee QTEE sanity testsuite.


%prep
%setup -q -n optee_test-%{version}
%patch -P0 -P1 -P2 -P3 -P4 -P5 -P6 -p1


%build
%cmake
%cmake_build


%install
%cmake_install

%files
%license LICENSE.md
%doc README.md
%{_bindir}/xtest_qtee


%changelog
* Sat Oct 17 2026 Abhinaba Rakshit <abhinaba.rakshit@oss.qualcomm.com> - 4.0.0-1.qli
- Initial RPM packaging with upstream 4.0.0
