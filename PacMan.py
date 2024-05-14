
import copy
from board import boards
import pygame
import math
pygame.init()

WIDTH = 900
HEIGHT = 950
screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)
level = copy.deepcopy(boards)
color = 'blue'
PI = math.pi
player_images = []
for i in range(1, 5):
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/player_images/{i}.png'), (45, 45)))
blinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/red.png'), (45, 45))

spooked_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/powerup.png'), (45, 45))
dead_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/dead.png'), (45, 45))
player_x = 450
player_y = 663
direction = 0
blinky_x = 56
blinky_y = 58
blinky_direction = 0

counter = 0
flicker = False
# R, L, U, D
turns_allowed = [False, False, False, False]
direction_command = 0
player_speed = 2
score = 0
powerup = False
power_counter = 0
eaten_ghost = [False, False, False, False]
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]
blinky_dead = False

blinky_box = False

moving = False
ghost_speeds = [2, 2, 2, 2]
startup_counter = 0
lives = 3
game_over = False
game_won = False


def check_node_ghost_plus(pos_x, pos_y, pac_x, pac_y, g0):
    list_node = []
    max_x = len(level) - 1
    max_y = len(level[0]) - 1

    # Kiểm tra node bên phải
    if pos_x + 1 <= max_x:
        right_node = level[pos_x + 1][pos_y]
        if right_node == 0 or right_node == 1 or right_node == 2:
            g = 1 + g0
            h = abs(pac_x - (pos_x + 1)) + abs(pac_y - pos_y)
            f = g + h
            list_node.append((pos_x + 1, pos_y, g, h, f, pos_x, pos_y))

    # Kiểm tra node bên trái
    if pos_x - 1 > 0:
        left_node = level[pos_x - 1][pos_y]
        if left_node == 0 or left_node == 1 or left_node == 2:
            g = 1 + g0
            h = abs(pac_x - (pos_x - 1)) + abs(pac_y - pos_y)
            f = g + h
            list_node.append((pos_x - 1, pos_y, g, h, f, pos_x, pos_y))

    # Kiểm tra node bên trên
    if pos_y - 1 > 0:
        upper_node = level[pos_x][pos_y - 1]
        if upper_node == 0 or upper_node == 1 or upper_node == 2:
            g = 1 + g0
            h = abs(pac_x - pos_x) + abs(pac_y - (pos_y - 1))
            f = g + h
            list_node.append((pos_x, pos_y - 1, g, h, f, pos_x, pos_y))

    # Kiểm tra node bên dưới
    if pos_y + 1 <= max_y:
        lower_node = level[pos_x][pos_y + 1]
        if lower_node == 0 or lower_node == 1 or lower_node == 2:
            g = 1 + g0
            h = abs(pac_x - pos_x) + abs(pac_y - (pos_y + 1))
            f = g + h
            list_node.append((pos_x, pos_y + 1, g, h, f, pos_x, pos_y))

    return list_node


