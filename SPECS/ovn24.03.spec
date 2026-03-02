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
Version: 24.03.7
Release: 62%{?commit0:.%{date}git%{shortcommit0}}%{?dist}
Provides: openvswitch%{pkgver}-ovn-common = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes: openvswitch%{pkgver}-ovn-common < 2.11.0-1

# Nearly all of openvswitch is ASL 2.0.  The bugtool is LGPLv2+, and the
# lib/sflow*.[ch] files are SISSL
License: ASL 2.0 and LGPLv2+ and SISSL

%define ovncommit 15839d7cb85c2dbdfe6e36ed9cf8efdc27ed82ca

# Always pull an upstream release, since this is what we rebase to.
Source: https://github.com/ovn-org/ovn/archive/%{ovncommit}.tar.gz#/ovn-%{version}.tar.gz

%define ovscommit 785a89b48db6803a2ce44e28e76d8a0025be1803
%define ovsshortcommit 785a89b

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

%if 0%{?rhel} >= 9
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
%{_bindir}/ovn-debug
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
%{_mandir}/man8/ovn-debug.8*
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
* Sat Feb 28 2026 Mark Michelson <mmichels@redhat.com> - 24.03.7-56
- Update dummy commit
[Upstream: 2ec451c9ce20c4d4555c8a972d49316a9fa0dabc]

