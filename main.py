from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math

app = Ursina()

# -----------------------------
# Window settings
# -----------------------------
window.title = "FPS Prototype"
window.fullscreen = True
window.borderless = False
window.exit_button.visible = False
window.fps_counter.enabled = False

mouse.visible = False
mouse.locked = True

# -----------------------------
# Game state
# -----------------------------
RESPAWN_DELAY = 5.0
respawn_timer = 0.0
is_respawning = False

SPAWN_POSITION = Vec3(0, 2, 18)

# -----------------------------
# Player
# -----------------------------
player = FirstPersonController(
    position=(SPAWN_POSITION.x, SPAWN_POSITION.y, SPAWN_POSITION.z),
    speed=7,
    mouse_sensitivity=(120, 120),
    gravity=1.5
)
player.cursor.visible = False
player.health = 150
player.camera_pivot.y = 1.7

player_body = Entity(
    model='cube',
    color=color.azure,
    scale=(1.0, 2.0, 1.0),
    position=(SPAWN_POSITION.x, SPAWN_POSITION.y - 1, SPAWN_POSITION.z),
    visible=False
)

# -----------------------------
# HUD
# -----------------------------
info_text = Text(
    text='Left click to shoot',
    position=(-0.8, 0.45),
    scale=1.3,
    origin=(0, 0),
    color=color.white
)

health_text = Text(
    text='Health: 150',
    position=(-0.8, 0.35),
    scale=1.2,
    origin=(0, 0),
    color=color.white
)

# -----------------------------
# Main floor / map area
# -----------------------------
ground = Entity(
    model='cube',
    texture='grass',
    color=color.white,
    position=(0, 0, 0),
    scale=(90, 1, 90),
    collider='box'
)

# -----------------------------
# Spawn room
# -----------------------------
room_center_z = 18
room_width = 18
room_depth = 18
room_height = 6

room_floor = Entity(
    model='cube',
    color=color.rgb(90, 180, 210),
    position=(0, 0.05, room_center_z),
    scale=(room_width, 0.1, room_depth),
    collider='box'
)

roof = Entity(
    model='cube',
    color=color.gray,
    position=(0, room_height, room_center_z),
    scale=(room_width, 0.5, room_depth),
    collider='box'
)

# Room walls
wall_blueprints = [
    ((-room_width / 2, room_height / 2, room_center_z), (1, room_height, room_depth)),
    ((room_width / 2, room_height / 2, room_center_z), (1, room_height, room_depth)),
    ((0, room_height / 2, room_center_z - room_depth / 2), (room_width, room_height, 1)),
    ((-5, room_height / 2, room_center_z + room_depth / 2), (8, room_height, 1)),
    ((5, room_height / 2, room_center_z + room_depth / 2), (8, room_height, 1)),
]

for pos, scale in wall_blueprints:
    Entity(
        model='cube',
        color=color.gray,
        position=pos,
        scale=scale,
        collider='box'
    )

# Door frame
door_frame_left = Entity(
    model='cube',
    color=color.dark_gray,
    position=(-2.5, 1.5, room_center_z + room_depth / 2 + 0.2),
    scale=(1, 3, 0.5),
    collider='box'
)

door_frame_right = Entity(
    model='cube',
    color=color.dark_gray,
    position=(2.5, 1.5, room_center_z + room_depth / 2 + 0.2),
    scale=(1, 3, 0.5),
    collider='box'
)

door_frame_top = Entity(
    model='cube',
    color=color.dark_gray,
    position=(0, 3.2, room_center_z + room_depth / 2 + 0.2),
    scale=(6, 0.5, 0.5),
    collider='box'
)

door_open = True
door = Entity(
    model='cube',
    color=color.brown,
    position=(0, 1.5, room_center_z + room_depth / 2 + 0.5),
    scale=(5.5, 3, 0.4),
    collider='box'
)

# Room collision boxes for enemy blocking
room_walls = [
    ((-9, 3, 18), (1, 6, 18)),
    ((9, 3, 18), (1, 6, 18)),
    ((0, 3, 9), (18, 6, 1)),
    ((-5, 3, 27), (8, 6, 1)),
    ((5, 3, 27), (8, 6, 1)),
    ((-2.5, 1.5, 27.2), (1, 3, 0.5)),
    ((2.5, 1.5, 27.2), (1, 3, 0.5)),
    ((0, 3.2, 27.2), (6, 0.5, 0.5)),
    ((0, 6, 18), (18, 0.5, 18)),
]

