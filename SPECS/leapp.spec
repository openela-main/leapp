# IMPORTANT: this is for the leapp-framework capability (it's not the real
# version of the leapp). The capability reflects changes in api and whatever
# functionality important from the point of repository. In case of
# incompatible changes, bump the major number and zero minor one. Otherwise
# bump the minor one.
# NOTE: we do not use this capability in the RHEL official rpms. But we provide
# it. In case of upstream, dependencies are set differently, but YUM is not
# capable enough to deal with them correctly all the time; we continue to use
# simplified deps in RHEL to ensure that YUM can deal with it.
%global framework_version 6.0

# IMPORTANT: everytime the requirements are changed, increment number by one
# - same for Provides in deps subpackage
%global framework_dependencies 6

# Do not build bindings for python3 for RHEL == 7
# # Currently Py2 is dead on Fedora and we don't have to support it. As well,
# # our current packaging is not prepared for Py2 & Py3 packages in the same
# # time. Instead of that, make Py2 and Py3 exclusive. Possibly rename macros..
%if 0%{?rhel} == 7
  %define leapp_python 2
  %define leapp_python_sitelib %{python2_sitelib}
  %define leapp_python_name python2
  %define leapp_py_build %{py2_build}
  %define leapp_py_install %{py2_install}

%else
  %define leapp_python 3
  %define leapp_python_sitelib %{python3_sitelib}
  %define leapp_python_name python3
  %define leapp_py_build %{py3_build}
  %define leapp_py_install %{py3_install}
  # we have to drop the dependency on python(abi) completely on el8+ because
  # of IPU (python abi is different between systems)
  %global __requires_exclude ^python\\(abi\\) = 3\\..+|/usr/libexec/platform-python|/usr/bin/python.*
%endif

Name:       leapp
Version:    0.19.0
Release:    1%{?dist}
Summary:    OS & Application modernization framework

License:    ASL 2.0
URL:        https://oamg.github.io/leapp/
Source0:    https://github.com/oamg/%{name}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

# NOTE: Our packages must be noarch. Do no drop this in any way.
BuildArch:  noarch

Requires: %{leapp_python_name}-%{name} = %{version}-%{release}
%{?python_disable_dependency_generator}

%if 0%{?rhel} == 7
# The leapp tool doesn't require the leapp-repository anymore. However for the
# compatibility purposes, we keep it here for RHEL 7 at least for a while.
# The dependency on leapp is expected to be set by packages providing the
# final functionality (e.g. conversion of system, in-place upgrade).
# IOW, people should look for rpms like leapp-convert or leapp-upgrade
# in future.

# Just ensure the leapp repository will be installed as well. Compatibility
# should be specified by the leapp-repository itself
Requires: leapp-repository
%endif # !fedora

# PATCHES HERE
# Patch0001: filename.patch

%description
Leapp utility provides the possibility to use the Leapp framework via CLI.
The utility itself does not define any subcommands but "help". All leapp
subcommands are expected to be provided by other packages under a specific
directory. See the man page for more details.


##################################################
# snactor package
##################################################
%package -n snactor
Summary: %{summary}
Requires: %{leapp_python_name}-%{name} = %{version}-%{release}
%{?python_disable_dependency_generator}

%description -n snactor
Leapp's snactor tool - actor development environment utility for creating and
managing actor projects.

##################################################
# the library package (the framework itself)
##################################################
%package -n %{leapp_python_name}-%{name}

Summary: %{summary}
%{?python_provide:%python_provide %{leapp_python_name}-%{name}}

%if %{leapp_python} == 2
# RHEL 7 only
BuildRequires:  python-devel
BuildRequires:  python-setuptools
Conflicts:      python3-%{name}
%else
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
Conflicts:      python2-%{name}

%{?python_disable_dependency_generator}
%define __provides_exclude_from ^.*$
%endif

Provides: leapp-framework = %{framework_version}
Requires: leapp-framework-dependencies = %{framework_dependencies}

%description -n %{leapp_python_name}-%{name}
Python %{leapp_python} leapp framework libraries.


##################################################
# DEPS package for external dependencies
##################################################
%package deps
Summary:    Meta-package with system dependencies of %{name} package

