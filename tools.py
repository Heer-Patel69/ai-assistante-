import os
import subprocess
import shutil
import glob
import requests
from docx import Document

# === Full system access — no sandbox ===
DESKTOP = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
DEFAULT_DIR = DESKTOP  # Default working directory


# --- File & Folder Tools ---

def create_folder(path):
    """Create a folder at the given path. Supports absolute or relative (to Desktop)."""
    if not os.path.isabs(path):
        path = os.path.join(DEFAULT_DIR, path)
    os.makedirs(path, exist_ok=True)
    return f"✅ Folder created: {path}"


def delete_path(path):
    """Delete a file or folder. Supports absolute or relative (to Desktop)."""
    if not os.path.isabs(path):
        path = os.path.join(DEFAULT_DIR, path)
    if os.path.isdir(path):
        shutil.rmtree(path)
        return f"✅ Folder deleted: {path}"
    elif os.path.isfile(path):
        os.remove(path)
        return f"✅ File deleted: {path}"
    return f"❌ Path not found: {path}"


def list_files(folder=""):
    """List files and folders. Defaults to Desktop if no path given."""
    path = folder if folder and os.path.isabs(folder) else os.path.join(DEFAULT_DIR, folder)
    if not os.path.exists(path):
        return f"❌ Path not found: {path}"
    items = os.listdir(path)
    if not items:
        return f"📂 {path} is empty."
    lines = [f"📂 {path}:"]
    for i in sorted(items):
        full = os.path.join(path, i)
        icon = "📁" if os.path.isdir(full) else "📄"
        size = ""
        if os.path.isfile(full):
            s = os.path.getsize(full)
            size = f" ({s:,} bytes)"
        lines.append(f"  {icon} {i}{size}")
    return "\n".join(lines)


def move_file(src_and_dst):
    """Move/rename a file or folder. Input: 'source | destination'."""
    parts = src_and_dst.split(" | ", 1)
    if len(parts) != 2:
        return "❌ Format: source | destination"
    src, dst = parts[0].strip(), parts[1].strip()
    if not os.path.isabs(src):
        src = os.path.join(DEFAULT_DIR, src)
    if not os.path.isabs(dst):
        dst = os.path.join(DEFAULT_DIR, dst)
    shutil.move(src, dst)
    return f"✅ Moved: {src} → {dst}"


def copy_file(src_and_dst):
    """Copy a file or folder. Input: 'source | destination'."""
    parts = src_and_dst.split(" | ", 1)
    if len(parts) != 2:
        return "❌ Format: source | destination"
    src, dst = parts[0].strip(), parts[1].strip()
    if not os.path.isabs(src):
        src = os.path.join(DEFAULT_DIR, src)
    if not os.path.isabs(dst):
        dst = os.path.join(DEFAULT_DIR, dst)
    if os.path.isdir(src):
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)
    return f"✅ Copied: {src} → {dst}"


def read_file(filepath):
    """Read and return the contents of a text file."""
    if not os.path.isabs(filepath):
        filepath = os.path.join(DEFAULT_DIR, filepath)
    if not os.path.isfile(filepath):
        return f"❌ File not found: {filepath}"
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    # Limit output to avoid flooding
    if len(content) > 2000:
        return content[:2000] + f"\n\n... (truncated, {len(content)} total chars)"
    return content


def organize_files(folder=""):
    """Organize files by grouping them into subfolders by extension."""
    path = folder if folder and os.path.isabs(folder) else os.path.join(DEFAULT_DIR, folder)
    if not os.path.exists(path):
        return f"❌ Path not found: {path}"

    moved = 0
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            ext = os.path.splitext(item)[1].lstrip(".").upper() or "NO_EXT"
            ext_folder = os.path.join(path, ext)
            os.makedirs(ext_folder, exist_ok=True)
            shutil.move(item_path, os.path.join(ext_folder, item))
            moved += 1

    return f"✅ Organized {moved} files into subfolders by type in {path}"


def search_files(query):
    """Search for files by name pattern. Input: 'pattern' or 'pattern | directory'."""
    parts = query.split(" | ", 1)
    pattern = parts[0].strip()
    search_dir = parts[1].strip() if len(parts) > 1 else DEFAULT_DIR

    if not os.path.isabs(search_dir):
        search_dir = os.path.join(DEFAULT_DIR, search_dir)

    results = []
    for root, dirs, files in os.walk(search_dir):
        for f in files:
            if pattern.lower() in f.lower():
                results.append(os.path.join(root, f))
                if len(results) >= 20:
                    break
        if len(results) >= 20:
            break

    if not results:
        return f"❌ No files matching '{pattern}' found in {search_dir}"
    return "🔍 Found:\n" + "\n".join(f"  📄 {r}" for r in results)


# --- App Launcher Tools ---

def open_app(app_name):
    """Open any application by name (e.g., notepad, calc, code, chrome)."""
    subprocess.Popen(app_name, shell=True)
    return f"✅ Opened {app_name}"


