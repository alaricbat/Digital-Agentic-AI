class Event:

    def __init__(self, time, event_type, machine_id, job_id= None):
        self.time = time
        self.event_type = event_type
        self.machine_id = machine_id
        self.job_id = job_id

    def __repr__(self):
        return f"[Time {self.time:.1f}] {self.event_type} on M{self.machine_id} (Job: {self.job_id})"