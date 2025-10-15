"""
Crash dump generation for BOLT AI Neural Agent System
"""

import json
import os
import signal
import sys
import threading
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
import structlog

logger = structlog.get_logger(__name__)


class CrashDumpGenerator:
    """Crash dump generator for debugging and analysis"""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("crash_dumps")
        self.output_dir.mkdir(exist_ok=True)

        # Setup signal handlers
        self._setup_signal_handlers()

        # Thread information
        self.main_thread = threading.current_thread()

        logger.info("Crash dump generator initialized", output_dir=str(self.output_dir))

    def _setup_signal_handlers(self):
        """Setup signal handlers for crash detection"""
        # SIGTERM handler
        signal.signal(signal.SIGTERM, self._signal_handler)

        # SIGINT handler (Ctrl+C)
        signal.signal(signal.SIGINT, self._signal_handler)

        # SIGABRT handler
        signal.signal(signal.SIGABRT, self._signal_handler)

        # SIGFPE handler (floating point exception)
        signal.signal(signal.SIGFPE, self._signal_handler)

        # SIGSEGV handler (segmentation fault)
        signal.signal(signal.SIGSEGV, self._signal_handler)

        # SIGILL handler (illegal instruction)
        signal.signal(signal.SIGILL, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Signal handler for crash detection"""
        signal_name = signal.Signals(signum).name
        logger.critical(f"Received signal: {signal_name}", signal_number=signum)

        # Generate crash dump
        self.generate_crash_dump(
            crash_type="signal",
            signal_name=signal_name,
            signal_number=signum,
            frame=frame,
        )

        # Re-raise the signal
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)

    def generate_crash_dump(
        self, crash_type: str = "exception", exception: Exception = None, **kwargs
    ) -> Path:
        """Generate crash dump file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        crash_file = self.output_dir / f"crash_dump_{timestamp}.json"

        try:
            # Collect crash information
            crash_info = self._collect_crash_info(crash_type, exception, **kwargs)

            # Write crash dump
            with open(crash_file, "w") as f:
                json.dump(crash_info, f, indent=2, default=str)

            logger.critical("Crash dump generated", crash_file=str(crash_file))
            return crash_file

        except Exception as e:
            logger.error("Failed to generate crash dump", error=str(e))
            return None

    def _collect_crash_info(
        self, crash_type: str, exception: Exception = None, **kwargs
    ) -> Dict[str, Any]:
        """Collect comprehensive crash information"""
        crash_info = {
            "timestamp": datetime.now().isoformat(),
            "crash_type": crash_type,
            "application": {
                "name": "BOLT AI Neural Agent System",
                "version": "1.0.0",
                "python_version": sys.version,
                "platform": sys.platform,
            },
            "system": self._collect_system_info(),
            "process": self._collect_process_info(),
            "threads": self._collect_thread_info(),
            "memory": self._collect_memory_info(),
            "environment": self._collect_environment_info(),
            "traceback": self._collect_traceback_info(exception),
            "additional_info": kwargs,
        }

        return crash_info

    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information"""
        try:
            return {
                "cpu_count": psutil.cpu_count(),
                "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "platform": sys.platform,
                "architecture": (
                    os.uname().machine if hasattr(os, "uname") else "unknown"
                ),
            }
        except Exception as e:
            return {"error": str(e)}

    def _collect_process_info(self) -> Dict[str, Any]:
        """Collect process information"""
        try:
            process = psutil.Process()
            return {
                "pid": process.pid,
                "ppid": process.ppid(),
                "name": process.name(),
                "status": process.status(),
                "create_time": datetime.fromtimestamp(
                    process.create_time()
                ).isoformat(),
                "cpu_percent": process.cpu_percent(),
                "memory_info": process.memory_info()._asdict(),
                "memory_percent": process.memory_percent(),
                "num_threads": process.num_threads(),
                "open_files": len(process.open_files()),
                "connections": len(process.connections()),
            }
        except Exception as e:
            return {"error": str(e)}

    def _collect_thread_info(self) -> List[Dict[str, Any]]:
        """Collect thread information"""
        threads = []

        try:
            for thread in threading.enumerate():
                thread_info = {
                    "name": thread.name,
                    "ident": thread.ident,
                    "is_alive": thread.is_alive(),
                    "is_daemon": thread.daemon,
                    "is_main_thread": thread is self.main_thread,
                }
                threads.append(thread_info)
        except Exception as e:
            threads.append({"error": str(e)})

        return threads

    def _collect_memory_info(self) -> Dict[str, Any]:
        """Collect memory information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            return {
                "virtual_memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free,
                },
                "swap_memory": {
                    "total": swap.total,
                    "used": swap.used,
                    "free": swap.free,
                    "percent": swap.percent,
                },
            }
        except Exception as e:
            return {"error": str(e)}

    def _collect_environment_info(self) -> Dict[str, Any]:
        """Collect environment information"""
        try:
            # Get relevant environment variables
            env_vars = {}
            relevant_vars = [
                "PATH",
                "PYTHONPATH",
                "LD_LIBRARY_PATH",
                "CUDA_VISIBLE_DEVICES",
                "TENSORFLOW_VISIBLE_DEVICES",
                "OMP_NUM_THREADS",
                "MKL_NUM_THREADS",
            ]

            for var in relevant_vars:
                if var in os.environ:
                    env_vars[var] = os.environ[var]

            return {
                "working_directory": os.getcwd(),
                "environment_variables": env_vars,
                "python_path": sys.path,
            }
        except Exception as e:
            return {"error": str(e)}

    def _collect_traceback_info(self, exception: Exception = None) -> Dict[str, Any]:
        """Collect traceback information"""
        try:
            if exception:
                return {
                    "exception_type": type(exception).__name__,
                    "exception_message": str(exception),
                    "traceback": traceback.format_exc(),
                    "traceback_lines": traceback.format_exc().splitlines(),
                }
            else:
                # Get current traceback
                tb = traceback.format_stack()
                return {"current_traceback": tb, "traceback_lines": tb}
        except Exception as e:
            return {"error": str(e)}

    def generate_memory_dump(self) -> Path:
        """Generate memory dump for analysis"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        memory_file = self.output_dir / f"memory_dump_{timestamp}.json"

        try:
            process = psutil.Process()
            memory_info = {
                "timestamp": datetime.now().isoformat(),
                "process_info": {
                    "pid": process.pid,
                    "name": process.name(),
                    "memory_info": process.memory_info()._asdict(),
                    "memory_percent": process.memory_percent(),
                },
                "system_memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent,
                },
                "threads": [
                    {
                        "name": thread.name,
                        "ident": thread.ident,
                        "is_alive": thread.is_alive(),
                    }
                    for thread in threading.enumerate()
                ],
            }

            with open(memory_file, "w") as f:
                json.dump(memory_info, f, indent=2, default=str)

            logger.info("Memory dump generated", memory_file=str(memory_file))
            return memory_file

        except Exception as e:
            logger.error("Failed to generate memory dump", error=str(e))
            return None

    def generate_performance_dump(self) -> Path:
        """Generate performance dump for analysis"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        performance_file = self.output_dir / f"performance_dump_{timestamp}.json"

        try:
            process = psutil.Process()
            performance_info = {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "process_cpu_percent": process.cpu_percent(),
                    "system_cpu_percent": psutil.cpu_percent(),
                    "cpu_count": psutil.cpu_count(),
                },
                "memory": {
                    "process_memory": process.memory_info()._asdict(),
                    "process_memory_percent": process.memory_percent(),
                    "system_memory": psutil.virtual_memory()._asdict(),
                },
                "disk": {"disk_usage": psutil.disk_usage("/")._asdict()},
                "network": {"io_counters": psutil.net_io_counters()._asdict()},
                "process": {
                    "num_threads": process.num_threads(),
                    "open_files": len(process.open_files()),
                    "connections": len(process.connections()),
                },
            }

            with open(performance_file, "w") as f:
                json.dump(performance_info, f, indent=2, default=str)

            logger.info(
                "Performance dump generated", performance_file=str(performance_file)
            )
            return performance_file

        except Exception as e:
            logger.error("Failed to generate performance dump", error=str(e))
            return None

    def cleanup_old_dumps(self, max_age_days: int = 30):
        """Clean up old crash dumps"""
        try:
            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 3600)

            for dump_file in self.output_dir.glob("*.json"):
                if dump_file.stat().st_mtime < cutoff_time:
                    dump_file.unlink()
                    logger.info("Cleaned up old crash dump", file=str(dump_file))

        except Exception as e:
            logger.error("Failed to cleanup old dumps", error=str(e))