# -----------------------------
# Outer walls around the whole arena
# -----------------------------
wall_data = [
    ((0, 2.5, -40), (80, 5, 1)),
    ((0, 2.5, 40), (80, 5, 1)),
    ((-40, 2.5, 0), (1, 5, 80)),
    ((40, 2.5, 0), (1, 5, 80)),
]

for pos, scale in wall_data:
    Entity(
        model='cube',
        color=color.gray,
        position=pos,
        scale=scale,
        collider='box'
    )

# -----------------------------
# Interior obstacles
# -----------------------------
obstacle_positions = [
    (-10, -8, 6, 6),
    (12, 5, 6, 6),
    (-18, 18, 7, 7),
    (22, -18, 7, 7),
    (0, -18, 8, 6),
    (18, 15, 6, 8),
    (-22, -22, 7, 5),
    (25, 0, 6, 6),
    (-25, 6, 6, 7),
]

obstacles = []

for x, z, sx, sz in obstacle_positions:
    block = Entity(
        model='cube',
        color=color.dark_gray,
        position=(x, 1.5, z),
        scale=(sx, 3, sz),
        collider='box'
    )
    obstacles.append(block)

# -----------------------------
# Gun
# -----------------------------
class Gun(Entity):
    def __init__(self):
        super().__init__(
            parent=camera,
            position=(0.7, -0.55, 1.2),
            rotation=(0, 0, 0),
            scale=(1, 1, 1)
        )

        self.body = Entity(
            parent=self,
            model='cube',
            color=color.black,
            scale=(0.14, 0.11, 0.9),
            position=(0, 0, 0)
        )

        self.grip = Entity(
            parent=self,
            model='cube',
            color=color.black,
            scale=(0.09, 0.22, 0.12),
            position=(0, -0.16, -0.10),
            rotation=(18, 0, 0)
        )

        self.barrel = Entity(
            parent=self,
            model='cube',
            color=color.black,
            scale=(0.05, 0.05, 0.7),
            position=(0, 0.04, 0.55)
        )

        self.muzzle = Entity(
            parent=self,
            model='cube',
            color=color.dark_gray,
            scale=(0.04, 0.04, 0.08),
            position=(0, 0.04, 1.05)
        )

        self.front_sight = Entity(
            parent=self,
            model='cube',
            color=color.dark_gray,
            scale=(0.02, 0.07, 0.02),
            position=(0, 0.11, 0.35)
        )

        self.back_sight = Entity(
            parent=self,
            model='cube',
            color=color.dark_gray,
            scale=(0.02, 0.05, 0.02),
            position=(0, 0.10, -0.22)
        )

        self.cooldown = 0.0

    def shoot(self):
        if self.cooldown > 0 or is_respawning:
            return

        hit = raycast(camera.world_position, camera.forward, distance=120, ignore=(player, player_body))
        if hit.hit:
            if hasattr(hit.entity, 'health'):
                hit.entity.health -= 35
                info_text.text = f'Enemy health: {int(hit.entity.health)}'
                if hit.entity.health <= 0:
                    destroy(hit.entity)
                    info_text.text = "Enemy eliminated!"
            else:
                info_text.text = "Hit wall / object"
        else:
            info_text.text = "Missed"

        self.cooldown = 0.25

    def update(self):
        if is_respawning:
            return
        self.cooldown -= time.dt

gun = Gun()

# -----------------------------
# Enemy spawn validation
# -----------------------------
def is_valid_enemy_spawn(x, z):
    # keep enemies out of the room
    if abs(x) < 12 and abs(z - room_center_z) < 12:
        return False

    if abs(x) > 32 or abs(z) > 32:
        return False

    for block in obstacles:
        bx = block.x
        bz = block.z
        sx = block.scale_x / 2 + 1.5
        sz = block.scale_z / 2 + 1.5
        if abs(x - bx) < sx and abs(z - bz) < sz:
            return False

    for wall_pos, wall_scale in room_walls:
        wx, wy, wz = wall_pos
        sx, sy, sz = wall_scale
        if abs(x - wx) < sx / 2 + 1.5 and abs(z - wz) < sz / 2 + 1.5:
            return False

    return True

