import threading
from queue import Queue, Empty
import requests
import os

from dotenv import load_dotenv
from SaveDTRLog import SaveDTRLog

#from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AttendanceQueueProcessor:
    """Handles background task queue processing"""
    
    def __init__(self) -> None:
        self.task_queue: Queue[SaveDTRLog] = Queue()
        self.worker_thread = None
        self.is_running = False
        
        # Validate that TARGET_API_URL is set

        dtr_api_dns: str | None = os.getenv('PAYROLL_API_DNS')
        hris_api_dns: str | None = os.getenv('HRIS_API_DNS')
        ouid = os.getenv('OUID')

        if not dtr_api_dns:
            raise ValueError("PAYROLL_API_DNS environment variable is not set")

        if not hris_api_dns:
            raise ValueError("HRIS_API_DNS environment variable is not set")

        if not ouid:
            raise ValueError("OUID environment variable is not set")

        self.dtr_api_dns: str = dtr_api_dns
        self.hris_api_dns: str = hris_api_dns
        self.OUID: int = int(ouid)
    
    def start(self) -> None:
        """Start the background worker thread"""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
            self.worker_thread.start()
            print(f"Task queue processor started, sending to: {self.dtr_api_dns}")
    
    def stop(self) -> None:
        """Stop the background worker thread"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
            print("Task queue processor stopped")
    
    def add_task(self, task_data) -> None:
        """Add a task to the queue"""
        self.task_queue.put(task_data)
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self.task_queue.qsize()
    
    def _process_queue(self):
        """Background worker that processes items from the queue"""
        while self.is_running:
            try:
                # Get item from queue (blocks until item is available)
                attendance_data = self.task_queue.get(timeout=1)

                # Process the task - send to external API
                try:
                    print(f"Processing task: {attendance_data}")

                    # Send to your external API endpoint
                    print(f"Saving employee {attendance_data.ScanningNo} dtr logs...")
                    response = requests.post(
                        self.dtr_api_dns + 'dtr/save-dtr-log',
                        json=attendance_data.gen_save_dtr_log_payload(),
                        timeout=30
                    )

                    print(f"Setting employee {attendance_data.ScanningNo} attendance...")
                    response = requests.post(
                        self.hris_api_dns + 'employee/attendance/setEmployeeAttendance',
                        json=attendance_data.gen_set_employee_attendance_payload(),
                        timeout=30
                    )

                    print(f"Task completed: Status Code: {response.status_code}")
                    print(f"{response.content}")

                except Exception as e:
                    self.task_queue.put(attendance_data)
                    print(f"Error processing task: {e}")

                finally:
                    # Mark task as done
                    self.task_queue.task_done()

            except Empty:
                # No tasks in queue, continue loop
                continue
