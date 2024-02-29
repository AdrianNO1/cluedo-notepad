import pygame, time, copy, sys, pickle, os, random

players = """
Billy
Mom
Dad
Jesus Christ
Elon Musk
""".strip().split("\n")

"""
Remember to set the players!

Controls:
- Left click to select a person, weapon, room, or player, Right click to deselect
- Left click on a tile to toggle it between X and O, Right click to remove the mark
- Press a number to add it to the hovered tile
- Press the same number again to remove it
- Press 'v' to mark a tile as shown to a player
- Press 'n' to mark that the selected player does not have the selected person, weapon and room
- Press 'h' to mark that the selected player has at least one of the selected person, weapon and room
- Press 'r' to randomize the board to confuse the players (redo to undo)
- Press 'u' to hide the entire board (redo to show again)
- Press 'a' to fill in more information on the board
- Press 's' to save the board to a file
- Press 'l' to load the board from the file (is done automatically on startup)
- Ctrl + Z to undo
- Ctrl + Y to redo
"""



pygame.font.init()


num_collums = len(players)
screen = pygame.display.set_mode((200+100*num_collums, 700))

empty_template = {"main": "", "nums": [], "extra": ""}

people_colors = {"Oberst Multe": (255, 255, 0), "Professor Lavendel": (128, 0, 128), "Sogneprest Bregne": (0, 128, 0), "Fru Blåklokke": (0, 0, 255), "Frøken Rose": (255, 0, 0), "Fru Hvitveis": (255, 255, 255)}

if os.path.exists("rows.pkl"):
    with open('rows.pkl', 'rb') as f:
        backups = pickle.load(f)
        current = len(backups)-1
        rows = copy.deepcopy(backups[-1])
else:
    rows = {
        "players": players,
        "people": {person: [copy.deepcopy(empty_template) for _ in range(num_collums)] for person in ["Oberst Multe", "Professor Lavendel", "Sogneprest Bregne", "Fru Blåklokke", "Frøken Rose", "Fru Hvitveis"]},
        "weapons": {weapon: [copy.deepcopy(empty_template) for _ in range(num_collums)] for weapon in ["Dolk", "Lysestake", "Revolver", "Reip", "Blyrør", "Skiftenøkkel"]},
        "rooms": {room: [copy.deepcopy(empty_template) for _ in range(num_collums)] for room in ["Hallen", "Salongen", "Spisestuen", "Kjøkkenet", "Dansesalen", "Vinterhagen", "Biljardrommet", "Biblioteket", "Arbeidsværelset"]}
    }

    backups = [copy.deepcopy(rows)]
    current = 0

selected_player = None
selected_person = None
selected_weapon = None
selected_room = None

target_framerate = 144

row_height = 30
collum_width = 100
row_margin = 20
row_start = (50, 10)
border_size = 3

text_color = pygame.Color('blue')
tile_border_color = (0, 0, 0)
background_color = (128, 128, 128)

hovered_tile = None
text_surfaces = {}

def fit_text_into_rect(text, rect, initial_font_size, font_name=None, offset=0):
    font_size = initial_font_size
    font = pygame.font.Font(font_name, font_size)
    color = text_color
    if text in people_colors:
        color = people_colors[text]
    text_surface = font.render(text, True, color)
    
    # Decrease the font size until the text fits within the rectangle
    while text_surface.get_width() > rect.width - offset or text_surface.get_height() > rect.height - offset:
        font_size -= 1
        font = pygame.font.Font(font_name, font_size)
        text_surface = font.render(text, True, color)
        
        if font_size == 1:  # Prevent infinite loop
            break
    
    return text_surface, font

def draw_text_on_rect(text, rect, placement="main"):
    if str(text) in text_surfaces.keys():
        text_surface, text_rect = text_surfaces[str(text)]
        if placement == "main":
            text_rect.center = rect.center
        elif placement == "num":
            text_rect.midright = rect.midright
            text_rect.x -= border_size*2
        elif placement == "extra":
            text_rect.midleft = rect.midleft
            text_rect.x += border_size*2

    else:
        text_surface, font = fit_text_into_rect(text, rect, 50, offset=11)
        text_rect = text_surface.get_rect(center=rect.center)
        text_surfaces[str(text)] = (text_surface, text_rect)
    screen.blit(text_surface, text_rect)

