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
Version: 24.03.5
Release: 88%{?commit0:.%{date}git%{shortcommit0}}%{?dist}
Provides: openvswitch%{pkgver}-ovn-common = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes: openvswitch%{pkgver}-ovn-common < 2.11.0-1

# Nearly all of openvswitch is ASL 2.0.  The bugtool is LGPLv2+, and the
# lib/sflow*.[ch] files are SISSL
License: ASL 2.0 and LGPLv2+ and SISSL

%define ovncommit f5a4704f9be07f7c29e45bb15e7e71126c6fea4a

# Always pull an upstream release, since this is what we rebase to.
Source: https://github.com/ovn-org/ovn/archive/%{ovncommit}.tar.gz#/ovn-%{version}.tar.gz

%define ovscommit 9f1d6a88e68bdbb3ad808104e24f65c5231d00bf
%define ovsshortcommit 9f1d6a8

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
* Wed May 21 2025 Numan Siddique <numans@ovn.org> - 24.03.5-88
- northd: Fix potential crash when creating chassisredirect port.
[Upstream: fcc9ea92f00aba00d888630b72b51570323941d8]

* Wed May 21 2025 Xavier Simonart <xsimonar@redhat.com> - 24.03.5-87
- multinode: Fix test "ovn multinode NAT ...".
[Upstream: ccec2e18c08aec2bdb196987451a7b1d3a39b5fd]

