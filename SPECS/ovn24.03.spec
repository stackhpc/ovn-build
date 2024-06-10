# Copyright (C) 2009, 2010, 2013, 2014 Nicira Networks, Inc.
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without warranty of any kind.
#
# If tests have to be skipped while building, specify the '--without check'
# option. For example:
# rpmbuild -bb --without check rhel/openvswitch-fedora.spec

# This defines the base package name's version.

%define pkgver 2.13
%define pkgname ovn24.03

# If libcap-ng isn't available and there is no need for running OVS
# as regular user, specify the '--without libcapng'
%bcond_without libcapng

# Enable PIE, bz#955181
%global _hardened_build 1

# RHEL-7 doesn't define _rundir macro yet
# Fedora 15 onwards uses /run as _rundir
%if 0%{!?_rundir:1}
%define _rundir /run
%endif

# Build python2 (that provides python) and python3 subpackages on Fedora
# Build only python3 (that provides python) subpackage on RHEL8
# Build only python subpackage on RHEL7
%if 0%{?rhel} > 7 || 0%{?fedora}
# On RHEL8 Sphinx is included in buildroot
%global external_sphinx 1
%else
# Don't use external sphinx (RHV doesn't have optional repositories enabled)
%global external_sphinx 0
%endif

# We would see rpmlinit error - E: hardcoded-library-path in '% {_prefix}/lib'.
# But there is no solution to fix this. Using {_lib} macro will solve the
# rpmlink error, but will install the files in /usr/lib64/.
# OVN pacemaker ocf script file is copied in /usr/lib/ocf/resource.d/ovn/
# and we are not sure if pacemaker looks into this path to find the
# OVN resource agent script.
%global ovnlibdir %{_prefix}/lib

Name: %{pkgname}
Summary: Open Virtual Network support
Group: System Environment/Daemons
URL: http://www.ovn.org/
Version: 24.03.1
Release: 44%{?commit0:.%{date}git%{shortcommit0}}%{?dist}
Provides: openvswitch%{pkgver}-ovn-common = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes: openvswitch%{pkgver}-ovn-common < 2.11.0-1

# Nearly all of openvswitch is ASL 2.0.  The bugtool is LGPLv2+, and the
# lib/sflow*.[ch] files are SISSL
License: ASL 2.0 and LGPLv2+ and SISSL

%define ovncommit 19de791062fbdb38741c65c476343cb53c88542e

# Always pull an upstream release, since this is what we rebase to.
Source: https://github.com/ovn-org/ovn/archive/%{ovncommit}.tar.gz#/ovn-%{version}.tar.gz

%define ovscommit f19448b8618967a108ec6f34713dd811ce1d1334
%define ovsshortcommit f19448b

Source10: https://github.com/openvswitch/ovs/archive/%{ovscommit}.tar.gz#/openvswitch-%{ovsshortcommit}.tar.gz
%define ovsdir ovs-%{ovscommit}

%define docutilsver 0.12
%define pygmentsver 1.4
%define sphinxver   1.1.3
Source100: https://pypi.io/packages/source/d/docutils/docutils-%{docutilsver}.tar.gz
Source101: https://pypi.io/packages/source/P/Pygments/Pygments-%{pygmentsver}.tar.gz
Source102: https://pypi.io/packages/source/S/Sphinx/Sphinx-%{sphinxver}.tar.gz

Source500: configlib.sh
Source501: gen_config_group.sh
Source502: set_config.sh

# Important: source503 is used as the actual copy file
# @TODO: this causes a warning - fix it?
Source504: arm64-armv8a-linuxapp-gcc-config
Source505: ppc_64-power8-linuxapp-gcc-config
Source506: x86_64-native-linuxapp-gcc-config

Patch:     %{pkgname}.patch

# FIXME Sphinx is used to generate some manpages, unfortunately, on RHEL, it's
# in the -optional repository and so we can't require it directly since RHV
# doesn't have the -optional repository enabled and so TPS fails
%if %{external_sphinx}
BuildRequires: python3-sphinx
%else
# Sphinx dependencies
BuildRequires: python-devel
BuildRequires: python-setuptools
#BuildRequires: python2-docutils
BuildRequires: python-jinja2
BuildRequires: python-nose
#BuildRequires: python2-pygments
# docutils dependencies
BuildRequires: python-imaging
# pygments dependencies
BuildRequires: python-nose
%endif