# Global crash dump generator instance
crash_dump_generator = CrashDumpGenerator()


def get_crash_dump_generator() -> CrashDumpGenerator:
    """Get global crash dump generator instance"""
    return crash_dump_generator


# Exception handler decorator
def handle_exceptions(func):
    """Decorator to handle exceptions and generate crash dumps"""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Generate crash dump
            crash_dump_generator.generate_crash_dump(
                crash_type="exception",
                exception=e,
                function_name=func.__name__,
                args=args,
                kwargs=kwargs,
            )

            # Re-raise the exception
            raise

    return wrapper


# Context manager for crash dump generation
class CrashDumpContext:
    """Context manager for crash dump generation"""

    def __init__(self, context_name: str, **context_info):
        self.context_name = context_name
        self.context_info = context_info
        self.start_time = datetime.now()

    def __enter__(self):
        logger.info(f"Entering context: {self.context_name}", **self.context_info)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()

        if exc_type:
            # Generate crash dump for exception
            crash_dump_generator.generate_crash_dump(
                crash_type="context_exception",
                exception=exc_val,
                context_name=self.context_name,
                context_info=self.context_info,
                duration_seconds=duration,
            )
            logger.error(
                f"Exception in context: {self.context_name}",
                exception=str(exc_val),
                duration=duration,
            )
        else:
            logger.info(f"Exiting context: {self.context_name}", duration=duration)

        return False  # Don't suppress exceptions
