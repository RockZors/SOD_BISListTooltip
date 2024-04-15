#!/usr/bin/env python

import sys
import time
import os
import json
import re
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from retry import retry


# Parses wowhead html and outputs a json file with the data. Should be updated to output a lua file instead later.

# Selenium binaries

CWD = os.path.dirname(__file__)
CHROMEDRIVER_PATH = os.path.join(CWD, "chrome/chromedriver-linux64/chromedriver")
CHROME_PATH = os.path.join(CWD, "chrome/chrome-linux64/chrome")

# WOWHEAD URLs
WOWHEAD_URLS = [
    # Druid
    {
        "class": "Druid",
        "spec": "Balance DPS",
        "list": "Druid Balance DPS",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/druid/balance/dps-bis-gear-pve"
    },
    {
        "class": "Druid",
        "spec": "Feral DPS",
        "list": "Druid Feral DPS",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/druid/feral/dps-bis-gear-pve"
    },
    {
        "class": "Druid",
        "spec": "Healer",
        "list": "Druid Healer",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/druid/healer-bis-gear-pve"
    },
    {
        "class": "Druid",
        "spec": "Tank",
        "list": "Druid Tank",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/druid/tank-bis-gear-pve"
    },
    
    # Hunter
    {
        "class": "Hunter",
        "spec": "DPS",
        "list": "Hunter DPS",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/hunter/dps-bis-gear-pve"
    },
    
    # Mage
    {
        "class": "Mage",
        "spec": "DPS",
        "list": "Mage DPS",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/mage/dps-bis-gear-pve"
    },
    {
        "class": "Mage",
        "spec": "Healer",
        "list": "Mage Healer",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/mage/healer-bis-gear-pve"
    },
    
    # Paladin
    {
        "class": "Paladin",
        "spec": "DPS",
        "list": "Paladin DPS",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/paladin/dps-bis-gear-pve"
    },
    {
        "class": "Paladin",
        "spec": "Healer",
        "list": "Paladin Healer",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/paladin/healer-bis-gear-pve"
    },
    {
        "class": "Paladin",
        "spec": "Tank",
        "list": "Paladin Tank",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/paladin/tank-bis-gear-pve"
        # Old P1 setting...
        # "custom_behaviors": {
        #     "suffix_from_column_text": True # The Paladin Tank list has a number of world drop items in a single row. These all have the same suffix. We need to use the text in the column to determine the suffix rather than from the item link.
        # }
    },
    
    # Priest
    {
        "class": "Priest",
        "spec": "DPS",
        "list": "Priest DPS",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/priest/dps-bis-gear-pve"
    },
    {
        "class": "Priest",
        "spec": "Healer",
        "list": "Priest Healer",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/priest/healer-bis-gear-pve"
    },
    
    # Rogue
    {
        "class": "Rogue",
        "spec": "DPS",
        "list": "Rogue DPS",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/rogue/dps-bis-gear-pve"
    },
    {
        "class": "Rogue",
        "spec": "Tank",
        "list": "Rogue Tank",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/rogue/tank-bis-gear-pve"
    },
    
    # Shaman
    {
        "class": "Shaman",
        "spec": "Elemental DPS",
        "list": "Shaman Elemental DPS",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/shaman/elemental/dps-bis-gear-pve"
    },
    {
        "class": "Shaman",
        "spec": "Enhancement DPS",
        "list": "Shaman Enhancement DPS",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/shaman/enhancement/dps-bis-gear-pve"
    },
    {
        "class": "Shaman",
        "spec": "Healer",
        "list": "Shaman Healer",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/shaman/healer-bis-gear-pve"
    },
    {
        "class": "Shaman",
        "spec": "Tank",
        "list": "Shaman Tank",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/shaman/tank-bis-gear-pve"
    },
    
    # Warlock
    {
        "class": "Warlock",
        "spec": "DPS",
        "list": "Warlock DPS",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/warlock/dps-bis-gear-pve"
    },
    {
        "class": "Warlock",
        "spec": "Tank",
        "list": "Warlock Tank",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/warlock/tank-bis-gear-pve"
    },
    
    # Warrior
    {
        "class": "Warrior",
        "spec": "DPS",
        "list": "Warrior DPS",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/warrior/dps-bis-gear-pve"
    },
    {
        "class": "Warrior",
        "spec": "Tank",
        "list": "Warrior Tank",
        "phase": "2",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/warrior/tank-bis-gear-pve"
    },
]
WOWHEAD_ITEM_URL_PREFIX = "https://classic.wowhead.com/item="

# WOWHEAD Image to Spec Mapping
WOWHEAD_IMAGE_TO_SPEC = {
    # Warlock DPS
    "spell_fire_burnout.gif": "Fire",
    "spell_shadow_shadowbolt.gif": "Shadow",

    # Warlock Tank
    "spell_fire_soulburn.gif": "Threat",
    "ability_warlock_demonicpower.gif": "Defensive"

}

# Allowed slots
WOW_SLOTS = [
    "head",
    "neck",
    "shoulders",
    "back",
    "chest",
    "wrist",
    "hands",
    "waist",
    "legs",
    "feet",
    "finger",
    "trinket",
    "main-hand",
    "two-hand",
    "off-hand",
    "one-hand",
    "ranged",
    "shield",
    "relic"
]

