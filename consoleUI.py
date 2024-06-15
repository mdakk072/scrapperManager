import curses
import threading
from datetime import datetime
import time
from ScraperManager import ScraperManager


STR_OFFSET = 20


class CursesUI:
    def __init__(self, manager):
        self.manager = manager
        self.menu_options = ["Profiles", "Scrapers"]
        self.current_selection = 0
        self.profile_selection = 0


    def display_profiles(self, stdscr):
        stdscr.clear()
        self.draw_top_bar(stdscr)

        profile_names = list(self.manager.config_profiles.keys())
        h, w = stdscr.getmaxyx()
        left_width = max(len(name) for name in profile_names) + 4

        # Draw the list of profile names on the left with a different background color
        stdscr.attron(curses.color_pair(3))
        for i in range(h - 2):
            stdscr.addstr(2 + i, 0, " " * left_width)
        stdscr.attroff(curses.color_pair(3))

        for i, name in enumerate(profile_names):
            if i == self.profile_selection:
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(2 + i, 0, f"{name}".ljust(left_width))
                stdscr.attroff(curses.color_pair(2))
            else:
                stdscr.attron(curses.color_pair(3))
                stdscr.addstr(2 + i, 0, f"{name}".ljust(left_width))
                stdscr.attroff(curses.color_pair(3))

        # Draw the selected profile's details on the right
        selected_profile_name = profile_names[self.profile_selection]
        selected_profile = self.manager.config_profiles[selected_profile_name]

        details_x = left_width + 2
        details_y = 2

        stdscr.addstr(details_y, details_x, f"Profile Details ({selected_profile_name}):", curses.A_BOLD | curses.A_UNDERLINE)
        details_y += 2

        # Show Config File and Interval
        stdscr.addstr(details_y, details_x, "Config File: ", curses.A_BOLD)
        stdscr.addstr(details_y, details_x + STR_OFFSET, f"{selected_profile.get('config_file', 'N/A')}")
        details_y += 1
        stdscr.addstr(details_y, details_x, "Interval: ", curses.A_BOLD)
        stdscr.addstr(details_y, details_x + STR_OFFSET, f"{selected_profile.get('interval', 'N/A')} minutes")
        details_y += 2  # Adding a space line

        # Show Unique ID, Publish Address, and Last Execution
        stdscr.addstr(details_y, details_x, "Unique ID: ", curses.A_BOLD)
        stdscr.addstr(details_y, details_x + STR_OFFSET, f"{selected_profile.get('unique_id', 'N/A')}")
        details_y += 1
        stdscr.addstr(details_y, details_x, "Publish Address: ", curses.A_BOLD)
        stdscr.addstr(details_y, details_x + STR_OFFSET, f"{selected_profile.get('publish_address', 'N/A')}")
        details_y += 1
        last_exec = selected_profile.get('last_exec')
        if last_exec:
            last_exec_str = last_exec.strftime('%Y-%m-%d %H:%M:%S')
        else:
            last_exec_str = 'N/A'
        stdscr.addstr(details_y, details_x, "Last Execution :   ", curses.A_BOLD)
        stdscr.addstr(details_y, details_x + STR_OFFSET, last_exec_str)
        details_y += 2  # Adding a space line

        # Show Running status with color
        running = selected_profile.get('running', False)
        stdscr.addstr(details_y, details_x, "Running: ", curses.A_BOLD)
        if running:
            stdscr.attron(curses.color_pair(4))  # Green background for running
            stdscr.addstr(details_y, details_x + STR_OFFSET, "Yes")
            stdscr.attroff(curses.color_pair(4))
        else:
            stdscr.attron(curses.color_pair(5))  # Red background for not running
            stdscr.addstr(details_y, details_x + STR_OFFSET, "No")
            stdscr.attroff(curses.color_pair(5))

        stdscr.refresh()

    def display_scrapers(self, stdscr):
        stdscr.clear()
        self.draw_top_bar(stdscr)

        scraper_ids = list(self.manager.scrapers.keys())
        if not scraper_ids:
            stdscr.addstr(2, 0, "No scrapers available.", curses.A_BOLD)
            stdscr.refresh()
            return

        # Adjust profile_selection if it is out of bounds
        if self.profile_selection >= len(scraper_ids):
            self.profile_selection = 0

        h, w = stdscr.getmaxyx()
        left_width = max(len(scraper_id) for scraper_id in scraper_ids) + 4

        # Draw the list of scraper IDs on the left with a different background color
        stdscr.attron(curses.color_pair(3))
        for i in range(h - 2):
            stdscr.addstr(2 + i, 0, " " * left_width)
        stdscr.attroff(curses.color_pair(3))

        for i, scraper_id in enumerate(scraper_ids):
            if i == self.profile_selection:  # Reuse profile_selection for simplicity
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(2 + i, 0, f"{scraper_id}".ljust(left_width))
                stdscr.attroff(curses.color_pair(2))
            else:
                stdscr.attron(curses.color_pair(3))
                stdscr.addstr(2 + i, 0, f"{scraper_id}".ljust(left_width))
                stdscr.attroff(curses.color_pair(3))

        # Draw the selected scraper's details on the right
        selected_scraper_id = scraper_ids[self.profile_selection]  # Reuse profile_selection for simplicity
        selected_scraper = self.manager.scrapers[selected_scraper_id]

        details_x = left_width + 2
        details_y = 2

        stdscr.addstr(details_y, details_x, f"Scraper Details ({selected_scraper_id}):", curses.A_BOLD | curses.A_UNDERLINE)
        details_y += 2

        # Function to safely add strings within screen bounds
        def safe_addstr(y, x, text, attr=0):
            if y < h and x < w:
                stdscr.addstr(y, x, text[:w - x], attr)

        # Show relevant details for the selected scraper
        safe_addstr(details_y, details_x, "Config File: ", curses.A_BOLD)
        safe_addstr(details_y, details_x + 20, f"{selected_scraper.config_file or 'N/A'}")
        details_y += 1
        safe_addstr(details_y, details_x, "Base Path: ", curses.A_BOLD)
        safe_addstr(details_y, details_x + 20, f"{selected_scraper.base_path or 'N/A'}")
        details_y += 1
        safe_addstr(details_y, details_x, "Virtual Env: ", curses.A_BOLD)
        safe_addstr(details_y, details_x + 20, f"{selected_scraper.venv_python or 'N/A'}")
        details_y += 2  # Adding a space line

        # Show more details
        safe_addstr(details_y, details_x, "Unique ID: ", curses.A_BOLD)
        safe_addstr(details_y, details_x + 20, f"{selected_scraper.unique_id or 'N/A'}")
        details_y += 1
        safe_addstr(details_y, details_x, "Publish Address: ", curses.A_BOLD)
        safe_addstr(details_y, details_x + 20, f"{selected_scraper.address or 'N/A'}")
        details_y += 1
        last_started = selected_scraper.last_started
        if last_started:
            last_started_str = last_started.strftime('%Y-%m-%d %H:%M:%S')
        else:
            last_started_str = 'N/A'
        safe_addstr(details_y, details_x, "Last Started: ", curses.A_BOLD)
        safe_addstr(details_y, details_x + 20, last_started_str)
        details_y += 2  # Adding a space line

        # Show Running status with color
        running = selected_scraper.process.poll() is None  # Check if the process is running
        safe_addstr(details_y, details_x, "Running: ", curses.A_BOLD)
        if running:
            stdscr.attron(curses.color_pair(4))  # Green background for running
            safe_addstr(details_y, details_x + 20, "Yes")
            stdscr.attroff(curses.color_pair(4))
        else:
            stdscr.attron(curses.color_pair(5))  # Red background for not running
            safe_addstr(details_y, details_x + 20, "No")
            stdscr.attroff(curses.color_pair(5))
        details_y += 2  # Adding a space line

        # Show monitoring details
        monitoring = selected_scraper.monitoring_data if selected_scraper.monitoring_data else {}
        safe_addstr(details_y, details_x, "Monitoring:", curses.A_BOLD | curses.A_UNDERLINE)
        details_y += 2
        safe_addstr(details_y, details_x, "State: ", curses.A_BOLD)
        safe_addstr(details_y, details_x + 20, str(monitoring.get('state', 'N/A')))
        details_y += 1
        safe_addstr(details_y, details_x, "Start Time: ", curses.A_BOLD)
        safe_addstr(details_y, details_x + 20, str(monitoring.get('start_time', 'N/A')))
        details_y += 1
        safe_addstr(details_y, details_x, "End Time: ", curses.A_BOLD)
        safe_addstr(details_y, details_x + 20, str(monitoring.get('end_time', 'N/A')))
        details_y += 1
        safe_addstr(details_y, details_x, "Duration: ", curses.A_BOLD)
        safe_addstr(details_y, details_x + 20, str(monitoring.get('duration', 'N/A')))
        details_y += 1
        safe_addstr(details_y, details_x, "Status: ", curses.A_BOLD)
        safe_addstr(details_y, details_x + 20, str(monitoring.get('status', 'N/A')))
        details_y += 1
        safe_addstr(details_y, details_x, "Last Updated: ", curses.A_BOLD)
        safe_addstr(details_y, details_x + 20, str(monitoring.get('last_updated', 'N/A')))
        details_y += 1
        safe_addstr(details_y, details_x, "Num Requests: ", curses.A_BOLD)
        safe_addstr(details_y, details_x + 20, str(monitoring.get('num_requests', 'N/A')))
        details_y += 1
        safe_addstr(details_y, details_x, "Successful Requests: ", curses.A_BOLD)
        safe_addstr(details_y, details_x + 20, str(monitoring.get('successful_requests', 'N/A')))
        details_y += 1
        safe_addstr(details_y, details_x, "Failed Requests: ", curses.A_BOLD)
        safe_addstr(details_y, details_x + 20, str(monitoring.get('failed_requests', 'N/A')))
        details_y += 1
        safe_addstr(details_y, details_x, "Requests/Minute: ", curses.A_BOLD)
        safe_addstr(details_y, details_x + 20, str(monitoring.get('requests_per_minute', 'N/A')))
        details_y += 1
        safe_addstr(details_y, details_x, "Fault: ", curses.A_BOLD)
        safe_addstr(details_y, details_x + 20, str(monitoring.get('fault', 'N/A')))

        stdscr.refresh()

    
    def draw_top_bar(self, stdscr):
        h, w = stdscr.getmaxyx()
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(0, 0, " " * w)
        stdscr.attroff(curses.color_pair(1))

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(0, 2, current_time)
        stdscr.attroff(curses.color_pair(1))

        for idx, option in enumerate(self.menu_options):
            x = w // 2 - len(" | ".join(self.menu_options)) // 2 + sum(len(o) + 3 for o in self.menu_options[:idx])
            if idx == self.current_selection:
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(0, x, f" {option} ")
                stdscr.attroff(curses.color_pair(2))
            else:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(0, x, f" {option} ")
                stdscr.attroff(curses.color_pair(1))
        
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(1, 0, "─" * w)
        stdscr.attroff(curses.color_pair(1))

    def main_ui(self, stdscr):
        curses.curs_set(0)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_RED)
        
        stdscr.nodelay(True)  # Make getch() non-blocking
        stdscr.clear()
        self.draw_top_bar(stdscr)

        while True:
            self.draw_top_bar(stdscr)

            if self.menu_options[self.current_selection] == "Profiles":
                self.display_profiles(stdscr)
            elif self.menu_options[self.current_selection] == "Scrapers":
                self.display_scrapers(stdscr)

            key = stdscr.getch()
            if key == curses.KEY_RIGHT and self.current_selection < len(self.menu_options) - 1:
                self.current_selection += 1
            elif key == curses.KEY_LEFT and self.current_selection > 0:
                self.current_selection -= 1
            elif key == curses.KEY_UP and self.profile_selection > 0:
                self.profile_selection -= 1
            elif key == curses.KEY_DOWN and self.profile_selection < len(self.manager.config_profiles) - 1:
                self.profile_selection += 1

            stdscr.refresh()
            time.sleep(0.1)  # Refresh every second

    def run(self):
        curses.wrapper(self.main_ui)

class Main:
    def __init__(self, manager):
        self.manager = manager
        self.ui = CursesUI(manager)

    def start(self):
        manager_thread = threading.Thread(target=self.manager.run)
        manager_thread.daemon = True
        manager_thread.start()

        self.ui.run()

if __name__ == "__main__":
    base_path = "/home/mdakk072/projects/coreScraperProject/kijijiCarScraper"
    manager = ScraperManager(base_path)
    main = Main(manager)
    main.start()
