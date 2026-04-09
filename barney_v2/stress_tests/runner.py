"""
Runner: The orchestrator for cognitive stress tests.
(Stress Test Layer #11)
"""

import sys
import os

# Add barney_v2 to path for core imports (Step #11 Fix)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stress_tests.scenarios import confident_idiot


def run_all_scenarios():
    """Main Entry Point for Judgment Day."""
    print("\n" + "="*80)
    print(" 🧠 JUDGMENT DAY: barney_v2 BRUTAL STRESS TESTS 🧠 ")
    print("="*80)
    
    # 1. RUN CONFIDENT IDIOT v2
    confident_idiot.run()
    
    print("\n" + "="*80)
    print(" 🏁 STRESS TESTS COMPLETE 🏁 ")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_all_scenarios()