def check_path_ghost(ghost_x, ghost_y, pac_x, pac_y):
    best_path = []  # đường đi tốt nhât
    close = []  # tập đóng
    open = []  # tập mở
    h0 = abs(ghost_x - pac_x) + abs(ghost_y - pac_y)
    f0 = h0
    g0 = 0
    open.append((ghost_x, ghost_y, g0, h0, f0, ghost_x, ghost_y))
    while (len(open) != 0):
        set_f = [row[4] for row in open]  # lấy ra chi phí ước lượng f từ 4 node xung quanh
        min_f = min(set_f)  # chọn ra chi phí nhỏ nhất
        min_index = set_f.index(min_f)
        # Nếu nút có chi phí nhỏ nhất là nút cần tìm(vị trí của pacman) thì đưa nút vào tập đóng và kết thúc
        if open[min_index][0] == pac_x and open[min_index][1] == pac_y:
            print("Search Completed")
            close.append(open[min_index])
            # print(close)
            return
        # Nếu chưa tìm thấy pacman thì tiếp tục xét nút kế tiếp có chi phí nhỏ nhất
        else:
            g0 = open[min_index][2]  # chi phí từ ghost tới nút đang xét
            nodes = check_node_ghost_plus(open[min_index][0], open[min_index][1], pac_x, pac_y, g0)
            # print(nodes)
            close.append(open[min_index])
            for i in range(len(nodes)):
                count_o = 0
                count_c = 0
                for j in range(len(open)):
                    if nodes[i][0] == open[j][0] and nodes[i][1] == open[j][1]:
                        if nodes[i][2] < open[j][2]:
                            open[j] = nodes[i]
                    else:
                        count_o += 1

                for k in range(len(close)):
                    if len(close) != 0:
                        if nodes[i][0] == close[k][0] and nodes[i][1] == close[k][1]:
                            count_c += 1

                if count_o == len(open) and len(close) != 0 and count_c == 0:
                    open.append(nodes[i])
            del open[min_index]
    best_path.append(close[len(close) - 1])

    x = 0
    for i in range(len(close) - 1, -1, -1):
        if close[i][0] == best_path[x][5] and close[i][1] == best_path[x][6]:
            best_path.append(close[i])
            x += 1
    print("BP");
    best_path.reverse()

    # Vẽ đường đi tìm được từ ghost tới pacman

    for i in range(len(best_path) - 1):
        current_cell = best_path[i]
        next_cell = best_path[i + 1]

        start_position = (current_cell[1] * 20 + 20 // 2, current_cell[0] * 20 + 20 // 2)
        end_position = (next_cell[1] * 20 + 20 // 2, next_cell[0] * 20 + 20 / 2)
        pygame.draw.line(screen, "red", start_position, end_position, 2)
    print(best_path)
    return best_path

class Ghost:
    def __init__(self, x_coord, y_coord, target, speed, img, direct, dead, box, id):
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direct
        self.dead = dead
        self.in_box = box
        self.id = id
        self.turns, self.in_box = self.check_collisions()
        self.rect = self.draw()

    def draw(self):
        if (not powerup and not self.dead) or (eaten_ghost[self.id] and powerup and not self.dead):
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif powerup and not self.dead and not eaten_ghost[self.id]:
            screen.blit(spooked_img, (self.x_pos, self.y_pos))
        else:
            screen.blit(dead_img, (self.x_pos, self.y_pos))
        ghost_rect = pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        return ghost_rect

    def check_collisions(self):
        # R, L, U, D
        num1 = ((HEIGHT - 50) // 32)
        num2 = (WIDTH // 30)
        num3 = 15
        self.turns = [False, False, False, False]
        if 0 < self.center_x // 30 < 29:
            if level[(self.center_y - num3) // num1][self.center_x // num2] == 9:
                self.turns[2] = True
            if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[1] = True
            if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[0] = True
            if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[3] = True
            if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[2] = True

            if self.direction == 2 or self.direction == 3:
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num2) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num2) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[0] = True

            if self.direction == 0 or self.direction == 1:
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[0] = True
        else:
            self.turns[0] = True
            self.turns[1] = True
        if 350 < self.x_pos < 550 and 370 < self.y_pos < 480:
            self.in_box = True
        else:
            self.in_box = False
        return self.turns, self.in_box

    # def move_ghost(self):
    #     blinky_x = self.y_pos // 20
    #     blinky_y = self.x_pos// 20
    #     pac_x = (player_y + 15) // 20
    #     pac_y = (player_x + 15) // 20
    #     path = check_path_ghost(blinky_x, blinky_y, pac_x, pac_y)
    #     if path[0][0] == path[1][0]:
    #         if path[0][1] - path[1][1] <= 0 and self.x_pos <= path[1][1] * 20 + 10:
    #             self.x_pos += ghost_speeds
    #         else:
    #             if (path[1][1] * 20 + 10) <= self.x_pos:
    #                 self.x_pos = - ghost_speeds
    #     if path[0][1] == path[1][1]:
    #         if path[0][0] - path[1][0] <= 0:
    #             d = path[1][0] * 20 + 10
    #             if (self.y_pos <= (path[1][0] * 20 + 10)):
    #                 print(d)
    #                 print(self.y_pos)
    #                 self.y_pos += ghost_speeds
    #         else:
    #             if path[1][0] * 20 + 10 <= self.y_pos:
    #                 self.y_pos = ghost_speeds
    #
    #     # print(self.x_pos)
    #     # print(self.y_pos)
    #     return self.x_pos, self.y_pos, 0

    def move_blinky(self):
        path = check_path_ghost(self.x_pos, self.y_pos, player_x, player_y)
        if not path:
            # Nếu không có đường đi được tìm thấy, Blinky sẽ không thể di chuyển
            return self.x_pos, self.y_pos, self.direction

        # Lấy ô tiếp theo trên đường đi (path[0] là vị trí hiện tại của Blinky)
        next_cell = path[0]

        # So sánh vị trí của ô tiếp theo với vị trí hiện tại của Blinky để xác định hướng di chuyển
        if next_cell[0] > self.x_pos:
            self.direction = 0  # Đi về phải
        elif next_cell[0] < self.x_pos:
            self.direction = 1  # Đi về trái
        elif next_cell[1] < self.y_pos:
            self.direction = 2  # Đi lên trên
        elif next_cell[1] > self.y_pos:
            self.direction = 3  # Đi xuống dưới

        # Di chuyển Blinky theo hướng đã xác định
        if self.direction == 0:
            self.x_pos += self.speed
        elif self.direction == 1:
            self.x_pos -= self.speed
        elif self.direction == 2:
            self.y_pos -= self.speed
        elif self.direction == 3:
            self.y_pos += self.speed

        # Kiểm tra xem Blinky có đi hết đoạn đường hay không
        if self.x_pos == next_cell[0] and self.y_pos == next_cell[1]:
            # Nếu đã đi hết đoạn đường, loại bỏ ô đầu tiên trong đường đi
            path.pop(0)

        # Kiểm tra và xử lý việc Blinky đi ra khỏi ranh giới của màn hình
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos -= 30

        return self.x_pos, self.y_pos, self.direction


def draw_misc():
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 920))
    if powerup:
        pygame.draw.circle(screen, 'blue', (140, 930), 15)
    for i in range(lives):
        screen.blit(pygame.transform.scale(player_images[0], (30, 30)), (650 + i * 40, 915))
    if game_over:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300],0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Game over! Space bar to restart!', True, 'red')
        screen.blit(gameover_text, (100, 300))
    if game_won:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300],0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Victory! Space bar to restart!', True, 'green')
        screen.blit(gameover_text, (100, 300))


