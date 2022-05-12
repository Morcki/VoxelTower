from scene import Scene; import taichi as ti; from taichi.math import vec3
floor_height = -64
scene = Scene(voxel_edges = 0, exposure = 1.2)
scene.set_floor(-1, (1.0, 1.0, 1.0))
scene.set_background_color((0.5, 0.5, 0.4))
scene.set_directional_light((1, 1, 1), 0.2, (1.0, 0.8, 0.6))

direct = ti.Matrix([[ 1,  1], [ 1, -1], [-1, -1], [-1,  1]])
offset = ti.Matrix([[-1, 0, 0, -1], [-1, 0,  0,  1], [1, 0,  0, 1], [1, 0, 0, -1]])
coeff  = ti.Matrix([[-1, 0, 1, -1], [ 0, 1, -1, -1], [1, 0, -1, 1], [0, -1, 1, 1]])
oddadd = ti.Matrix([[ 0, 1, 0,  1], [ 1, 0,  0, -1], [0,-1,  0,-1], [-1, 0, 0, 1]])
cplane = vec3(0.168, 0.836, 0.898); cwall = vec3(.973, .992, .773); 
clight = vec3(.925, .852, .01); cnoise = vec3(0.05, 0.02, 0.02)
inner_size = 10; outter_size = 14; guard_size = 12
first_level_height = 12; others_level_height = 8; guard_height = 3

@ti.func
def mix_color(color1, color2, a):
    return color1 * (1.0 - a) + color2 * a
@ti.func
def draw_tower_level_light(height, wall_height, size, color):
    start1 = size * 1.5; start2 = size * 0.5
    for i in ti.static(range(4)):
        scene.set_voxel(vec3(direct[i, 0] * start1 + offset[i, 0], height + wall_height, direct[i, 1] * start2 + offset[i, 1]), 2, color)
        scene.set_voxel(vec3(direct[i, 0] * start2 + offset[i, 2], height + wall_height, direct[i, 1] * start1 + offset[i, 3]), 2, color)
@ti.func
def draw_tower_top_square(height, half_size, color, color_noise, mat_type = 1):
    for i, j in ti.ndrange(half_size * 2, half_size * 2):
        scene.set_voxel(vec3(-half_size + i, height, -half_size + j), mat_type, color + color_noise * ti.random())
@ti.func
def draw_tower_level_plane(height, size, color, color_noise, mat_type = 1):
    full_ = size * 3; half_ = full_ * 0.5; cmp_ = size * 2;
    for i, j in ti.ndrange(full_, full_):
        if (((i + j < full_ - cmp_ - 1) or (i + j > full_ + cmp_ - 1)) or (i - j < -cmp_) or (i - j > cmp_)): continue
        scene.set_voxel(vec3(-half_ + i, height    , -half_ + j), mat_type, color + color_noise * ti.random())
        scene.set_voxel(vec3(-half_ + i, height + 1, -half_ + j), mat_type, color + color_noise * ti.random())
@ti.func
def draw_tower_level_window(height, size, window_size):
    start1 = size * 1.5; start2 = size * 0.5; half0 = start2 - 1; half1 = start2; h = height + (size - window_size) * 0.5
    for i, j in ti.ndrange(window_size, window_size * 0.5):
        for k in ti.static(range(4)):
            scene.set_voxel(vec3(direct[k, 0] * (start1 - half0 + j), h + i, direct[k, 1] * (start2 + half0 - j)), 0, vec3(0.0, 0.0, 0.0))
            scene.set_voxel(vec3(direct[k, 0] * (start1 - half1 - j), h + i, direct[k, 1] * (start2 + half1 + j)), 0, vec3(0.0, 0.0, 0.0))
