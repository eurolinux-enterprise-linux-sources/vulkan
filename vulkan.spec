%global use_git 0
%global use_layers 1

%global commit  d4cd34fd49caa759cf01cafa5fa271401b17c3b9
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global srcname Vulkan-LoaderAndValidationLayers

%if 0%{?use_layers}
%global commit1 807a0d9e2f4e176f75d62ac3c179c81800ec2608
%global srcname1 glslang

%global commit2 37422e9dba1a3a8cb8028b779dd546d43add6ef8
%global srcname2 SPIRV-Tools

%global commit3 c470b68225a04965bf87d35e143ae92f831e8110
%global srcname3 SPIRV-Headers
%endif

Name:           vulkan
Version:        1.0.39.1
%if 0%{?use_git}
Release:        0.2.git%{shortcommit}%{?dist}
%else
Release:        2%{?dist}
%endif
Summary:        Vulkan loader and validation layers

License:        ASL 2.0
URL:            https://github.com/KhronosGroup

%if 0%{?use_git}
Source0:        %url/%{srcname}/archive/%{commit}.tar.gz#/%{srcname}-%{commit}.tar.gz
%else
Source0:        %url/%{srcname}/archive/sdk-%{version}.tar.gz#/%{srcname}-sdk-%{version}.tar.gz
%endif
%if 0%{?use_layers}
Source1:        %url/%{srcname1}/archive/%{commit1}.tar.gz#/%{srcname1}-%{commit1}.tar.gz
Source2:        %url/%{srcname2}/archive/%{commit2}.tar.gz#/%{srcname2}-%{commit2}.tar.gz
Source3:        %url/%{srcname3}/archive/%{commit3}.tar.gz#/%{srcname3}-%{commit3}.tar.gz
%else
Source4:        https://raw.githubusercontent.com/KhronosGroup/glslang/master/SPIRV/spirv.hpp
%endif
# All patches taken from ajax's repo
# https://github.com/nwnk/Vulkan-LoaderAndValidationLayers/tree/sdk-1.0.3-fedora
Patch0:         0003-layers-Don-t-set-an-rpath.patch
Patch1:         0008-demos-Don-t-build-tri-or-cube.patch
Patch2:		hacked-python2.patch

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  bison
BuildRequires:  cmake
BuildRequires:  /usr/bin/chrpath
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(pciaccess)
%if 0%{?fedora}
BuildRequires:  python3
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-cursor)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wayland-egl)
%else
BuildRequires:  python
%endif
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
%if 0%{?use_git}
%autosetup -p1 -n %{srcname}-%{commit}
%else
%autosetup -p1 -n %{srcname}-sdk-%{version}
%endif
%if 0%{?use_layers}
mkdir -p build/ external/glslang/build/install external/spirv-tools/build/ external/spirv-tools/external/spirv-headers
tar -xf %{SOURCE1} -C external/glslang --strip 1
tar -xf %{SOURCE2} -C external/spirv-tools --strip 1
tar -xf %{SOURCE3} -C external/spirv-tools/external/spirv-headers --strip 1
# fix spurious-executable-perm
chmod 0644 README.md
chmod 0644 external/glslang/SPIRV/spirv.hpp
chmod +x scripts/lvl_genvk.py
%else
mkdir -p build/
cp %{SOURCE4} .
%endif
# fix wrong-script-end-of-line-encoding
sed -i 's/\r//' README.md

# sigh inttypes
sed -i 's/inttypes.h/cinttypes/' layers/*.{cpp,h}

%build
%if 0%{?use_layers}
pushd external/glslang/build/
CFLAGS="$RPM_OPT_FLAGS" ; export CFLAGS ; 
CXXFLAGS="$RPM_OPT_FLAGS" ; export CXXFLAGS ; 
LDFLAGS="$RPM_LD_FLAGS" ; export LDFLAGS ;
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON ..
%make_build
make install
popd
pushd external/spirv-tools/build/
cmake -DSPIRV_WERROR=OFF -DCMAKE_BUILD_TYPE=Release -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON ..
%make_build
popd
%endif
pushd build/
%cmake -DCMAKE_BUILD_TYPE=Release \
       -DCMAKE_SKIP_INSTALL_RPATH:BOOL=yes \
       -DCMAKE_SKIP_RPATH:BOOL=yes \
       -DBUILD_VKJSON=OFF \
       -DCMAKE_INSTALL_SYSCONFDIR:PATH=%{_sysconfdir} \
       -DBUILD_WSI_MIR_SUPPORT=OFF \
%if 0%{?rhel}
       -DBUILD_WSI_WAYLAND_SUPPORT=OFF \
%endif
%if 0%{?use_layers}
 ..
%else
       -DGLSLANG_SPIRV_INCLUDE_DIR=./ \
       -DBUILD_TESTS=OFF \
       -DBUILD_LAYERS=OFF ..
%endif
%make_build
popd

%install
pushd build/
%{make_install}
popd

%if 0%{?use_layers}
mkdir -p %{buildroot}%{_datadir}/vulkan/implicit_layer.d
mv %{buildroot}%{_sysconfdir}/vulkan/explicit_layer.d/ %{buildroot}%{_datadir}/vulkan/
%endif

# remove RPATH
chrpath -d %{buildroot}%{_bindir}/vulkaninfo

mkdir -p %{buildroot}%{_sysconfdir}/vulkan/icd.d

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license LICENSE.txt COPYRIGHT.txt
%doc README.md CONTRIBUTING.md
%{_bindir}/vulkaninfo
%if 0%{?use_layers}
%{_datadir}/vulkan/explicit_layer.d/*.json
%{_libdir}/libVkLayer_*.so
%endif
%{_libdir}/lib%{name}.so.*

%files devel
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so

%files filesystem
%dir %{_sysconfdir}/vulkan
%dir %{_sysconfdir}/vulkan/icd.d
%if 0%{?use_layers}
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/explicit_layer.d
%dir %{_datadir}/%{name}/implicit_layer.d
%endif

%changelog
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
