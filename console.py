from rich.console import Console
from rich.theme import Theme

custom_theme = Theme(
    {
        "keyword": "bold yellow",
        "debug": "green",
        "info": "blue",
        "warning": "magenta",
        "danger": "bold red",
        "error": "bold red",
        "critical": "bold reverse red",
    }
)
console = Console(theme=custom_theme)
