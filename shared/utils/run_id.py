from datetime import datetime
import uuid


def generate_run_id():
    """
    Generates a unique, human-readable run ID.

    Example:
    RUN-20260805-132315-A83F19
    """

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    suffix = uuid.uuid4().hex[:6].upper()

    return f"RUN-{timestamp}-{suffix}"