* Wed May 21 2025 Numan Siddique <numans@ovn.org> - 24.03.5-86
- Add support for centralize routing for distributed gw ports. (#FDP-1417)
[Upstream: 04533ea43adefd352879dcb9d2cd2b9e4f168525]

* Wed May 21 2025 Numan Siddique <numans@ovn.org> - 24.03.5-85
- northd: Refactor chassisresident port checking.
[Upstream: d44c4f6778ae1e233c9a378e3f9b818f2e49da18]

* Wed May 21 2025 Ihar Hrachyshka <ihrachys@redhat.com> - 24.03.5-84
- northd: Remove unused nbrp arg in ls_port_reinit.
[Upstream: 28330203cfad3cffbab55ce099b548de99cdeec5]

* Wed May 21 2025 Ihar Hrachyshka <ihrachys@redhat.com> - 24.03.5-83
- northd: Remove unused `sb` arg in ls_port_create.
[Upstream: 474ba3837d0b9ce8b2ee35220ee32df0e9335302]

* Wed May 21 2025 Ihar Hrachyshka <ihrachys@redhat.com> - 24.03.5-82
- northd: Don't create pb in ls_port_init too early.
[Upstream: b10bae3905d5a9d042d5b57cb281547970e592d4]

* Wed May 21 2025 Ihar Hrachyshka <ihrachys@redhat.com> - 24.03.5-81
- tests: Correct tunnel ids exhaustion scenario.
[Upstream: 5bd13c0056d44b606f258b0f024ed4daa64aa0bc]

* Wed May 21 2025 Ihar Hrachyshka <ihrachys@redhat.com> - 24.03.5-80
- northd: Don't detach op->list when it wasn't used.
[Upstream: 6f316554dbeccde9aa6a29d62408012e19866ae2]

* Wed May 21 2025 Ihar Hrachyshka <ihrachys@redhat.com> - 24.03.5-79
- northd: Don't cleanup op in ovn_port_allocate_key.
[Upstream: a375b2d7205e7e6efc3d0096d1ddf61347c0bd89]

* Wed May 21 2025 Numan Siddique <numans@ovn.org> - 24.03.5-78
- northd: Don't reparse lport's addresses while adding L2_LKUP flows.
[Upstream: a9e8d8931c12d194efe1a15ac96536b100fcfa40]

* Tue May 20 2025 Alexandra Rukomoinikova <arukomoinikova@k2.cloud> - 24.03.5-77
- cksum: Added checksum for pipeline stages.
[Upstream: 07352c8a4432166988c45fefcf32c6e180f75ecd]

* Tue May 20 2025 Lucas Vargas Dias \(Dev - MGC - SDN\) <lucas.vdias@luizalabs.com> - 24.03.5-76
- ic: Fix lrp and lsp orphan route learn or advertise.
[Upstream: e914b50254a6068bf9f8fd25f823043d22f0e41f]

* Wed May 14 2025 Ales Musil <amusil@redhat.com> - 24.03.5-75
- ci: Add permanent fix for /etc/hosts file.
[Upstream: 1995bb1edb037f48496b2e2d9460f3695bed7d76]

* Mon May 12 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.5-74
- pinctrl: Remove useless volatile qualifier.
[Upstream: 0ccb896cba1e5f02b26f450d0c708f0eedc5f592]

* Tue May 06 2025 Mark Michelson <mmichels@redhat.com> - 24.03.5-73
- northd: Set REGBIT_CONNTRACK_COMMIT earlier. (#FDP-1321)
[Upstream: c26b6a3b260b9412b8b71413a63d6a676bb6a4e6]

* Tue Apr 29 2025 Ales Musil <amusil@redhat.com> - 24.03.5-72
- contoller, northd: Limit number of claims for virtual ports. (#FDP-443)
[Upstream: 8e825d936cd8f610870d641f488ce30e1d995cdc]

* Tue Apr 29 2025 Ales Musil <amusil@redhat.com> - 24.03.5-71
- controller: Remove only commited virtual port binding requests.
[Upstream: 60b58842eddd009c30db9003ce68fafb4c5f14f6]

* Tue Apr 29 2025 Ales Musil <amusil@redhat.com> - 24.03.5-70
- inc-engine: Adjust the force recompute API. (#FDP-753)
[Upstream: c5feb5025a0fd04b72b7888fea3d3cb0eba9ed36]

* Tue Apr 29 2025 Mark Michelson <mmichels@redhat.com> - 24.03.5-69
- Add ovn_smap_get_llong().
[Upstream: 187f900a5a071b8dddae6790539d829f14623d65]

* Thu Apr 24 2025 Felix Huettner <felix.huettner@stackit.cloud> - 24.03.5-68
- tests: Fix racy hard_age value.
[Upstream: 7c1821f176f625544e1f833a71c618a908f71ce6]

* Wed Apr 23 2025 Ales Musil <amusil@redhat.com> - 24.03.5-67
- northd: Fix the match not being cleared inside the loop.
[Upstream: 7071fef507482e61ad86e3ee862dea00f2f8057b]

* Wed Apr 23 2025 Xavier Simonart <xsimonar@redhat.com> - 24.03.5-66
- northd: Fix pmtud related issues. (#FDP-685 FDP-1149)
[Upstream: 239e9783b70e1e49b9eeacece108efb9d7210d17]

* Wed Apr 23 2025 Ales Musil <amusil@redhat.com> - 24.03.5-65
- tests: Fix flaky PMTUD flows test.
[Upstream: e2fbac23a71cfa44f3a37d40a24ecaa946f9db49]

* Wed Apr 23 2025 Lorenzo Bianconi <lorenzo.bianconi@redhat.com> - 24.03.5-64
- northd: Fix pmtud for non routed traffic. (#FDP-524 FDP-362)
[Upstream: b54f6b0dbba919a2f02d8f462e656aa4d33949a3]

* Wed Apr 23 2025 Rosemarie O'Riorden <rosemarie@redhat.com> - 24.03.5-63
- ovn-nb: Improve docs for nbctl --template lb-add. (#FDP-1066)
[Upstream: 22c9e5866b3790b48adbc22691c1b644400433cd]

* Wed Apr 23 2025 Martin Morgenstern <martin.morgenstern@cloudandheat.com> - 24.03.5-62
- ovn-nbctl.8: Document the "--route-table" option.
[Upstream: 948663deea8875e6cccec1ee154bf7926cb4d22f]

* Wed Apr 23 2025 Martin Morgenstern <martin.morgenstern@cloudandheat.com> - 24.03.5-61
- ovn-architecture.7: Fix outdated nb_cfg description.
[Upstream: 3ec68095670eb589dab3cf7b4c66c445493bcf58]

* Tue Apr 15 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.5-60
- northd: Avoid matching on ct_state.dnat in logical flows. (#FDP-1271)
[Upstream: da13d4af9510052d1f0a5fc625922e85b0ba97c6]

* Tue Apr 15 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.5-59
- lib: northd: Add a new ct-state-save feature flag.
[Upstream: 48c6452cf8759ee74dd7a889879026593f8d213d]

* Tue Apr 15 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.5-58
- lib: ovn-controller: Add a new ct_state_save() logical action.
[Upstream: 17ced0a3ac162d42a20085ac7edd7adc611fd5d9]

* Tue Apr 08 2025 Numan Siddique <numans@ovn.org> - 24.03.5-57
- northd: Limit flooding the self originated neigh disc packets.
[Upstream: 655381c6abd15ded15f67f49eaa4aba922a14866]

* Thu Apr 03 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.5-56
- northd: Fix network_id computation for IPv6 LRP networks.
[Upstream: e8fa98cfa54e029d2a77ce3349b97b4108dd01ed]

* Thu Apr 03 2025 Rosemarie O'Riorden <rosemarie@redhat.com> - 24.03.5-55
- ovn-nbctl: Add --template option for lb-add. (#FDP-1050)
[Upstream: 6fabeae65b573e8264b1ea4ccd14f0eee27a0d4b]

* Thu Apr 03 2025 Frode Nordahl <fnordahl@ubuntu.com> - 24.03.5-54
- tests: Use scapy contrib BFD implementation.
[Upstream: f1f19c00b67fba839dc17a1de7df94a4202576fd]

* Thu Apr 03 2025 Ales Musil <amusil@redhat.com> - 24.03.5-53
- controller, northd: Add command to enable time warp.
[Upstream: cf351abcb67ff0e227faf72635d9f62ebf0f6e55]

* Wed Apr 02 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.5-52
- statctrl: Add visibility into how long each stats node run lasts.
[Upstream: b02bb1b3162504b18d6212d6d043b3ea200cd324]

* Tue Apr 01 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.5-51
- docs: Fix up stage-hint ovn-sb documentation.
[Upstream: f911084fb157d5a013103ba5439b22b99cb104e7]

* Tue Apr 01 2025 Lorenzo Bianconi <lorenzo.bianconi@redhat.com> - 24.03.5-50
- northd: Do not drop ip traffic with destination vip expressed via template vars. (#FDP-988)
[Upstream: 05e0b1f6046e2672018aaadf314f58a21d0806e1]

* Tue Apr 01 2025 Rosemarie O'Riorden <rosemarie@redhat.com> - 24.03.5-49
- northd: Use next-hop network for SNAT when lb_force_snat_ip=router_ip. (#FDP-871)
[Upstream: c9a2a635776ffc716560a7cc066c2bce4d251f0f]

* Mon Mar 31 2025 Frode Nordahl <fnordahl@ubuntu.com> - 24.03.5-48
- ovs: Update the submodule to include python F824 fix.
[Upstream: fc4a72c1e2303ab8197b01035fc28a734242c428]

* Fri Mar 21 2025 Ales Musil <amusil@redhat.com> - 24.03.5-47
- ci: Add missing llvm package into Fedora.
[Upstream: 27573c2f1ff2719a33f1428c1015d39b53d31d5f]

* Thu Mar 20 2025 Xavier Simonart <xsimonar@redhat.com> - 24.03.5-46
- controller: Redirect traffic for container port. (#FDP-1223)
[Upstream: 884a140767bb47a8ccf269635aa40e44fc4c2c31]

* Thu Mar 20 2025 Xavier Simonart <xsimonar@redhat.com> - 24.03.5-45
- multinode tests: Simplify/Cleanup migration test.
[Upstream: 3b4d4f914c31802365ad769c1d6c759a8d159398]

* Thu Mar 20 2025 Ales Musil <amusil@redhat.com> - 24.03.5-44
- lb: Make the LB validation consistent.
[Upstream: 24454ce798e3438aadd460412c4eafc78a1117a8]

* Tue Mar 18 2025 Ales Musil <amusil@redhat.com> - 24.03.5-43
- tests: Ignore FDB transaction errors.
[Upstream: 3f562048ad9952058417a79d97f8bb2322e8b517]

* Tue Mar 18 2025 Lorenzo Bianconi <lorenzo.bianconi@redhat.com> - 24.03.5-42
- controller: Fix active mac-binding refresh for IPv6.
[Upstream: 6884bcba797430a0500ac577552935259538abea]

* Fri Mar 14 2025 Xavier Simonart <xsimonar@redhat.com> - 24.03.5-41
- tests: Avoid adding two similar load balancers.
[Upstream: 09308d47eaf6ef19f71eaef3b30799366b5fec5c]

* Fri Mar 14 2025 Xavier Simonart <xsimonar@redhat.com> - 24.03.5-40
- Fix missing load balancer hairpin flows.
[Upstream: 44448414aefa9f846d6aca9848d5ac14d560cf14]

* Wed Mar 12 2025 Lorenzo Bianconi <lorenzo.bianconi@redhat.com> - 24.03.5-39
- controller: Send ARP/ND for stale mac_bindings entries. (#FDP-1135)
[Upstream: 58ce60d2f1d932b842512763c2b8fc0943e1f8e3]

* Wed Mar 12 2025 Lorenzo Bianconi <lorenzo.bianconi@redhat.com> - 24.03.5-38
- controller: Introduce send_self_originated_neigh_packet routine.
[Upstream: 02072ad3ac6cdd792e8c4ac212dbb7bce803164f]

* Wed Mar 12 2025 Lorenzo Bianconi <lorenzo.bianconi@redhat.com> - 24.03.5-37
- controller: Use xxreg1 for lookup_nd_ip() and get_nd() actions.
[Upstream: 11db241f12586535ab70bc38c05730f2a96fdb96]

* Wed Mar 12 2025 Lorenzo Bianconi <lorenzo.bianconi@redhat.com> - 24.03.5-36
- controller: Update OFTABLE_MAC_CACHE_USE for ARP reply generated by the tracked device.
[Upstream: 955ed9a32c37ca1695c01e643e65c3c586595998]

* Wed Mar 12 2025 Ales Musil <amusil@redhat.com> - 24.03.5-35
- controller: Use datapath key for the mac cache thresholds.
[Upstream: 35b7ab29da3f27ffafebdfed28aecde948afade2]

* Wed Mar 12 2025 Ales Musil <amusil@redhat.com> - 24.03.5-34
- controller: Merge the mac-cache and mac-learn.
[Upstream: 16fb1ed0c94018b392d5107798a2953828b7ba32]

* Wed Mar 12 2025 Ales Musil <amusil@redhat.com> - 24.03.5-33
- controller: Rename mac_cache to to mac-cache.
[Upstream: 295f88673a408e348b877ec2cb421923707561cf]

* Wed Mar 12 2025 Ales Musil <amusil@redhat.com> - 24.03.5-32
- ci: Bump the Ubuntu image to 24.04.
[Upstream: 2da8deb3f909fec7624e764ef48dfcd4b0fc38a5]

* Mon Mar 10 2025 Ilya Maximets <i.maximets@ovn.org> - 24.03.5-31
- containers: Get sparse from the official GitHub mirror.
[Upstream: 5adc6391eebd49aadfeb5debc91d25d6414dd097]

* Wed Mar 05 2025 Ilya Maximets <i.maximets@ovn.org> - 24.03.5-30
- github: Use ubuntu-22.04 for DPDK build.
[Upstream: 249d99266aa8e7ad51dbff5c528f7589ee25c635]

* Tue Mar 04 2025 Ilya Maximets <i.maximets@ovn.org> - 24.03.5-29
- ovs: Update the submodule to v3.3.4.
[Upstream: 1837fd5b18036f8e5e65ce7e811890f7c2a2d344]

* Fri Feb 28 2025 Lorenzo Bianconi <lorenzo.bianconi@redhat.com> - 24.03.5-28
- northd: Fix action parsing in build_lb_vip_actions(). (#FDP-1095)
[Upstream: 480f238f6c2230e6150f3fe9f2a8e94447b35658]

* Fri Feb 28 2025 Ales Musil <amusil@redhat.com> - 24.03.5-27
- actions: Make sure all action opcodes have string representation.
[Upstream: a3a45a1a6c3294368a27032c76d48dd001dd8afb]

* Wed Feb 26 2025 Ales Musil <amusil@redhat.com> - 24.03.5-26
- northd: Prevent assert with wrong LSP configuration.
[Upstream: ddd0b86642e456ffdc86929d8b756ca1c392aa13]

* Thu Feb 20 2025 Lucas Vargas Dias <lucas.vdias@luizalabs.com> - 24.03.5-25
- ic: Fix denylist for IPv6 with same prefix length.
[Upstream: a5f7ff7b0d900e061b3e61f5d051e07214d07d25]

* Thu Feb 20 2025 Ilya Maximets <i.maximets@ovn.org> - 24.03.5-24
- tests: Fix conntrack not being flushed between tests.
[Upstream: 31e0c0ca46ec870da3663df798351514259d045a]

* Thu Feb 20 2025 Felix Huettner <felix.huettner@stackit.cloud> - 24.03.5-23
- northd: Fix onesided LRP peers.
[Upstream: d1ae41c389310733c8a7be990e9a4106d05fe61d]

* Wed Feb 19 2025 Xavier Simonart <xsimonar@redhat.com> - 24.03.5-22
- controller: Support migration of container ports. (#FDP-1037)
[Upstream: c497923186d43e0c906fee36cd381613dea1b33c]

* Wed Feb 19 2025 Xavier Simonart <xsimonar@redhat.com> - 24.03.5-21
- controller: Also log port up for container ports.
[Upstream: b3df8467a75035e77ac78f261a5d473afe007ac9]

* Tue Feb 18 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.5-20
- Revert "ovn-controller: Remove monitor all of chassis private."
[Upstream: 131e04f174ee2482bdc49c29016cd057b3e2ce65]

* Thu Feb 13 2025 Dumitru Ceara <dceara@redhat.com> - 24.03.5-19
- controller: Update ovn-monitor-all documentation.
[Upstream: ed2790153c07a376890f28b0a16bc321e3af016b]

* Thu Feb 13 2025 Lucas Vargas Dias <lucas.vdias@luizalabs.com> - 24.03.5-18
- ovn-controller: Remove monitor all of chassis private.
[Upstream: 2c57869a3ced4fd7462cd8c233f9983564f99225]

* Wed Feb 05 2025 Ales Musil <amusil@redhat.com> - 24.03.5-17
- controller: Omit alert for FDB and MAC binding timestamp.
[Upstream: 5ea9b593cd282c39853ef75caaeeaf84491accef]

* Tue Feb 04 2025 Ilya Maximets <i.maximets@ovn.org> - 24.03.5-16
- mac-cache: Fix expiration of active FDB entry due to skipped update. (#FDP-1132)
[Upstream: e036f8d41d24091237f6439e6358a3e47682e6ae]

* Tue Feb 04 2025 Ilya Maximets <i.maximets@ovn.org> - 24.03.5-15
- mac-cache: Fix expiration of active MAC binding due to skipped update. (#FDP-1130)
[Upstream: b5f1b884fcc68a9b5854b15de0da3ed997a8a747]

* Tue Feb 04 2025 Ilya Maximets <i.maximets@ovn.org> - 24.03.5-14
- mac-cache: Fix MAC binding entry lookup for timestamp refresh. (#FDP-1131)
[Upstream: 0870ebd44dfce38f86404778cc6bee5df40cdf5c]

* Tue Feb 04 2025 Ilya Maximets <i.maximets@ovn.org> - 24.03.5-13
- tests: Fix use of bash arrays in MAC binding tests.
[Upstream: b0d75de69887346f8a139520ec9ef0a3b7d41108]

* Tue Feb 04 2025 Ilya Maximets <i.maximets@ovn.org> - 24.03.5-12
- tests: Fix incorrect invocations of send_garp.
[Upstream: ba62948045ff772dcba85b13a5894c0d7b4eba78]

* Wed Jan 29 2025 Ales Musil <amusil@redhat.com> - 24.03.5-11
- northd: Do not attempt to install LS flows for LR IGMP group.
[Upstream: c60440befc464a0ec786345806f216a841476a19]

* Wed Jan 29 2025 Lorenzo Bianconi <lorenzo.bianconi@redhat.com> - 24.03.5-10
- northd: Trigger a full recompute if lb neigh_mode option is updated. (#FDP-1054)
[Upstream: 784be94567a88cc055855446aab14b046dfccb15]

* Fri Jan 24 2025 Ilya Maximets <i.maximets@ovn.org> - 24.03.5-9
- controller: Fix IPv6 dp flow explosion by setting flow table prefixes. (#FDP-1024)
[Upstream: 5d045ce28525388fa2c9c6fdb189e7289ccc6768]

* Thu Jan 23 2025 Frode Nordahl <fnordahl@ubuntu.com> - 24.03.5-8
- ic: Fix NULL ptr deref on log of duplicate routes.
[Upstream: a2f001eba006f08be7974589fb1d5616b07588fd]

* Tue Jan 21 2025 Mark Michelson <mmichels@redhat.com> - 24.03.5-7
- Prepare for 24.03.6.
[Upstream: 7dd5d8f82030e4927fca24d99d2b46816b6de4dc]

