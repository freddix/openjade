%define		pre	1

Summary:	DSSSL parser
Name:		openjade
Version:	1.3.3
Release:	0.pre%{pre}.12
Epoch:		1
License:	Free (Copyright (C) 1999 The OpenJade group)
Group:		Applications/Publishing/SGML
Source0:	http://downloads.sourceforge.net/openjade/%{name}-%{version}-pre%{pre}.tar.gz
# Source0-md5:	cbf3d8be3e3516dcb12b751de822b48c
Patch0:		%{name}-nls-from-1.4.patch
Patch1:		%{name}-libs.patch
URL:		http://openjade.sourceforge.net/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	gettext-devel
BuildRequires:	libtool
BuildRequires:	opensp-devel
BuildRequires:	perl-base
Requires(post,postun):	/usr/sbin/ldconfig
Requires(post,postun):	sgml-common
Requires:	sgml-common
Requires:	sgmlparser
Provides:	dssslparser
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		sgmldir		/usr/share/sgml
%define		_datadir	%{sgmldir}/%{name}-%{version}

# FIXME: all libraries underlinked
%define		skip_post_check_so	lib.*\.so.*

%description
Jade (James' DSSSL Engine) is an implementation of the DSSSL style
language. OpenJade is successor of Jade.

%package devel
Summary:	OpenJade header files
Group:		Development/Libraries
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description devel
Openjade header files.

%prep
%setup -q -n %{name}-%{version}-pre%{pre}
%patch0 -p1
%patch1 -p1

sed -i 's|iostream.h|iostream|g' style/MultiLineInlineNote.cxx

%build
LDFLAGS=""; export LDFLAGS
ln -sf config/configure.in .
# smr_SWITCH and OJ_SIZE_T_IS_UINT
tail -n +3349 config/aclocal.m4 | head -n 64 > acinclude.m4
%{__gettextize}
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%configure \
	--disable-static					\
	--enable-default-catalog=%{_sysconfdir}/sgml/catalog	\
	--enable-default-search-path=%{_prefix}/share/sgml	\
	--enable-html						\
	--enable-mif						\
	--enable-splibdir=%{_libdir}				\
	--enable-threads
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_datadir}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	localedir=%{_prefix}/share/locale

# simulate jade
ln -sf openjade $RPM_BUILD_ROOT%{_bindir}/jade

# files present in openjade 1.4
install dsssl/{catalog,dsssl.dtd,extensions.dsl,fot.dtd,style-sheet.dtd} \
$RPM_BUILD_ROOT%{_datadir}
install -d $RPM_BUILD_ROOT%{_includedir}/OpenJade
install include/*.h grove/Node.h spgrove/{GroveApp,GroveBuilder}.h \
	style/{DssslApp,FOTBuilder}.h $RPM_BUILD_ROOT%{_includedir}/OpenJade

%find_lang jade

%clean
rm -rf $RPM_BUILD_ROOT

%post
/usr/sbin/ldconfig
if ! grep -q %{_sysconfdir}/sgml/openjade.cat %{_sysconfdir}/sgml/catalog ; then
%{_bindir}/install-catalog --add %{_sysconfdir}/sgml/openjade.cat \
%{_datadir}/catalog
elif grep -sq %{_prefix}/share/OpenJade/catalog %{_sysconfdir}/sgml/openjade.cat ; then
	# upgrade
%{_bindir}/install-catalog --remove %{_sysconfdir}/sgml/openjade.cat \
%{_prefix}/share/OpenJade/catalog
%{_bindir}/install-catalog --add %{_sysconfdir}/sgml/openjade.cat \
%{_datadir}/catalog
fi

%postun
/usr/sbin/ldconfig
if [ "$1" = "0" ] ; then
%{_bindir}/install-catalog --remove %{_sysconfdir}/sgml/openjade.cat \
%{_datadir}/catalog
fi

%files -f jade.lang
%defattr(644,root,root,755)
%doc COPYING ChangeLog NEWS README doc/*.htm jadedoc
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %ghost %{_libdir}/lib*.so.?
%attr(755,root,root) %{_libdir}/lib*.so.*.*.*
%{_datadir}

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so
%{_libdir}/lib*.la
%{_includedir}/OpenJade

