import enum

class JobStatus(enum.Enum):
    """Class for job status enumerated type."""
    QUEUED = "In queue"
    RUNNING = "Actively running"
    DONE = "Done"
    CANCELLED = "Cancelled"
    ERROR = "Error"


JOB_FINAL_STATES = (JobStatus.DONE, JobStatus.CANCELLED, JobStatus.ERROR)