# IMPORTANT: everytime the requirements are changed, increment number by one
# same for requirements in main package above
Provides: leapp-framework-dependencies = %{framework_dependencies}
##################################################
# Real requirements for the leapp HERE
##################################################
%if 0%{?rhel} && 0%{?rhel} == 7
Requires: python-six
Requires: python-setuptools
Requires: python-requests
Requires: PyYAML
%else # <> rhel 7
# for Fedora & RHEL 8+ deliver just python3 stuff
# NOTE: requirement on python3 refers to the general version of Python
# for the particular system (3.6 on RHEL 8, 3.9 on RHEL 9, ...)
# Do not use python(abi) deps, as on RHEL 8 it's provided by platform-python
# which is not helpful for us
Requires: python3
Requires: python3-six
Requires: python3-setuptools
Requires: python3-requests
Requires: python3-PyYAML
%endif
Requires: findutils
##################################################
# end requirements here
##################################################

%description deps
%{summary}


##################################################
# Prep
##################################################
%prep
%setup -n %{name}-%{version}


# APPLY REGISTERED PATCHES HERE


##################################################
# Build
##################################################
%build
%{leapp_py_build}


##################################################
# Install
##################################################
%install

install -m 0755 -d %{buildroot}%{_mandir}/man1
install -m 0644 -p man/snactor.1 %{buildroot}%{_mandir}/man1/

# This block of files was originally skipped for fedora. Adding now
install -m 0755 -d %{buildroot}%{_datadir}/leapp
install -m 0755 -d %{buildroot}%{_datadir}/leapp/report_schema
install -m 0644 -p report-schema-v110.json %{buildroot}%{_datadir}/leapp/report_schema/report-schema.json
install -m 0700 -d %{buildroot}%{_sharedstatedir}/leapp
install -m 0755 -d %{buildroot}%{_sysconfdir}/leapp
install -m 0755 -d %{buildroot}%{_sysconfdir}/leapp/actor_conf.d/
install -m 0755 -d %{buildroot}%{_sysconfdir}/leapp/repos.d
install -m 0600 -d %{buildroot}%{_sysconfdir}/leapp/answers
# standard directory should have permission set to 0755, however this directory
# could contain sensitive data, hence permission for root only
install -m 0700 -d %{buildroot}%{_sysconfdir}/leapp/answers
# same for this dir; we need it for the frontend in cockpit
install -m 0700 -d %{buildroot}%{_localstatedir}/log/leapp
install -m 0644 etc/leapp/*.conf %{buildroot}%{_sysconfdir}/leapp
install -m 0644 -p man/leapp.1 %{buildroot}%{_mandir}/man1/

%{leapp_py_install}


##################################################
# leapp files
##################################################

%files
%doc README.md
%license COPYING
%{_mandir}/man1/leapp.1*
%config(noreplace) %{_sysconfdir}/leapp/leapp.conf
%config(noreplace) %{_sysconfdir}/leapp/logger.conf
%dir %{_sysconfdir}/leapp
%dir %{_sysconfdir}/leapp/actor_conf.d
%dir %{_sysconfdir}/leapp/answers
%dir %{_sysconfdir}/leapp/repos.d
%{_bindir}/leapp
%dir %{_sharedstatedir}/leapp
%dir %{_localstatedir}/log/leapp
%dir %{_datadir}/leapp/
%dir %{_datadir}/leapp/report_schema/
%{_datadir}/leapp/report_schema
%{leapp_python_sitelib}/leapp/cli


##################################################
# snactor files
##################################################
%files -n snactor
%license COPYING
%{leapp_python_sitelib}/leapp/snactor
%{_mandir}/man1/snactor.1*
%{_bindir}/snactor


##################################################
# python[23]-leapp files
##################################################
%files -n %{leapp_python_name}-%{name}
%license COPYING
%{leapp_python_sitelib}/*
# These are delivered in other subpackages
%exclude %{leapp_python_sitelib}/leapp/cli
%exclude %{leapp_python_sitelib}/leapp/snactor


%files deps
# no files here

%changelog
* Fri Feb 14 2025 Petr Stodulka <pstodulk@redhat.com> - 0.19.0-1
- Rebase to new upstream version 0.19.0
- Add possibility to use a specified execution context for snactor run in an existing leapp.db
- Increase limits on the number of opened file descriptors and maximum size
  of manipulated files when running leapp
- Resolves: RHEL-57042

* Mon Nov 18 2024 Matej Matuska <mmatuska@redhat.com> - 0.18.0-4
- Bump leapp-framework to 6.0
- Bump leapp-framework-dependencies to 6
- Require python3-PyYAML
- [Technical preview] Introduce configurability for leapp actors
- Resolves: RHEL-57042

* Thu Sep 19 2024 Petr Stodulka <pstodulk@redhat.com> - 0.18.0-3
- Rebuild to apply changes for gating
- Resolves:  RHEL-57042

* Thu Sep 12 2024 Petr Stodulka <pstodulk@redhat.com> - 0.18.0-2
- Initial build for el9
- Resolves:  RHEL-57042
