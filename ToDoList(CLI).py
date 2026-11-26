"""
Professional Terminal To-Do List
Features: view, add, edit, complete/reopen, remove, search,
filter, clear all, duplicate prevention, and file persistence.
"""

FILENAME = "tasks.txt"

# Optional terminal colors:
# Install with: pip install colorama
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    CYAN = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    BLUE = Fore.BLUE
    RESET = Style.RESET_ALL
except ImportError:
    GREEN = RED = YELLOW = CYAN = MAGENTA = BLUE = RESET = ""


def line(char="─", width=54):
    print(char * width)


def title(text):
    print(f"\n{CYAN}{'═' * 54}{RESET}")
    print(f"{CYAN}{text.center(54)}{RESET}")
    print(f"{CYAN}{'═' * 54}{RESET}")


def pause():
    input(f"\n{YELLOW}Press Enter to continue...{RESET}")


# ---------- File handling ----------

def load_tasks():
    tasks = []
    try:
        with open(FILENAME, "r", encoding="utf-8") as file:
            for line_text in file:
                line_text = line_text.rstrip("\n")
                if not line_text:
                    continue

                if line_text.startswith("0|") or line_text.startswith("1|"):
                    done = line_text[0] == "1"
                    text = line_text[2:]
                else:
                    done = False
                    text = line_text

                if text.strip():
                    tasks.append({"text": text, "done": done})
    except FileNotFoundError:
        pass
    except OSError as error:
        print(f"{RED}Could not read tasks: {error}{RESET}")

    return tasks


def save_tasks(tasks):
    try:
        with open(FILENAME, "w", encoding="utf-8") as file:
            for task in tasks:
                status = "1" if task["done"] else "0"
                file.write(f"{status}|{task['text']}\n")
        return True
    except OSError as error:
        print(f"{RED}Could not save tasks: {error}{RESET}")
        return False


# ---------- Helpers ----------

def is_duplicate(tasks, text, skip_index=None):
    normalized = " ".join(text.lower().split())

    for index, task in enumerate(tasks):
        if index == skip_index:
            continue
        existing = " ".join(task["text"].lower().split())
        if existing == normalized:
            return True

    return False


def print_task(number, task):
    if task["done"]:
        mark = f"{GREEN}[✓] DONE{RESET}"
    else:
        mark = f"{YELLOW}[ ] TODO{RESET}"

    print(f"  {CYAN}{number:>2}.{RESET} {mark}  {task['text']}")


def ask_task_number(tasks, prompt):
    choice = input(prompt).strip()

    if not choice.isdigit():
        print(f"{RED}Please enter a valid number.{RESET}")
        return None

    index = int(choice) - 1

    if 0 <= index < len(tasks):
        return index

    print(f"{RED}That task number does not exist.{RESET}")
    return None


def show_statistics(tasks):
    total = len(tasks)
    completed = sum(task["done"] for task in tasks)
    pending = total - completed
    progress = (completed / total * 100) if total else 0

    print(f"\n{BLUE}TASK OVERVIEW{RESET}")
    line("─", 54)
    print(f"  Total tasks      : {CYAN}{total}{RESET}")
    print(f"  Completed        : {GREEN}{completed}{RESET}")
    print(f"  Pending          : {YELLOW}{pending}{RESET}")
    print(f"  Progress         : {MAGENTA}{progress:.0f}%{RESET}")
    line("─", 54)


# ---------- Features ----------

def view_tasks(tasks):
    title("YOUR TASK LIST")

    if not tasks:
        print(f"{YELLOW}  No tasks yet. Add your first task!{RESET}")
    else:
        for number, task in enumerate(tasks, start=1):
            print_task(number, task)

    show_statistics(tasks)


def add_task(tasks):
    title("ADD A NEW TASK")
    text = input("  Enter task: ").strip()

    if not text:
        print(f"{RED}Task cannot be empty.{RESET}")
        return

    if is_duplicate(tasks, text):
        print(f"{YELLOW}This task already exists.{RESET}")
        return

    tasks.append({"text": text, "done": False})

    if save_tasks(tasks):
        print(f"{GREEN}✓ Task added successfully: {text}{RESET}")


def complete_task(tasks):
    title("UPDATE TASK STATUS")

    if not tasks:
        print(f"{YELLOW}  No tasks available.{RESET}")
        return

    for number, task in enumerate(tasks, start=1):
        print_task(number, task)

    index = ask_task_number(tasks, "\n  Enter task number: ")
    if index is None:
        return

    tasks[index]["done"] = not tasks[index]["done"]
    status = "completed" if tasks[index]["done"] else "pending"

    if save_tasks(tasks):
        print(f"{GREEN}✓ Task marked as {status}.{RESET}")


