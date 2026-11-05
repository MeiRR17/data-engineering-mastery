"""Stage 12 student exercise. No external services or sensitive data."""
def authorize(role,action):
    raise NotImplementedError("Implement least-privilege action matrix")

def compute_slo(runs,events,now,policy):
    raise NotImplementedError("Compute SLO, freshness and error budget")

def forecast_cost(events_per_day,bytes_per_event,retention_days,
                  price_per_gib_month,compute_hours,compute_rate):
    raise NotImplementedError("Define bounded cost scenarios with explicit units")

def backup_database(source,directory,label):
    raise NotImplementedError("Create verified immutable backup + digest")

def verify_backup(archive,manifest):
    raise NotImplementedError("Validate backup SHA, schema and row count")

def restore_to_new(archive,manifest,destination):
    raise NotImplementedError("Restore only to a new file; never overwrite live state")