def open_vscode(path=""):
    """Open Visual Studio Code, optionally with a file or folder path."""
    cmd = f'code "{path}"' if path else "code"
    subprocess.Popen(cmd, shell=True)
    return f"✅ Opened VS Code{' with ' + path if path else ''}"


def open_terminal():
    """Open a new terminal / command prompt window."""
    subprocess.Popen("start cmd", shell=True)
    return "✅ Opened terminal"


# --- Document Tools ---

def create_document(args):
    """Create a Word document (.docx). Input: 'filename | content'."""
    parts = args.split(" | ", 1)
    if len(parts) != 2:
        return "❌ Format: filename | content"
    filename, content = parts[0].strip(), parts[1].strip()
    if not filename.endswith(".docx"):
        filename += ".docx"
    if not os.path.isabs(filename):
        filename = os.path.join(DEFAULT_DIR, filename)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc = Document()
    for line in content.split("\n"):
        doc.add_paragraph(line)
    doc.save(filename)
    return f"✅ Document created: {filename}"


def create_text_file(args):
    """Create/write a text file. Input: 'filename | content'."""
    parts = args.split(" | ", 1)
    if len(parts) != 2:
        return "❌ Format: filename | content"
    filename, content = parts[0].strip(), parts[1].strip()
    if not os.path.isabs(filename):
        filename = os.path.join(DEFAULT_DIR, filename)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return f"✅ File created: {filename}"


# --- Internet Tools ---

def get_public_ip():
    """Fetch the user's public IP address from the internet."""
    return str(requests.get("https://api64.ipify.org?format=json").json())


# --- Terminal Tools ---

def run_terminal_command(command):
    """Run any terminal/shell command and return the output."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        output = result.stdout or result.stderr
        if len(output) > 2000:
            output = output[:2000] + "\n...(truncated)"
        return f"✅ Output:\n{output}"
    except subprocess.TimeoutExpired:
        return "❌ Command timed out (30s limit)."
    except Exception as e:
        return f"❌ Error: {e}"


# ============================================
# TOOL REGISTRY — AI reads these to auto-select
# ============================================

TOOL_REGISTRY = [
    {
        "name": "create_folder",
        "func": create_folder,
        "description": "Create a folder. Input: folder path (absolute or relative to Desktop).",
    },
    {
        "name": "delete_path",
        "func": delete_path,
        "description": "Delete a file or folder. Input: path (absolute or relative to Desktop).",
    },
    {
        "name": "list_files",
        "func": list_files,
        "description": "List files in a directory. Input: path (defaults to Desktop if empty).",
    },
    {
        "name": "move_file",
        "func": move_file,
        "description": "Move or rename a file/folder. Input: 'source | destination'.",
    },
    {
        "name": "copy_file",
        "func": copy_file,
        "description": "Copy a file or folder. Input: 'source | destination'.",
    },
    {
        "name": "read_file",
        "func": read_file,
        "description": "Read contents of a text file. Input: file path.",
    },
    {
        "name": "search_files",
        "func": search_files,
        "description": "Search for files by name. Input: 'pattern' or 'pattern | directory'.",
    },
    {
        "name": "organize_files",
        "func": organize_files,
        "description": "Organize files into subfolders by type. Input: folder path (defaults to Desktop).",
    },
    {
        "name": "open_app",
        "func": open_app,
        "description": "Open any application by name (notepad, calc, chrome, etc). Input: app name.",
    },
    {
        "name": "open_vscode",
        "func": open_vscode,
        "description": "Open VS Code, optionally with a file/folder. Input: optional path.",
    },
    {
        "name": "open_terminal",
        "func": open_terminal,
        "description": "Open a new terminal window. No input needed.",
    },
    {
        "name": "create_document",
        "func": create_document,
        "description": "Create a Word .docx file. Input: 'filename | content'.",
    },
    {
        "name": "create_text_file",
        "func": create_text_file,
        "description": "Create/write any text file (.txt, .py, .js, etc). Input: 'filename | content'.",
    },
    {
        "name": "get_public_ip",
        "func": get_public_ip,
        "description": "Get user's public IP address. No input needed.",
    },
    {
        "name": "run_terminal_command",
        "func": run_terminal_command,
        "description": "Run any shell/terminal command. Input: the command string.",
    },
]


def get_tool_descriptions():
    """Return formatted tool list for the AI."""
    lines = []
    for i, tool in enumerate(TOOL_REGISTRY, 1):
        lines.append(f"{i}. {tool['name']}: {tool['description']}")
    return "\n".join(lines)


def find_tool(name):
    """Find a tool by name."""
    for tool in TOOL_REGISTRY:
        if tool["name"].lower() == name.lower():
            return tool
    return None


def execute_tool(name, arg=""):
    """Execute a tool by name with an argument."""
    tool = find_tool(name)
    if not tool:
        return f"❌ Tool '{name}' not found."

    func = tool["func"]

    # Tools that take no args
    if name in ("open_terminal", "get_public_ip"):
        return func()

    return func(arg)
