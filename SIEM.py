import os
import platform
import re
from dataclasses import dataclass
from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Input, Static, Footer, Label
from textual.binding import Binding
from rich.text import Text

# ---------------------------------------------------------------------------
# Data Model & Parsing
# ---------------------------------------------------------------------------

@dataclass
class LogEntry:
    timestamp: str
    level: str
    source: str
    message: str
    raw: str

def get_system_log_paths() -> list[str]:
    """Identifies log file locations based on the operating system."""
    sys_name = platform.system()
    if sys_name == "Darwin": # macOS
        return ["/var/log/system.log", "/var/log/wifi.log", "/var/log/install.log"]
    elif sys_name == "Linux":
        return ["/var/log/syslog", "/var/log/auth.log", "/var/log/kern.log"]
    return []

def parse_log_line(line: str, source_file: str) -> LogEntry:
    """Parses raw text into structured log data."""
    clean_line = line.strip()
    
    # 1. Determine Severity
    lower_line = clean_line.lower()
    level = "INFO"
    if any(x in lower_line for x in ["error", "fail", "deny", "crit", "fatal"]):
        level = "ERROR"
    elif "warn" in lower_line:
        level = "WARNING"

    # 2. Extract Timestamp (Standard syslog/macOS format)
    timestamp = "-"
    match = re.match(r'^([A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2})', clean_line)
    if match:
        timestamp = match.group(1)
        message = clean_line[match.end():].strip()
    else:
        message = clean_line

    return LogEntry(
        timestamp=timestamp,
        level=level,
        source=os.path.basename(source_file),
        message=message,
        raw=clean_line
    )

# ---------------------------------------------------------------------------
# UI Widgets
# ---------------------------------------------------------------------------

class Banner(Static):
    """Banner styled as shown in the template."""
    def __init__(self, os_name: str):
        super().__init__(f"━━━ SIEM rīks - <{os_name}> ━━━")

class CommandsPanel(Static):
    """Right-side command list with a dashed border."""
    def render(self) -> Text:
        t = Text("Commands list\n\n", style="bold", justify="center")
        t.append("Global:\n", style="bold underline")
        t.append("  [Ctrl+Q]  Quit\n")
        t.append("  [Ctrl+L]  Add custom log\n\n")
        t.append("Filtering Syntax:\n", style="bold underline")
        t.append("  @source  ", style="cyan")
        t.append("Filter by file\n")
        t.append("  %LEVEL   ", style="bold red")
        t.append("Filter by severity\n")
        t.append("  text     ", style="white")
        t.append("General search\n\n")
        t.append("Example:\n", style="dim italic")
        t.append("  @system.log %ERROR failed", style="dim")
        return t

# ---------------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------------

class SIEMApp(App):
    # CSS fixed to avoid variable parsing errors in border properties
    CSS = """
    Screen { background: $surface-darken-2; layout: vertical; }
    
    Banner {
        content-align: center middle;
        height: 3;
        color: #7b61ff;
        text-style: bold;
    }

    #main-container { layout: horizontal; height: 1fr; }

    #left-pane { width: 3fr; layout: vertical; padding: 1; }

    #filter-input { dock: top; margin-bottom: 1; }

    DataTable {
        height: 1fr;
        border: solid gray;
    }

    #right-pane {
        width: 1fr;
        border: dashed gray; 
        background: $surface;
        margin: 1 2 1 1;
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+l", "load_custom", "Load Custom")
    ]

    def __init__(self):
        super().__init__()
        self.log_lake: list[LogEntry] = []
        self.os_name = platform.system()

    def compose(self) -> ComposeResult:
        yield Banner(self.os_name)
        with Horizontal(id="main-container"):
            with Vertical(id="left-pane"):
                yield Input(placeholder="Search logs... (@file %LEVEL search)", id="filter-input")
                yield DataTable(id="log-table")
            yield CommandsPanel(id="right-pane")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("Time", "Level", "Source", "Message")

        # Automatically ingest system logs
        self.ingest_logs(get_system_log_paths())
        self.refresh_table()

    def ingest_logs(self, file_paths: list[str]) -> None:
        """Copies and parses log files into the analysis engine."""
        for path in file_paths:
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", errors="ignore") as f:
                    lines = f.readlines()[-2000:] # Limit for performance
                    for line in lines:
                        if line.strip():
                            self.log_lake.append(parse_log_line(line, path))
            except PermissionError:
                # Log the permission error directly into the UI table
                self.log_lake.append(LogEntry("-", "ERROR", os.path.basename(path), "Permission denied (Run with sudo)", ""))
        
        # Keep newest logs at top
        self.log_lake.sort(key=lambda x: x.timestamp, reverse=True)

    def refresh_table(self, filter_query: str = "") -> None:
        """Applies multi-parameter filtering to the ingested data."""
        table = self.query_one(DataTable)
        table.clear()

        query_source = None
        query_level = None
        query_text = []

        for term in filter_query.split():
            if term.startswith("@"): query_source = term[1:].lower()
            elif term.startswith("%"): query_level = term[1:].upper()
            else: query_text.append(term.lower())

        for log in self.log_lake:
            if query_source and query_source not in log.source.lower(): continue
            if query_level and query_level != log.level: continue
            if query_text and not all(t in log.raw.lower() for t in query_text): continue

            # Severity styling
            styles = {"ERROR": "bold red", "WARNING": "bold yellow", "INFO": "green"}
            level_text = Text(f"[{log.level}]", style=styles.get(log.level, "white"))
            
            table.add_row(log.timestamp, level_text, log.source, log.message[:150])

    def on_input_changed(self, event: Input.Changed) -> None:
        """Real-time table updates as you type."""
        self.refresh_table(event.value)

    def action_load_custom(self) -> None:
        """Simulates loading a custom file."""
        self.notify("Load custom feature active. Place log in project root.", severity="information")

if __name__ == "__main__":
    SIEMApp().run()