def check_collisions(scor, power, power_count, eaten_ghosts):
    num1 = (HEIGHT - 50) // 32
    num2 = WIDTH // 30
    if 0 < player_x < 870:
        if level[center_y // num1][center_x // num2] == 1:
            level[center_y // num1][center_x // num2] = 0
            scor += 10
        if level[center_y // num1][center_x // num2] == 2:
            level[center_y // num1][center_x // num2] = 0
            scor += 50
            power = True
            power_count = 0
            eaten_ghosts = [False, False, False, False]
    return scor, power, power_count, eaten_ghosts


def draw_board():
    num1 = ((HEIGHT - 50) // 32)
    num2 = (WIDTH // 30)
    for i in range(len(level)):
        for j in range(len(level[i])):

            # CELL_SIZE = num2
            # CELL = num1
            # pygame.draw.rect(screen, 'red', (j * CELL_SIZE, i * CELL, CELL_SIZE, CELL), 1)

            if level[i][j] == 1:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 4)
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 10)
            if level[i][j] == 3:
                pygame.draw.line(screen, color, (j * num2 + (0.5 * num2), i * num1),
                                 (j * num2 + (0.5 * num2), i * num1 + num1), 3)
            if level[i][j] == 4:
                pygame.draw.line(screen, color, (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
            if level[i][j] == 5:
                pygame.draw.arc(screen, color, [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                                0, PI / 2, 3)
            if level[i][j] == 6:
                pygame.draw.arc(screen, color,
                                [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1], PI / 2, PI, 3)
            if level[i][j] == 7:
                pygame.draw.arc(screen, color, [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1], PI,
                                3 * PI / 2, 3)
            if level[i][j] == 8:
                pygame.draw.arc(screen, color,
                                [(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1], 3 * PI / 2,
                                2 * PI, 3)
            if level[i][j] == 9:
                pygame.draw.line(screen, 'white', (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)


def draw_player():
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    if direction == 0:
        screen.blit(player_images[counter // 5], (player_x, player_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter // 5], True, False), (player_x, player_y))
    elif direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 90), (player_x, player_y))
    elif direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 270), (player_x, player_y))


def check_position(centerx, centery):
    turns = [False, False, False, False]
    num1 = (HEIGHT - 50) // 32
    num2 = (WIDTH // 30)
    num3 = 15
    # check collisions based on center x and center y of player +/- fudge number
    if centerx // 30 < 29:
        if direction == 0:
            if level[centery // num1][(centerx - num3) // num2] < 3:
                turns[1] = True
        if direction == 1:
            if level[centery // num1][(centerx + num3) // num2] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery + num3) // num1][centerx // num2] < 3:
                turns[3] = True
        if direction == 3:
            if level[(centery - num3) // num1][centerx // num2] < 3:
                turns[2] = True

        if direction == 2 or direction == 3:
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num2) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num2) // num2] < 3:
                    turns[0] = True
        if direction == 0 or direction == 1:
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num1) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num1) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True
    else:
        turns[0] = True
        turns[1] = True

    return turns


def move_player(play_x, play_y):
    # r, l, u, d
    if direction == 0 and turns_allowed[0]:
        play_x += player_speed
    elif direction == 1 and turns_allowed[1]:
        play_x -= player_speed
    if direction == 2 and turns_allowed[2]:
        play_y -= player_speed
    elif direction == 3 and turns_allowed[3]:
        play_y += player_speed
    return play_x, play_y


def get_targets(blink_x, blink_y):
    if player_x < 450:
        runaway_x = 900
    else:
        runaway_x = 0
    if player_y < 450:
        runaway_y = 900
    else:
        runaway_y = 0
    return_target = (380, 400)
    if powerup:
        if not blinky.dead and not eaten_ghost[0]:
            blink_target = (runaway_x, runaway_y)
        elif not blinky.dead and eaten_ghost[0]:
            if 340 < blink_x < 560 and 340 < blink_y < 500:
                blink_target = (400, 100)
            else:
                blink_target = (player_x, player_y)
        else:
            blink_target = return_target

    else:
        if not blinky.dead:
            if 340 < blink_x < 560 and 340 < blink_y < 500:
                blink_target = (400, 100)
            else:
                blink_target = (player_x, player_y)
        else:
            blink_target = return_target

    return blink_target


run = True
while run:
    timer.tick(fps)
    if counter < 19:
        counter += 1
        if counter > 3:
            flicker = False
    else:
        counter = 0
        flicker = True
    if powerup and power_counter < 600:
        power_counter += 1
    elif powerup and power_counter >= 600:
        power_counter = 0
        powerup = False
        eaten_ghost = [False, False, False, False]
    if startup_counter < 180 and not game_over and not game_won:
        moving = False
        startup_counter += 1
    else:
        moving = True

    screen.fill('black')
    draw_board()
    center_x = player_x + 23
    center_y = player_y + 24
    if powerup:
        ghost_speeds = 1
    else:
        ghost_speeds = 2
    if eaten_ghost:
        ghost_speeds = 2
    if blinky_dead:
        ghost_speeds = 4


    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i]:
            game_won = False

    player_circle = pygame.draw.circle(screen, 'black', (center_x, center_y), 20, 2)
    draw_player()
    blinky = Ghost(blinky_x, blinky_y, targets, ghost_speeds, blinky_img, blinky_direction, blinky_dead,
                   blinky_box, 0)

    draw_misc()
    targets = get_targets(blinky_x, blinky_y)

    turns_allowed = check_position(center_x, center_y)
    if moving:
        player_x, player_y = move_player(player_x, player_y)
        if not blinky_dead and not blinky.in_box:
            blinky_x, blinky_y, blinky_direction = blinky.move_blinky()

    score, powerup, power_counter, eaten_ghost = check_collisions(score, powerup, power_counter, eaten_ghost)

    if not powerup:
        if (player_circle.colliderect(blinky.rect) and not blinky.dead) :
            if lives > 0:
                lives -= 1
                startup_counter = 0
                powerup = False
                power_counter = 0
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                blinky_x = 56
                blinky_y = 58
                blinky_direction = 0

                eaten_ghost = [False, False, False, False]
                blinky_dead = False

            else:
                game_over = True
                moving = False
                startup_counter = 0
    if powerup and player_circle.colliderect(blinky.rect) and eaten_ghost[0] and not blinky.dead:
        if lives > 0:
            powerup = False
            power_counter = 0
            lives -= 1
            startup_counter = 0
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            blinky_x = 56
            blinky_y = 58
            blinky_direction = 0

            eaten_ghost = [False, False, False, False]
            blinky_dead = False

        else:
            game_over = True
            moving = False
            startup_counter = 0

    if powerup and player_circle.colliderect(blinky.rect) and not blinky.dead and not eaten_ghost[0]:
        blinky_dead = True
        eaten_ghost[0] = True
        score += (2 ** eaten_ghost.count(True)) * 100


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                direction_command = 0
            if event.key == pygame.K_LEFT:
                direction_command = 1
            if event.key == pygame.K_UP:
                direction_command = 2
            if event.key == pygame.K_DOWN:
                direction_command = 3
            if event.key == pygame.K_SPACE and (game_over or game_won):
                powerup = False
                power_counter = 0
                lives -= 1
                startup_counter = 0
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                blinky_x = 56
                blinky_y = 58
                blinky_direction = 0


                eaten_ghost = [False, False, False, False]
                blinky_dead = False

                score = 0
                lives = 3
                level = copy.deepcopy(boards)
                game_over = False
                game_won = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and direction_command == 0:
                direction_command = -1
            if event.key == pygame.K_LEFT and direction_command == 1:
                direction_command = -1
            if event.key == pygame.K_UP and direction_command == 2:
                direction_command = -1
            if event.key == pygame.K_DOWN and direction_command == 3:
                direction_command = -1

    if direction_command == 0 and turns_allowed[0]:
        direction = 0
    if direction_command == 1 and turns_allowed[1]:
        direction = 1
    if direction_command == 2 and turns_allowed[2]:
        direction = 2
    if direction_command == 3 and turns_allowed[3]:
        direction = 3

    if player_x > 900:
        player_x = -47
    elif player_x < -50:
        player_x = 897

    if blinky.in_box and blinky_dead:
        blinky_dead = False

    pygame.display.flip()
pygame.quit()