def edit_task(tasks):
    title("EDIT A TASK")

    if not tasks:
        print(f"{YELLOW}  No tasks available to edit.{RESET}")
        return

    for number, task in enumerate(tasks, start=1):
        print_task(number, task)

    index = ask_task_number(tasks, "\n  Enter task number: ")
    if index is None:
        return

    print(f"\n  Current task: {tasks[index]['text']}")
    new_text = input("  New task text: ").strip()

    if not new_text:
        print(f"{RED}Task cannot be empty.{RESET}")
        return

    if is_duplicate(tasks, new_text, skip_index=index):
        print(f"{YELLOW}Another task with this name already exists.{RESET}")
        return

    old_text = tasks[index]["text"]
    tasks[index]["text"] = new_text

    if save_tasks(tasks):
        print(f"{GREEN}✓ Task updated: {old_text} → {new_text}{RESET}")


def remove_task(tasks):
    title("REMOVE A TASK")

    if not tasks:
        print(f"{YELLOW}  Nothing to remove.{RESET}")
        return

    for number, task in enumerate(tasks, start=1):
        print_task(number, task)

    index = ask_task_number(tasks, "\n  Enter task number: ")
    if index is None:
        return

    answer = input(
        f"  Are you sure you want to remove '{tasks[index]['text']}'? (yes/no): "
    ).strip().lower()

    if answer == "yes":
        removed = tasks.pop(index)
        if save_tasks(tasks):
            print(f"{GREEN}✓ Removed: {removed['text']}{RESET}")
    else:
        print(f"{YELLOW}Removal cancelled.{RESET}")


def search_tasks(tasks):
    title("SEARCH TASKS")
    keyword = input("  Search keyword: ").strip().lower()

    if not keyword:
        print(f"{RED}Search word cannot be empty.{RESET}")
        return

    matches = [
        (number, task)
        for number, task in enumerate(tasks, start=1)
        if keyword in task["text"].lower()
    ]

    if not matches:
        print(f"{YELLOW}No matching tasks found.{RESET}")
        return

    print(f"\n{GREEN}Found {len(matches)} matching task(s):{RESET}")
    for number, task in matches:
        print_task(number, task)


def filter_tasks(tasks, completed):
    heading = "COMPLETED TASKS" if completed else "PENDING TASKS"
    title(heading)

    matches = [
        (number, task)
        for number, task in enumerate(tasks, start=1)
        if task["done"] == completed
    ]

    if not matches:
        message = "No completed tasks." if completed else "No pending tasks."
        print(f"{YELLOW}{message}{RESET}")
        return

    for number, task in matches:
        print_task(number, task)


def clear_tasks(tasks):
    title("CLEAR ALL TASKS")

    if not tasks:
        print(f"{YELLOW}  Your task list is already empty.{RESET}")
        return

    answer = input(
        f"  Delete all {len(tasks)} tasks? This cannot be undone (yes/no): "
    ).strip().lower()

    if answer == "yes":
        old_tasks = tasks.copy()
        tasks.clear()

        if save_tasks(tasks):
            print(f"{GREEN}✓ All tasks cleared.{RESET}")
        else:
            tasks.extend(old_tasks)
            print(f"{YELLOW}Tasks restored in memory because saving failed.{RESET}")
    else:
        print(f"{YELLOW}Operation cancelled. No tasks deleted.{RESET}")


# ---------- Main program ----------

def show_menu():
    title("MAIN MENU")
    print(f"  {CYAN}1.{RESET}  View all tasks")
    print(f"  {CYAN}2.{RESET}  Add a new task")
    print(f"  {CYAN}3.{RESET}  Mark done / pending")
    print(f"  {CYAN}4.{RESET}  Edit a task")
    print(f"  {CYAN}5.{RESET}  Remove a task")
    print(f"  {CYAN}6.{RESET}  Search tasks")
    print(f"  {CYAN}7.{RESET}  View pending tasks")
    print(f"  {CYAN}8.{RESET}  View completed tasks")
    print(f"  {CYAN}9.{RESET}  Clear all tasks")
    print(f"  {RED}0.{RESET}  Exit")
    line()


def main():
    tasks = load_tasks()

    print(f"\n{MAGENTA}{'═' * 54}{RESET}")
    print(f"{MAGENTA}        WELCOME TO YOUR TO-DO MANAGER{RESET}")
    print(f"{MAGENTA}{'═' * 54}{RESET}")
    print(f"  Your tasks are saved automatically in {FILENAME}.")

    while True:
        show_menu()
        choice = input("  Choose an option (0-9): ").strip()

        if choice == "1":
            view_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
        elif choice == "3":
            complete_task(tasks)
        elif choice == "4":
            edit_task(tasks)
        elif choice == "5":
            remove_task(tasks)
        elif choice == "6":
            search_tasks(tasks)
        elif choice == "7":
            filter_tasks(tasks, completed=False)
        elif choice == "8":
            filter_tasks(tasks, completed=True)
        elif choice == "9":
            clear_tasks(tasks)
        elif choice == "0":
            print(f"\n{GREEN}Thank you for using To-Do Manager. Goodbye!{RESET}")
            break
        else:
            print(f"{RED}Invalid option. Please choose 0-9.{RESET}")

        pause()


if __name__ == "__main__":
    main()
