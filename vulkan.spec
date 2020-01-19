
%global srcname Vulkan-Loader

%global commit1 05d12a9461dd0a76053bdd42f062a37a10d56afb
%global srcname1 glslang

%global commit2 8bea0a266ac9b718aa0818d9e3a47c0b77c2cb23
%global srcname2 spirv-headers

%global ver3 2019.1
%global srcname3 spirv-tools

%global srcname4 Vulkan-Headers
%global srcname5 Vulkan-ValidationLayers
%global srcname6 Vulkan-Tools

Name:           vulkan
Version:        1.1.97.0
Release:        1%{?dist}
Summary:        Vulkan loader and validation layers

License:        ASL 2.0
URL:            https://github.com/KhronosGroup

Source0:        %url/%{srcname}/archive/sdk-%{version}.tar.gz#/%{srcname}-sdk-%{version}.tar.gz
Source1:        %url/%{srcname1}/archive/%{commit1}.tar.gz#/%{srcname1}-%{commit1}.tar.gz
Source2:        %url/%{srcname2}/archive/%{commit2}.tar.gz#/%{srcname2}-%{commit2}.tar.gz
Source3:        %url/%{srcname3}/archive/%{ver3}.tar.gz#/%{srcname3}-%{ver3}.tar.gz
Source4:        %url/%{srcname4}/archive/sdk-%{version}.tar.gz#/%{srcname4}-sdk-%{version}.tar.gz
Source5:        %url/%{srcname5}/archive/sdk-%{version}.tar.gz#/%{srcname5}-sdk-%{version}.tar.gz
Source6:        %url/%{srcname6}/archive/sdk-%{version}.tar.gz#/%{srcname6}-sdk-%{version}.tar.gz
Source7:        spirv_tools_commit_id.h
Source8:        cmake-3.4.3.tar.gz

Patch0: fix_shared.patch
Patch1: spirv-tools-fix.patch
Patch2: layers-no-rpath.patch

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  bison
BuildRequires:  cmake
BuildRequires:  /usr/bin/chrpath
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(pciaccess)
BuildRequires:  python3
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-cursor)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xrandr)

Requires:       vulkan-filesystem = %{version}-%{release}

%if 0%{?fedora}
Recommends:     mesa-vulkan-drivers
%endif

%description
Vulkan is a new generation graphics and compute API that provides
high-efficiency, cross-platform access to modern GPUs used in a wide variety of
devices from PCs and consoles to mobile phones and embedded platforms.

This package contains the reference ICD loader and validation layers for
Vulkan.

%package devel
Summary:        Vulkan development package
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Development headers for Vulkan applications.

%package filesystem
Summary:        Vulkan filesystem package
BuildArch:      noarch

%description filesystem
Filesystem for Vulkan.

%prep
%setup -T -D -b 0 -n %{srcname}-sdk-%{version}
%setup -T -D -b 8 -n cmake-3.4.3
%setup -T -D -b 2 -n SPIRV-Headers-%{commit2}
%setup -T -D -b 3 -n SPIRV-Tools-%{ver3}
%patch1 -p1
%setup -T -D -b 1 -n glslang-%{commit1}
%setup -T -D -b 4 -n %{srcname4}-sdk-%{version}
%setup -T -D -b 5 -n %{srcname5}-sdk-%{version}
%patch0 -p1
%patch2 -p1
%setup -T -D -b 6 -n %{srcname6}-sdk-%{version}
cd -

%build

cd ../cmake-3.4.3
BUILD_DIR=`pwd`/cmake_build
cmake . -DCMAKE_INSTALL_PREFIX=$BUILD_DIR
make
make install
cd -

export PATH=$BUILD_DIR/bin:$PATH
%global __cmake $BUILD_DIR/bin/cmake

# install into somewhere outside the buildroot temporarily
export DESTDIR=../../install
export USRDIR=$PWD/../install/usr
cd ..
pushd %{srcname4}-sdk-%{version}
mkdir -p build
cd build
%cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON ..
%make_build
make install
cd -
popd

pushd SPIRV-Headers-%{commit2}
mkdir -p build
cd build
%cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON ..
%make_build
make install
cd -
popd

