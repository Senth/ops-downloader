import json
import re
import time
from pathlib import Path
from time import sleep
from typing import List, Optional

import chromedriver_autoinstaller
from colored import attr, fg
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from tealprint import TealPrint

from ..config import config
from ..core.type import Types

sleep_time = 0.5
get_element_timeout = 15


class OPSEpisodeInfo:
    def __init__(self) -> None:
        self.number: str = ""
        self.title: str = ""
        self.url: str = ""
        self.ffmpeg_url: str = ""


class OPS:
    _base_url = "https://www.objectivepersonalitysystem.com"
    _episode_regexp = re.compile(r"([\w&]+) (\d+[a-d]?).*")

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

        service = Service(executable_path=str(path))
        self.driver = webdriver.Chrome(service=service, options=options)

    def get_new_episodes(self, type: Types, latest_episode: str) -> List[OPSEpisodeInfo]:
        episodes: List[OPSEpisodeInfo] = []

        self._login()

        episodes = self._get_all_episodes_on_page(type)
        # TODO: Remove episodes that are earlier than latest_episode

        # TODO: Get next page if we didn't find our latest episode

        # Get the ffmpeg URL for each episode
        for episode in episodes:
            self._get_ffmpeg_url(episode)

        return episodes

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

    def _get_all_episodes_on_page(self, type: Types) -> List[OPSEpisodeInfo]:
        TealPrint.info("Getting all episodes on page", color=attr("bold"), push_indent=True)
        episodes: List[OPSEpisodeInfo] = []

        try:
            list_items = self.driver.find_elements(By.XPATH, ".//div[contains(@role,'listitem')]")

            for item in list_items:
                episode_info = self._get_episode_info(type, item)
                if episode_info:
                    episodes.append(episode_info)

        except NoSuchElementException as e:
            TealPrint.error(f"Failed to get videos on page; {e.msg}", exit=True)

        TealPrint.pop_indent()

        return episodes

    def _get_episode_info(self, type: Types, item: WebElement) -> Optional[OPSEpisodeInfo]:
        episode = OPSEpisodeInfo()

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
            episode.number = match[2]

            # Map op
            internal_type = OPS._op_type_to_internal_enum(op_type)
            if not internal_type:
                TealPrint.error(f"Unknown op type; {op_type}", exit=True)
            elif internal_type != type:
                return None

            # Video URL page
            episode.url = item.find_element(By.XPATH, ".//a").get_attribute("href")

        except NoSuchElementException as e:
            TealPrint.error(f"Failed to get title and episode spans; {e.msg}", exit=True)

        return episode

    @staticmethod
    def _op_type_to_internal_enum(op_type: str) -> Optional[Types]:
        if op_type == "Q&A":
            return Types.QA
        if op_type == "Class":
            return Types.CLASS

    def _get_ffmpeg_url(self, episode: OPSEpisodeInfo) -> None:
        TealPrint.info(f"Getting ffmpeg URL for {episode.title}", color=attr("bold"), push_indent=True)

        self.driver.get(episode.url)
        sleep(5)

        self._get_logs()

        TealPrint.info("Got ffmpeg URL", color=fg("green"), pop_indent=True)

    def _get_logs(self):
        logs = self.driver.get_log("performance")
        events = [json.loads(log["message"])["message"] for log in logs]
        # events = [event for event in events if "Network.response" in event["method"]]

        with open("events.txt", "w") as f:
            f.writelines(json.dumps(events, indent=4))

        exit(0)

    def _get_element(self, type: str, value: str) -> WebElement:
        started = time.time()
        while True:
            try:
                return self.driver.find_element(type, value)
            except NoSuchElementException as e:
                if time.time() - started > get_element_timeout:
                    raise e