# Headings are inconsistent. This is a mapping of aliases to the correct heading
WOW_SLOT_ALIASES = {
    "cloak": "back",
    "shoulder": "shoulders",
    "wrists": "wrist",
    "glove": "hands",
    "gloves": "hands",
    "hand": "hands",
    "boot": "feet",
    "boots": "feet",
    "foot": "feet",
    "belt": "waist",
    "rings": "finger",
    "ring": "finger",
    "fingers": "finger",
    "trinkets": "trinket",
    "staves": "two-hand",
    "staff": "two-hand",
    "weapon": "two-hand",
    "weapons": "two-hand", #Paladin weapon causing error on update
    "two-handed": "two-hand",
    "two-hander": "two-hand",
    "weapon-single-target": "two-hand", # Paladin P2 header. I honestly forget why I even track slots so putting in this hack for now. Could likely clean this up and/or add exceptions per page
    "weapon-cleave": "two-hand", # Same as above (Palandin DPS P2)
    "weapon-martyrdom": "two-hand", # Same as above (Palandin Tank P2)
    "weapon-divine-storm-human": "two-hand", # Same as above (Palandin Tank P2)
    "weapon-divine-storm-dwarf": "two-hand", # Same as above (Palandin Tank P2)
    "duel-wield": "one-hand",
    "dual-wield": "one-hand",
    "wand": "ranged",
    "wands": "ranged",
    "idol": "relic",
    "idols": "relic",
    "relics": "relic",
    "libram": "relic",
    "librams": "relic",
}

# Mapping file for english suffixes (ex: 'of the Whale) to their corresponding suffix ids as well as
# an internal 'key' which can be referenced in the lua file and work around localization issues
WOW_SUFFIX_MAPPING_FILE = os.path.join(CWD, "../data/wow-suffix-mapping.json")

# Mapping file for english suffixes (ex: 'of the Whale) and their itemid to their corresponding bis suffix id
# We do this to reduce the number of requests we need to make
ITEM_BIS_SUFFIX_CACHE_FILE = os.path.join(CWD, "../data/item-bis-suffix-cache.json")
USE_ITEM_BIS_SUFFIX_CACHE = True

# Output
OUTPUT_PATH = os.path.join(CWD, "../data/wowhead.json")

class SuffixNotFoundException(Exception):
    def __init__(self, item_id, suffix):
        self.message = f"Failed to find matching suffix for item {item_id} with suffix {suffix}"
        super().__init__(self.message)