* Thu Feb 26 2026 Ales Musil <amusil@redhat.com> - 24.03.7-55
- northd: Do not fully parse LSP port security. (#FDP-3245)
[Upstream: 3024718cfec061cbea310f1c8553c3d9c226f107]

* Wed Feb 25 2026 MJ Ponsonby <mj.ponsonby@canonical.com> - 24.03.7-54
- tests: Sort output in flaky s390x tests.
[Upstream: f6556dc14118eabe9196b3a14d5804916a83cfca]

* Mon Feb 23 2026 Erlon R. Cruz <erlon@canonical.com> - 24.03.7-53
- controller: ACL correctly handles fragmented traffic. (#FDP-1992)
[Upstream: 8fbda461fdc03640e56b89fab1b6973568deba53]

* Mon Feb 23 2026 Dumitru Ceara <dceara@redhat.com> - 24.03.7-52
- utilities/containers/*/Dockerfile: Install dhclient.
[Upstream: a9982a90ae4861c4101a9bbae1be149ce3df04ef]

* Wed Feb 18 2026 Ales Musil <amusil@redhat.com> - 24.03.7-51
- controller: Add option to make port security compliant with RFC 9568. (#FDP-2979)
[Upstream: ef8f5c1ac63e8094eaf13507013e310991db45a2]

* Wed Feb 18 2026 Ales Musil <amusil@redhat.com> - 24.03.7-50
- ovn-util: Add helper for parsing and working with masked MACs.
[Upstream: 69a7eee0e42f4ff60531b43a85bf7bb6534478b3]

* Wed Feb 18 2026 Ales Musil <amusil@redhat.com> - 24.03.7-49
- lflow: Change the port security parsing log from INFO to WARN.
[Upstream: 3c581c038c92a1aaab52b8aea4571597c802ee19]

* Tue Feb 17 2026 Lorenzo Bianconi <lorenzo.bianconi@redhat.com> - 24.03.7-48
- northd: Do not forward unknown ether type to router ports. (#FDP-1908)
[Upstream: fac50ea32813e5253e550875ec7bbcaf2c8c2715]

* Mon Feb 16 2026 Dumitru Ceara <dceara@redhat.com> - 24.03.7-47
- inc-proc-eng: Assert that node states are in the right range.
[Upstream: d80e5570ef94d8a6f0d3ee484e191884c505ce0f]

* Mon Feb 09 2026 Ales Musil <amusil@redhat.com> - 24.03.7-46
- tests: Replace wget with curl for failing commands.
[Upstream: 4ebf80ec9263431781e03e5615042c6f1217e8d4]

* Mon Feb 09 2026 Martin Morgenstern <martin.morgenstern@cloudandheat.com> - 24.03.7-45
- controller: Prevent crash when SB_Global is empty.
[Upstream: 6eddcd3fe8124fa18f5f7e9e0a0515fecfa7ddb8]

* Mon Feb 09 2026 Ilya Maximets <i.maximets@ovn.org> - 24.03.7-44
- tests: Don't use potentially unreachable IPs for IPFIX.
[Upstream: d04b400d0b770657bf344a317d6256aca050ddc4]

* Mon Feb 09 2026 Ales Musil <amusil@redhat.com> - 24.03.7-43
- ci: Increase the disk size for CirrusCI VM.
[Upstream: 1d2c3bb3414fedb29456013896a0dae2c9e84774]

* Thu Feb 05 2026 Ihar Hrachyshka <ihar.hrachyshka@gmail.com> - 24.03.7-42
- tests: Use `command -v` instead of `which`.
[Upstream: 28321487a9ac2c8868646db92eeb201e93641050]

* Thu Feb 05 2026 Ales Musil <amusil@redhat.com> - 24.03.7-41
- lflow: Add missing match on eth.src for ND port security.
[Upstream: 7d0b7f11b7913b0e767d418fc853f15d65d209b5]

* Mon Feb 02 2026 Lorenzo Bianconi <lorenzo.bianconi@redhat.com> - 24.03.7-40
- northd: Do not send ICMP packet too big for multicast traffic. (#FDP-2652)
[Upstream: 27f9a0ac551469c68ae1ea6881b191deec7cad3e]

* Fri Jan 23 2026 Ales Musil <amusil@redhat.com> - 24.03.7-39
- lflow: Enable default drop for ND NS in with port security enabled.
[Upstream: 4613d30139d8d5d0d9b23ae234adfab40d91f9af]

* Thu Jan 22 2026 Alexandra Rukomoinikova <arukomoinikova@k2.cloud> - 24.03.7-38
- northd: Improvements of ICMP TTL exceeded behavior. (#FDP-2870)
[Upstream: b56d5097c4b04a5f2199141b26989171a813d86c]

* Tue Jan 20 2026 Xavier Simonart <xsimonar@redhat.com> - 24.03.7-37
- tests: Fix "ACL log_related" system-test.
[Upstream: fe8e43d0085a80964e64f87430362c695185cb7a]

* Wed Jan 14 2026 jun.gu <jun.gu@easystack.cn> - 24.03.7-36
- controller: Add missing nw_ttl field to match against legit NAs.
[Upstream: ff36db4fd92359ff6fac00b789e0403fbe62e8b2]

* Tue Jan 13 2026 Ales Musil <amusil@redhat.com> - 24.03.7-35
- pinctrl: Avoid unaligned access to dhcpv6 options.
[Upstream: bcd0c5a8558cbf354f9f6547c17b55419430b1ba]

* Tue Jan 13 2026 Ales Musil <amusil@redhat.com> - 24.03.7-34
- controller-vtep: Properly free the ovn version at the end.
[Upstream: 5ca819d7e35e94a7b2ef08829e5826255e8ac542]

* Tue Jan 13 2026 Ales Musil <amusil@redhat.com> - 24.03.7-33
- binding: Prevent maybe-uninitialized error for queue variable.
[Upstream: b08ecb8f476d0052322de2e375ac79b9917691ec]

* Tue Jan 06 2026 Ales Musil <amusil@redhat.com> - 24.03.7-32
- northd: Do not assign requested tunnel key to the derived CR port. (#FDP-2764)
[Upstream: 083d9fd20d84235fd1c69033031c53a33149ae7d]

* Thu Dec 18 2025 Xie Liu <liushyshy@gmail.com> - 24.03.7-31
- tests: Fix ACL direction consistency.
[Upstream: 9e3942ed49eea8518b01324e2ef4cb546d4d88d8]

* Thu Dec 18 2025 Xie Liu <liushyshy@gmail.com> - 24.03.7-30
- controller: CT zone allocation for DGP LSPs enabled ACL.
[Upstream: 73327991d684534ee964446cd9a6d7a888a93fd5]

* Tue Dec 16 2025 Ihar Hrachyshka <ihar.hrachyshka@gmail.com> - 24.03.7-29
- tests: Ignore AT_CHECK stderr for `grep ... | grep -q`.
[Upstream: b867e7111b4e0a75fd16f2ff5f58debfff50a2b8]

* Tue Dec 16 2025 Frode Nordahl <fnordahl@ubuntu.com> - 24.03.7-28
- tests: Fix test for tc rounding behavior change.
[Upstream: ced8157fc9a6a98de44657c89cf42402ae5bf9ae]

* Thu Dec 11 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.7-27
- tests/ovn-ic: Add missing OVN_CLEANUP_IC call.
[Upstream: a9d2ec49dbccd14432f984784ed1e2709f02461b]

* Thu Dec 11 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.7-26
- tests/ovn-controller: Add missing cleanup.
[Upstream: 91e14feec77d03368207c99f384d37d23003b1aa]

* Thu Dec 11 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.7-25
- tests/ovn: Add missing partial cleanups.
[Upstream: a238fd1deae94a89b19abfdbca62af68cd4dcf6d]

* Thu Dec 11 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.7-24
- tests/ovn: Add missing OVN_CLEANUP calls.
[Upstream: 91080a0a5487232819b7752d799ebf23594fab7d]

* Thu Dec 11 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.7-23
- tests: Add OVN_CLEANUP_DBS and use it in tests that already stopped northd.
[Upstream: 369276c1c3959d8646e120cd6a620c30b53f2420]

* Thu Dec 11 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.7-22
- tests/ovn-controller-vtep: Remove unused test net.
[Upstream: 02ead19698d92b0bf555018050a491ee09bc9f48]

* Thu Dec 11 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.7-21
- tests/ovn-controller-vtep: Add missing OVN_CONTROLLER_VTEP_STOP calls.
[Upstream: de5cac684af53038c575da3ec5f90975a7ee8c1c]

* Thu Dec 11 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.7-20
- tests: Add missing OVN_CLEANUP_NORTHD calls.
[Upstream: 64dfd08c8c1ed5c6f0deffb97a2198482a91374f]

* Mon Dec 08 2025 Ihar Hrachyshka <ihar.hrachyshka@gmail.com> - 24.03.7-19
- tests: Require scapy for 'IP packet buffering'.
[Upstream: 9331d8076a2de2afc0e2dbc19043ca5de37ac510]

* Thu Dec 04 2025 Ilya Maximets <i.maximets@ovn.org> - 24.03.7-18
- ovs: Bump to include fix for non-existent rows in idl uuid lookup. (#FDP-2807)
[Upstream: 18c635009943866ed39dc82b06a4f636e5d0f389]

* Thu Dec 04 2025 Ales Musil <amusil@redhat.com> - 24.03.7-17
- northd: Skip transient SB datapath IDL records. (#FDP-2784)
[Upstream: db72a15e55fe1b7b672fdf35aca8506eb1c20144]

* Thu Dec 04 2025 Ales Musil <amusil@redhat.com> - 24.03.7-16
- pinctrl: Make sure we can learn IGMP groups only on switches.
[Upstream: 423485a3614fc013233218fe36442089c02d1651]

* Tue Dec 02 2025 Xavier Simonart <xsimonar@redhat.com> - 24.03.7-15
- pinctrl: Fix Service_Monitor reported online very slowly. (#FDP-2649)
[Upstream: 80aede654f7226ccfebcbcd93c12ad05852639ee]

* Tue Dec 02 2025 Xavier Simonart <xsimonar@redhat.com> - 24.03.7-14
- pinctrl: Fix Service_Monitor status change not updated.
[Upstream: f458fa380b6202dea2cc44f870733b05947bca5b]

* Tue Dec 02 2025 Xavier Simonart <xsimonar@redhat.com> - 24.03.7-13
- pinctrl: Speed up Service_Monitor updates.
[Upstream: 3ecaa269f2468c56eb0ed4227f934a5484162732]

* Tue Dec 02 2025 Xavier Simonart <xsimonar@redhat.com> - 24.03.7-12
- pinctrl: Avoid waking-up pinctrl thread too often.
[Upstream: e33d4450afbc764619ab8dc3ea2480341ab43878]

* Thu Nov 20 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.7-11
- tests: Ensure all central components stop at the end of the test.
[Upstream: b8c618a89d8fb6b6ad993d5e1cf1d4c602807206]

* Thu Nov 20 2025 Ales Musil <amusil@redhat.com> - 24.03.7-10
- pinctrl: Prevent leak of mac_binding and fdb struct.
[Upstream: 3169ba2204f3049af5162e8a2bc87b13dc6494e4]

* Wed Nov 19 2025 Mark Michelson <mmichels@redhat.com> - 24.03.7-9
- Prepare for 24.03.8.
[Upstream: f3c31c02b44cf0b4cbb017e1ce1cd800d9fe8d99]

