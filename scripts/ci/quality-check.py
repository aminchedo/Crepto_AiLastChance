#!/usr/bin/env python3
"""
Quality check script for BOLT AI Neural Agent System
"""
import os
import sys
import subprocess
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple


class QualityChecker:
    """Quality checker for the BOLT AI system"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_root = project_root / "backend"
        self.frontend_root = project_root
        self.results = {
            "python_linting": {"passed": False, "issues": []},
            "typescript_linting": {"passed": False, "issues": []},
            "security_scan": {"passed": False, "issues": []},
            "dependency_check": {"passed": False, "issues": []},
            "overall": {"passed": False}
        }
    
    def run_command(self, command: List[str], cwd: Path = None) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)
    
    def check_python_linting(self) -> bool:
        """Check Python code quality"""
        print("🔍 Checking Python code quality...")
        
        # Black formatting check
        exit_code, stdout, stderr = self.run_command([
            "python", "-m", "black", "--check", "--diff", "."
        ], cwd=self.backend_root)
        
        if exit_code != 0:
            self.results["python_linting"]["issues"].append({
                "tool": "black",
                "message": "Code formatting issues found",
                "details": stdout
            })
        
        # isort import sorting check
        exit_code, stdout, stderr = self.run_command([
            "python", "-m", "isort", "--check-only", "--diff", "."
        ], cwd=self.backend_root)
        
        if exit_code != 0:
            self.results["python_linting"]["issues"].append({
                "tool": "isort",
                "message": "Import sorting issues found",
                "details": stdout
            })
        
        # flake8 linting
        exit_code, stdout, stderr = self.run_command([
            "python", "-m", "flake8", ".", "--max-line-length=100", "--extend-ignore=E203,W503"
        ], cwd=self.backend_root)
        
        if exit_code != 0:
            self.results["python_linting"]["issues"].append({
                "tool": "flake8",
                "message": "Code style issues found",
                "details": stdout
            })
        
        # mypy type checking
        exit_code, stdout, stderr = self.run_command([
            "python", "-m", "mypy", ".", "--ignore-missing-imports", "--no-strict-optional"
        ], cwd=self.backend_root)
        
        if exit_code != 0:
            self.results["python_linting"]["issues"].append({
                "tool": "mypy",
                "message": "Type checking issues found",
                "details": stdout
            })
        
        passed = len(self.results["python_linting"]["issues"]) == 0
        self.results["python_linting"]["passed"] = passed
        
        if passed:
            print("✅ Python code quality checks passed")
        else:
            print(f"❌ Python code quality checks failed: {len(self.results['python_linting']['issues'])} issues")
        
        return passed
    
    def check_typescript_linting(self) -> bool:
        """Check TypeScript/JavaScript code quality"""
        print("🔍 Checking TypeScript/JavaScript code quality...")
        
        # ESLint check
        exit_code, stdout, stderr = self.run_command(["npm", "run", "lint"])
        
        if exit_code != 0:
            self.results["typescript_linting"]["issues"].append({
                "tool": "eslint",
                "message": "JavaScript/TypeScript linting issues found",
                "details": stdout
            })
        
        # TypeScript type check
        exit_code, stdout, stderr = self.run_command(["npm", "run", "type-check"])
        
        if exit_code != 0:
            self.results["typescript_linting"]["issues"].append({
                "tool": "typescript",
                "message": "TypeScript type checking issues found",
                "details": stdout
            })
        
        passed = len(self.results["typescript_linting"]["issues"]) == 0
        self.results["typescript_linting"]["passed"] = passed
        
        if passed:
            print("✅ TypeScript/JavaScript code quality checks passed")
        else:
            print(f"❌ TypeScript/JavaScript code quality checks failed: {len(self.results['typescript_linting']['issues'])} issues")
        
        return passed
    
    def check_security(self) -> bool:
        """Check security vulnerabilities"""
        print("🔍 Checking security vulnerabilities...")
        
        # Python security scan with bandit
        exit_code, stdout, stderr = self.run_command([
            "python", "-m", "bandit", "-r", ".", "-f", "json"
        ], cwd=self.backend_root)
        
        if exit_code != 0:
            try:
                bandit_results = json.loads(stdout)
                for issue in bandit_results.get("results", []):
                    self.results["security_scan"]["issues"].append({
                        "tool": "bandit",
                        "severity": issue.get("severity", "unknown"),
                        "message": f"{issue.get('test_name', 'Unknown')} in {issue.get('filename', 'Unknown')}",
                        "details": issue.get("more_info", "")
                    })
            except json.JSONDecodeError:
                self.results["security_scan"]["issues"].append({
                    "tool": "bandit",
                    "message": "Security scan failed",
                    "details": stdout
                })
        
        # Node.js security audit
        exit_code, stdout, stderr = self.run_command(["npm", "audit", "--audit-level=high"])
        
        if exit_code != 0:
            self.results["security_scan"]["issues"].append({
                "tool": "npm-audit",
                "message": "Node.js dependency vulnerabilities found",
                "details": stdout
            })
        
        # Python dependency security check
        exit_code, stdout, stderr = self.run_command([
            "python", "-m", "safety", "check", "--json"
        ], cwd=self.backend_root)
        
        if exit_code != 0:
            try:
                safety_results = json.loads(stdout)
                for issue in safety_results:
                    self.results["security_scan"]["issues"].append({
                        "tool": "safety",
                        "message": f"Vulnerable package: {issue.get('package', 'Unknown')}",
                        "details": issue.get("advisory", "")
                    })
            except json.JSONDecodeError:
                self.results["security_scan"]["issues"].append({
                    "tool": "safety",
                    "message": "Dependency security scan failed",
                    "details": stdout
                })
        
        passed = len(self.results["security_scan"]["issues"]) == 0
        self.results["security_scan"]["passed"] = passed
        
        if passed:
            print("✅ Security checks passed")
        else:
            print(f"❌ Security checks failed: {len(self.results['security_scan']['issues'])} issues")
        
        return passed
    
    def check_dependencies(self) -> bool:
        """Check dependency health"""
        print("🔍 Checking dependencies...")
        
        # Check Python dependencies
        exit_code, stdout, stderr = self.run_command([
            "python", "-m", "pip", "check"
        ], cwd=self.backend_root)
        
        if exit_code != 0:
            self.results["dependency_check"]["issues"].append({
                "tool": "pip-check",
                "message": "Python dependency conflicts found",
                "details": stdout
            })
        
        # Check Node.js dependencies
        exit_code, stdout, stderr = self.run_command(["npm", "ls", "--depth=0"])
        
        if exit_code != 0:
            self.results["dependency_check"]["issues"].append({
                "tool": "npm-ls",
                "message": "Node.js dependency issues found",
                "details": stdout
            })
        
        # Check for outdated dependencies
        exit_code, stdout, stderr = self.run_command(["npm", "outdated"])
        
        if exit_code == 0 and stdout.strip():
            self.results["dependency_check"]["issues"].append({
                "tool": "npm-outdated",
                "message": "Outdated Node.js dependencies found",
                "details": stdout
            })
        
        passed = len(self.results["dependency_check"]["issues"]) == 0
        self.results["dependency_check"]["passed"] = passed
        
        if passed:
            print("✅ Dependency checks passed")
        else:
            print(f"❌ Dependency checks failed: {len(self.results['dependency_check']['issues'])} issues")
        
        return passed
    
    def generate_sbom(self) -> bool:
        """Generate Software Bill of Materials"""
        print("🔍 Generating Software Bill of Materials...")
        
        try:
            # Python SBOM
            exit_code, stdout, stderr = self.run_command([
                "python", "-m", "cyclonedx_py", "-o", "sbom-backend.json", "."
            ], cwd=self.backend_root)
            
            if exit_code != 0:
                print(f"❌ Python SBOM generation failed: {stderr}")
                return False
            
            # Node.js SBOM
            exit_code, stdout, stderr = self.run_command([
                "npx", "@cyclonedx/cyclonedx-npm", "-o", "sbom-frontend.json"
            ])
            
            if exit_code != 0:
                print(f"❌ Node.js SBOM generation failed: {stderr}")
                return False
            
            print("✅ SBOM generation completed")
            return True
            
        except Exception as e:
            print(f"❌ SBOM generation failed: {e}")
            return False
    
    def run_all_checks(self) -> bool:
        """Run all quality checks"""
        print("🚀 Starting quality checks for BOLT AI Neural Agent System")
        print("=" * 60)
        
        checks = [
            self.check_python_linting,
            self.check_typescript_linting,
            self.check_security,
            self.check_dependencies,
        ]
        
        all_passed = True
        for check in checks:
            if not check():
                all_passed = False
        
        # Generate SBOM
        self.generate_sbom()
        
        self.results["overall"]["passed"] = all_passed
        
        # Print summary
        print("\n" + "=" * 60)
        print("QUALITY CHECK SUMMARY")
        print("=" * 60)
        
        for check_name, result in self.results.items():
            if check_name == "overall":
                continue
            
            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            print(f"{check_name.replace('_', ' ').title()}: {status}")
            
            if not result["passed"] and result["issues"]:
                for issue in result["issues"]:
                    print(f"  - {issue['message']}")
        
        print(f"\nOverall Status: {'✅ PASSED' if all_passed else '❌ FAILED'}")
        
        return all_passed
    
    def save_results(self, output_file: Path):
        """Save results to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Results saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Quality checker for BOLT AI Neural Agent System")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root directory")
    parser.add_argument("--output", type=Path, help="Output file for results")
    parser.add_argument("--check", choices=["python", "typescript", "security", "dependencies", "all"], 
                       default="all", help="Specific check to run")
    
    args = parser.parse_args()
    
    checker = QualityChecker(args.project_root)
    
    if args.check == "python":
        success = checker.check_python_linting()
    elif args.check == "typescript":
        success = checker.check_typescript_linting()
    elif args.check == "security":
        success = checker.check_security()
    elif args.check == "dependencies":
        success = checker.check_dependencies()
    else:
        success = checker.run_all_checks()
    
    if args.output:
        checker.save_results(args.output)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
