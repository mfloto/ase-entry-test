import sys
import json
import urllib.request
import urllib.error

def check_requirements(filepath):
    deps_checked = 0
    pkgs_not_in_pypi = 0
    versions_not_in_pypi = 0
    
    oldest_time = None
    oldest_release = None

    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Could not find '{filepath}'")
        sys.exit(1)

    for line in lines:
        # Strip comments and whitespace
        line = line.split('#')[0].strip()
        if not line:
            continue
            
        # Strip environment markers (e.g., "package==1.0 ; python_version<'3.8'")
        if ';' in line:
            line = line.split(';')[0].strip()

        # Parse package name and pinned version
        if '==' in line:
            name, version = [part.strip() for part in line.split('==', 1)]
        else:
            name = line.strip()
            version = None

        deps_checked += 1
        pkg_exists = True

        # 1. Check if the package exists in PyPI
        pkg_url = f"https://pypi.org/pypi/{name}/json"
        try:
            urllib.request.urlopen(pkg_url)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                pkgs_not_in_pypi += 1
                pkg_exists = False
            else:
                print(f"Warning: HTTP {e.code} when checking package {name}")

        # 2. Check if the specific version exists in PyPI (if pinned)
        if version:
            if not pkg_exists:
                # If the package doesn't exist, inherently the version doesn't exist either
                versions_not_in_pypi += 1
            else:
                ver_url = f"https://pypi.org/pypi/{name}/{version}/json"
                try:
                    resp = urllib.request.urlopen(ver_url)
                    data = json.loads(resp.read().decode('utf-8'))
                    
                    # Track the oldest pinned release based on upload_time
                    urls = data.get('urls', [])
                    if urls:
                        upload_time = urls[0].get('upload_time')
                        if upload_time:
                            # PyPI returns ISO-8601 strings, which can be evaluated lexicographically
                            if oldest_time is None or upload_time < oldest_time:
                                oldest_time = upload_time
                                oldest_release = f"{name}=={version} ({upload_time[:4]})"

                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        versions_not_in_pypi += 1
                    else:
                        print(f"Warning: HTTP {e.code} when checking version {name}=={version}")

    # Output Results
    print(f"1. Number of dependencies checked: {deps_checked}")
    print(f"2. Number of packages which are not in PyPI: {pkgs_not_in_pypi}")
    print(f"3. Number of packages versions which are not in PyPI: {versions_not_in_pypi}")
    
    if oldest_release:
        print(f"4. The oldest pinned release which exists: {oldest_release}")
    else:
        print("4. The oldest pinned release which exists: None found")

if __name__ == "__main__":        
    check_requirements("requirements.txt")