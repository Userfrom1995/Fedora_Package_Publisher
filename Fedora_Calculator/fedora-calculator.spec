Name:           fedora-calculator
Version:        1.0
Release:        1%{?dist}
Summary:        A simple terminal calculator for Fedora

License:        MIT
URL:            https://github.com/unconventional-guy/Fedora_Calculator
Source0:        fedora-calculator-1.0.tar.gz

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
* Sat Mar 23 2025 Your Name <userfrom1995@gmail.com> - 1.0-1
- Initial release
