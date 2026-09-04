"""
Comprehensive test runner for Carbon Market Intelligence platform.
Runs all tests and provides a summary report.
"""

import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=ROOT,
            shell=True,
            capture_output=False,
            text=True
        )
        success = result.returncode == 0
        if success:
            print(f"✓ {description} PASSED")
        else:
            print(f"✗ {description} FAILED (exit code: {result.returncode})")
        return success
    except Exception as e:
        print(f"✗ {description} FAILED: {e}")
        return False


def main():
    """Run all tests and generate report."""
    print("="*60)
    print("CARBON MARKET INTELLIGENCE - TEST SUITE")
    print("="*60)
    
    results = []
    
    # Test 1: Phase 3 Model Validation
    results.append(("Phase 3 Model Validation", run_command(
        "python test_phase3_models.py",
        "Phase 3 Model Validation"
    )))
    
    # Test 2: Backend API Tests
    results.append(("Backend API Tests", run_command(
        "python test_backend.py",
        "Backend API Tests"
    )))
    
    # Generate summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "-"*60)
    print(f"Total: {passed}/{total} test suites passed")
    print("-"*60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nNext steps:")
        print("1. Start backend: python run_backend.py")
        print("2. Install frontend: cd frontend && npm install")
        print("3. Start frontend: npm run dev")
        print("4. Open browser: http://localhost:3000")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Please review the errors above and fix before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
