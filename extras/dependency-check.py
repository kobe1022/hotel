# https://docs.microsoft.com/en-us/powershell/scripting/developer/cmdlet/approved-verbs-for-windows-powershell-commands?view=powershell-7

# Aufruf:   uv run extras/dependency-check.py

"""Python-Script, um OWASP Dependency Check aufzurufen."""

import subprocess  # ruff: ignore[suspicious-subprocess-import]
from os import environ
from pathlib import Path
from sysconfig import get_platform

from dotenv import load_dotenv

load_dotenv()
nvd_api_key = environ.get('NVD_API_KEY')
print(f"nvd_api_key={nvd_api_key}")

project = "Hotelgast"

base_script = "dependency-check"
betriebssystem = get_platform()
if betriebssystem in {"win-amd64", "win-arm64", "win32"}:
    base_exec_path = Path("C:/") / "Zimmermann"
    extension = "bat"
    base_script += ".bat"
    base_data_path = Path("C:\\") / "Zimmermann"
else:
    base_exec_path = Path("Zimmermann")
    base_data_path = Path("Zimmermann")

script = base_exec_path / "dependency-check" / "bin" / base_script
print(f"script={script}")

data_path = base_data_path / "dependency-check-data"
pyproject_path = Path(".")
report_path = "."

options = " ".join([
    f"--nvdApiKey {nvd_api_key} --project {project} --scan {pyproject_path}",
    f"--suppression extras/suppression.xml --out {report_path} --data {data_path}",
    # dependency-check.bat --advancedHelp
    "--disableArchive",
    "--disableAssembly",
    "--disableAutoconf",
    "--disableBundleAudit",
    "--disableCarthageAnalyzer",
    "--disableCentral",
    "--disableCentralCache",
    "--disableCmake",
    "--disableCocoapodsAnalyzer",
    "--disableComposer",
    "--disableCpan",
    "--disableDart",
    "--disableGolangDep",
    "--disableGolangMod",
    "--disableJar",
    "--disableMavenInstall",
    "--disableMixAudit",
    "--disableMSBuild",
    "--disableNodeAudit",
    "--disableNodeAuditCache",
    "--disableNodeJS",
    "--disableNugetconf",
    "--disableNuspec",
    "--disableOssIndex",
    "--disablePipfile",
    "--disablePnpmAudit",
    "--disableRubygems",
    "--disableSwiftPackageManagerAnalyzer",
    "--disableSwiftPackageResolvedAnalyzer",
    "--disableYarnAudit",
])
print(f"options={options}")
print()

subprocess.run(f"{script} {options}", shell=True)  # ruff: ignore[subprocess-run-without-check, subprocess-popen-with-shell-equals-true]
