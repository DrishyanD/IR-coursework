"""Keeps the weekly crawler schedule and manual run jobs in one place."""

from inspect import signature

from apscheduler.schedulers.background import BackgroundScheduler


class CrawlerScheduler:
    JOB_ID = "weekly_coventry_crawl"

    def __init__(self, update_service):
        self.update_service = update_service
        # The scheduler stays running so manual updates still work when the weekly job is disabled.
        self.scheduler = BackgroundScheduler(timezone="UTC")

    def configure_weekly_job(self, configuration: dict):
        self.scheduler.add_job(
            self._run_scheduled,
            trigger="cron",
            day_of_week=configuration["day_of_week"],
            hour=configuration["hour"],
            minute=configuration["minute"],
            timezone=configuration["timezone"],
            id=self.JOB_ID,
            name="Weekly Coventry publication crawl and index update",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )

    def _run_scheduled(self):
        if getattr(self.update_service, "current_run_id", None) is not None:
            return {"status": "skipped", "reason": "crawl_already_running"}

        parameters = signature(self.update_service.run).parameters
        if "trigger_type" in parameters:
            return self.update_service.run(trigger_type="scheduled")
        return self.update_service.run()

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()

    def apply_configuration(self, configuration: dict):
        if configuration["enabled"]:
            self.configure_weekly_job(configuration)
        else:
            self.disable_weekly_job()

    def disable_weekly_job(self):
        job = self.get_job()
        if job is not None:
            self.scheduler.remove_job(job.id)

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def get_job(self):
        return self.scheduler.get_job(self.JOB_ID)

    def run_now(self):
        parameters = signature(self.update_service.run).parameters
        if "trigger_type" in parameters:
            return self.update_service.run(trigger_type="manual")
        return self.update_service.run()
