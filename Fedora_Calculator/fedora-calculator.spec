Name:           fedora-calculator
Version:        1.0
Release:        1%{?dist}
Summary:        A simple terminal calculator for Fedora

License:        MIT
URL:            https://github.com/Userfrom1995/Fedora_Calculator
Source0:        https://github.com/Userfrom1995/Fedora_Calculator/archive/refs/tags/version1.tar.gz

BuildArch:      noarch
Requires:       python3

%description
Fedora Calculator is a simple terminal-based calculator that evaluates
mathematical expressions entered by the user.

%prep
%autosetup

%build

%install
install -Dm755 calculator.py %{buildroot}%{_bindir}/fedora-calculator

%files
%license LICENSE
%{_bindir}/fedora-calculator

%changelog
* Mon Mar 25 2025 User1995 <userfrom1995@gmail.com> - 1.0-1
- Initial release

