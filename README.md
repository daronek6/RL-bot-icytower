# Reinforcement learning bot for platformer game "Icy Tower v1.5.1" with open-ai gym custom environment.
**Project made for my bachelor's degree at Military University of Technology. Project works only on Windows.**

## Requirements: 
- Python 3.8+ - recommended Anaconda - https://www.anaconda.com/products/individual
- gym 0.19.0 - pip install gym==0.19.0 - https://github.com/openai/gym 
- stable-baselines3 1.3.0 - pip install stable-baselines3==1.3.0 - https://github.com/DLR-RM/stable-baselines3 
- sb3-contrib 1.3.0 - pip install sb3-contrib==1.3.0 - https://github.com/Stable-Baselines-Team/stable-baselines3-contrib 
- pydirectinput 1.0.4 - pip install pydirectinput==1.0.4 - https://github.com/learncodebygaming/pydirectinput
- pywin32 300 - pip install pywin32==300 - https://github.com/mhammond/pywin32 
- pymeow 1.5 - pip package not available, download zip from https://github.com/qb-0/PyMeow/releases, extract then install "pip install ." 
- torch 1.10.1+cu102 (if machine has nvidia gpu with CUDA support) or version that supports only cpu - installation methods are on official website https://pytorch.org/
- Cheat Engine - https://www.cheatengine.org/
- Icy Tower v1.5.1 - modified version (removed background for better visibility) - https://drive.google.com/drive/folders/1SGBRsgZQLTaNW_LzHfP9Doz8TA3GlF3b?usp=sharing


## Registering custom gym environment: 
1. Go to "../RL-bot-icytower"
2. Install custom enviroment "pip install -e gym-icytower"


## Setting up environment (finding game memory addresses)
1. Download the game and put it in the main folder "../RL-bot-icytower"
2. Launch Icy Tower
3. Launch Cheat Engine 
4. Attach Icy Tower v 1.5.1 to Cheat Engine
5. In game select "play game" -> "classic game"
6. Find variable showing that the game is active (you are able to controll character)
    1. In Cheat Engine type 1 in field "Value:"
    2. Press "First Scan" 
    3. Fail in game by jumping up few platforms then jump below camera view 
    4. In Cheat Engine change value in field "Value:" to 0 and click "Next Scan"
    5. Reset the game by selecting "PLAY AGAIN" (shown after "Game over" screen) 
    6. Repeat all steps above but insted pressing "First Scan" in step #2 press "Next Scan". Repeat until you are left with 3 or less memory addresses 
    7. Observe what happenes to values in thoes addresses while you fail or reset (if value only displays values 0 or 1 then its correct value to use) 
    8. Copy address and paste in environment creation method gym.make() to argument "game_active_mem_address" (do it in "model.py", "test.py", "bot.py" and dont forget to add "0x" before address value as it is represented as hex value)
7. Find variable showing that game is main menu 
    1. In Cheat Engine type 0 in field "Value:"
    2. Press "First Scan" 
    3. Leave game to main menu by pressing ESC button twice 
    4. In Cheat Engine change value in field "Value:" to 1 and click "Next Scan" 
    5. In game select "play game" -> "classic game"
    6. Repeat all steps above but insted pressing "First Scan" in step #2 press "Next Scan". Repeat until you are left with 5 or less memory addresses 
    7. Observe what happenes to values in thoes addresses while main menu is present (if value only displays values 0 (while game is not in main menu) or 1 (while game is in main menu) then its correct value to use) 
    8. Copy address and paste in environment creation method gym.make() to argument "main_menu_active_mem_address" (do it in "model.py", "test.py", "bot.py" and dont forget to add "0x" before address value as it is represented as hex value)
8. Find variable showing platform level difference 
    1. In Cheat Engine type 0 in field "Value:"
    2. Press "First Scan" 
    3. Jump on 1st platform 
    4. In Cheat Engine change value in field "Value:" to 1 and click "Next Scan" 
    5. In game jump on the 2nd platform and in Cheat Engine click "Next Scan"
    6. In game jump down to 1st platform 
    7. In Cheat Engine change value in field "Value:" to 0 and click "Next Scan" 
    8. There should be 2 or less memory adresses left. Observe what happenes to values in thoes addresses when you jump up more than 1 platform apart (if the value changes to 2 if you jump to 2nd next platform or 3 if 3rd etc. then its correct value to use) 
    9. Copy address and paste in environment creation method gym.make() to argument "level_dif_mem_address" (do it in "model.py", "test.py", "bot.py" and dont forget to add "0x" before address value as it is represented as hex value)
9. Find variable showing last platform that character landed on befor combo 
    1. In Cheat Engine type 0 in field "Value:"
    2. Press "First Scan" 
    3. Jump on platfrom higher than 2 (ex. 3rd platform)
    4. In Cheat Engine change value in field "Value:" to number of a platform that you stoped on and click "Next Scan" 
    5. In game jump down by 1 platform 
    6. In Cheat Engine change value in field "Value:" to number of a platform that you stoped on and click "Next Scan" 
    7. There should be 3 or less memory adresses left. Observe what happenes to values in thoes addresses when make a combination (combo) of jumps (if you started combo on platform #5 then the value should update to correct platform number after timer on left top corner runs out or you fail a combo (fall from platfrom or jump exacly 1 platfrom apart), then its correct value to use) 
    8. Copy address and paste in environment creation method gym.make() to argument "level_pre_combo_mem_address" (do it in "model.py", "test.py", "bot.py" and dont forget to add "0x" before address value as it is represented as hex value)

##  Available scripts 
- model.py - Script used to train the bot (If you want to train your own model change names of saved models so old ones won't get overwritten)
- test.py - Script used to compare saved models (Run it if you want to see how seved models will perform this time. Results may vary.)
- bot.py - Script used as main product of a project (Model chosen in this script was the best one in terms of average score. Use it if you want to observe how it performs)

## Prelearned models
- https://drive.google.com/drive/folders/19ehOnEpzj9mR_nGYJcGBlVjRF-_yHnY9?usp=sharing