class Item:
    def __init__(self):
        self.name = None
        self.id = None
        self.source = None
        self.rank = None
        self.suffixkey = None
        self.bissuffixid = None # The best possible roll for a given suffix. This is interpreted by this script and not defined explicitly in the wowhead data. This should be optionally displayed in the output.
        self.prioritytext = None
        self.prioritynumber = None
        self.phase = None
        self.key = None
        self.slot = None

    def __str__(self):
        return f"{self.name} ({self.id})"

    def __repr__(self):
        return self.__str__()
    
    def get_name(self) -> str:
        return self.name
    
    def set_name(self, name: str) -> None:
        name = name.replace("\n", "")
        logger.debug(f"Setting name to \"{name}\"")
        self.name = name

    def get_id(self) -> str:
        return self.id
    
    def set_id(self, id: str) -> None:
        id = id.replace("\n", "")
        self.id = id

    def get_key(self) -> str:
        return self.key
    
    def set_key(self, key: str) -> None:
        key = key.replace("\n", "")
        logger.debug(f"Setting key to \"{key}\"")
        self.key = key

    def get_source(self) -> str:
        return self.source
    
    def set_source(self, source: str) -> None:
        source = source.replace("\n", "")
        self.source = source

    def get_rank(self) -> str:
        return self.rank
    
    def set_rank(self, rank: str) -> None:    
        # Remove any newline characters
        rank = rank.replace("\n", "")
        self.rank = rank

    def get_suffixkey(self) -> str:
        return self.suffixkey
    
    def set_suffixkey(self, suffixkey: str) -> None:
        suffixkey = suffixkey.replace("\n", "")
        self.suffixkey = suffixkey

    def get_prioritytext(self) -> str:
        return self.prioritytext
    
    def set_prioritytext(self, prioritytext: str) -> None:
        prioritytext = prioritytext.replace("\n", "")
        self.prioritytext = prioritytext

    def get_prioritynumber(self) -> int:
        return self.prioritynumber
    
    def set_prioritynumber(self, prioritynumber: int) -> None:
        self.prioritynumber = prioritynumber

    def get_phase(self) -> str:
        return self.phase
    
    def set_phase(self, phase: str) -> None:
        self.phase = phase

    def get_slot(self) -> str:
        return self.slot
    
    def set_slot(self, slot: str) -> None:
        if slot not in WOW_SLOTS:
            if slot in WOW_SLOT_ALIASES:
                slot = WOW_SLOT_ALIASES[slot]
            else:
                raise Exception(f"Invalid slot {slot}")
        self.slot = slot

    def get_bissuffixid(self) -> str:
        return self.bissuffixid
    
    def set_bissuffixid(self, bissuffixid: str) -> None:
        self.bissuffixid = bissuffixid
    
    def to_json(self) -> dict:
        return {
            "Rank": self.rank,
            "PriorityText": self.prioritytext,
            "PriorityNumber": self.prioritynumber,
            "Phase": self.phase,
            "ItemName": self.name,
            "ItemID": self.id,
            "ItemSuffixKey": self.suffixkey,
            "ItemBISSuffixID": self.bissuffixid,
            "Source": self.source,
            "Slot": self.slot,
        }
    
    @staticmethod
    def get_bis_suffix_id(item_browser: webdriver, wow_suffix_mapping: dict, item_bis_suffix_cache: dict, item_id: str, suffix: str) -> str:
        """
        Determines the best possible suffix id for this item and sets it in self.bissuffixid.

        param item_browser: The selenium browser
        param wow_suffix_mapping: The suffix mapping dictionary
        param item_bis_suffix_cache: The item bis suffix cache dictionary. Format: {"itemid": {"suffix": "suffixid"}}
        param item_id: The item id to check
        param suffix: The suffix to check (ex: 'of the Bear')

        return: None if the item id has no possible suffixes (i.e. missing the "Random Enchantments" h2 tag). Otherwise, the best possible suffix id.

        raises: SuffixNotFoundException if there are possible suffixes but the provided suffix is not one of them
        raises: Exception If there was an issue parsing the suffixes
        """

        found_matching_suffix = False
        best_attributes = []


        if USE_ITEM_BIS_SUFFIX_CACHE:
            # Check if the item id is in the cache
            if item_id in item_bis_suffix_cache:
                # Check if the suffix is in the cache
                if suffix in item_bis_suffix_cache[item_id]:
                    # We have a match. Return the suffix id
                    logger.info(f"Found matching suffix {suffix} for item {item_id} in cache")
                    return item_bis_suffix_cache[item_id][suffix]

        # Get the item page
        item_url = f"{WOWHEAD_ITEM_URL_PREFIX}{item_id}"
        logger.debug(f"Getting {item_url}")
        get_with_retry(item_browser, item_url)
        
        # Get h2 with the text "Random Enchantments"
        # Find the following <ul> and iterate over each <li>
        # Each <li> has a <div> with a <span> with the suffix name followed by <br> then the attributes
        # Example:
        # <h2>Random Enchantments</h2>
        # <div class="random-enchantments">
        #   <ul>
        #     <li>
        #         <div>
        #             <span class="q2">...of the Monkey</span>
        #             <small class="q0">(18.0% chance)</small><br>
        #             +(3 - 4) Agility , +(3 - 4) Stamina
        #         </div>
        #     </li>
        #   </ul>
        # </div>

        # Find the h2 with the text "Random Enchantments"

        # Get all h2 tags
        h2s = item_browser.find_elements(By.TAG_NAME, "h2")
        enchant_header = None

        # Check if any of the h2 tags have the text "Random Enchantments"
        for h2 in h2s:
            if h2.text.strip() == "Random Enchantments":
                enchant_header = h2
                break

        if enchant_header is None:
            logger.warning(f"Failed to find heading with text 'Random Enchantments' for item {item_id}. Returning None")
            return None
        
        # Find the next <ul> following the h2
        uls = enchant_header.find_elements(By.XPATH, "./following::ul")

        ul_count = 0
        for ul in uls:
            ul_count += 1
            # We never need to go above 2 uls
            if ul_count > 2:
                break
            logger.info(f"Processing ul {ul_count}")
            if ul is None:
                logger.error(f"Failed to find ul following 'Random Enchantments' heading for item {item_id}")
                # Raise exception
                raise Exception(f"Failed to find ul following 'Random Enchantments' heading for item {item_id}")
            
            # Iterate over each <li>
            lis = ul.find_elements(By.XPATH, "./li")
            if lis is None:
                logger.error(f"Failed to find li elements following ul for item {item_id}")
                # Raise exception
                raise Exception(f"Failed to find li elements following ul for item {item_id}")
            
            for li in lis:
                # Each <li> has a <div> with a <span> with the suffix name followed by <br> then the attributes
                # Example:
                # <li>
                #   <div>
                #       <span class="q2">...of the Monkey</span>
                #       <small class="q0">(18.0% chance)</small><br>
                #       +(3 - 4) Agility , +(3 - 4) Stamina
                #   </div>
                # </li>

                if found_matching_suffix:
                    # We already found the matching suffix. Skip the rest of the suffixes
                    continue

                # Find the <div>
                try:
                    div = li.find_element(By.XPATH, "./div")
                except NoSuchElementException:
                    logger.warning(f"Failed to find div following li for item {item_id} (ul: {ul_count})")
                    break

                if div is None:
                    logger.error(f"Failed to find div following li for item {item_id}")
                    # Raise exception
                    raise Exception(f"Failed to find div following li for item {item_id}")
                
                # Find the <span> with the suffix name
                span = div.find_element(By.XPATH, "./span")
                if span is None:
                    logger.error(f"Failed to find span following div for item {item_id}")
                    # Raise exception
                    raise Exception(f"Failed to find span following div for item {item_id}")
                
                # Get text after <br> in the div
                raw_attributes = div.text.split("\n")[1]
                suffix_name = span.text
                
                # Remove ... from suffix name if it starts with ...
                if suffix_name.startswith("..."):
                    suffix_name = suffix_name[3:]

                # Split raw_attributes by comma
                raw_attributes = raw_attributes.split(",")

                # Trim each attribute
                raw_attributes = [x.strip() for x in raw_attributes]

                # Check if the suffix_name matches the provided suffix
                if suffix_name.lower() != suffix.lower():
                    # Suffix name does not match. Skip this suffix
                    logger.debug(f"Skipping suffix {suffix_name} because it does not match {suffix}")
                    continue
                
                # Suffix name matches
                found_matching_suffix = True
                for raw_attribute in raw_attributes:
                    # Find the best roll for each attribute
                    best_suffix = get_best_suffix_roll(raw_attribute)
                    best_attributes.append(best_suffix)
                    
        if not found_matching_suffix:
            # We did not find a matching suffix. Raise exception
            logger.error(f"Failed to find matching suffix for item {item_id} with suffix {suffix}")
            raise SuffixNotFoundException(item_id, suffix)
        
        # We now have a list of best attributes. Let's find the best one from suffix_mapping

        # Example:
        #   suffix = "of the Monkey"
        #   attributes = ["+6 Agility", "+6 Stamina"]

        # Iterate over each suffix in the suffix_mapping and find the matching suffix
        for mapping_suffix_name in wow_suffix_mapping:
            if mapping_suffix_name.lower() == suffix.lower():

                # Example:
                #   mapping_suffix_name = "of the Monkey"

                logger.info(f"Found matching suffix {mapping_suffix_name} for item {item_id}")

                # Iterate over each "value_attributes" and find the matching attributes from best_attributes
                for mapping_attribute_id in wow_suffix_mapping[mapping_suffix_name]["value_attributes"]:
                    mapping_suffix_attributes = wow_suffix_mapping[mapping_suffix_name]["value_attributes"][mapping_attribute_id].split("|")

                    # Example:
                    #   mapping_attribute_id = "598"
                    #   mapping_suffix_attributes = ["+6 Agility", "+6 Stamina"]

                    # We need to find if all elements of "attributes" matches all elements of "mapping_suffix_attributes"
                    if set(best_attributes) == set(mapping_suffix_attributes):
                        logger.info(f"Found matching attributes {best_attributes} for suffix {mapping_suffix_name} for item {item_id} with attribute id {mapping_attribute_id}")

                        # Log this in cache
                        if item_id not in item_bis_suffix_cache:
                            item_bis_suffix_cache[item_id] = {}
                        item_bis_suffix_cache[item_id][suffix] = mapping_attribute_id

                        # We found a match. Return the suffix id
                        return mapping_attribute_id
        
        # We did not find a match. Raise exception
        logger.error(f"Failed to find matching suffix for item {item_id} with suffix {suffix}")
        raise SuffixNotFoundException(item_id, suffix)



    
    # static method to convert item column html to an Item object
    @staticmethod
    def from_column_html(item_browser: webdriver, item: "Item", link_num: int, column_html: str, column_text: str, links: list, wow_suffix_mapping: dict, item_bis_suffix_cache: dict, custom_behaviors: dict) -> tuple["Item", str]:
        """
        Converts the html of a column to an Item object
        param item_browser: The selenium browser
        param item: The Item object to update
        param link_num: The link number to convert
        param column_html: The innerHtml of the column
        param column_text: The text of the column
        param links: The list of selenium links in the column
        param wow_suffix_mapping: The suffix mapping dictionary

        return: An Item object
        return: A string containing the reason for error
        """

        if item is None:
            item = Item()


        # Custom behaviors
        suffix_from_column_text = False
        if custom_behaviors is not None and "suffix_from_column_text" in custom_behaviors:
            logger.info("Using custom behavior suffix_from_column_text")
            suffix_from_column_text = custom_behaviors["suffix_from_column_text"]

        # Let's iterate over each item_link_data_testing["links"] and see if we print the following...
        # * Name of the item (link.text.strip())
        # * Any text between the link and the next link (link.tail.strip())
        # * The href (link.get_attribute("href"))
                
        # Iterate over item_link_data_testing["links"] using an index so we can get the next link
        for item_link_num in range(len(links)):
            if item_link_num != link_num:
                continue
            link = links[item_link_num]
            
            # Get the href
            href = link.get_attribute("href")

            logger.debug(f"Processing link {link.text.strip()}")
            if "item=" not in href:
                # Not an item link. We don't care about it
                return None, f"Skipping link {link.text.strip()} in because it is not an item link"

            # Get the text between the link and the next link
            text_between = ""
            if item_link_num == len(links) - 1:
                # Get html of the current link
                link_html = link.get_attribute("outerHTML")

                # Get all text after the link
                text_between = column_html.split(link_html)[1].strip()
            else:
                next_link = links[item_link_num + 1]

                # Get html of the current link
                link_html = link.get_attribute("outerHTML")
                # Get html of the next link
                next_link_html = next_link.get_attribute("outerHTML")
                # Get the text between the two links
                text_between = column_html.split(link_html)[1].split(next_link_html)[0].strip()
                

            logger.debug("Text between link and next link: " + text_between)
            if text_between == "":
                item_name = link.text.strip()
            else:

                # Remove any html tags from the text between
                # An html tag is defined as < followed by any number of characters that are not > followed by >
                text_between = re.sub(r"<[^>]*>", "", text_between)

                other_characters_to_remove = [
                    "/",
                    "&nbsp;"
                ]
                characters_to_remove_from_end = [
                    ","
                ]
                for character in other_characters_to_remove:
                    text_between = text_between.replace(character, "")

                # Remove whitespace
                text_between = text_between.strip()

                # Remove any characters from the end of the string
                for character in characters_to_remove_from_end:
                    if text_between.endswith(character):
                        text_between = text_between[:-1]
                
                # remove whitespace again
                text_between = text_between.strip()

                if text_between == "":
                    item_name = link.text.strip()
                else:
                    item_name = f"{link.text.strip()} {text_between}"

            # If there are double spaces, replace them with single spaces
            while "  " in item_name:
                logger.debug(f"Replacing double spaces in \"{item_name}\"")
                item_name = item_name.replace("  ", " ")

            
            logger.debug(f"href: {href}")

            # Get the item id
            item_id = href.split("item=")[1].split("/")[0]

            # If "&&" is in the link, it's probably rand or enchants. We can discard those.
            if "&&" in item_id:
                item_id = item_id.split("&&")[0]

            logger.debug(f"item_id: {item_id}")

            # Get the item name
            logger.debug(f"item_name: \"{item_name}\"")

            # Check if item_name contains any key from wow_suffix_mapping. Not using 'endswith' as some lists have inconsistent naming.
            #   For example, Rogue DPS lists "Cutthroat's Cape of the Tiger" as "Cutthroat's Cape of the Tiger +4/+4"
            # If it does, use the key as the suffix id
            # If it doesn't, use "" as the suffix id
            suffix_key = ""
            bis_suffix_id = ""
            for key in wow_suffix_mapping:
                if suffix_from_column_text:
                    # Special way - match the suffix in the column text
                    if key.lower() in column_text.lower():
                        # We have a suspected suffix match. Let's hit the wowhead page for the item and confirm

                        try:
                            bis_suffix_id = Item.get_bis_suffix_id(item_browser, wow_suffix_mapping, item_bis_suffix_cache, item_id, key)
                        except SuffixNotFoundException as e:
                            logger.warning(f"ItemID {item_id} has possible suffixes but none match {key}. Skipping determining the BIS Suffix for {item_name}")
                            suffix_key = wow_suffix_mapping[key]["key"]
                            break

                        # There is a difference between no possible suffixes and no matching suffixes
                        # If there are no possible suffixes, bis_suffix_id and suffix_key will be None/""
                        # If there are possible suffixes but none match, bis_suffix_id will be None/"" but suffix_key will be the key

                        if bis_suffix_id is None:
                            # No possible suffixes. Skip this item
                            logger.warning(f"ItemID {item_id} does not have possible suffixes. Skipping suffix match for {item_name} even though it contains {key}")
                            break
    
                        suffix_key = wow_suffix_mapping[key]["key"]
                        break
                else:
                    # Normal way - match the suffix in the item name
                    if key.lower() in item_name.lower():
                        # We have a suspected suffix match. Let's hit the wowhead page for the item and confirm
                        try:
                            bis_suffix_id = Item.get_bis_suffix_id(item_browser, wow_suffix_mapping, item_bis_suffix_cache, item_id, key)
                        except SuffixNotFoundException as e:
                            logger.warning(f"ItemID {item_id} has possible suffixes but none match {key}. Skipping determining the BIS Suffix for {item_name}")
                            suffix_key = wow_suffix_mapping[key]["key"]
                            break

                        if bis_suffix_id is None:
                            # No possible suffixes. Skip this item
                            logger.warning(f"ItemID {item_id} does not have possible suffixes. Skipping suffix match for {item_name} even though it contains {key}")
                            break
                        
                        suffix_key = wow_suffix_mapping[key]["key"]
                        break

            if bis_suffix_id is None:
                bis_suffix_id = ""

            item_key = f"{item_id}|{suffix_key}"
            item.set_key(item_key)
            item.set_id(item_id)
            item.set_name(item_name)
            item.set_suffixkey(suffix_key)
            item.set_bissuffixid(bis_suffix_id)
        
        return item, None
        
    

