def start():

    import random

    legend = {".": {"name": "pebble",
                    "prob": None,
                    "max": None,
                    "character": "."},
              "c": {"name": "coin",
                    "prob": 0.05,
                    "max": None,
                    "character": "c"},
              "#": {"name": "rock",
                    "prob": 0.2,
                    "max": 30,
                    "character": "#"},              
              "s": {"name": "strong rock",
                    "prob": 0.4,
                    "max": None,
                    "character": "s"},
              "g": {"name": "gold rock",
                    "prob": 0.025,
                    "max": None,
                    "character": "g"},
              "<": {"name": "stair down",
                    "prob": 0.05,
                    "max": None,
                    "character": "<"},
              "@": {"name": "Player",
                    "prob": None,
                    "max": 1,
                    "character": "@"}
              }

    rooms = []
    d = []
    rt = 1

    maxlines = 40
    maxchars = 60
    maxrooms = 6
    room_nr = 0
    rock_nr = 0

    maxpebbles = legend["."]["max"]
    maxcoins = legend["c"]["max"]
    maxrocks = legend["#"]["max"]
    maxsrocks = legend["s"]["max"]
    maxgoldrocks = legend["g"]["max"]
    maxstairsdown = legend["<"]["max"]

    pebble_prob = legend["."]["prob"]
    coin_prob = legend["c"]["prob"]
    rock_prob = legend["#"]["prob"]
    srock_prob = legend["s"]["prob"]
    goldrock_prob = legend["g"]["prob"]
    stairdown_prob = legend["<"]["prob"]

    pebble_character = legend["."]["character"]
    coin_character = legend["c"]["character"]
    rock_character = legend["#"]["character"]
    srock_character = legend["s"]["character"]
    goldrock_character = legend["g"]["character"]
    stairdown_character = legend["<"]["character"]
    player_character = legend["@"]["character"]

    for y, line in enumerate(range(maxlines)):
        l = []
        #if line == 0 or line == 1 or line == 2 or line == 3 or line == 4 or line == 5 or line == 6 or line == 7 or line == 8 or line == 9:
        for x, char in enumerate(range(maxchars)):
            if x == 0 or x == maxchars-1 or y == 0 or y == maxlines-1:
                l.append(srock_character)
            #l.append(random.choice(list(legend.keys())))
            else:
                l.append(random.choice((rock_character)))
        d.append(l)
        
    # ---- snake ----

    y = random.randint(1, maxlines-1)
    for x in range(1, maxchars-1):
        d[y][x] = pebble_character
        z = random.random()
        if z < 0.5:
            # i want to go deeper
            howmuch = random.randint(1, 7)
            if y + howmuch < maxlines-2:
                for _ in range(howmuch):
                    y += 1
                    d[y][x] = pebble_character
        #elif z < 0.5:
        else:
            # i want to go higher
            howmuch = random.randint(1, 7)
            if y - howmuch > 1:
                for _ in range(howmuch):
                    y -= 1
                    d[y][x] = pebble_character
        # ---- new room? ----
        if rt == 1:
            rt = 0
            room_nr += 1
            maxbreite = maxchars-2 - x
            b = min(random.randint(3, 15), maxbreite)
            maxtiefe = maxlines-2 - y
            h = min(random.randint(2, 10), maxtiefe)
            rooms.append((x, y, b, h))
        elif random.random() < 0.1 and room_nr < maxrooms:
            room_nr += 1
            maxbreite = maxchars-2 - x
            b = min(random.randint(3, 15), maxbreite)
            maxtiefe = maxlines-2 - y
            h = min(random.randint(2, 10), maxtiefe)
            rooms.append((x, y, b, h))

    # --- snake2 ---

    for x in range(1, maxchars-1):
        d[y][x] = pebble_character
        if random.random() > 0.5:
            # i want to go deeper
            howmuch = random.randint(1, 7)
            if y + howmuch < maxlines-2:
                for _ in range(howmuch):
                    y += 1
                    d[y][x] = pebble_character
        elif random.random() < 0.5:
            # i want to go higher
            howmuch = random.randint(1, 7)
            if y - howmuch > 1:
                for _ in range(howmuch):
                    y -= 1
                    d[y][x] = pebble_character
        # ---- new room? ----
        elif rt == 1:
            rt = 0
            room_nr += 1
            maxbreite = maxchars-2 - x
            b = min(random.randint(3, 15), maxbreite)
            maxtiefe = maxlines-2 - y
            h = min(random.randint(2, 10), maxtiefe)
            rooms.append((x, y, b, h))
        elif random.random() < 0.1 and room_nr < maxrooms:
            room_nr += 1
            maxbreite = maxchars-2 - x
            b = min(random.randint(3, 15), maxbreite)
            maxtiefe = maxlines-2 - y
            h = min(random.randint(2, 10), maxtiefe)
            rooms.append((x, y, b, h))
    # ---- create rooms ----

    #for r in range(random.randint(minrooms, maxrooms)):
    #    # linke obere ecke, x coordinate
    #    x = random.randint(1, maxchars-10)
    #    # linke obere ecke, y coordinate
    #    y = random.randint(1, maxlines-5)
    #    # raumbreite
    #    b = random.randint(1, 8)
    #    # raumhöhe
    #    h = random.randint(1, 3)
    #    rooms.append((x, y, b, h))
        
    # ---- carve out rooms ----

    for r in rooms:
        x1 , y1, b, h = r
        for y, line in enumerate(d):
            for x, char in enumerate(line):
                if y >= y1 and y <= y1+h and x >= x1 and x <= x1+ b:
                    d[y][x] = "."     
    #                if ft == 1:
    #                    ft = 0
    #                    d[y][x] = "<"     
    #                elif random.random() < stairdown_prob and stair_nr < maxstairs:
    #                    stair_nr += 1
    #                    d[y][x] = "<"
    #                elif et == 1:
    #                    et = 0
    #                    d[y][x] = ">"
    #                elif random.random() < stairup_prob and stair_nr < maxstairs:
    #                    stair_nr += 1
    #                    d[y][x] = ">"
                    if random.random() < rock_prob:
                        if rock_nr < maxrocks and y > y1 and y < y1+ h and x > x1 and x < x1+b:
                            rock_nr += 1
                            d[y][x] = rock_character
    pebbles = []
    for y, line in enumerate(d):
        for x, char in enumerate(line):
            if d[y][x] == pebble_character:
                pebbles.append((x,y))
    max_pebbles = len(pebbles)
    
    walls = []
    for y, line in enumerate(d):
        for x, char in enumerate(line):
            if d[y][x] == rock_character:
                walls.append((x, y))
    max_walls = len(walls)

    # buschschleife

    random.shuffle(pebbles)
    n = 0
    for n in range(1, random.randint(1, max_pebbles//4)):
        x = pebbles[n][0]
        y = pebbles[n][1]
        if random.random() < coin_prob:
            d[y][x] = coin_character

    # treppenschleife

    random.shuffle(pebbles)
    n = 0
    x = pebbles[n][0]
    y = pebbles[n][1]
    d[y][x] = stairdown_character

    for n in range(1, random.randint(1, max_pebbles//4)):
        x = pebbles[n][0]
        y = pebbles[n][1]
        if random.random() < stairdown_prob:
            d[y][x] = stairdown_character
    
    random.shuffle(walls)
    for n in range(0, random.randint(1, max_walls//4)):
        x = walls[n][0]
        y = walls[n][1]
        if random.random() < srock_prob:
            d[y][x] = srock_character
    random.shuffle(walls)
    for n in range(0, random.randint(1, max_walls//4)):
        x = walls[n][0]
        y = walls[n][1]
        if random.random() < goldrock_prob:
            d[y][x] = goldrock_character
    
    # player generiert

    random.shuffle(pebbles)
    n = 0
    x = pebbles[n][0]
    y = pebbles[n][1]
    d[y][x] = player_character


    # ---- dungeon printer ----

    with open("dungeon.txt", "w") as f:
        for l in d:
            for char in l:
                print(char, end="")
                f.write(char)
            print()
            f.write("\n")    
        #print(rooms)
        
if __name__ == "__main__":
    start()
