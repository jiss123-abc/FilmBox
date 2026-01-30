import traceback
try:
    from verify_phase_18 import verify_churn_detection
    verify_churn_detection()
except Exception:
    traceback.print_exc()
