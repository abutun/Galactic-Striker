import os
import json
import pygame
from enemy.alien import NonBossAlien, BossAlien


def load_level_json(level_number):
    filename = os.path.join("assets", "levels", f"{level_number:03d}.json")
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
        if self.level_data.get("level_type", "normal") == "boss":
            boss_data = self.level_data.get("boss", {})
            spawn_time = boss_data.get("spawn_time", 0)
            boss_type = boss_data.get("boss_type", self.level_number // 25)
            x = boss_data.get("x", 400)
            y = boss_data.get("y", -150)

            def spawn_func():
                new_enemy = BossAlien(x, y, self.enemy_bullets, boss_type=boss_type)
                self.enemy_group.add(new_enemy)
                self.all_sprites.add(new_enemy)

            self.scheduled_spawns.append({"spawn_time": spawn_time, "spawn_function": spawn_func, "spawned": False})
        else:
            if "individual_enemies" in self.level_data:
                for enemy in self.level_data["individual_enemies"]:
                    spawn_time = enemy.get("spawn_time", 0)
                    enemy_category = enemy.get("enemy_category", "small")
                    enemy_type = enemy.get("enemy_type", 1)
                    subtype = enemy.get("subtype", 1)
                    x = enemy.get("x", 0)
                    y = enemy.get("y", 0)
                    movement_pattern = enemy.get("movement_pattern", "direct")

                    def spawn_func(e_cat=enemy_category, e_type=enemy_type, sub=subtype, ex=x, ey=y,
                                   move=movement_pattern):
                        new_enemy = NonBossAlien(ex, ey, self.enemy_bullets,
                                                 enemy_category=e_cat,
                                                 enemy_type=e_type,
                                                 subtype=sub)
                        new_enemy.movement_pattern = move
                        self.enemy_group.add(new_enemy)
                        self.all_sprites.add(new_enemy)

                    self.scheduled_spawns.append({
                        "spawn_time": spawn_time,
                        "spawn_function": spawn_func,
                        "spawned": False
                    })
            if "enemy_groups" in self.level_data:
                for group in self.level_data["enemy_groups"]:
                    group_spawn_time = group.get("spawn_time", 0)
                    path = group.get("path", [])
                    screen = pygame.display.get_surface()
                    if screen:
                        sw, sh = screen.get_size()
                        abs_path = [[pt[0] * sw, pt[1] * sh] for pt in path]
                    else:
                        abs_path = path
                    group_movement_pattern = group.get("group_movement_pattern", "direct")
                    for enemy in group.get("enemies", []):
                        spawn_delay = enemy.get("spawn_delay", 0)
                        enemy_category = enemy.get("enemy_category", "small")
                        enemy_type = enemy.get("enemy_type", 1)
                        subtype = enemy.get("subtype", 1)
                        offset = enemy.get("offset", [0, 0])
                        spawn_time = group_spawn_time + spawn_delay

                        def spawn_func(e_cat=enemy_category, e_type=enemy_type, sub=subtype, off=offset,
                                       move=group_movement_pattern):
                            if abs_path:
                                base_x, base_y = abs_path[0]
                            else:
                                base_x, base_y = (0, 0)
                            ex = base_x + off[0]
                            ey = base_y + off[1]
                            new_enemy = NonBossAlien(ex, ey, self.enemy_bullets,
                                                     enemy_category=e_cat,
                                                     enemy_type=e_type,
                                                     subtype=sub)
                            new_enemy.movement_pattern = move
                            self.enemy_group.add(new_enemy)
                            self.all_sprites.add(new_enemy)

                        self.scheduled_spawns.append({
                            "spawn_time": spawn_time,
                            "spawn_function": spawn_func,
                            "spawned": False
                        })

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
