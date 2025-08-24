import os, sys, math, time, random
import pygame
GRID_W, GRID_H = 180, 120
PIXEL_SIZE = 5
FPS_CAP = 60
TITLE = "Falling Sand - Single Player"
EMPTY, SAND, WATER, STONE, WOOD, FIRE, PLANT, SMOKE = range(8)
NAMES = ["빈칸","모래","물","돌","목재","불","식물","연기"]
COLORS = [(24,24,32),(228,196,111),(74,144,226),(110,120,130),(120,84,52),(255,101,47),(64,168,88),(160,160,160)]
FLAMMABLE = { WOOD: True, PLANT: True }
grid = [EMPTY]*(GRID_W*GRID_H)
fire_life = [0]*(GRID_W*GRID_H)
running = True
brush = 5
elem = SAND
def idx(x,y): return y*GRID_W + x
def clamp(v,a,b): return a if v<a else (b if v>b else v)
def neighbors8(x,y):
    return [(x-1,y-1),(x,y-1),(x+1,y-1),(x-1,y),(x+1,y),(x-1,y+1),(x,y+1),(x+1,y+1)]
def near_any(arr, x, y, pred):
    for nx,ny in neighbors8(x,y):
        if 0<=nx<GRID_W and 0<=ny<GRID_H:
            if pred(arr[idx(nx,ny)]): return True
    return False
def try_move(next_grid, next_fire, x, y, nx, ny, allow_swap_water=False):
    if not (0<=nx<GRID_W and 0<=ny<GRID_H): return False
    i = idx(x,y); j = idx(nx,ny)
    target = next_grid[j]; c = next_grid[i]
    if target == EMPTY:
        next_grid[j] = c; next_grid[i] = EMPTY
        if c == FIRE: next_fire[j] = next_fire[i]; next_fire[i] = 0
        return True
    if allow_swap_water and target == WATER:
        next_grid[j] = c; next_grid[i] = WATER
        return True
    return False
def simulate_once():
    cur = grid; next_grid = cur.copy(); next_fire = fire_life.copy()
    import random
    x_start = 0 if random.random() < 0.5 else GRID_W-1
    x_dir = 1 if x_start == 0 else -1
    for y in range(GRID_H-1, -1, -1):
        x = x_start
        while 0 <= x < GRID_W:
            i = idx(x,y); c = cur[i]
            if c != EMPTY:
                if next_grid[i] != c and c not in (FIRE, SMOKE): x += x_dir; continue
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
                        if not try_move(next_grid, next_fire, x,y, x,y-1): try_move(next_grid, next_fire, x,y, x+updir,y-1)
                elif c == SMOKE:
                    import random as R
                    if not try_move(next_grid, next_fire, x,y, x,y-1): try_move(next_grid, next_fire, x,y, x+(-1 if R.random()<0.5 else 1), y-1)
                    if R.random()<0.02: next_grid[i] = EMPTY
            x += x_dir
    global grid, fire_life; grid = next_grid; fire_life = next_fire
def paint_at(cx, cy, erase=False, dropper=False):
    global elem, brush
    r = brush
    for dy in range(-r, r+1):
        for dx in range(-r, r+1):
            if dx*dx + dy*dy > r*r: continue
            x, y = cx+dx, cy+dy
            if 0<=x<GRID_W and 0<=y<GRID_H:
                i = idx(x,y)
                if erase:
                    grid[i] = EMPTY; fire_life[i] = 0
                elif dropper:
                    elem = grid[i]
                else:
                    grid[i] = elem
                    if elem == FIRE: fire_life[i] = 200 + int(__import__('random').random()*200)
def clear_all():
    global grid, fire_life; grid = [EMPTY]*(GRID_W*GRID_H); fire_life = [0]*(GRID_W*GRID_H)
def save_screenshot(surface):
    import time, pygame, os
    os.makedirs("screenshots", exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    path = os.path.join("screenshots", f"sand-{ts}.png")
    pygame.image.save(surface, path); print("Saved:", path)
def main():
    global running, brush, elem, PIXEL_SIZE
    pygame.init(); clock = pygame.time.Clock()
    screen = pygame.display.set_mode((GRID_W*PIXEL_SIZE, GRID_H*PIXEL_SIZE), pygame.RESIZABLE)
    pygame.display.set_caption(TITLE)
    font = pygame.font.SysFont("consolas", 16)
    def draw():
        surf = pygame.Surface((GRID_W, GRID_H)); px = pygame.surfarray.pixels3d(surf)
        for y in range(GRID_H):
            off = y*GRID_W
            for x in range(GRID_W):
                v = grid[off+x]; px[x,y] = COLORS[v]
        del px
        scaled = pygame.transform.scale(surf, (GRID_W*PIXEL_SIZE, GRID_H*PIXEL_SIZE))
        screen.blit(scaled, (0,0))
        hud = f"[{NAMES[elem]}] Brush:{brush}  {'RUN' if running else 'PAUSE'}  FPS:{int(clock.get_fps())}"
        txt = font.render(hud, True, (230,230,235)); screen.blit(txt, (10, 8))
        pygame.display.flip()
    is_down=False; erase=False; dropper=False; last_cell=(-1,-1)
    def clamp_int(n,a,b): return a if n<a else (b if n>b else n)
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit(0)
            elif ev.type == pygame.VIDEORESIZE:
                win_w, win_h = ev.size; PIXEL_SIZE = clamp_int(win_w//GRID_W, 2, 10)
                screen = pygame.display.set_mode((GRID_W*PIXEL_SIZE, GRID_H*PIXEL_SIZE), pygame.RESIZABLE)
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1: is_down=True; erase=False; dropper=False
                elif ev.button == 3: is_down=True; erase=True; dropper=False
                elif ev.button == 2: is_down=True; erase=False; dropper=True
                elif ev.button == 4: brush = clamp_int(brush+1, 1, 40)
                elif ev.button == 5: brush = clamp_int(brush-1, 1, 40)
            elif ev.type == pygame.MOUSEBUTTONUP: is_down=False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE: running = not running
                elif ev.key == pygame.K_c: clear_all()
                elif ev.key == pygame.K_s: save_screenshot(screen)
                elif ev.key == pygame.K_g: PIXEL_SIZE = clamp_int(PIXEL_SIZE-1, 2, 10)
                elif ev.key == pygame.K_h: PIXEL_SIZE = clamp_int(PIXEL_SIZE+1, 2, 10)
                elif ev.key in (pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_5,pygame.K_6,pygame.K_7):
                    elem = [SAND,WATER,STONE,WOOD,FIRE,PLANT,SMOKE][ev.key - pygame.K_1]
        if is_down:
            mx, my = pygame.mouse.get_pos()
            cx = clamp(mx // PIXEL_SIZE, 0, GRID_W-1); cy = clamp(my // PIXEL_SIZE, 0, GRID_H-1)
            lx, ly = last_cell
            if lx>=0:
                steps = max(abs(cx-lx), abs(cy-ly))
                for i in range(1, steps+1):
                    ix = round(lx + (cx-lx)*i/steps); iy = round(ly + (cy-ly)*i/steps)
                    paint_at(ix, iy, erase, dropper)
            paint_at(cx, cy, erase, dropper); last_cell = (cx, cy)
        else: last_cell = (-1,-1)
        if running: simulate_once()
        draw(); clock.tick(FPS_CAP)
if __name__ == "__main__":
    main()
