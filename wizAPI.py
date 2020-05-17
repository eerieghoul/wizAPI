import win32gui
import pyautogui
import cv2
import time


class wizAPI:
    def __init__(self, handle=None):
        self._handle = handle
        self._spell_memory = {}
        self._friends_area = (625, 65, 20, 240)
        self._spell_area = (245, 290, 370, 70)
        self._enemy_area = (68, 26, 650, 35)

    def wait(self, s):
        time.sleep(s)
        return self

    def register_window(self, name="Wizard101", nth=0):
        def win_enum_callback(handle, param):
            if name == str(win32gui.GetWindowText(handle)):
                param.append(handle)

        handles = []
        win32gui.EnumWindows(win_enum_callback, handles)
        handles.sort()
        self._handle = handles[nth]
        return self

    def is_active(self):
        return self._handle == win32gui.GetForegroundWindow()

    def set_active(self):
        if not self.is_active():
            """ Press alt before and after to prevent a nasty bug """
            pyautogui.press('alt')
            win32gui.SetForegroundWindow(self._handle)
            pyautogui.press('alt')
        return self

    def get_window_rect(self):
        """Get the bounding rectangle of the window"""
        rect = win32gui.GetWindowRect(self._handle)
        return [rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]]

    def match_image(self, largeImg, smallImg, threshold=0.1, debug=False):
        method = cv2.TM_SQDIFF_NORMED

        # Read the images from the file
        small_image = cv2.imread(smallImg)
        large_image = cv2.imread(largeImg)
        w, h = small_image.shape[:-1]

        result = cv2.matchTemplate(small_image, large_image, method)

        # We want the minimum squared difference
        mn, _, mnLoc, _ = cv2.minMaxLoc(result)

        if (mn >= threshold):
            return False

        # Extract the coordinates of our best match
        x, y = mnLoc

        if debug:
            # Draw the rectangle:
            # Get the size of the template. This is the same size as the match.
            trows, tcols = small_image.shape[:2]

            # Draw the rectangle on large_image
            cv2.rectangle(large_image, (x, y),
                          (x+tcols, y+trows), (0, 0, 255), 2)

            # Display the original image with the rectangle around the match.
            cv2.imshow('output', large_image)

            # The image is only displayed if we call this
            cv2.waitKey(0)

        # Return coordinates to center of match
        return (x + (w * 0.5), y + (h * 0.5))

    def pixel_matches_color(self, coords, rgb, tolerance=0):
        wx, wy = self.get_window_rect()[:2]
        x, y = coords
        return pyautogui.pixelMatchesColor(x + wx, y + wy, rgb, tolerance=tolerance)

    def move_mouse(self, x, y, speed=.5):
        wx, wy = self.get_window_rect()[:2]
        pyautogui.moveTo(wx + x, wy + y, speed)
        return self

    def click(self, x, y, delay=.1, speed=.5, button='left'):
        (self.set_active()
         .move_mouse(x, y, speed=speed)
         .wait(delay))

        pyautogui.click(button=button)
        return self

    def screenshot(self, name, region=False):
        self.set_active()
        # region should be a tuple
        # Example: (x, y, width, height)
        window = self.get_window_rect()
        if not region:
            region = window
        else:
            # Adjust the region so that it is relative to the window
            wx, wy = window[:2]
            region = list(region)
            region[0] += wx
            region[1] += wy

        pyautogui.screenshot(name, region=region)

    def teleport_to_friend(self, match_img):
        self.set_active()
        # Check if friends already opened (and close it)
        while self.pixel_matches_color((780, 364), (230, 0, 0), 40):
            self.click(780, 364).wait(0.2)

        # Open friend menu
        self.click(780, 50)

        # Find friend that matches friend match_img
        self.screenshot('friend_area.png', region=self._friends_area)

        found = self.match_image(
            'friend_area.png', match_img)

        if found is not False:
            x, y = found
            offset_x, offset_y = self._friends_area[:2]
            (self.click(offset_x + x + 50, offset_y + y)  # Select friend
             .click(450, 115)  # Select port
             .click(415, 395)  # Select yes
             )
            return self
        else:
            print('Friend cound not be found')
            return False

    def enter_dungeon_dialog(self):
        self.set_active()
        return (self.pixel_matches_color((253, 550), (4, 195, 4), 5) and
                self.pixel_matches_color((284, 550), (20, 218, 11), 5))

    def is_DS_loading(self):
        self.set_active()
        """ Matches an orange pixel in the Dragonspyre loading screen """
        return self.pixel_matches_color((108, 551), (252, 127, 5), 20)

    def hold_key(self, key, holdtime):
        self.set_active()
        pyautogui.keyDown(key)
        time.sleep(holdtime)
        pyautogui.keyUp(key)
        return self

    def press_key(self, key):
        self.set_active()
        pyautogui.press(key)
        return self

    def is_health_low(self):
        self.set_active()
        return not self.pixel_matches_color((23, 563), (126, 41, 3), 10)

    def is_mana_low(self):
        self.set_active()
        return not self.pixel_matches_color((110, 594), (68, 13, 75), 10)

    def use_potion_if_needed(self):
        mana_low = self.is_mana_low()
        health_low = self.is_health_low()

        if mana_low:
            print('Mana is low, using potion')
        if health_low:
            print('Health is low, using potion')
        # if mana_low or health_low:
            self.click(160, 590, delay=.2)

    def pass_turn(self):
        self.click(254, 398, delay=.5)
        return self

    def is_turn_to_play(self):
        """ matches a pixel in the bottom right indicating the first player in battle """
        return self.pixel_matches_color((237, 398), (255, 255, 0), 20)

    def wait_for_next_turn(self):
        """ Wait for spell round to begin """
        while self.is_turn_to_play():
            self.wait(1)

        print('Spell round begins')

        """ Start detecting if it's our turn to play again """
        while not self.is_turn_to_play():
            self.wait(1)

        print('Our turn to play')
        return self

    def wait_for_end_of_round(self):
        """ Wait for spell round to begin """
        while self.is_turn_to_play():
            self.wait(1)

        self.flush_spell_memory()
        """ Start detecting if it's our turn to play again """
        """ Or if it's the end of the battle """
        while not (self.is_turn_to_play() or self.is_idle()):
            self.wait(1)

        return self

    def is_idle(self):
        """ Matches a pink pixel in the pet icon (only visible when not in battle) """
        return self.pixel_matches_color((140, 550), (252, 146, 206), 2)

    def find_spell(self, spell_name, threshold=0.15, max_tries=2, recapture=True):
        self.set_active()
        tries = 0
        res = False
        while not res and tries < max_tries:
            tries += 1

            if tries > 1:
                # Wait 1 second before re-trying
                self.wait(1)
                recapture = True

            if recapture:
                self.mouse_out_of_area(self._spell_area)
                self.screenshot('spell_area.png', region=self._spell_area)

            res = self.match_image(
                'spell_area.png', ('spells/' + spell_name + '.png'), threshold)

        if res is not False:
            x, y = res
            offset_x, offset_y = self._spell_area[:2]
            spell_pos = (offset_x + x, offset_y + y)
            # Remember location
            self._spell_memory[spell_name] = spell_pos
            return spell_pos
        else:
            return False

    def find_unusable_spells(self, limit=-1):
        self.set_active()
        self.mouse_out_of_area(self._spell_area)
        self.screenshot('spell_area.png', region=self._spell_area)
        w, h = (28, 38)  # The size of the gray area we're looking for
        img = cv2.imread('spell_area.png')
        rows, cols = img.shape[:2]
        pts = []

        # Determine if a pixel is gray enough
        def isGray(pixel, threshold):
            return abs(int(min(*pixel)) - int(max(*pixel))) <= threshold

        i = 2
        j = 0
        while j < (cols - w):
            """ find a rectangle with no color """
            grayScale = True
            for y in range(h):
                for x in range(w):
                    pixel = img[i + y, j + x]
                    if not isGray(pixel, threshold=30):
                        grayScale = False

                    if not grayScale:
                        break

                if not grayScale:
                    break

            if grayScale:
                offset_x, offset_y = self._spell_area[:2]
                spell_pos = (offset_x + j + w/2, offset_y + i+h/2)
                pts.append(spell_pos)
                j += w
                # Break if we've reached the limit in requested areas
                if limit > 0 and len(pts) >= limit:
                    break

            j += 1

        self._spell_memory["unusable"] = pts
        return pts

    def discard_unusable_spells(self, limit=-1):
        count = 0
        while True:
            count += 1
            print(count)
            try:
                # Try accessing from memory
                card_pos = self._spell_memory["unusable"][0]
            except (KeyError, IndexError):
                result = self.find_unusable_spells(limit=1)
                if len(result) is not 0:
                    card_pos = result[0]
                else:
                    break
            print(card_pos)
            # Right click the card position
            self.click(*card_pos, button='right', delay=.2)
            # Flush card memory
            self.flush_spell_memory()

    def flush_spell_memory(self):
        self._spell_memory = {}
        return

    def select_spell(self, spell):
        try:
            spell_pos = self._spell_memory[spell]
        except KeyError:
            spell_pos = self.find_spell(spell)

        if spell_pos is not False:
            self.click(*spell_pos, delay=.3)
            return self
        else:
            return False

    def cast_spell(self, spell):
        if self.find_spell(spell):
            print('Casting', spell)
            self.flush_spell_memory()
            return self.select_spell(spell)
        else:
            return False

    def enchant(self, spell_name, enchant_name, threshold=0.1, silent_fail=False):
        if self.find_spell(spell_name, threshold=threshold) and self.find_spell(enchant_name, recapture=False, threshold=threshold):
            print('Enchanting', spell_name, 'with', enchant_name)
            self.select_spell(enchant_name)
            self.select_spell(spell_name)
            self.flush_spell_memory()
            return self
        else:
            if not silent_fail:
                print("One or more spells couldn't be found:",
                      spell_name, enchant_name)
            return False

    def get_enemy_pos(self, enemy_img):
        self.screenshot('enemy_area.png', region=self._enemy_area)

        found = self.match_image('enemy_area.png', enemy_img, threshold=.2)

        if found is not False:
            found_x, _ = found
            enemy_pos = round((found_x - 60) / 170) + 1
            return enemy_pos
        else:
            return False

    def at_target(self, target_pos):
        """ Clicks the target """
        x = (170 * (target_pos - 1)) + 130
        y = 50
        self.click(x, y, delay=.2)
        return self

    def mouse_out_of_area(self, area):
        # Adjust the region so that it is relative to the window
        wx, wy = self.get_window_rect()[:2]
        region = list(area)
        region[0] += wx
        region[1] += wy

        def in_area(area):
            px, py = pyautogui.position()
            x, y, w, h = area
            return (px > x and px < (x + w) and py > y and py < (y + h))

        while in_area(region):
            pyautogui.moveRel(0, -100, duration=0.5)

        return self

    def face_arrow(self):
        self.set_active()
        pyautogui.keyDown('a')
        count = 0
        while not self.pixel_matches_color((385, 531), (133, 120, 14), 2):
            count += 1
            pass
        pyautogui.keyUp('a')
        self.hold_key('d', min(count / 100, 0.2))
        return self