pushd SPIRV-Tools-%{ver3}
mkdir -p build
cd build
%cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON .. -DSPIRV-Headers_SOURCE_DIR=$USRDIR
%make_build
make install
cd -
popd

pushd %{srcname}-sdk-%{version}
mkdir -p build
cd build
%cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON .. -DVULKAN_HEADERS_INSTALL_DIR=$USRDIR
%make_build
make install
cd -
popd

pushd glslang-%{commit1}
mkdir -p build
cd build
%cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON .. -DVULKAN_HEADERS_INSTALL_DIR=$USRDIR -DCMAKE_INSTALL_LIBDIR=%{_libdir} -DCMAKE_SKIP_RPATH:BOOL=yes -DBUILD_SHARED_LIBS=OFF
%make_build
make install
cd -
popd

# hack to avoid running of memory on aarch64 and i686 build
%ifarch %{ix86} aarch64
# Decrease debuginfo verbosity to reduce memory consumption even more
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%endif

pushd %{srcname5}-sdk-%{version}
mkdir -p build
cd build
%cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON .. -DVULKAN_HEADERS_INSTALL_DIR=$USRDIR -DGLSLANG_INSTALL_DIR=$USRDIR
%make_build
cd -
popd

pushd %{srcname6}-sdk-%{version}
mkdir -p build
cd build
%cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON .. -DVULKAN_HEADERS_INSTALL_DIR=$USRDIR -DGLSLANG_INSTALL_DIR=$USRDIR -DBUILD_CUBE:BOOL=OFF
%make_build
cd -
popd

%install

cd ..
pushd %{srcname4}-sdk-%{version}/build
%{make_install}
popd

pushd %{srcname}-sdk-%{version}/build
%{make_install}
popd

pushd SPIRV-Tools-%{ver3}/build
%{make_install}
popd

pushd %{srcname5}-sdk-%{version}/build
# this doesn't use the macro as we don't want to trigger cmake rebuilds here
DESTDIR=$RPM_BUILD_ROOT cmake -P cmake_install.cmake
popd

pushd %{srcname6}-sdk-%{version}/build
# this doesn't use the macro as we don't want to trigger cmake rebuilds here
DESTDIR=$RPM_BUILD_ROOT cmake -P cmake_install.cmake
popd
cd -
# create the filesystem
mkdir -p %{buildroot}%{_sysconfdir}/vulkan/{explicit,implicit}_layer.d/ \
%{buildroot}%{_datadir}/vulkan/{explicit,implicit}_layer.d/ \
%{buildroot}{%{_sysconfdir},%{_datadir}}/vulkan/icd.d

# don't want spirv-tools
rm -f %{buildroot}%{_bindir}/spirv-*
rm -f %{buildroot}%{_libdir}/pkgconfig/SPIRV*
rm -rf %{buildroot}%{_includedir}/spirv-tools
rm -f %{buildroot}%{_libdir}/libSPIRV-Tools-link.so
rm -f %{buildroot}%{_libdir}/libSPIRV-Tools-reduce.so
rm -f %{buildroot}%{_libdir}/libSPIRV-Tools-shared.so

