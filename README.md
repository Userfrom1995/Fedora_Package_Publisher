# Copr Publisher

## Overview
Copr Publisher is a command-line tool that automates publishing Fedora packages to [Copr](https://copr.fedorainfracloud.org/). It simplifies package submission and management, making it easier to publish RPM packages with minimal effort.

## Installation
You can install Copr Publisher directly from Copr using the following steps:

```sh
sudo dnf copr enable user1995/Copr_Publisher
sudo dnf install fedora-package-publisher
```

Alternatively, you can clone the repository and run the script manually:

```sh
git clone https://github.com/Userfrom1995/Fedora_Package_Publisher.git
cd Fedora_Package_Publisher
python3 fedora-package-publisher.py
```

## Usage
Once installed, you can run the tool using:

```sh
fedora-package-publisher
```

### How It Works
1. The tool will prompt you to provide the path to your `.spec` file.
2. It will generate the source RPM (`.src.rpm`) automatically.
3. The package will be submitted to Copr for building and publishing.
4. The script will guide you through the process and confirm successful publication.

## Important Notes
- Ensure that your `.spec` file is valid before running the tool. You can check its validity using:
  ```sh
  rpmlint your-package.spec
  ```
- Ubuntu and other non-Fedora systems do not support Copr, so this tool is designed to run on Fedora.

## Troubleshooting
If you encounter issues, try the following:
- Run the tool with Python directly:
  ```sh
  python3 /usr/bin/fedora-package-publisher
  ```
- If the command is not found after installation, check its location:
  ```sh
  which fedora-package-publisher
  ```
- If an older version is installed, remove it and install the latest version:
  ```sh
  sudo dnf remove fedora-package-publisher
  sudo dnf install fedora-package-publisher
  ```
  
## Copr Project :
https://copr.fedorainfracloud.org/coprs/user1995/Copr_Publisher/

## Contributing
Feel free to contribute to this project by submitting pull requests or reporting issues on the [GitHub repository](https://github.com/Userfrom1995/Fedora_Package_Publisher).

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.


