# IMPORTANT: this is for the leapp-framework capability (it's not the real
# version of the leapp). The capability reflects changes in api and whatever
# functionality important from the point of repository. In case of
# incompatible changes, bump the major number and zero minor one. Otherwise
# bump the minor one.
# NOTE: we do not use this capability in the RHEL official rpms. But we provide
# it. In case of upstream, dependencies are set differently, but YUM is not
# capable enough to deal with them correctly all the time; we continue to use
# simplified deps in RHEL to ensure that YUM can deal with it.
%global framework_version 3.1

# IMPORTANT: everytime the requirements are changed, increment number by one
# - same for Provides in deps subpackage
%global framework_dependencies 5

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
Version:    0.15.1
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
# %%patch0001 -p1


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
* Tue Feb 21 2023 Petr Stodulka <pstodulk@redhat.com> - 0.15.1-1
- Rebase to v0.15.1
- Change DAC for /var/lib/leapp to 0700 to make it accessible for root only
- Propagate error messages from leapp actors to the main leapp process
- Prevent unicode errors when printing error messages
- Resolves: rhbz#2162710

* Thu Sep 08 2022 Petr Stodulka <pstodulk@redhat.com> - 0.15.0-2
- Fix the check of missing required answers
- Resolves: rhbz#2124332

* Wed Aug 24 2022 Petr Stodulka <pstodulk@redhat.com> - 0.15.0-1
- Rebase to v0.15.0
- Bump leapp-framework to 3.1
- Deprecate `reporting.(Tags|Flags)` replaced by `reporting.Groups`
- Fix crashes when processing invalid FQDNs
- Fix the error msg when a leapp CLI command does not exist
- Introduce new report JSON schema v1.2.0 (default: 1.1.0)
- Resolves: rhbz#2090992, rhbz#2106065

* Mon Mar 14 2022 Petr Stodulka <pstodulk@redhat.com> - 0.14.0-1
- Rebase to v0.14.0
- Bump leapp-framework to 2.2
- Bump leapp-framework-dependencies to 5
- Add depency on python3 (distribution python)
- Added possibility to specify the report format version
- Check the answerfile upon loading and prevent creation of invalid answerfile
- Dialogs: print the reason field for question in the answerfile
- Fix the JSON serialization in Dialogs on Python3
- Introduced new functions in the leapp standard library
- Updated man page
- Resolves: rhbz#1997075

* Thu Sep 30 2021 Petr Stodulka <pstodulk@redhat.com> - 0.13.0-10
- Rebase to v0.13.0
- Bump the provided leapp-framework capability to 2.0
- The commands for the leapp tool (e.g. preupgrade, upgrade) are now
  defined in the leapp-repository component
- The leapp tool scans the available CLI commands dynamically
- First build for the IPU 8 -> 9
- Resolves: #1997075

* Fri Apr 23 2021 Petr Stodulka <pstodulk@redhat.com> - 0.12.1-1
- Rebase to v0.12.1
- Added rerun command for experimental purposes to be able to re-run manually
  the last phase when needed (experimental)
- Resolves: #1952885

* Thu Feb 04 2021 Dominik Rehak <drehak@redhat.com> - 0.12.0-1
- Rebase to v0.12.0
- Bump leapp-framework capability to 1.4
- Add JSON schema of leapp reports for validation
- Add a stable report identifier for each generated report
- Resolves: #1915508

* Wed Oct 21 2020 Dominik Rehak <drehak@redhat.com> - 0.11.1-1
- Rebase to v0.11.1
- Fix conversion of deprecation messages to reports
- Fix various issues regarding suppressing of deprecation
- Remove pytest residuals in spec file
- Update documentation and manpages
- Resolves: #1887913

* Tue Aug 18 2020 Michal Bocek <mbocek@redhat.com> - 0.11.0-1
- Rebase to v0.11.0
- Bump leapp-framework capability to 1.3
- Preserve verbose/debug options during the whole upgrade workflow
- Print the informative error block to the STDOUT instead of STDERR
- Add new reporting tags: `PUBLIC_CLOUD` and `RHUI`
- Add the possibility to skip actor discovery to improve performance of tests when an actor context is injected directly
- Introduce the `deprecated` and `suppress_deprecation` decorators to support the deprecation process
- Store dialog answers in the leapp.db
- Update and improve man pages
- Raising a missing exception with tests failing under py3
- Adde the --actor-config option to `snactor run` to specify a workflow configuration model that should be consumed by actors
- The `call` function has been improved to be working on MacOS
- Known issue: the `suppress_deprecation` decorator causes a traceback in certain cases

* Thu Jul 30 2020 Michal Bocek <mbocek@redhat.com> - 0.10.0-3
- A temporary build to run TPS tests against
- Relates: #1860373

* Mon Apr 20 2020 Michal Bocek <mbocek@redhat.com> - 0.10.0-2
- Make debug/verbose setting persistent across the upgrade
- Relates: #1821712