def draw_tile(i, i2, i3, value):
    global hovered_tile
    rect = pygame.Rect(row_start[0] + i3*collum_width - border_size*i3, row_start[1] + i2*row_height + i*row_margin - border_size*i2, collum_width, row_height)
    if rect.collidepoint(pygame.mouse.get_pos()):
        #if i3 > 0 and i2 > 0:
        hovered_tile = {"rect": rect, "row": i2, "collum": i3, "value": value}
        #else:
            #hovered_name_tile = {"rect": rect, "row": i2, "collum": i3, "value":}
            #i22 = 0
            #for i1, (key, value1) in enumerate(rows.items()):
            #    if i1 > 0:
            #        for row, value22 in value1.items():
            #            i22 += 1
            #            if i22 == i2:
            #                break
            #                print(row)
    pygame.draw.rect(screen, tile_border_color, rect, width=border_size)
    if value:
        if isinstance(value, str):
            draw_text_on_rect(value, rect)
        else:
            draw_text_on_rect(value["main"], rect, "main")
            draw_text_on_rect("".join(value["nums"]), rect, "num")
            draw_text_on_rect(value["extra"], rect, "extra")

def num_pressed(num):
    num = str(num)
    if hovered_tile and hovered_tile["collum"] != 0 and hovered_tile["row"] != 0:
        value = get_tile_value_from_hovered_tile()
        if num in value["nums"]:
            value["nums"].remove(num)
        else:
            value["nums"].append(num)
            value["nums"].sort()
        create_backup()

def get_tile_value_from_hovered_tile():
    i2 = 0
    for i, (key, value) in enumerate(rows.items()):
        if i > 0:
            for row, value2 in value.items():
                i2 += 1
                if i2 == hovered_tile["row"]:
                    return value2[hovered_tile["collum"]-1]

def create_backup():
    global current
    if rows != backups[-1]:
        print("Creating backup")
        backups.append(copy.deepcopy(rows))
        current = len(backups)-1
        with open('rows.pkl', 'wb') as f:
            pickle.dump(backups, f, pickle.HIGHEST_PROTOCOL)
    else:
        print("No changes")

def fill_in(create_backupa=False):
    i2 = 0
    collums_nums = [[[] for _ in range(10)] for _ in range(num_collums)]
    for i, (key, value) in enumerate(rows.items()):
        if i > 0:
            for row, value2 in value.items():
                i2 += 1
                i3 = 0
                for value3 in value2:
                    for num in value3["nums"]:
                        collums_nums[i3][int(num)].append({"num": num, "row": i2, "value": value3})
                    i3 += 1
                row_main = [x["main"] for x in value2]
                if row_main.count("O") > 1:
                    print(f"WARNING: THE BOARD IS INVALID. TWO PEOPLE HAVE THE {row} CARD")
                if row_main.count("") != 0 and row_main.count("O") == 1:
                    for value3 in value2:
                        if value3["main"] != "O":
                            value3["main"] = "X"
    for collum in collums_nums:
        #print(collum)
        for num in collum:
            if [x["value"]["main"] for x in num].count("X") == 2:
                for x in num:
                    if x["value"]["main"] == "":
                        x["value"]["main"] = "O"
                        break
    if create_backupa:
        create_backup()


