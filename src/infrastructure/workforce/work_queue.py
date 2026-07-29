import logging
from typing import Dict, Any, List, Optional
import time

logger = logging.getLogger("document_intelligence.work_queue")


class WorkQueueManager:
    """Manages Departmental Work Queues, Task Priority Scheduling & Workload Balancing."""

    def __init__(self):
        self.queues: Dict[str, List[Dict[str, Any]]] = {
            "Finance": [],
            "Legal": [],
            "HR": [],
            "Operations": [],
        }

    def enqueue_task(self, department: str, task_name: str, payload: Dict[str, Any], priority: str = "medium") -> Dict[str, Any]:
        task_id = f"task_q_{int(time.time() * 1000)}"
        item = {
            "task_id": task_id,
            "task_name": task_name,
            "department": department,
            "payload": payload,
            "priority": priority,
            "status": "queued",
            "enqueued_at": time.time(),
        }

        if department not in self.queues:
            self.queues[department] = []
        self.queues[department].append(item)

        logger.info(f"Enqueued Task '{task_id}' ({task_name}) into Department Queue '{department}' [Priority: {priority}]")
        return item

    def get_queue_status(self, department: Optional[str] = None) -> Dict[str, Any]:
        if department:
            return {
                "department": department,
                "pending_tasks_count": len(self.queues.get(department, [])),
                "tasks": self.queues.get(department, []),
            }
        total_pending = sum(len(q) for q in self.queues.values())
        return {
            "total_pending_tasks": total_pending,
            "departments": {dept: len(tasks) for dept, tasks in self.queues.items()},
        }