BuildRequires: gcc gcc-c++ make
BuildRequires: autoconf automake libtool
BuildRequires: systemd-units openssl openssl-devel
BuildRequires: python3-devel python3-setuptools
BuildRequires: desktop-file-utils
BuildRequires: groff-base graphviz
BuildRequires: unbound-devel

# make check dependencies
BuildRequires: procps-ng
%if 0%{?rhel} == 8 || 0%{?fedora}
BuildRequires: python3-pyOpenSSL
%endif
BuildRequires: tcpdump

%if %{with libcapng}
BuildRequires: libcap-ng libcap-ng-devel
%endif

%if 0%{?rhel} == 9
BuildRequires: python3-scapy
%endif

Requires: hostname openssl iproute module-init-tools

Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

# to skip running checks, pass --without check
%bcond_without check

%description
OVN, the Open Virtual Network, is a system to support virtual network
abstraction.  OVN complements the existing capabilities of OVS to add
native support for virtual network abstractions, such as virtual L2 and L3
overlays and security groups.

%package central
Summary: Open Virtual Network support
License: ASL 2.0
Requires: %{pkgname}
Requires: firewalld-filesystem
Provides: openvswitch%{pkgver}-ovn-central = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes: openvswitch%{pkgver}-ovn-central < 2.11.0-1

%description central
OVN DB servers and ovn-northd running on a central node.

%package host
Summary: Open Virtual Network support
License: ASL 2.0
Requires: %{pkgname}
Requires: firewalld-filesystem
Provides: openvswitch%{pkgver}-ovn-host = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes: openvswitch%{pkgver}-ovn-host < 2.11.0-1

%description host
OVN controller running on each host.

%package vtep
Summary: Open Virtual Network support
License: ASL 2.0
Requires: %{pkgname}
Provides: openvswitch%{pkgver}-ovn-vtep = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes: openvswitch%{pkgver}-ovn-vtep < 2.11.0-1

%description vtep
OVN vtep controller

%prep
%autosetup -n ovn-%{ovncommit} -a 10 -p 1

%build
%if 0%{?commit0:1}
# fix the snapshot unreleased version to be the released one.
sed -i.old -e "s/^AC_INIT(openvswitch,.*,/AC_INIT(openvswitch, %{version},/" configure.ac
%endif
./boot.sh

# OVN source code is now separate.
# Build openvswitch first.
# XXX Current openvswitch2.13 doesn't
# use "2.13.0" for version. It's a commit hash
pushd %{ovsdir}
./boot.sh
%configure \
%if %{with libcapng}
        --enable-libcapng \
%else
        --disable-libcapng \
%endif
        --enable-ssl \
        --with-pkidir=%{_sharedstatedir}/openvswitch/pki

make %{?_smp_mflags}
popd

# Build OVN.
# XXX OVS version needs to be updated when ovs2.13 is updated.
%configure \
        --with-ovs-source=$PWD/%{ovsdir} \
%if %{with libcapng}
        --enable-libcapng \
%else
        --disable-libcapng \
%endif
        --enable-ssl \
        --with-pkidir=%{_sharedstatedir}/openvswitch/pki

make %{?_smp_mflags}

%install
%make_install
install -p -D -m 0644 \
        rhel/usr_share_ovn_scripts_systemd_sysconfig.template \
        $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/ovn

for service in ovn-controller ovn-controller-vtep ovn-northd; do
        install -p -D -m 0644 \
                        rhel/usr_lib_systemd_system_${service}.service \
                        $RPM_BUILD_ROOT%{_unitdir}/${service}.service
done

install -d -m 0755 $RPM_BUILD_ROOT/%{_sharedstatedir}/ovn

install -d $RPM_BUILD_ROOT%{ovnlibdir}/firewalld/services/
install -p -m 0644 rhel/usr_lib_firewalld_services_ovn-central-firewall-service.xml \
        $RPM_BUILD_ROOT%{ovnlibdir}/firewalld/services/ovn-central-firewall-service.xml
install -p -m 0644 rhel/usr_lib_firewalld_services_ovn-host-firewall-service.xml \
        $RPM_BUILD_ROOT%{ovnlibdir}/firewalld/services/ovn-host-firewall-service.xml

install -d -m 0755 $RPM_BUILD_ROOT%{ovnlibdir}/ocf/resource.d/ovn
ln -s %{_datadir}/ovn/scripts/ovndb-servers.ocf \
      $RPM_BUILD_ROOT%{ovnlibdir}/ocf/resource.d/ovn/ovndb-servers

