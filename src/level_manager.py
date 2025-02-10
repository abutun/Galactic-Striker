import json
import os
import pygame
from enemy.grunt_enemy import GruntEnemy
from enemy.swarmer_enemy import SwarmerEnemy
from enemy.boss_enemy import BossEnemy


def load_level_json(level_number):
    filename = os.path.join("assets", "levels", f"{level_number:02d}.json")
    with open(filename, "r") as f:
        return json.load(f)


class LevelManager:
    def __init__(self, level_number, enemy_group, all_sprites, enemy_bullets):
        self.level_number = level_number
        self.level_data = load_level_json(level_number)
        self.start_time = pygame.time.get_ticks()
        self.enemy_group = enemy_group
        self.all_sprites = all_sprites
        self.enemy_bullets = enemy_bullets
        self.scheduled_spawns = []
        self.prepare_spawns()

    def prepare_spawns(self):
        if "individual_enemies" in self.level_data:
            for enemy in self.level_data["individual_enemies"]:
                spawn_time = enemy.get("spawn_time", 0)
                enemy_type = enemy.get("type", "grunt")
                x = enemy.get("x", 0)
                y = enemy.get("y", 0)

                def spawn_func(e_type=enemy_type, ex=x, ey=y):
                    if e_type == "grunt":
                        new_enemy = GruntEnemy(ex, ey, self.enemy_bullets)
                    elif e_type == "swarmer":
                        new_enemy = SwarmerEnemy(ex, ey, self.enemy_bullets)
                    elif e_type == "boss":
                        new_enemy = BossEnemy(ex, ey, self.enemy_bullets)
                    else:
                        new_enemy = GruntEnemy(ex, ey, self.enemy_bullets)
                    self.enemy_group.add(new_enemy)
                    self.all_sprites.add(new_enemy)

                self.scheduled_spawns.append({"spawn_time": spawn_time, "spawn_function": spawn_func, "spawned": False})
        if "enemy_groups" in self.level_data:
            for group in self.level_data["enemy_groups"]:
                group_spawn_time = group.get("spawn_time", 0)
                path = group.get("path", [])
                for enemy in group.get("enemies", []):
                    spawn_delay = enemy.get("spawn_delay", 0)
                    enemy_type = enemy.get("type", "grunt")
                    offset = enemy.get("offset", [0, 0])
                    spawn_time = group_spawn_time + spawn_delay

                    def spawn_func(e_type=enemy_type, off=offset):
                        if path:
                            base_x, base_y = path[0]
                        else:
                            base_x, base_y = (0, 0)
                        ex = base_x + off[0]
                        ey = base_y + off[1]
                        if e_type == "grunt":
                            new_enemy = GruntEnemy(ex, ey, self.enemy_bullets)
                        elif e_type == "swarmer":
                            new_enemy = SwarmerEnemy(ex, ey, self.enemy_bullets)
                        elif e_type == "boss":
                            new_enemy = BossEnemy(ex, ey, self.enemy_bullets)
                        else:
                            new_enemy = GruntEnemy(ex, ey, self.enemy_bullets)
                        self.enemy_group.add(new_enemy)
                        self.all_sprites.add(new_enemy)

                    self.scheduled_spawns.append(
                        {"spawn_time": spawn_time, "spawn_function": spawn_func, "spawned": False})

    def update(self):
        current_time = pygame.time.get_ticks() - self.start_time
        for event in self.scheduled_spawns:
            if not event["spawned"] and current_time >= event["spawn_time"]:
                event["spawn_function"]()
                event["spawned"] = True

    def is_level_complete(self):
        return all(e["spawned"] for e in self.scheduled_spawns) and len(self.enemy_group) == 0

    def load_next_level(self, next_level_number):
        self.level_number = next_level_number
        self.level_data = load_level_json(next_level_number)
        self.start_time = pygame.time.get_ticks()
        self.scheduled_spawns = []
        self.prepare_spawns()
