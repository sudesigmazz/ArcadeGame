import pygame
import sys
import random

pygame.init()
pygame.mixer.init()

# --- Ekran ---
WIDTH, HEIGHT = 578, 678
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SUDE'NİN KAÇIŞI")
clock = pygame.time.Clock()
FPS = 60

# --- Renkler ---
WHITE = (245, 240, 230)
BLACK = (40, 30, 20)
RED = (205, 92, 92)           # Can rengi
GREEN = (222, 184, 135)       # Skor rengi
PINK = (255, 160, 122)        # Game over mesajı
BLUE = (210, 105, 30)         # High score rengi
GOLD = (255, 140, 0)          # Level rengi

# --- Font ---
font = pygame.font.SysFont("dejavuserif", 35, bold=True)


# --- Sesler ---
pygame.mixer.music.load("backgroundmusic.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

star_sound = pygame.mixer.Sound("star.mp3")
hit_sound = pygame.mixer.Sound("pain.mp3")
levelup_sound = pygame.mixer.Sound("levelup.mp3")
gameover_sound = pygame.mixer.Sound("gameover.mp3")

# --- Spritelar ---
background = pygame.image.load("background.png")
player_idle = pygame.image.load("idle.png")
walk_frames = [pygame.image.load("walk1.png"), pygame.image.load("walk2.png")]
walk_index = 0
walk_cooldown = 200
last_update = pygame.time.get_ticks()

enemy_img1 = pygame.image.load("enemy.png")
enemy_img2 = pygame.image.load("enemy2.png")
enemy_images = [enemy_img1, enemy_img2]

star_img = pygame.image.load("star01.png")

# --- Oyuncu ---
player_speed = 5
player_lives = 3
player_rect = player_idle.get_rect(topleft=(50, HEIGHT-150))
is_walking = False

# --- Oyun durumu ---
score = 0
high_score = 0
level = 1
level_up_score = 5
max_level = 5

level_up = False
level_up_timer = 0
LEVEL_UP_DISPLAY = 1500  # ms

game_over = False
game_win = False

mode = None
enemies = []

music_on = True

# --- Fonksiyonlar ---
def draw_button(text, x, y, w, h, color, hover_color):
    mouse = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, w, h)
    if rect.collidepoint(mouse):
        pygame.draw.rect(screen, hover_color, rect)
    else:
        pygame.draw.rect(screen, color, rect)
    label = font.render(text, True, BLACK)
    screen.blit(label, (x + (w - label.get_width())//2, y + (h - label.get_height())//2))
    return rect

def reset_player():
    return player_idle.get_rect(topleft=(50, HEIGHT-150))

def spawn_star():
    x = random.randint(50, WIDTH-50-star_img.get_width())
    y = random.randint(50, HEIGHT-50-star_img.get_height())
    return pygame.Rect(x, y, star_img.get_width(), star_img.get_height())

def set_mode_settings():
    global enemies, level_up_score
    enemies.clear()
    if mode == "kolay":
        positions = [(500,400),(200,300)]
        level_up_score = 6
        speed_range = (2,2)
    elif mode == "orta":
        positions = [(500,400),(200,300),(300,100)]
        level_up_score = 5
        speed_range = (2,3)
    else:  # zor
        positions = [(500,400),(200,300),(300,100),(400,200)]
        level_up_score = 4
        speed_range = (3,4)
    for pos in positions:
        img = random.choice(enemy_images)
        enemies.append({"rect": img.get_rect(topleft=pos),
                        "speed": random.randint(speed_range[0], speed_range[1]),
                        "dir":1,
                        "img": img})

def restart_game():
    global player_rect, player_lives, score, star_rect, game_over, game_win, level, enemies, level_up
    player_rect = reset_player()
    player_lives = 3
    score = 0
    level = 1
    star_rect = spawn_star()
    game_over = False
    game_win = False
    level_up = False
    set_mode_settings()

def settings_menu():
    global music_on
    in_settings = True
    while in_settings:
        screen.fill(BLACK)
        title = font.render("AYARLAR", True, GOLD)
        screen.blit(title, ((WIDTH-title.get_width())//2, 100))
        if music_on:
            music_btn = draw_button("Müziği Kapat", WIDTH//2-100, 250, 200, 50, GREEN, (0,200,0))
        else:
            music_btn = draw_button("Müziği Aç", WIDTH//2-100, 250, 200, 50, GREEN, (0,200,0))
        back_btn = draw_button("Geri", WIDTH//2-100, 350, 200, 50, GOLD, (255,215,0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if music_btn.collidepoint(event.pos):
                    music_on = not music_on
                    if music_on:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
                elif back_btn.collidepoint(event.pos):
                    in_settings = False

        pygame.display.update()
        clock.tick(FPS)

# Menü kontrol değişkenleri
menu = True
select_mode = False  # Zorluk seçimi ekranı açılacak mı?

while menu:
    screen.fill(BLACK)
    title = font.render("SUDE'NIN KAÇIŞI", True, GOLD)
    screen.blit(title, ((WIDTH-title.get_width())//2, 100))

    start_btn = draw_button("Başla", WIDTH//2-100, 250, 200, 50, GREEN, (0,200,0))
    settings_btn = draw_button("Ayarlar", WIDTH//2-100, 350, 200, 50, GOLD, (255,215,0))
    exit_btn = draw_button("Çıkış", WIDTH//2-100, 450, 200, 50, RED, (255,100,100))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if start_btn.collidepoint(event.pos):
                select_mode = True  # Zorluk seçimi ekranı açılacak
            elif settings_btn.collidepoint(event.pos):
                settings_menu()
            elif exit_btn.collidepoint(event.pos):
                pygame.quit()
                sys.exit()

    # --- Zorluk seçimi ekranı ---
    while select_mode:
        screen.fill(BLACK)
        title2 = font.render("Zorluk Seçin", True, GOLD)
        screen.blit(title2, ((WIDTH-title2.get_width())//2, 150))

        easy_btn = draw_button("Kolay", WIDTH//2-100, 250, 200, 50, GREEN, (0,200,0))
        normal_btn = draw_button("Orta", WIDTH//2-100, 350, 200, 50, GOLD, (255,215,0))
        hard_btn = draw_button("Zor", WIDTH//2-100, 450, 200, 50, RED, (255,100,100))

        for event2 in pygame.event.get():
            if event2.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event2.type == pygame.MOUSEBUTTONDOWN and event2.button == 1:
                if easy_btn.collidepoint(event2.pos):
                    mode = "kolay"
                    set_mode_settings()
                    select_mode = False
                    menu = False
                elif normal_btn.collidepoint(event2.pos):
                    mode = "orta"
                    set_mode_settings()
                    select_mode = False
                    menu = False
                elif hard_btn.collidepoint(event2.pos):
                    mode = "zor"
                    set_mode_settings()
                    select_mode = False
                    menu = False

        pygame.display.update()
        clock.tick(FPS)

    pygame.display.update()
    clock.tick(FPS)


# --- Oyun başlasın ---
star_rect = spawn_star()
star_float_offset = 0
star_float_direction = 1
set_mode_settings()

running = True
while running:
    screen.fill(WHITE)
    screen.blit(background, (0,0))

    # --- Event kontrolü ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if (game_over or game_win) and restart_rect.collidepoint(event.pos):
                restart_game()

    # --- Tuş kontrolleri ---
    keys = pygame.key.get_pressed()
    is_walking = False
    if keys[pygame.K_LEFT]:
        player_rect.x -= player_speed
        is_walking = True
    if keys[pygame.K_RIGHT]:
        player_rect.x += player_speed
        is_walking = True
    if keys[pygame.K_UP]:
        player_rect.y -= player_speed
        is_walking = True
    if keys[pygame.K_DOWN]:
        player_rect.y += player_speed
        is_walking = True

    # --- Karakter animasyonu ---
    if is_walking:
        now = pygame.time.get_ticks()
        if now - last_update > walk_cooldown:
            last_update = now
            walk_index = (walk_index + 1) % len(walk_frames)
        screen.blit(walk_frames[walk_index], player_rect)
    else:
        screen.blit(player_idle, player_rect)

    # --- Düşmanlar ---
    for enemy in enemies:
        enemy["rect"].x += enemy["speed"] * enemy["dir"]
        if enemy["rect"].right >= WIDTH or enemy["rect"].left <= 0:
            enemy["dir"] *= -1
        screen.blit(enemy["img"], enemy["rect"])

        if player_rect.colliderect(enemy["rect"]):
            player_lives -= 1
            player_rect = reset_player()
            hit_sound.play()
            if player_lives <= 0 and not game_over:
                game_over = True
                pygame.mixer.stop()  # Arka plan durur
                gameover_sound.play()

    # --- Yıldız ---
    star_float_offset += 0.2 * star_float_direction
    if abs(star_float_offset) > 5:
        star_float_direction *= -1
    screen.blit(star_img, (star_rect.x, star_rect.y + star_float_offset))

    if player_rect.colliderect(star_rect):
        score += 1
        star_sound.play()
        star_rect = spawn_star()
        star_float_offset = 0
        if score > high_score:
            high_score = score
        if score >= 10 and not game_win:
            game_win = True
            pygame.mixer.stop()

    # --- Level atlama ---
    if score >= level * level_up_score and level < max_level:
        level += 1
        level_up = True
        level_up_timer = pygame.time.get_ticks()
        levelup_sound.play()
        img = random.choice(enemy_images)
        new_enemy = {"rect": img.get_rect(topleft=(random.randint(50, WIDTH-50),
                                                   random.randint(50, HEIGHT-150))),
                     "speed": random.randint(2 + level//2, 4 + level//2), "dir":1, "img": img}
        enemies.append(new_enemy)

    # --- Gösterimler ---
    can_text = font.render("Can:", True, RED)
    screen.blit(can_text, (10,10))
    for i in range(player_lives):
        pygame.draw.rect(screen, RED, (90 + i*35, 10, 30, 30))

    score_text = font.render(f"Skor: {score}", True, GREEN)
    screen.blit(score_text, (10, 50))
    high_text = font.render(f"High: {high_score}", True, BLUE)
    screen.blit(high_text, (10, 90))
    level_text = font.render(f"Level: {level}", True, GOLD)
    screen.blit(level_text, (WIDTH - 150, 10))

    if level_up:
        elapsed = pygame.time.get_ticks() - level_up_timer
        text = font.render(f" Level {level}!", True, GOLD)
        screen.blit(text, ((WIDTH - text.get_width())//2, HEIGHT//2 - 50))
        if elapsed > LEVEL_UP_DISPLAY:
            level_up = False

    if game_over:
        end_text = font.render("Öldünüz! Tekrar Başlayın!", True, PINK)
    elif game_win:
        end_text = font.render("Kazandınız! Tebrikler!", True, GREEN)
    if game_over or game_win:
        screen.blit(end_text, ((WIDTH - end_text.get_width())//2, HEIGHT//2 - 100))
        restart_rect = draw_button("Yeniden Başla", (WIDTH - 200)//2, HEIGHT//2, 200, 50, GOLD, (255,215,0))
        player_rect = reset_player()
        for enemy in enemies:
            enemy["speed"] = 0


    
    


    pygame.display.update()
    clock.tick(FPS)



pygame.quit()
sys.exit()