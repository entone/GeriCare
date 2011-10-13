import subprocess, os

class MemoryMonitor(object):

    def __init__(self):
        """Create new MemoryMonitor instance."""
        self.pid = os.getpid()

    def usage(self):
        """Return int containing memory used by user's processes."""
        self.process = subprocess.Popen("ps -p %s -o rss | awk '{sum+=$1} END {print sum}'" % self.pid,
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        )
        self.stdout_list = self.process.communicate()[0].split('\n')
        return int(self.stdout_list[0])
