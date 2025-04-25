import pyautogui
import time
import pyperclip

time.sleep(5)

pyautogui.PAUSE = 0.5

pyautogui.click(x=583, y=525)
pyautogui.write("3014") #aqui viria a lista do excel com cod veiculo
pyautogui.click(x=901, y=412)

time.sleep(2)

pyautogui.doubleClick(x=458, y=612)

time.sleep(2)

pyautogui.press("tab")
pyautogui.press("enter")
pyautogui.doubleClick(x=536, y=765)
time.sleep(0.5)
pyautogui.keyDown("ctrl")
pyautogui.press("c")
pyautogui.keyUp("ctrl")
pyautogui.press("enter")
time.sleep(0.3)
pyautogui.press("win")
pyautogui.write("edge")
pyautogui.press("enter")
time.sleep(0.3)
pyautogui.write("ecooparts.com")
pyautogui.press("enter")

time.sleep(2)

pyautogui.click(x=1099, y=665)
pyautogui.keyDown("ctrl")
pyautogui.press("v")
pyautogui.keyUp("ctrl")
pyautogui.press("enter")