* Thu Apr 16 2020 Petr Stodulka <pstodulk@redhat.com> - 0.10.0-1
- Rebase to v0.10.0
- Add the --enablerepo option for Leapp to use an existing custom yum/dnf
  repository during the upgrade
- Add the --no-rhsm option for Leapp for use without subscription-manager
  (#622)
- Add `leapp answer` to answer Dialog questions in CLI (#592)
- Add `stdin` and `encoding` parameters in the run function (#583, #595)
- Add new dependency on python-requests
- Add the DESKTOP tag for the leapp report (#612)
- Display a warning when leapp is used in an unsupported (devel/testing) mode
  (#577)
- Drop dependency on python-jinja2
- Error messages are now part of the preupgrade report
- Fix json export capabilities using serialization (#598)
- Introduce DialogModel that could be processed by actors to add related
  information into the report (#589)
- Introduce Workflow API (#618)
- Move all leapp and snactor files into related rpms instead of python2-leapp
  (#591)
- Print errors on stdout in pretty format (#593)
- Report inhibitors separately from errors on stdout (#620)
- Show progress in non-verbose executions (#621)
- The verbosity options (--verbose | --debug) are available for leapp commands
  as well
- Resolves: #1821712


* Thu Oct 24 2019 Petr Stodulka <pstodulk@redhat.com> - 0.9.0-1
- Rebase to v0.9.0
- Add sanity-check command for snactor
- Add the /var/log/leapp directory to the leapp RPM
- Handle string types in compatible way
- Introduce answerfile generation & usage
- Introduce report composability, remove renders (#543)
- Show help message for proper subcommand of leapp
- Stop adding 'process-end' audit entry (#538)
- Various fixes in displaying of generated reports
- Resolves: #1753583

* Wed Jul 24 2019 Petr Stodulka <pstodulk@redhat.com> - 0.8.1-1
- Rebase to v0.8.1
  Relates: #1723113
- Fix issue undefined ReportReference

* Mon Jul 15 2019 Petr Stodulka <pstodulk@redhat.com> - 0.8.0-1
- Rebase to v0.8.0
  Relates: #1723113
- add the preupgrade subcommand to be able check system and generate report for
  upgrade without run of the upgrade itself
- add checks of arguments for cmdline parameters
- log output of commands to logfile (#520)
- avoid spurious output about missing logger
- exit non-zero on unhandled exceptions and errors
- fix actor library loading, so libraries do not have to be imported in
  lexicographical order
- log on the ERROR level by default instead of DEBUG
- create a dynamic configuration phase that allows creation of configuration
  for repository workflow
- add JSON report generation
- stdlib: add option to `run()` to ignore exit code

* Sun Jun 23 2019 Vojtech Sokol <vsokol@redhat.com> - 0.7.0-3
- Rebuild
  Resolves: #1723113

* Mon Apr 29 2019 Petr Stodulka <pstodulk@redhat.com> - 0.7.0-2
- load checkpoints ordered by 'id' instead of timestamp
  Relates: #1636478

* Wed Apr 17 2019 Vojtech Sokol <vsokol@redhat.com> - 0.7.0-1
- Rebase to v0.7.0
  Relates: #1636478
- add the ability to stop and resume workflow in any phase
- fix incompatibilities with Python3
- store logs in one place and support archiving of previous logs
- fix handling of Unicode in the run function of leapp stdlib

* Mon Apr 08 2019 Vojtech Sokol <vsokol@redhat.com> - 0.6.0-2
- Fix specfile
  Relates: #1636478

* Mon Apr 08 2019 Vojtech Sokol <vsokol@redhat.com> - 0.6.0-1
- Rebase to v0.6.0
  Relates: #1636478
- snactor
  - `repo new` subcommand: display message if directory with same name exists
  - `discover subcommand`: fix wrong path
  - `workflow run` subcommand: introduce `--save-output` parameter
  - fix cryptic message without user repo config
  - show global repos in repo list
  - fix trace on topic creation
- stdlib
  - make api directly available in stdlib
  - external program exec function - audit data generation and storage
- models
  - introduction of the JSON field type
- new debug and verbose modes
- new reporting capabilities
- change default loglevel to ERROR

* Thu Jan 24 2019 Petr Stodulka <pstodulk@redhat.com> - 0.5.0-1
- Rebase to v0.5.0
  Relates: #1636478
- Models has been refactored to be more comprehensible and reliable
- Introduced standard library
- Introduced the actor convenience api for actors and repository libraries
- Added localization support
- Extended serialization support
- Added exception to be able to stop actor execution
- Packaging: Move system dependencies into the metapackage

* Fri Nov 23 2018 Petr Stodulka <pstodulk@redhat.com> - 0.4.0-1
- Rebase to v0.4.0
  Relates: #1636478

* Wed Nov 07 2018 Petr Stodulka <pstodulk@redhat.com> - 0.3.1-1
- Rebase to v0.3.1
  Relates: #1636478

* Wed Nov 07 2018 Petr Stodulka <pstodulk@redhat.com> - 0.3-1
- Initial rpm
  Resolves: #1636478
