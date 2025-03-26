import os
import subprocess
import sys

CONFIG_FILE = os.path.expanduser("~/.config/copr")

# Check if Copr CLI is authenticated
def is_copr_authenticated():
    return os.path.isfile(CONFIG_FILE) and subprocess.run(["copr-cli", "whoami"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

def get_default_fedora_builds():
    try:
        output = subprocess.run(["copr-cli", "list-chroots"], capture_output=True, text=True, check=True).stdout
        builds = [line.strip() for line in output.split("\n") if line.startswith("fedora-") and "-x86_64" in line]
        builds.sort()
        return builds
    except subprocess.CalledProcessError:
        return []

def prompt_for_additional_builds(default_builds):
    print("Detected default Fedora builds:")
    print(" ".join(default_builds))
    extra_builds = input("Enter additional Fedora builds (space-separated) or press Enter to continue: ").split()
    return default_builds + extra_builds

def get_existing_chroots(copr_user, project_name):
    """Retrieve existing chroots for the Copr project."""
    result = subprocess.run(
        ["copr", "get-chroots", f"{copr_user}/{project_name}"], capture_output=True, text=True
    )
    return result.stdout.split() if result.returncode == 0 else []

if is_copr_authenticated():
    print("Copr CLI is already authenticated.")
else:
    print("Copr CLI is not authenticated. Let's set it up.")
    print("\nPlease visit https://copr.fedorainfracloud.org/api and log in to retrieve your API key.")
    print("Once you have your API key, enter your credentials below.")

    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    login = input("Enter your Copr login (API token name): ")
    username = input("Enter your Copr username: ")
    token = input("Enter your Copr API token: ")
    copr_url = "https://copr.fedorainfracloud.org"

    with open(CONFIG_FILE, "w") as f:
        f.write(f"[copr-cli]\nlogin = {login}\nusername = {username}\ntoken = {token}\ncopr_url = {copr_url}\n")
    os.chmod(CONFIG_FILE, 0o600)

    print("\nCopr authentication configured. Verifying...")
    subprocess.run(["copr-cli", "whoami"])


# Get spec file
spec_file = input("Enter the path to your spec file (leave empty to search in the current directory): ")
if not spec_file:
    spec_files = [f for f in os.listdir('.') if f.endswith('.spec')]
    spec_file = spec_files[0] if spec_files else None

if not spec_file or not os.path.isfile(spec_file):
    print("Error: No valid spec file found!")
    sys.exit(1)
print(f"Using spec file: {spec_file}")

# Extract Source0 URL from the spec file
source_path = None
with open(spec_file) as f:
    for line in f:
        if line.startswith("Source0:"):
            source_path = line.split()[1]
            break

if not source_path:
    print("Error: No Source0 found in spec file!")
    sys.exit(1)

os.makedirs(os.path.expanduser("~/rpmbuild/SOURCES/"), exist_ok=True)

tarball_path = os.path.basename(source_path)
if source_path.startswith("http"):
    print(f"Downloading source tarball: {source_path}")
    subprocess.run(["wget", "-O", tarball_path, source_path], check=True)
    subprocess.run(["mv", tarball_path, os.path.expanduser("~/rpmbuild/SOURCES/")])
elif os.path.isfile(source_path):
    subprocess.run(["cp", source_path, os.path.expanduser("~/rpmbuild/SOURCES/")])
else:
    print(f"Error: Source file '{source_path}' not found!")
    sys.exit(1)

# Generate SRPM
srpm_dir = input("Enter the directory to save the SRPM file (leave empty for current directory): ") or "."
os.makedirs(srpm_dir, exist_ok=True)
print("Generating source RPM...")
subprocess.run(["rpmbuild", "-bs", spec_file, "--define", f"_srcrpmdir {srpm_dir}"], check=True)

srpm_files = sorted([f for f in os.listdir(srpm_dir) if f.endswith(".src.rpm")], key=os.path.getmtime, reverse=True)
srpm_path = os.path.join(srpm_dir, srpm_files[0]) if srpm_files else None
if not srpm_path:
    print("Error: SRPM generation failed!")
    sys.exit(1)

print("SRPM generation complete!")

# Ensure Copr CLI authentication
if subprocess.run(["copr", "whoami"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
    print("Copr CLI is not authenticated! Please run: copr login")
    sys.exit(1)

# Fetch available Fedora chroots
default_builds = get_default_fedora_builds()
all_builds = prompt_for_additional_builds(default_builds)

# print("Detected default Fedora builds:")
# print(" ".join(valid_builds))
# extra_builds = input("Enter additional Fedora builds (space-separated) or press Enter to continue: ").split()
# all_builds = valid_builds + extra_builds
print("All builds")
print(all_builds)
print("All builds index 0 ")
print(all_builds[0])

copr_user = subprocess.run(["copr", "whoami"], capture_output=True, text=True).stdout.strip()
project_name = input("Enter the Copr project name: ")
copr_url = f"https://copr.fedorainfracloud.org/coprs/{copr_user}/{project_name}/"

# Check if the project exists
if subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", copr_url], capture_output=True, text=True).stdout.strip() == "200":
    print(f"Copr repository '{project_name}' exists! Proceeding with the build...")
    # Retrieve existing chroots and merge with new ones
    existing_chroots = get_existing_chroots(copr_user, project_name)
    updated_chroots = list(set(existing_chroots + all_builds))
    # Apply all chroots in a single modify command
    subprocess.run(["copr", "modify", f"{copr_user}/{project_name}"] + sum([["--chroot", ch] for ch in updated_chroots], []))
else:
    print(f"Copr repository '{project_name}' does not exist. Creating it...")
    subprocess.run(["copr", "create", f"{copr_user}/{project_name}"] + sum([["--chroot", ch] for ch in all_builds], []))



print("Submitting build...")
subprocess.run(["copr", "build", project_name, srpm_path])
print("Build submitted successfully!")