clock = pygame.time.Clock()
running = True
while running:
    clock.tick(target_framerate)
    screen.fill(background_color)

    hovered_tile = None
    i2 = 0
    for i, (key, value) in enumerate(rows.items()):
        if i == 0:
            for i3, person in enumerate(value):
                draw_tile(i+1, i2, i3+1, person)
            i2 += 1
        else:
            for name, row in value.items():
                for i3, value in enumerate([name] + row):
                    draw_tile(i, i2, i3, value)
                i2 += 1
    if hovered_tile:
        pygame.draw.rect(screen, (255, 0, 0), hovered_tile["rect"], width=border_size)
    if selected_person:
        pygame.draw.rect(screen, (0, 255, 0), selected_person["rect"], width=border_size)
    if selected_weapon:
        pygame.draw.rect(screen, (0, 255, 0), selected_weapon["rect"], width=border_size)
    if selected_room:
        pygame.draw.rect(screen, (0, 255, 0), selected_room["rect"], width=border_size)
    if selected_player:
        pygame.draw.rect(screen, (0, 255, 0), selected_player["rect"], width=border_size)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # check if left button was clicked
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if hovered_tile:
                if hovered_tile["collum"] == 0:
                    if event.button == 1:
                        if hovered_tile["row"] > 12:
                            selected_room = copy.deepcopy(hovered_tile)
                        elif hovered_tile["row"] > 6:
                            selected_weapon = copy.deepcopy(hovered_tile)
                        else:
                            selected_person = copy.deepcopy(hovered_tile)
                    elif event.button == 3:
                        if hovered_tile["row"] > 12:
                            selected_room = None
                        elif hovered_tile["row"] > 6:
                            selected_weapon = None
                        else:
                            selected_person = None

                elif hovered_tile["row"] == 0:
                    if event.button == 1:
                        selected_player = copy.deepcopy(hovered_tile)
                    elif event.button == 3:
                        selected_player = None
                else:
                    value2 = get_tile_value_from_hovered_tile()
                    if event.button == 1:
                        if value2["main"] == "X":
                            value2["main"] = "O"
                        else:
                            value2["main"] = "X"
                    elif event.button == 3:
                        value2["main"] = ""
                    create_backup()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                print("undo")
                current -= 1
                current = max(0, current)
                rows = copy.deepcopy(backups[current])
            elif event.key == pygame.K_y and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                print("redo")
                current += 1
                current = min(len(backups)-1, current)
                rows = copy.deepcopy(backups[current])
                    
            elif event.key == pygame.K_s:
                with open('rows.pkl', 'wb') as f:
                    pickle.dump(backups, f, pickle.HIGHEST_PROTOCOL)

            elif event.key == pygame.K_l:
                with open('rows.pkl', 'rb') as f:
                    backups = pickle.load(f)
                    current = len(backups)-1
                    rows = copy.deepcopy(backups[-1])
            
            elif event.key == pygame.K_1:
                num_pressed(1)
            elif event.key == pygame.K_2:
                num_pressed(2)
            elif event.key == pygame.K_3:
                num_pressed(3)
            elif event.key == pygame.K_4:
                num_pressed(4)
            elif event.key == pygame.K_5:
                num_pressed(5)
            elif event.key == pygame.K_6:
                num_pressed(6)
            elif event.key == pygame.K_7:
                num_pressed(7)
            elif event.key == pygame.K_8:
                num_pressed(8)
            elif event.key == pygame.K_9:
                num_pressed(9)
            
            elif event.key == pygame.K_v:
                value = get_tile_value_from_hovered_tile()
                value["extra"] = "V" if value["extra"] != "V" else ""
                create_backup()
            
            elif event.key == pygame.K_n:
                if selected_player:
                    i2 = 0
                    for i, (key, value) in enumerate(rows.items()):
                        if i > 0:
                            for row, value2 in value.items():
                                i2 += 1
                                if selected_person:
                                    if i2 == selected_person["row"]:
                                        value2[selected_player["collum"]-1]["main"] = "X"
                                if selected_weapon:
                                    if i2 == selected_weapon["row"]:
                                        value2[selected_player["collum"]-1]["main"] = "X"
                                if selected_room:
                                    if i2 == selected_room["row"]:
                                        value2[selected_player["collum"]-1]["main"] = "X"
                                
                    create_backup()
            
            elif event.key == pygame.K_h:
                if selected_player:
                    i2 = 0
                    new_num = 0
                    for i, (key, value) in enumerate(rows.items()):
                        if i > 0:
                            for row, value2 in value.items():
                                new_num = max([new_num] + [int(x) for x in value2[selected_player["collum"]-1]["nums"]])
                    new_num = str(new_num+1)

                    i2 = 0
                    for i, (key, value) in enumerate(rows.items()):
                        if i > 0:
                            for row, value2 in value.items():
                                i2 += 1
                                if selected_person:
                                    if i2 == selected_person["row"]:
                                        value2[selected_player["collum"]-1]["nums"].append(new_num)
                                if selected_weapon:
                                    if i2 == selected_weapon["row"]:
                                        value2[selected_player["collum"]-1]["nums"].append(new_num)
                                if selected_room:
                                    if i2 == selected_room["row"]:
                                        value2[selected_player["collum"]-1]["nums"].append(new_num)
                                
                    create_backup()
            
            elif event.key == pygame.K_r:
                for i, (key, value) in enumerate(rows.items()):
                    if i > 0:
                        for row, value2 in value.items():
                            for value3 in value2:
                                value3["main"] = random.choice(["X", "O"]) if random.randint(1, 6) == 1 else ""
                                value3["nums"] = list(str(random.randint(1, 99))) if random.randint(1, 10) == 1 else []
                                value3["extra"] = "V" if random.randint(1, 15) == 1 else ""
            elif event.key == pygame.K_u:
                for i, (key, value) in enumerate(rows.items()):
                    if i > 0:
                        for row, value2 in value.items():
                            for value3 in value2:
                                value3["main"] = ""
                                value3["nums"] = []
                                value3["extra"] = ""
            
            elif event.key == pygame.K_a:
                for _ in range(10):
                    fill_in()
                fill_in(True)
            

    pygame.display.flip()