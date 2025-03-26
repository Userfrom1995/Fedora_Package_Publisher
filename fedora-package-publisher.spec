Name:           fedora-package-publisher
Version:        1.0.0
Release:        1%{?dist}
Summary:        A tool to automate publishing Fedora packages to Copr

License:        MIT
URL:           https://github.com/Userfrom1995/Fedora_Package_Publisher
Source0:       https://github.com/Userfrom1995/Fedora_Package_Publisher/releases/download/version1/fedora-package-publisher-1.0.0.tar.gz

BuildArch:      noarch
Requires:       python3

%description
Fedora Package Publisher is a command-line tool that automates the process of 
publishing Fedora packages to Copr. It simplifies package submission and 
management.

%prep
%setup -q

%build
# No compilation required since it's a Python script

%install
mkdir -p %{buildroot}%{_bindir}
install -m 0755 Main.py %{buildroot}%{_bindir}/fedora-package-publisher

%files
%license LICENSE
%{_bindir}/fedora-package-publisher

%changelog
* Wed Mar 26 2025 User1995 <userfrom1995@gmail.com> - 1.0.0-1
- Initial package