# remove unused includes and registry
rm -rf %{buildroot}%{_datadir}/vulkan/registry
rm -f %{buildroot}%{_includedir}/vk*.h %{buildroot}%{_includedir}/hash*.h %{buildroot}%{_includedir}/*.cpp

# remove RPATH
chrpath -d %{buildroot}%{_bindir}/vulkaninfo

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license LICENSE.txt
%doc README.md CONTRIBUTING.md
%{_bindir}/vulkaninfo
%{_datadir}/vulkan/explicit_layer.d/*.json
%{_libdir}/libVkLayer_*.so
%{_libdir}/libvulkan.so.*
%{_libdir}/libSPIRV*so

%files devel
%{_includedir}/vulkan/
%{_libdir}/pkgconfig/vulkan.pc
%{_libdir}/libvulkan.so

%files filesystem
%dir %{_sysconfdir}/vulkan/
%dir %{_sysconfdir}/vulkan/explicit_layer.d/
%dir %{_sysconfdir}/vulkan/icd.d/
%dir %{_sysconfdir}/vulkan/implicit_layer.d/
%dir %{_datadir}/vulkan/
%dir %{_datadir}/vulkan/explicit_layer.d/
%dir %{_datadir}/vulkan/icd.d/
%dir %{_datadir}/vulkan/implicit_layer.d/

%changelog
* Tue Feb 19 2019 Dave Airlie <airlied@redhat.com> 1.1.97.0-1
- Update to 1.1.97.0
- rework spec for new upstream layout

* Tue May 08 2018 Dave Airlie <airlied@redhat.com> 1.1.73.0-1
- Update to 1.1.73.0 release
- fixup spec for spirv-tools etc

* Tue Oct 10 2017 Dave Airlie <airlied@redhat.com> - 1.0.61.1-2
- fix 32-bit textrels

* Thu Sep 21 2017 Dave Airlie <airlied@redhat.com> - 1.0.61.1-1
- Update to 1.0.61.1 release
- bring spec updates in from Fedora spec.

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.39.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan 31 2017 Leigh Scott <leigh123linux@googlemail.com> - 1.0.39.1-1
- Update to 1.0.39.1 release

* Tue Jan 24 2017 Leigh Scott <leigh123linux@googlemail.com> - 1.0.39.0-1
- Update to 1.0.39.0 release
- Add build requires libXrandr-devel

* Fri Dec 16 2016 leigh scott <leigh123linux@googlemail.com> - 1.0.37.0-1
- Update to 1.0.37.0 release
- Disable Mir as it's lame ubuntu rubbish

* Fri Dec 02 2016 leigh scott <leigh123linux@googlemail.com> - 1.0.34.0-0.1.gitd4cd34f
- Update to latest git

* Thu Dec 01 2016 leigh scott <leigh123linux@googlemail.com> - 1.0.30.0-2
- Fix VkLayer undefined symbol: util_GetExtensionProperties

* Sat Oct 15 2016 Leigh Scott <leigh123linux@googlemail.com> - 1.0.30.0-1
- Update to 1.0.30.0 release

* Mon Oct 10 2016 Leigh Scott <leigh123linux@googlemail.com> - 1.0.26.0-4
- Build with wayland support (rhbz 1383115)

* Tue Sep 27 2016 Leigh Scott <leigh123linux@googlemail.com> - 1.0.26.0-3
- Move unversioned libraries
- Disable vkjson build
- Fix license tag

* Sun Sep 11 2016 Leigh Scott <leigh123linux@googlemail.com> - 1.0.26.0-2
- Make layers conditional. 

* Sun Sep 11 2016 Leigh Scott <leigh123linux@googlemail.com> - 1.0.26.0-1
- Update to 1.0.26.0 release

* Thu Sep 08 2016 Leigh Scott <leigh123linux@googlemail.com> - 1.0.26.0-0.3.gitfbb8667
- Clean up

* Thu Sep 08 2016 Leigh Scott <leigh123linux@googlemail.com> - 1.0.26.0-0.2.gitfbb8667
- Change build requires python3
- Use release for cmake
- Make build verbose

* Wed Sep 07 2016 Leigh Scott <leigh123linux@googlemail.com> - 1.0.26.0-0.1.gitfbb8667
- Update to latest git

* Tue Feb 16 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 1.0.3-0.1.git1affe90
- Add ldconfig in post/postun
- Use upstream tarball from commit + patches
- Fix versioning. In fact it was never released
- Fixup mixing of spaces/tabs
- Remove rpath from vulkaninfo
- Make filesystem subpkg noarch (it is really noarch)
- BuildRequire gcc and gcc-c++ explicitly
- Require main pkg with isa tag
- Fix perms and perm of README.md
- Use %%license tag

* Tue Feb 16 2016 Adam Jackson <ajax@redhat.com> - 1.0.3-0
- Update loader to not build cube or tri. Drop bundled LunarGLASS and llvm
  since they're only needed for those demos.

* Tue Feb 16 2016 Adam Jackson <ajax@redhat.com> - 1.0.3-0
- Initial packaging