@ti.func
def draw_tower_level_door(height, size, door_width, door_height):
    start1 = size * 1.5; start2 = size * 0.5; index = (size - door_width) * 0.5; start_arr = [start2, start1, -start2, -start1, start2]
    for i, j in ti.ndrange(door_width, door_height + 1):
        if ((i == 0 or i == door_width - 1) and j == door_height): continue
        for k in ti.static(range(4)):
            scene.set_voxel(vec3(start_arr[k] + coeff[k, 0] * (i + index), height + 1 + j, start_arr[k + 1] + coeff[k, 1] * (i + index)), 0, vec3(0.0, 0.0, 0.0))
@ti.func
def draw_tower_level_wall(height, wall_height, evensize, color, color_noise, mat_type = 1):
    is_odd_size = evensize % 2; size = evensize - is_odd_size; start1 = size * 1.5; start2 = size * 0.5; start_arr = [start2, start1, -start2, -start1, start2]
    for i, j in ti.ndrange(size + 1, wall_height):
        for k in ti.static(range(4)):
            scene.set_voxel(vec3(start_arr[k] + coeff[k, 0] * i + is_odd_size * oddadd[k, 0], height + 1 + j, start_arr[k + 1] + coeff[k, 1] * i + is_odd_size * oddadd[k, 1]), mat_type, color + color_noise * ti.random())
            scene.set_voxel(vec3(start_arr[k] + coeff[k, 2] * i + is_odd_size * oddadd[k, 2], height + 1 + j, start_arr[k + 1] + coeff[k, 3] * i + is_odd_size * oddadd[k, 3]), mat_type, color + color_noise * ti.random())
@ti.func
def draw_tower_top(height, size):
    for i in range(size * 0.5 - 1):
        inner_size = size - 4 if i == 0 else size - i * 2 - 2
        draw_tower_level_plane(height + i * 2, size - i * 2, mix_color(cplane, cwall, (i * 2 + 1) / size), cnoise, 1)
        draw_tower_level_plane(height + i * 2, inner_size, cplane, cnoise, 0)
    for i in range(3):
        draw_tower_level_plane(height + size - 3 + i, 2, cwall, cnoise, 1)
        draw_tower_top_square(height  + size - 3 + i, 2, cwall, cnoise, 0)
        draw_tower_top_square(height  + size + i    , 2, cwall, cnoise, 1)
        draw_tower_top_square(height  + size + i + 3, 1, cwall, cnoise, 1)
    draw_tower_top_square(height + size, 1, clight, cnoise, 2)
@ti.kernel
def draw_tower():
    draw_tower_level_plane(floor_height, outter_size, vec3(0.489, 0.479, 0.449), cnoise)
    draw_tower_level_wall(floor_height + 1, first_level_height, inner_size, cwall, cnoise)
    draw_tower_level_light(floor_height + 1, first_level_height, inner_size, clight)
    draw_tower_level_door(floor_height + 1, inner_size, 6, 7)
    for ilevel in range(1, 7):
        height = floor_height + 2 + first_level_height + (ilevel - 1) * (others_level_height + 2)
        draw_tower_level_plane(height, outter_size, cplane, cnoise)
        draw_tower_level_plane(height, inner_size - 2, cwall, cnoise, 0)
        draw_tower_level_wall(height + 1, others_level_height, inner_size, cwall, cnoise)
        draw_tower_level_wall(height + 1, guard_height, inner_size + 2, mix_color(cplane, cwall, 0.85), cnoise)
        draw_tower_level_wall(height + 1, guard_height, inner_size - 2, mix_color(cplane, cwall, 0.35), cnoise)
        draw_tower_level_wall( height + 1, guard_height - 1, guard_size + 1, mix_color(cplane, cwall, 0.2), cnoise)
        draw_tower_level_window(height + 1, inner_size, 2)
        draw_tower_level_door(height + 1, inner_size, 4, 5)
        draw_tower_level_light(height + 1, others_level_height, inner_size, clight)
    draw_tower_top(floor_height + 2 + first_level_height + 6 * (others_level_height + 2), outter_size)
draw_tower()
scene.finish()