# Represents a single BIS page of data
class Page:
    def __init__(self, name: str, url: str, phase: str, spec: str, classname: str):
        self.name = name
        self.url = url
        self.phase = phase
        self.spec = spec
        self.classname = classname
        self.items = [] # List of Items
        self.item_keys = {} # Dictionary of itemid|suffixid to name.
        self.errors = []
        self.warnings = []


    def __str__(self):
        return f"{self.name} ({self.url})"

    def __repr__(self):
        return self.__str__()

    def add_item(self, item: Item) -> None:
        self.items.append(item)

    def get_items(self) -> list:
        return self.items
    
    def add_item_key(self, key: str, name: str) -> None:
        self.item_keys[key] = name
    
    def get_item_keys(self) -> dict:
        return self.item_keys

    def get_name(self):
        return self.name

    def get_url(self):
        return self.url
    
    def get_phase(self):
        return self.phase
    
    def get_classname(self):
        return self.classname
    
    def get_spec(self):
        return self.spec
    
    def add_error(self, error: str) -> None:
        self.errors.append(error)
    
    def get_errors(self):
        return self.errors
    
    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)
    
    def get_warnings(self):
        return self.warnings
    
    def get_item_json(self):
        output = []
        for item in self.items:
            output.append(item.to_json())
        return output

