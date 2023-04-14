import json
import re
import time
from pathlib import Path
from time import sleep
from typing import Any, List, Optional, Set

import chromedriver_autoinstaller
from colored import attr, fg
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from tealprint import TealPrint

from ..config import config
from ..core.episode import Episode
from ..core.type import Types

sleep_time = 0.5
page_load_time = 5
get_element_timeout = 15


class OPS:
    _base_url = "https://www.objectivepersonalitysystem.com"
    _episode_regexp = re.compile(r"([\w&]+) (\d+\.?\d?).*")

    def __init__(self) -> None:
        path = chromedriver_autoinstaller.install()
        if not Path:
            TealPrint.error("Could not download chromedriver", exit=True)
            return

        options = Options()
        options.headless = True
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--lang=en-us")
        options.add_argument("--remote-debugging-port=9222")

        desired_capabilities: Any = DesiredCapabilities.CHROME
        desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

        service = Service(executable_path=str(path))
        self.driver = webdriver.Chrome(service=service, options=options, desired_capabilities=desired_capabilities)

        self.found_masters: Set[str] = set()
        self.found_master_index: int = -1

    def get_new_episodes(self, type: Types, latest_episode: Episode) -> List[Episode]:
        episodes: List[Episode] = []

        self._login()

        TealPrint.info("Getting episodes", color=attr("bold"), push_indent=True)
        while True:
            episodes.extend(self._get_all_episodes_on_page(type))

            # Break if we have loaded more than the previous latest episode
            last_episode = episodes[-1]
            if last_episode.ops.number <= latest_episode.ops.number:
                break

            # Get the previous episode
            self._search_episode(last_episode.ops.previous_episode())

        TealPrint.pop_indent()

        # Only save later episodes than latest_episode
        episodes = [episode for episode in episodes if episode.ops.number > latest_episode.ops.number]

        # Sort episodes by number
        episodes.sort(key=lambda episode: episode.ops.number)

        return episodes

    def close(self) -> None:
        self.driver.close()

    def _login(self) -> None:
        TealPrint.info("Logging in to OPS", color=attr("bold"), push_indent=True)
        TealPrint.info("Opening login page")
        self.driver.get(OPS._base_url)
        sleep(sleep_time)

        try:
            # Find the library button
            self.driver.find_element(By.XPATH, ".//a[contains(@href,'/library')]")
            sleep(sleep_time)

        except NoSuchElementException as e:
            TealPrint.error(f"Failed to find library button; {e.msg}", exit=True)

        self.driver.get(f"{OPS._base_url}/library")
        sleep(sleep_time)

        try:
            login_button = self._get_element(By.XPATH, ".//*[contains(text(), 'Log In')]")
            TealPrint.info("Clicking login button")
            login_button.click()
            sleep(sleep_time)

            TealPrint.info("Entering email")
            email_input = self.driver.find_element(By.NAME, "email")
            email_input.send_keys(config.ops.email)
            sleep(sleep_time)

            TealPrint.info("Entering password")
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(config.ops.password)
            sleep(sleep_time)

            TealPrint.info("Clicking login button")
            login_button = self.driver.find_element(By.XPATH, ".//*[contains(text(), 'Log in')]")
            login_button.click()
            sleep(sleep_time)

        except NoSuchElementException as e:
            TealPrint.error(f"Failed to get element; {e.msg}", exit=True)

        TealPrint.info("Logged in to OPS", color=fg("green"), pop_indent=True)
        sleep(page_load_time)

    def _search_episode(self, number: float) -> None:
        TealPrint.info(f"Searching for episode {int(number)}")

        try:
            search_input = self._get_element(By.XPATH, './/input[@type="text"]')

            # Search for the episode
            search_input.send_keys(Keys.CONTROL + "a")
            search_input.send_keys(f"{int(number)}")
            search_input.send_keys(Keys.RETURN)
        except NoSuchElementException:
            TealPrint.error("Failed to find search input", exit=True)

        sleep(page_load_time)

    def _get_all_episodes_on_page(self, type: Types) -> List[Episode]:
        episodes: List[Episode] = []

        try:
            list_items = self.driver.find_elements(By.XPATH, ".//div[contains(@role,'listitem')]")

            for item in list_items:
                episode_info = self._get_episode_info(type, item)
                if episode_info:
                    episodes.append(episode_info)

        except NoSuchElementException as e:
            TealPrint.error(f"Failed to get videos on page; {e.msg}", exit=True)

        return episodes

    def _get_episode_info(self, type: Types, item: WebElement) -> Optional[Episode]:
        episode = Episode()
        episode.type = type

        # Get Title, Number, and URL to video page
        try:
            spans = item.find_elements(By.XPATH, ".//p[contains(@class,'font_8')]/span")

            if len(spans) != 2:
                TealPrint.error("Title and episode spans are not equal to 2", exit=True)

            # Title
            episode.title = spans[0].text

            # Extract episode type and number
            match = OPS._episode_regexp.match(spans[1].text)
            if not match:
                TealPrint.error(f"Could not match episode regexp; {spans[1].text}", exit=True)
                return

            op_type = match[1]
            episode.ops.number = float(match[2])

            # Map op
            internal_type = OPS._op_type_to_internal_enum(op_type)
            if not internal_type:
                TealPrint.error(f"Unknown op type; {op_type}", exit=True)
            elif internal_type != type:
                return None

            # Video URL page
            episode.ops.url = item.find_element(By.XPATH, ".//a").get_attribute("href")

        except NoSuchElementException as e:
            TealPrint.error(f"Failed to get title and episode spans; {e.msg}", exit=True)

        return episode

    @staticmethod
    def _op_type_to_internal_enum(op_type: str) -> Optional[Types]:
        if op_type == "Q&A":
            return Types.QA
        if op_type == "Class":
            return Types.CLASS

    def get_download_url(self, episode: Episode) -> None:
        TealPrint.info(f"Getting ffmpeg URL for {episode.ops.number}: {episode.title}", push_indent=True)

        self.driver.get(episode.ops.url)
        sleep(page_load_time)

        # Click on the iframe
        try:
            iframe = self._get_element(By.XPATH, ".//iframe")

            iframe.click()
            sleep(page_load_time)

            url = self._get_next_master_json()
            if not url:
                TealPrint.error("Failed to find master.json", exit=True)
                return

            # Convert the URL to work with yt-dlp
            episode.ops.download_url = url.replace(".json?base64_init=1&", ".mpd?")

        except NoSuchElementException as e:
            TealPrint.error(f"Failed to get element; {e.msg}\nURL: {episode.ops.url}", exit=True)

        TealPrint.info("Got ffmpeg URL", color=fg("green"), pop_indent=True)
        return

    def _get_next_master_json(self) -> Optional[str]:
        logs = self.driver.get_log("performance")

        for i in range(len(logs)):
            message = logs[i]["message"]
            if "master.json" not in message:
                continue

            json_message = json.loads(message)["message"]
            if json_message["method"] != "Network.requestWillBeSent":
                continue

            url = json_message["params"]["request"]["url"]
            if not url or "master.json" not in url:
                continue

            # Check if this was already found before, then skip it
            if url in self.found_masters:
                continue

            # Add to found masters
            self.found_masters.add(url)
            return url

        return None

    def _get_logs(self):
        logs = self.driver.get_log("performance")
        events = [json.loads(log["message"])["message"] for log in logs]
        events2 = [event for event in events if "Network.response" in event["method"]]

        with open("events.txt", "w") as f:
            f.writelines(json.dumps(events, indent=4))
            f.write("—— RESPONSES ——")
            f.writelines(json.dumps(events2, indent=4))

        exit(0)

    def _get_element(self, type: str, value: str) -> WebElement:
        started = time.time()
        while True:
            try:
                return self.driver.find_element(type, value)
            except NoSuchElementException as e:
                if time.time() - started > get_element_timeout:
                    raise e
