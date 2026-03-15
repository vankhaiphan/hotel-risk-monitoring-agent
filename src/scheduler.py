import schedule
import time
from datetime import datetime
from src.main import HotelRiskMonitoringAgent

class MonitoringScheduler:
    """Scheduler for daily monitoring runs."""
    
    def __init__(self, run_time: str = "09:00"):
        """
        Initialize scheduler.
        
        Args:
            run_time: Time to run daily monitoring in HH:MM format (24-hour)
        """
        self.run_time = run_time
        self.agent = HotelRiskMonitoringAgent()
    
    def schedule_daily_run(self):
        """Schedule the monitoring to run daily at specified time."""
        schedule.every().day.at(self.run_time).do(self._run_job)
        print(f"✓ Monitoring scheduled for {self.run_time} daily")
    
    def _run_job(self):
        """Job wrapper with error handling."""
        try:
            print(f"\nScheduled run starting at {datetime.now().isoformat()}")
            self.agent.run_monitoring()
        except Exception as e:
            print(f"✗ Error during scheduled run: {e}")
            import traceback
            traceback.print_exc()
    
    def start(self):
        """Start the scheduler (blocking)."""
        print("Starting Hotel Risk Monitoring Agent - Scheduler Mode")
        print(f"Scheduled to run daily at {self.run_time}")
        print("Press Ctrl+C to stop\n")
        
        self.schedule_daily_run()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n✓ Scheduler stopped by user")
    
    def run_once(self):
        """Run monitoring once (useful for testing)."""
        self._run_job()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Hotel Risk Monitoring Agent')
    parser.add_argument('--mode', choices=['once', 'daemon'], default='daemon',
                       help='Run once or as daemon scheduler')
    parser.add_argument('--time', default='09:00',
                       help='Daily run time (HH:MM format, 24-hour)')
    
    args = parser.parse_args()
    
    scheduler = MonitoringScheduler(run_time=args.time)
    
    if args.mode == 'once':
        scheduler.run_once()
    else:
        scheduler.start()


if __name__ == '__main__':
    main()