def is_expected_attribute_pattern(attribute: str) -> bool:
    """
    Given an attribute, return True if it matches the expected pattern.

    Expected patterns:
    * +DIGIT TEXT
    * +DIGIT% TEXT
    """

    regex = re.compile(r"^\+(\d+)(%)? .+$")
    matches = regex.findall(attribute)
    if matches is not None and len(matches) > 0:
        return True
    return False

def get_best_suffix_roll(raw_attribute: str) -> str:
    """
    Given a raw attribute string, return the best roll.

    Example input: "+(3 - 4) Agility"
    Example output: "+4 Agility"
    """

    # Trim the leading and trailing spaces
    raw_attribute = raw_attribute.strip()

    # Confirm there is only one set of parentheses
    if raw_attribute.count("(") > 1 or raw_attribute.count(")") > 1:
        logger.error(f"Found raw attribute {raw_attribute} with more than one set of parentheses")
        raise Exception(f"Found raw attribute {raw_attribute} with more than one set of parentheses")
    
    # If there are no parentheses, return the raw attribute
    if raw_attribute.count("(") == 0 and raw_attribute.count(")") == 0:
        logger.debug(f"Found raw attribute {raw_attribute} with no parentheses")
        if is_expected_attribute_pattern(raw_attribute):
            logger.debug(f"Found expected attribute pattern for raw attribute {raw_attribute}")
            return raw_attribute
        else:
            logger.error(f"Found unexpected attribute pattern for raw attribute {raw_attribute}")
            raise Exception(f"Found unexpected attribute pattern for raw attribute {raw_attribute}")

    # Get all text between the parentheses
    open_paren_index = raw_attribute.find("(")
    close_paren_index = raw_attribute.find(")")
    raw_roll = raw_attribute[open_paren_index + 1:close_paren_index]
    logger.debug(f"Found raw roll {raw_roll} for raw attribute {raw_attribute}")

    # Get the last number in raw_roll
    # Example: raw_roll = "3 - 4"
    regex = re.compile(r"(\d+)")
    matches = regex.findall(raw_roll)
    if matches is None or len(matches) == 0:
        logger.error(f"Failed to find number in raw roll {raw_roll} for raw attribute {raw_attribute}")
        raise Exception(f"Failed to find number in raw roll {raw_roll} for raw attribute {raw_attribute}")
    
    # Get the last number
    roll = matches[-1]
    logger.debug(f"Found roll {roll} for raw roll {raw_roll} for raw attribute {raw_attribute}")

    # Replace the parantheses with the roll using open_paren_index and close_paren_index
    # Example: raw_attribute = "+(3 - 4) Agility" -> "+4 Agility"
    best_roll = raw_attribute[:open_paren_index] + roll + raw_attribute[close_paren_index + 1:]
    logger.debug(f"Found best roll {best_roll} for raw roll {raw_roll} for raw attribute {raw_attribute}")

    return best_roll

