import shlex
from typing import List, Optional

# Allowlisted commands and their subcommands if applicable
ALLOWLIST = {
    "kubectl": ["get", "describe", "logs", "top", "events"],
    "ps": [],
    "top": [],
    "free": [],
    "df": [],
    "du": [],
    "uptime": [],
    "uname": [],
    "hostname": [],
    "env": [],
    "ss": [],
    "netstat": [],
    "ip": [],
    "ping": [],
    "dig": [],
    "nslookup": [],
    "traceroute": [],
    "lsof": [],
    "journalctl": [],
    "cat": [],
    "tail": [],
    "docker": ["ps", "inspect", "logs", "stats"],
    "mount": [],
    "lsblk": [],
    "pvs": [],
    "vgs": [],
    "lvs": [],
}

# Explicitly blocked patterns or arguments to avoid escapes
BLOCKLIST_PATTERNS = [
    ">", ">>", "|", "&", ";", "`", "$", "(", ")", "{", "}", "[", "]", "*", "?", "!", "\\",
    "sudo", "su", "chmod", "chown", "rm", "mv", "cp", "dd", "mkfs", "fdisk", "parted", "wipefs",
    "iptables", "systemctl", "reboot", "shutdown", "halt", "poweroff"
]

def validate_command(command_str: str) -> bool:
    """ Validates a command against the allowlist and blocklist. """
    try:
        args = shlex.split(command_str)
        if not args:
            return False
            
        base_cmd = args[0]
        
        # Check if base command is in allowlist
        if base_cmd not in ALLOWLIST:
            return False
            
        # If the command has required subcommands (e.g., kubectl, docker)
        required_subcmds = ALLOWLIST[base_cmd]
        if required_subcmds:
            if len(args) < 2 or args[1] not in required_subcmds:
                return False

        # Additional hygiene: No shell metacharacters or redirections allowed
        # (Though shlex.split helps, we want to be explicit)
        for arg in args:
            for pattern in BLOCKLIST_PATTERNS:
                if pattern in arg:
                    return False
        
        return True
    except Exception:
        return False

def clean_command(command_str: str) -> List[str]:
    """ Parses a command into a list of arguments for safe subprocess execution. """
    return shlex.split(command_str)