# -----------------------------
# Enemy
# -----------------------------
class Enemy(Entity):
    def __init__(self, position=(0, 1, 0)):
        super().__init__(
            model='cube',
            color=color.rgb(220, 40, 40),
            position=position,
            scale=(1.8, 3, 1.8),
            collider='box'
        )
        self.health = 100
        self.speed = 1.2
        self.attack_cooldown = 0.0

    def update(self):
        if is_respawning:
            return

        if self.health <= 0:
            destroy(self)
            return

        self.attack_cooldown -= time.dt
        distance = distance_2d(self.position, player.position)

        if distance < 35:
            direction = Vec3(player.x - self.x, 0, player.z - self.z)
            if direction.length() > 0:
                direction = direction.normalized()

            new_pos = self.position + direction * self.speed * time.dt

            valid = True

            if abs(new_pos.x) > 38 or abs(new_pos.z) > 38:
                valid = False

            for wall_pos, wall_scale in room_walls:
                wx, wy, wz = wall_pos
                sx, sy, sz = wall_scale
                if abs(new_pos.x - wx) < sx / 2 + 1.5 and abs(new_pos.z - wz) < sz / 2 + 1.5:
                    valid = False
                    break

            if valid:
                for block in obstacles:
                    bx = block.x
                    bz = block.z
                    sx = block.scale_x / 2 + 1.5
                    sz = block.scale_z / 2 + 1.5
                    if abs(new_pos.x - bx) < sx and abs(new_pos.z - bz) < sz:
                        valid = False
                        break

            if valid:
                self.position = new_pos

            self.rotation_y = math.degrees(math.atan2(direction.x, direction.z))

            if distance < 2.8 and self.attack_cooldown <= 0:
                player.health -= 15
                self.attack_cooldown = 1.0
                health_text.text = f"Health: {int(player.health)}"

                if player.health <= 0:
                    player.health = 0
                    health_text.text = "Health: 0"
                    info_text.text = "You died!"
                    start_respawn()

def spawn_enemy():
    for _ in range(200):
        x = random.uniform(-30, 30)
        z = random.uniform(-30, 30)
        if is_valid_enemy_spawn(x, z):
            Enemy(position=(x, 1, z))
            return

for _ in range(10):
    spawn_enemy()

# -----------------------------
# Freeze / unfreeze player
# -----------------------------
def freeze_player():
    player.speed = 0
    player.gravity = 0
    player.velocity = Vec3(0, 0, 0)

def unfreeze_player():
    player.speed = 7
    player.gravity = 1.5

# -----------------------------
# Respawn system
# -----------------------------
def respawn_player():
    global is_respawning, respawn_timer

    player.position = Vec3(SPAWN_POSITION.x, SPAWN_POSITION.y, SPAWN_POSITION.z)
    player_body.position = Vec3(SPAWN_POSITION.x, SPAWN_POSITION.y - 1, SPAWN_POSITION.z)

    player.health = 150
    player.rotation_x = 0
    player.rotation_y = 0
    player.camera_pivot.rotation_x = 0

    health_text.text = "Health: 150"
    info_text.text = "You respawned"
    mouse.visible = False
    mouse.locked = True
    is_respawning = False
    respawn_timer = 0.0
    unfreeze_player()

def start_respawn():
    global is_respawning, respawn_timer
    is_respawning = True
    respawn_timer = RESPAWN_DELAY
    freeze_player()
    mouse.visible = False
    mouse.locked = True
    info_text.text = f"Respawning in {RESPAWN_DELAY:.0f}s"

# -----------------------------
# Door logic
# -----------------------------
def toggle_door():
    global door_open
    if door_open:
        door.y = 6
        door_open = False
        info_text.text = "Door closed"
    else:
        door.y = 1.5
        door_open = True
        info_text.text = "Door open"

# -----------------------------
# Input
# -----------------------------
def input(key):
    if key == 'left mouse down':
        gun.shoot()

    if key == 'escape':
        mouse.visible = True
        mouse.locked = False
        application.quit()

    if key == 'r':
        respawn_player()

    if key == 'f':
        toggle_door()

# -----------------------------
# Update loop
# -----------------------------
def update():
    global respawn_timer

    player_body.position = Vec3(player.x, player.y - 1, player.z)
    player_body.rotation_y = player.rotation_y

    if is_respawning:
        respawn_timer -= time.dt
        info_text.text = f"Respawning in {respawn_timer:.1f}s"
        if respawn_timer <= 0:
            respawn_player()
        return

    if player.health <= 0:
        start_respawn()

    health_text.text = f"Health: {int(player.health)}"
    gun.update()

app.run()