@retry(TimeoutException, tries=3)
def get_with_retry(driver, url):
    logger.debug(f"Getting {url}")
    driver.get(url)

def parse_wowhead_url(browser: webdriver, item_browser: webdriver, url: str, listname: str, phase: str, spec: str, classname: str, custom_behaviors: dict, wow_suffix_mapping: dict, item_bis_suffix_cache: dict) -> Page:
    """
    Parses a wowhead url and returns a Page object with the following:
    - data (list of dictionaries)
        - Rank
        - ItemName
        - ItemID
        - Source
    - errors (list of strings)
    - warnings (list of strings)
    """

    # Get page
    logger.debug(f"Getting {url}")
    get_with_retry(browser, url)

    # Get data within id=guide-body
    logger.debug("Getting guide-body")
    guide_body = browser.find_element(By.ID, "guide-body")

    # Find all tables within guide_body
    logger.debug("Getting tables")
    tables = guide_body.find_elements(By.TAG_NAME, "table")

    page = Page(name=listname, url=url, phase=phase, spec=spec, classname=classname)

    # Iterate over tables and find the one with the correct columns
    # Correct columns are "Rank", "Item", and "Source" in that order in the first row
    logger.debug("Iterating over tables")
    for table in tables:
        # Find all rows in the table
        logger.debug("Getting rows")
        rows = table.find_elements(By.TAG_NAME, "tr")

        # Find the column names from the first row of each table
        columns = rows[0].find_elements(By.TAG_NAME, "td")
        column_names = []
        for column in columns:
            column_names.append(column.text.strip())

        if len(column_names) >= 3 and column_names[0] == "Rank" and column_names[1] == "Item" and column_names[2] == "Source":
            logger.info("Found a table with the correct columns")
        else:
            logger.info("Did not find a table with the correct columns")
            logger.info(f"Found columns {column_names}")
            continue

        

        # Determine slot by finding previous h3 tag with an id in (back, chest, head, neck, shoulders, waist, wrist, feet, finger, hands, legs, mainn-hand, off-hand, ranged, trinket)
        # Get the previous h3 tag
        item_slot = None
        previous_h3 = table.find_elements(By.XPATH, "preceding::h3")
        if len(previous_h3) > 0:
            previous_h3 = previous_h3[-1]
            logger.debug(f"Found previous h3 tag with text {previous_h3.text.strip()}")
            if previous_h3.get_attribute("id") is not None:
                logger.debug(f"Found previous h3 tag with id {previous_h3.get_attribute('id')}")

                # Get the id
                item_slot = str(previous_h3.get_attribute("id"))

                logger.info(f"Found slot {item_slot}")
        else:
            logger.error("Did not find previous h3 tag (item_slot)")
            raise Exception("Did not find previous h3 tag (item_slot)")
        
        

        # Find the data in each row
        row_current = 0
        row_count = len(rows) - 1
        for row in rows[1:]:
            row_current += 1

            # Get the number of Items per row - edge case but some rows have multiple items
            items_per_row = 0
            items_column_html = None
            item_links = []
            for i, column in enumerate(row.find_elements(By.TAG_NAME, "td")):
                column_name = column_names[i]
                if column_name == "Item":
                    item_links = column.find_elements(By.TAG_NAME, "a")
                    items_column_html = column.get_attribute("innerHTML")
                    if len(item_links) > 0:
                        items_per_row = len(item_links)
                        logger.debug(f"Found {items_per_row} items in row {row_current}")
                        break
            
            for itemanchornum in range(items_per_row):
                logger.info(f"-------------------------- Row: {row_current}, Anchor: {itemanchornum} --------------------------")
                logger.debug(f"Processing item {itemanchornum} in row {row_current}")

                item = Item()
                item.set_slot(item_slot)

                rank_found = False
                item_found = False
                source_found = False

                skip_row = False

                for i, column in enumerate(row.find_elements(By.TAG_NAME, "td")):
                    column_name = column_names[i]

                    if skip_row:
                        continue

                    
                    if column_name == "Rank":
                        rank_found = True

                        # Check if the column has a span with class="icontiny". If it does exist, get the background image from the style attribute. For the following example, we expect the output to be "spell_shadow_shadowbolt.gif":
                        # <span class="icontiny" style="background-image: url("https://wow.zamimg.com/images/wow/icons/tiny/spell_shadow_shadowbolt.gif");'></span>
                        
                        icons = column.find_elements(By.CLASS_NAME, "icontiny")
                        icon = None
                        if len(icons) > 0:
                            icon = icons[0]
                        if icon:
                            style = icon.get_attribute("style")
                            logger.debug(f"Found icon {style}")
                            if style is not None and style.strip() != "":
                                icon_image = style.split("url(\"")[1].split("\"")[0].split("/")[-1]

                                if icon_image in WOWHEAD_IMAGE_TO_SPEC:
                                    item.set_rank(column.text.strip() + f" ({WOWHEAD_IMAGE_TO_SPEC[icon_image]})")
                                else:
                                    page.add_error(f"Unknown icon image {icon_image}")
                                    item.set_rank(column.text.strip() + f" ({icon_image})")
                            else:
                                # No style attribute
                                page.add_warning(f"No style attribute for icon in row {row_current} in page {page.get_name()}")
                                item.set_rank(column.text.strip())
                        else:
                            item.set_rank(column.text.strip())

                        # Log the row number as "Priority"
                        item.set_prioritytext(f"{row_current}/{row_count}") # For example, 1/10
                        item.set_prioritynumber(row_current) # For example, 1. Useful for ordering the items for presentation
                        item.set_phase(phase)
                    elif column_name == "Item":
                        if item_found:
                            # Don't process item in a single row
                            logger.debug(f"Skipping item {item.get_name()} because item was already found")
                            continue

                        item, reason = Item.from_column_html(item_browser, item, itemanchornum, items_column_html, column.text.strip(), item_links, wow_suffix_mapping, item_bis_suffix_cache, custom_behaviors)
                        if item is None:
                            logger.warning(reason)
                            page.add_warning(reason)
                            skip_row = True
                            continue

                        item_found = True

                        logger.info(f"Found item {item.get_name()} with id {item.get_id()} and suffix key {item.get_suffixkey()}")
                        page.add_item_key(item.get_key(), item.get_name())
                    elif column_name == "Source":
                        source_found = True
                        if items_per_row > 1:
                            # If there are multiple items in the row,  just specify "multiple"
                            item.set_source("Multiple")
                        else:
                            item.set_source(column.text.strip())
                    elif column_name == "Location":
                        # Warrior sheets. Append to source
                        if items_per_row > 1:
                            pass
                        elif item.get_source() is not None:
                            item.set_source(f"{item.get_source()} ({column.text.strip()})")
                    else:
                        logger.warning(f"Unknown column name {column_name}")
                        page.add_warning(f"Unknown column name {column_name}")
                        #raise Exception(f"Unknown column name {column_name}")
                    
                if skip_row:
                    logger.debug(f"Skipping row {row_current}")
                    continue

                # Confirm that all columns were found
                if not rank_found:
                    page.add_error(f"Did not find Rank column in row {row_current}")
                    logger.error(f"Did not find Rank column in row {row_current}")
                if not item_found:
                    page.add_error(f"Did not find Item column in row {row_current}")
                    logger.error(f"Did not find Item column in row {row_current}")
                if not source_found:
                    page.add_error(f"Did not find Source column in row {row_current}")
                    logger.error(f"Did not find Source column in row {row_current}")
                
                logger.debug(f"Adding row {row_current} to data")
                page.add_item(item)

    if len(page.get_items()) == 0:
        page.add_error("Did not find any data")
        logger.error("Did not find any data")
    
    return page

