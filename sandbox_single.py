def simulate_once():
    global grid, fire_life   # ⬅️ 반드시 함수 제일 위에!

    cur = grid
    next_grid = cur.copy()
    next_fire = fire_life.copy()
    import random
    x_start = 0 if random.random() < 0.5 else GRID_W-1
    x_dir = 1 if x_start == 0 else -1

    for y in range(GRID_H-1, -1, -1):
        x = x_start
        while 0 <= x < GRID_W:
            i = idx(x,y); c = cur[i]
            if c != EMPTY:
                if next_grid[i] != c and c not in (FIRE, SMOKE):
                    x += x_dir; continue

                if c == SAND:
                    if try_move(next_grid, next_fire, x,y, x,y+1, True): ...
                    elif try_move(next_grid, next_fire, x,y, x+( -1 if random.random()<0.5 else 1 ), y+1, True): ...
                    elif try_move(next_grid, next_fire, x,y, x+( 1 if random.random()<0.5 else -1 ), y+1, True): ...

                elif c == WATER:
                    if try_move(next_grid, next_fire, x,y, x,y+1): ...
                    else:
                        left_first = random.random() < 0.5
                        if left_first:
                            if try_move(next_grid, next_fire, x,y, x-1,y): ...
                            elif try_move(next_grid, next_fire, x,y, x+1,y): ...
                        else:
                            if try_move(next_grid, next_fire, x,y, x+1,y): ...
                            elif try_move(next_grid, next_fire, x,y, x-1,y): ...
                        if not try_move(next_grid, next_fire, x,y, x + (-1 if left_first else 1), y+1):
                            try_move(next_grid, next_fire, x,y, x + (1 if left_first else -1), y+1)

                elif c == WOOD:
                    if near_any(cur, x,y, lambda v: v==FIRE) and random.random()<0.03:
                        next_grid[i] = FIRE; next_fire[i] = 250 + int(random.random()*180)

                elif c == PLANT:
                    if near_any(cur, x,y, lambda v: v==WATER) and random.random()<0.08:
                        neigh = neighbors8(x,y); random.shuffle(neigh)
                        for nx,ny in neigh:
                            if 0<=nx<GRID_W and 0<=ny<GRID_H and next_grid[idx(nx,ny)]==EMPTY:
                                next_grid[idx(nx,ny)] = PLANT; break
                    if near_any(cur, x,y, lambda v: v==FIRE) and random.random()<0.2:
                        next_grid[i] = FIRE; next_fire[i] = 220 + int(random.random()*160)

                elif c == FIRE:
                    life = max(0, fire_life[i]-1)
                    for nx,ny in neighbors8(x,y):
                        if 0<=nx<GRID_W and 0<=ny<GRID_H:
                            j = idx(nx,ny); v = cur[j]
                            if v in (WOOD,PLANT) and random.random()<0.12:
                                next_grid[j] = FIRE; next_fire[j] = 220 + int(random.random()*180)
                            if v == WATER: life = max(0, life-6)
                    import random as R
                    if R.random()<0.35 and y-1>=0 and next_grid[idx(x,y-1)]==EMPTY:
                        next_grid[idx(x,y-1)] = SMOKE
                    if life <= 0:
                        next_grid[i] = EMPTY if R.random()<0.5 else STONE; next_fire[i] = 0
                    else:
                        next_fire[i] = life; updir = -1 if R.random()<0.5 else 1
                        if not try_move(next_grid, next_fire, x,y, x,y-1):
                            try_move(next_grid, next_fire, x,y, x+updir,y-1)

                elif c == SMOKE:
                    import random as R
                    if not try_move(next_grid, next_fire, x,y, x,y-1):
                        try_move(next_grid, next_fire, x,y, x+(-1 if R.random()<0.5 else 1), y-1)
                    if R.random()<0.02: next_grid[i] = EMPTY

            x += x_dir

    # 최종 반영
    grid = next_grid
    fire_life = next_fire