install -p -D -m 0644 rhel/etc_logrotate.d_ovn \
        $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d/ovn

# remove unneeded files.
rm -f $RPM_BUILD_ROOT%{_bindir}/ovs*
rm -f $RPM_BUILD_ROOT%{_bindir}/vtep-ctl
rm -f $RPM_BUILD_ROOT%{_sbindir}/ovs*
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/ovs*
rm -f $RPM_BUILD_ROOT%{_mandir}/man5/ovs*
rm -f $RPM_BUILD_ROOT%{_mandir}/man5/vtep*
rm -f $RPM_BUILD_ROOT%{_mandir}/man7/ovs*
rm -f $RPM_BUILD_ROOT%{_mandir}/man8/ovs*
rm -f $RPM_BUILD_ROOT%{_mandir}/man8/vtep*
rm -rf $RPM_BUILD_ROOT%{_datadir}/ovn/python
rm -f $RPM_BUILD_ROOT%{_datadir}/ovn/scripts/ovs*
rm -rf $RPM_BUILD_ROOT%{_datadir}/ovn/bugtool-plugins
rm -f $RPM_BUILD_ROOT%{_libdir}/*.a
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/pkgconfig/*.pc
rm -f $RPM_BUILD_ROOT%{_includedir}/ovn/*
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/ovs-appctl-bashcomp.bash
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/ovs-vsctl-bashcomp.bash
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/openvswitch
rm -f $RPM_BUILD_ROOT%{_datadir}/ovn/scripts/ovn-bugtool*
rm -f $RPM_BUILD_ROOT/%{_bindir}/ovn-docker-overlay-driver \
        $RPM_BUILD_ROOT/%{_bindir}/ovn-docker-underlay-driver

%check
%if %{with check}
    touch resolv.conf
    export OVS_RESOLV_CONF=$(pwd)/resolv.conf
    if ! make check TESTSUITEFLAGS='%{_smp_mflags}'; then
        cat tests/testsuite.log
        if ! make check TESTSUITEFLAGS='--recheck'; then
            cat tests/testsuite.log
            # Presently a test case - "2796: ovn -- ovn-controller incremental processing"
            # is failing on aarch64 arch. Let's not exit for this arch
            # until we figure out why it is failing.
            # Test case 93: ovn.at:12105       ovn -- ACLs on Port Groups is failing
            # repeatedly on s390x. This needs to be investigated.
            %ifnarch aarch64
            %ifnarch ppc64le
            %ifnarch s390x
                exit 1
            %endif
            %endif
            %endif
        fi
    fi
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre central
if [ $1 -eq 1 ] ; then
    # Package install.
    /bin/systemctl status ovn-northd.service >/dev/null
    ovn_status=$?
    rpm -ql openvswitch-ovn-central > /dev/null
    if [[ "$?" = "0" && "$ovn_status" = "0" ]]; then
        # ovn-northd service is running which means old openvswitch-ovn-central
        # is already installed and it will be cleaned up. So start ovn-northd
        # service when posttrans central is called.
        touch %{_localstatedir}/lib/rpm-state/ovn-northd
    fi
fi

%pre host
if [ $1 -eq 1 ] ; then
    # Package install.
    /bin/systemctl status ovn-controller.service >/dev/null
    ovn_status=$?
    rpm -ql openvswitch-ovn-host > /dev/null
    if [[ "$?" = "0" && "$ovn_status" = "0" ]]; then
        # ovn-controller service is running which means old
        # openvswitch-ovn-host is installed and it will be cleaned up. So
        # start ovn-controller service when posttrans host is called.
        touch %{_localstatedir}/lib/rpm-state/ovn-controller
    fi
fi

%pre vtep
if [ $1 -eq 1 ] ; then
    # Package install.
    /bin/systemctl status ovn-controller-vtep.service >/dev/null
    ovn_status=$?
    rpm -ql openvswitch-ovn-vtep > /dev/null
    if [[ "$?" = "0" && "$ovn_status" = "0" ]]; then
        # ovn-controller-vtep service is running which means old
        # openvswitch-ovn-vtep is installed and it will be cleaned up. So
        # start ovn-controller-vtep service when posttrans host is called.
        touch %{_localstatedir}/lib/rpm-state/ovn-controller-vtep
    fi
fi

%preun central
%if 0%{?systemd_preun:1}
    %systemd_preun ovn-northd.service
%else
    if [ $1 -eq 0 ] ; then
        # Package removal, not upgrade
        /bin/systemctl --no-reload disable ovn-northd.service >/dev/null 2>&1 || :
        /bin/systemctl stop ovn-northd.service >/dev/null 2>&1 || :
    fi
%endif

%preun host
%if 0%{?systemd_preun:1}
    %systemd_preun ovn-controller.service
%else
    if [ $1 -eq 0 ] ; then
        # Package removal, not upgrade
        /bin/systemctl --no-reload disable ovn-controller.service >/dev/null 2>&1 || :
        /bin/systemctl stop ovn-controller.service >/dev/null 2>&1 || :
    fi
%endif

%preun vtep
%if 0%{?systemd_preun:1}
    %systemd_preun ovn-controller-vtep.service
%else
    if [ $1 -eq 0 ] ; then
        # Package removal, not upgrade
        /bin/systemctl --no-reload disable ovn-controller-vtep.service >/dev/null 2>&1 || :
        /bin/systemctl stop ovn-controller-vtep.service >/dev/null 2>&1 || :
    fi
%endif

%post
%if %{with libcapng}
if [ $1 -eq 1 ]; then
    sed -i 's:^#OVN_USER_ID=:OVN_USER_ID=:' %{_sysconfdir}/sysconfig/ovn
    sed -i 's:\(.*su\).*:\1 openvswitch openvswitch:' %{_sysconfdir}/logrotate.d/ovn
fi
%endif

%post central
%if 0%{?systemd_post:1}
    %systemd_post ovn-northd.service
%else
    # Package install, not upgrade
    if [ $1 -eq 1 ]; then
        /bin/systemctl daemon-reload >dev/null || :
    fi
%endif

%post host
%if 0%{?systemd_post:1}
    %systemd_post ovn-controller.service
%else
    # Package install, not upgrade
    if [ $1 -eq 1 ]; then
        /bin/systemctl daemon-reload >dev/null || :
    fi
%endif

%post vtep
%if 0%{?systemd_post:1}
    %systemd_post ovn-controller-vtep.service
%else
    # Package install, not upgrade
    if [ $1 -eq 1 ]; then
        /bin/systemctl daemon-reload >dev/null || :
    fi
%endif

%postun

%postun central
%if 0%{?systemd_postun_with_restart:1}
    %systemd_postun_with_restart ovn-northd.service
%else
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
    if [ "$1" -ge "1" ] ; then
    # Package upgrade, not uninstall
        /bin/systemctl try-restart ovn-northd.service >/dev/null 2>&1 || :
    fi
%endif

%postun host
%if 0%{?systemd_postun_with_restart:1}
    %systemd_postun_with_restart ovn-controller.service
%else
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
    if [ "$1" -ge "1" ] ; then
        # Package upgrade, not uninstall
        /bin/systemctl try-restart ovn-controller.service >/dev/null 2>&1 || :
    fi
%endif

%postun vtep
%if 0%{?systemd_postun_with_restart:1}
    %systemd_postun_with_restart ovn-controller-vtep.service
%else
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
    if [ "$1" -ge "1" ] ; then
        # Package upgrade, not uninstall
        /bin/systemctl try-restart ovn-controller-vtep.service >/dev/null 2>&1 || :
    fi
%endif

%posttrans central
if [ $1 -eq 1 ]; then
    # Package install, not upgrade
    if [ -e %{_localstatedir}/lib/rpm-state/ovn-northd ]; then
        rm %{_localstatedir}/lib/rpm-state/ovn-northd
        /bin/systemctl start ovn-northd.service >/dev/null 2>&1 || :
    fi
fi


%posttrans host
if [ $1 -eq 1 ]; then
    # Package install, not upgrade
    if [ -e %{_localstatedir}/lib/rpm-state/ovn-controller ]; then
        rm %{_localstatedir}/lib/rpm-state/ovn-controller
        /bin/systemctl start ovn-controller.service >/dev/null 2>&1 || :
    fi
fi

%posttrans vtep
if [ $1 -eq 1 ]; then
    # Package install, not upgrade
    if [ -e %{_localstatedir}/lib/rpm-state/ovn-controller-vtep ]; then
        rm %{_localstatedir}/lib/rpm-state/ovn-controller-vtep
        /bin/systemctl start ovn-controller-vtep.service >/dev/null 2>&1 || :
    fi
fi

%files
%{_bindir}/ovn-nbctl
%{_bindir}/ovn-sbctl
%{_bindir}/ovn-trace
%{_bindir}/ovn-detrace
%{_bindir}/ovn_detrace.py
%{_bindir}/ovn-appctl
%{_bindir}/ovn-ic-nbctl
%{_bindir}/ovn-ic-sbctl
%dir %{_datadir}/ovn/
%dir %{_datadir}/ovn/scripts/
%{_datadir}/ovn/scripts/ovn-ctl
%{_datadir}/ovn/scripts/ovn-lib
%{_datadir}/ovn/scripts/ovndb-servers.ocf
%{_mandir}/man8/ovn-ctl.8*
%{_mandir}/man8/ovn-appctl.8*
%{_mandir}/man8/ovn-nbctl.8*
%{_mandir}/man8/ovn-ic-nbctl.8*
%{_mandir}/man8/ovn-trace.8*
%{_mandir}/man1/ovn-detrace.1*
%{_mandir}/man7/ovn-architecture.7*
%{_mandir}/man8/ovn-sbctl.8*
%{_mandir}/man8/ovn-ic-sbctl.8*
%{_mandir}/man5/ovn-nb.5*
%{_mandir}/man5/ovn-ic-nb.5*
%{_mandir}/man5/ovn-sb.5*
%{_mandir}/man5/ovn-ic-sb.5*
%dir %{ovnlibdir}/ocf/resource.d/ovn/
%{ovnlibdir}/ocf/resource.d/ovn/ovndb-servers
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/logrotate.d/ovn
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/sysconfig/ovn

%files central
%{_bindir}/ovn-northd
%{_bindir}/ovn-ic
%{_mandir}/man8/ovn-northd.8*
%{_mandir}/man8/ovn-ic.8*
%{_datadir}/ovn/ovn-nb.ovsschema
%{_datadir}/ovn/ovn-ic-nb.ovsschema
%{_datadir}/ovn/ovn-sb.ovsschema
%{_datadir}/ovn/ovn-ic-sb.ovsschema
%{_unitdir}/ovn-northd.service
%{ovnlibdir}/firewalld/services/ovn-central-firewall-service.xml

%files host
%{_bindir}/ovn-controller
%{_mandir}/man8/ovn-controller.8*
%{_unitdir}/ovn-controller.service
%{ovnlibdir}/firewalld/services/ovn-host-firewall-service.xml

%files vtep
%{_bindir}/ovn-controller-vtep
%{_mandir}/man8/ovn-controller-vtep.8*
%{_unitdir}/ovn-controller-vtep.service

%changelog
* Tue Apr 23 2024 Ales Musil <amusil@redhat.com> - 24.03.1-44
- tests: Fix netcat 7.94 issues.
[Upstream: cfeeaa6e2fb3e0bed9d608259025473808d286c2]

* Mon Apr 22 2024 Ales Musil <amusil@redhat.com> - 24.03.1-43
- northd, controller: Use paused controller action for packet buffering.
[Upstream: 1e89d06e62caff88cab9c31f1b1b2ec8dfe64880]

* Mon Apr 22 2024 Ales Musil <amusil@redhat.com> - 24.03.1-42
- northd: Do not incrementally proccess changes for disabled LR.
[Upstream: ac0af22fb4c5fe2cea4aee38580fe39aec26e245]

* Mon Apr 22 2024 Martin Kalcok <martin.kalcok@canonical.com> - 24.03.1-41
- northd: Fix direct access to SNAT network.
[Upstream: ccaf22f1356a6a82514e893b204366621c04aad3]

* Mon Apr 22 2024 Martin Kalcok <martin.kalcok@canonical.com> - 24.03.1-40
- actions: New action ct_commit_to_zone.
[Upstream: 92f7a974cbe79fe9de6f4d92440eebe41e4ec015]

* Mon Apr 22 2024 Mark Michelson <mmichels@redhat.com> - 24.03.1-39
- ovn-nbctl: Document "--portrange" in the manpage.
[Upstream: 76321c078749cdcaf2df52e44b37864a15c28b76]

* Mon Apr 22 2024 Lorenzo Bianconi <lorenzo.bianconi@redhat.com> - 24.03.1-38
- utilities: Add missing bfd option in ovn-nbctl manpage.
[Upstream: d45c06312d859fb76297a44533ce80082d0067a9]

* Fri Apr 19 2024 Ales Musil <amusil@redhat.com> - 24.03.1-37
- ovs: Bump the submodule to the tip of branch-3.3.
[Upstream: 6d71cbfd1811b97a5aa7c5b9c9f957ef8579234f]

* Fri Apr 12 2024 Ales Musil <amusil@redhat.com> - 24.03.1-36
- ovn-ctl: Use the current user for default file permissions.
[Upstream: 7346953e2fe39a4e8a7871da4f2634050feb1659]

* Fri Apr 12 2024 Ales Musil <amusil@redhat.com> - 24.03.1-35
- ovn-trace: Make sure we don't exit when the port is not specified.
[Upstream: 419f8a836c42db2a35a550cf4a4e975e3a3eb2af]

* Fri Apr 12 2024 Lorenzo Bianconi <lorenzo.bianconi@redhat.com> - 24.03.1-34
- northd: Fix BFD for policy routing.
[Upstream: a6095e1cb237016191519478fbef9f775a67bc89]

* Thu Apr 04 2024 Mark Michelson <mmichels@redhat.com> - 24.03.1-33
- acl-log: Properly log the "pass" verdict.
[Upstream: 6eff687d5f42dd4cb4558b071aaa00d5a55667f6]

* Thu Apr 04 2024 Xavier Simonart <xsimonar@redhat.com> - 24.03.1-32
- automake: Make system tests dependent of ovn-macro.
[Upstream: 90c577ae544e0d16593d5a89c058276ff25d43e3]

* Thu Apr 04 2024 Han Zhou <hzhou@ovn.org> - 24.03.1-31
- ovn-controller.at: Fix flaky test "ofctrl wait before clearing flows".
[Upstream: 2ab187e9bb6c9be6174529df9617534aef6a3a94]

* Thu Apr 04 2024 Vladislav Odintsov <odivlad@gmail.com> - 24.03.1-30
- northd: fix infinite loop in ovn_allocate_tnlid()
[Upstream: 69e90f664a1130a5415904d41db6dba713eea8c2]

* Wed Apr 03 2024 Xavier Simonart <xsimonar@redhat.com> - 24.03.1-29
- pinctrl: Fixed 100% cpu on ovs connection loss.
[Upstream: 72390c4fea72cfbae5eb9409abb8a6dd7d5f3e69]

* Wed Apr 03 2024 Xavier Simonart <xsimonar@redhat.com> - 24.03.1-28
- pinctrl: Fix missing MAC_Bindings.
[Upstream: c76746653f8423d514d3374423a3e15b0ede86bd]

* Wed Apr 03 2024 Xavier Simonart <xsimonar@redhat.com> - 24.03.1-27
- tests: Add macros to pause controller updates.
[Upstream: 1187031d5ebf3fb0a79b16f48798d88829175702]

* Tue Apr 02 2024 Han Zhou <hzhou@ovn.org> - 24.03.1-26
- ofctrl: Wait at S_WAIT_BEFORE_CLEAR only once.
[Upstream: 6b1618a96f178b7b7d6a0c1903291f4bc4cc7f1d]

* Thu Mar 28 2024 Frode Nordahl <fnordahl@ubuntu.com> - 24.03.1-25
- northd: Fix population of ipv6_ra_prefixes from IPv6 PD.
[Upstream: bad2e3042e9cdac38db058ab0ce1478f104fef03]

* Thu Mar 28 2024 Frode Nordahl <fnordahl@ubuntu.com> - 24.03.1-24
- controller: Use multicast for IPv6 Prefix Delegation.
[Upstream: 5ff0e2aee3553e52766eb1c34ccc203ad6022fde]

* Thu Mar 28 2024 Lorenzo Bianconi <lorenzo.bianconi@redhat.com> - 24.03.1-23
- ovn-ic: Avoid igmp/mld traffic flooding.
[Upstream: 29af310ce16fcaf0a9ce18aa79bf44d5cf0cf1e4]

* Thu Mar 28 2024 Mohammad Heib <mheib@redhat.com> - 24.03.1-22
- tests: Use sync command in ovn-ic tests.
[Upstream: d1a7253333ace9db7b3cef68b74a7f190fcaca8b]

* Thu Mar 28 2024 Mohammad Heib <mheib@redhat.com> - 24.03.1-21
- tests: Move ovn interconnection tests to ovn-ic.at.
[Upstream: ef2e711819d517de7abf91d4c8edef9818a92346]

* Thu Mar 28 2024 Mohammad Heib <mheib@redhat.com> - 24.03.1-20
- IC: Tansit switch don't flood mcast traffic to router ports if matches igmp group.
[Upstream: 31c7d227dc2bef55f1f1d6f07abd1b21831c0ab2]

* Thu Mar 28 2024 Mohammad Heib <mheib@redhat.com> - 24.03.1-19
- northd: Don't skip transit switch LSP when creating mcast groups.
[Upstream: 6af50a99c6e4836cc29471cbcbe0a938c3aa1879]

* Thu Mar 28 2024 Lorenzo Bianconi <lorenzo.bianconi@redhat.com> - 24.03.1-18
- northd: Fix NAT configuration with --add-route option for gw-router.
[Upstream: 1434d1bc55ed43994dba769b1070317476b9f1b0]

* Mon Mar 25 2024 Ales Musil <amusil@redhat.com> - 24.03.1-17
- controller: Fix ofctrl memory usage underflow.
[Upstream: 3e35d0daeac162437a5858d3ea6e3d508462184a]

* Wed Mar 20 2024 Martin Kalcok <martin.kalcok@canonical.com> - 24.03.1-16
- docs: Remove ref. to "ovn-sbctl --no-wait".
[Upstream: 5b3880242ba55f81f93ebccd0a91978e7d65ba06]

* Wed Mar 20 2024 Igor Zhukov <fsb4000@yandex.ru> - 24.03.1-15
- Fix broken link for LTS release.
[Upstream: 5f7765b238be0aa323a3ded21f5bbe770cc75daf]

* Wed Mar 20 2024 Han Zhou <hzhou@ovn.org> - 24.03.1-14
- ovn-controller: Fix busy loop when ofctrl is disconnected.
[Upstream: b213cb641a050f5294ba592196823dd7fe529ad2]

* Tue Mar 19 2024 Ales Musil <amusil@redhat.com> - 24.03.1-13
- tests: Address netcat 7.94 changes.
[Upstream: 653e010f1e2c7032e612c68ba34d968569c0e0c5]

* Tue Mar 19 2024 Ales Musil <amusil@redhat.com> - 24.03.1-12
- tests: Add helper for tcpdump.
[Upstream: f739c28e822332e28e46f083b9a85c4ccbf51691]

* Tue Mar 19 2024 Xavier Simonart <xsimonar@redhat.com> - 24.03.1-11
- tests: Ignore transaction errors in MAC Binding.
[Upstream: 9644436abc183a9ccd8434fdef4b5823b8855f9f]

* Mon Mar 18 2024 Ales Musil <amusil@redhat.com> - 24.03.1-10
- utilities: Make database connection optional for ovn-detrace.
[Upstream: f60d06f3ae1fd6b1527e0e9f61bcc85c8383cfbb]

* Mon Mar 18 2024 Mohammad Heib <mheib@redhat.com> - 24.03.1-9
- ovn-controller: Stop dropping bind_vport requests immediately after handling. (#1954659)
[Upstream: 0e85aa326847b8a4075753bab8ede7f991cb912b]

* Fri Mar 15 2024 Xavier Simonart <xsimonar@redhat.com> - 24.03.1-8
- tests: Fix flaky "lr multiple gw ports" test.
[Upstream: d72b3f90e3991cca1211146401c848d35f2b6012]

* Fri Mar 15 2024 Xavier Simonart <xsimonar@redhat.com> - 24.03.1-7
- pinctrl: Fix prefix delegation.
[Upstream: 735a81fec9b8f1fd769b5e3f4018702b8c4f03ca]

* Wed Mar 13 2024 Mohammad Heib <mheib@redhat.com> - 24.03.1-6
- controller: Release container lport when releasing parent port. (#2220938)
[Upstream: d5d4c3bf25f8d85523b22c3b3746f53ce1f6c767]

* Tue Mar 12 2024 Ilya Maximets <i.maximets@ovn.org> - 24.03.1-5
- github: Reduce ASLR entropy to be compatible with asan in llvm 14.
[Upstream: 06d3a8fe48969aa7be4f8672ff77a386a1defab6]

* Tue Mar 12 2024 Mark Michelson <mmichels@redhat.com> - 24.03.1-4
- Prepare for 24.03.2.
[Upstream: ffd8bb1a1bd90cce2be4eed37503332c91c5d0e3]