@logger.catch(onerror=lambda _: sys.exit(1)) # Catch all exceptions and exit with code 1
def main():
    # Read WOWHEAD_WARLOCK_DPS_BIS_URL
    # Parse each table that has a columns "Rank", "Item", and "Source"
    # Extract the Rank, Item, and Source into a list of dictionaries
    # Output the list of dictionaries as a json file

    # Check if the chromedriver exists
    if not os.path.exists(CHROMEDRIVER_PATH):
        logger.critical("Chromedriver does not exist at " + CHROMEDRIVER_PATH)
        sys.exit(1)

    # Check if the chrome binary exists
    if not os.path.exists(CHROME_PATH):
        logger.critical("Chrome does not exist at " + CHROME_PATH)
        sys.exit(1)

    # Confirm the mapping file exists
    if not os.path.exists(WOW_SUFFIX_MAPPING_FILE):
        logger.critical("Mapping file does not exist at " + WOW_SUFFIX_MAPPING_FILE)
        sys.exit(1)

    # Confirm the suffix cache file exists
    if not os.path.exists(ITEM_BIS_SUFFIX_CACHE_FILE):
        logger.critical("Suffix cache file does not exist at " + ITEM_BIS_SUFFIX_CACHE_FILE)
        sys.exit(1)

    
    logger.info("Starting...")

    # Create a new Chrome session
    options = Options()
    options.add_argument("--headless") # Ensure GUI is off
    options.add_argument("--no-sandbox")

    # Set path to chrome/chromedriver as per your configuration
    options.binary_location = CHROME_PATH
    webdriver_service = Service(CHROMEDRIVER_PATH)

    # Read the mapping file as json into a dictionary
    wow_suffix_mapping = None
    with open(WOW_SUFFIX_MAPPING_FILE, "r") as f:
        wow_suffix_mapping = json.load(f)
    if wow_suffix_mapping is None:
        logger.critical("Failed to read mapping file")
        sys.exit(1)

    # Read the suffix cache file as json into a dictionary
    item_bis_suffix_cache = None
    with open(ITEM_BIS_SUFFIX_CACHE_FILE, "r") as f:
        item_bis_suffix_cache = json.load(f)
    if item_bis_suffix_cache is None:
        logger.critical("Failed to read suffix cache file")
        sys.exit(1)
    

    # Choose Chrome Browser
    browser = webdriver.Chrome(service=webdriver_service, options=options)
    browser.set_page_load_timeout(60)

    # Secondary browser for item pages
    item_browser = webdriver.Chrome(service=webdriver_service, options=options)
    item_browser.set_page_load_timeout(60)

    # Iterate over WOWHEAD_URLS
    pages = []
    errors = []
    warnings = []
    item_keys = {} # Dictionary of itemid|suffixid to item names
    for wowhead_url in WOWHEAD_URLS:
        logger.info(f"Processing {wowhead_url['list']} ({wowhead_url['url']})")
        custom_behaviors = None
        if "custom_behaviors" in wowhead_url:
            custom_behaviors = wowhead_url["custom_behaviors"]
        
        wowhead_page = parse_wowhead_url(browser=browser, item_browser=item_browser, url=wowhead_url["url"], listname=wowhead_url["list"], phase=wowhead_url["phase"], spec=wowhead_url["spec"], classname=wowhead_url["class"], custom_behaviors=custom_behaviors, wow_suffix_mapping=wow_suffix_mapping, item_bis_suffix_cache=item_bis_suffix_cache)
        if len(wowhead_page.get_errors()) > 0:
            logger.error("Errors:")
            for error in wowhead_page.get_errors():
                logger.error(error)
                errors.append(error)
        if len(wowhead_page.get_warnings()) > 0:
            logger.warning("Warnings:")
            for warning in wowhead_page.get_warnings():
                logger.warning(warning)
                warnings.append(warning)
        if len(wowhead_page.get_items()) > 0:
            logger.success(f"We have {len(wowhead_page.get_items())} rows of data for {wowhead_page.get_name()}")
            page = {
                "class": wowhead_page.get_classname(),
                "spec": wowhead_page.get_spec(),
                "list": wowhead_page.get_name(),
                "contents": wowhead_page.get_item_json()
            }
            pages.append(page)
            item_keys.update(wowhead_page.get_item_keys())



    # Summarize data
    output = {
        "items": item_keys,
        "pages": pages
    }
    # logger.debug(json.dumps(output, indent=4))

    # Write to file
    logger.info(f"Writing to {OUTPUT_PATH}")
    with open(OUTPUT_PATH, "w") as f:
        f.write(json.dumps(output, indent=4))

    # Write cache back to file
    logger.info(f"Writing suffix cache to {ITEM_BIS_SUFFIX_CACHE_FILE}")
    with open(ITEM_BIS_SUFFIX_CACHE_FILE, "w") as f:
        f.write(json.dumps(item_bis_suffix_cache, indent=4))



    # Close browser
    browser.quit()

    if len(errors) > 0:
        logger.error(f"Found {len(errors)} errors")
        for error in errors:
            logger.error(error)
        sys.exit(1)
    if len(warnings) > 0:
        logger.warning(f"Found {len(warnings)} warnings")
        for warning in warnings:
            logger.warning(warning)
    if len(errors) == 0 and len(warnings) == 0:
        logger.success("No errors or warnings")

    sys.exit(0)
    

if __name__ == "__main__":
    main()
