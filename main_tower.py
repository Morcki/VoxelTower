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
cplane = vec3(0.168, 0.836, 0.898); cwall = vec3(.973, .992, .773); clight = vec3(.925, .852, .01)
inner_size = 10; outter_size = 14; guard_size = 12
first_level_height = 12; others_level_height = 8; guard_height = 3

@ti.func
def mix_color(color1, color2, a):
    return color1 * (1.0 - a) + color2 * a
@ti.func
def draw_tower_level_light(h, wall_h, size, color):
    s1 = size * 1.5; s2 = size * 0.5
    for i in ti.static(range(4)):
        scene.set_voxel(vec3(direct[i, 0] * s1 + offset[i, 0], h + wall_h, direct[i, 1] * s2 + offset[i, 1]), 2, color)
        scene.set_voxel(vec3(direct[i, 0] * s2 + offset[i, 2], h + wall_h, direct[i, 1] * s1 + offset[i, 3]), 2, color)
@ti.func
def draw_tower_top_square(h, half_size, color, mat = 1):
    for i, j in ti.ndrange(half_size * 2, half_size * 2):
        scene.set_voxel(vec3(-half_size + i, h, -half_size + j), mat, color)
@ti.func
def draw_tower_level_plane(h, size, color, mat = 1):
    full_ = size * 3; half_ = full_ * 0.5; cmp_ = size * 2;
    for i, j in ti.ndrange(full_, full_):
        if (((i + j < full_ - cmp_ - 1) or (i + j > full_ + cmp_ - 1)) or (i - j < -cmp_) or (i - j > cmp_)): continue
        scene.set_voxel(vec3(-half_ + i, h    , -half_ + j), mat, color)
        scene.set_voxel(vec3(-half_ + i, h + 1, -half_ + j), mat, color)
@ti.func
def draw_tower_level_window(h, size, window_size):
    s1 = size * 1.5; s2 = size * 0.5; hf0 = s2 - 1; hf1 = s2; 
    h = h + (size - window_size) * 0.5
    for i, j in ti.ndrange(window_size, window_size * 0.5):
        for k in ti.static(range(4)):
            scene.set_voxel(vec3(direct[k,0] * (s1 - hf0 + j), h + i, direct[k,1] * (s2 + hf0 - j)), 0, cwall)
            scene.set_voxel(vec3(direct[k,0] * (s1 - hf1 - j), h + i, direct[k,1] * (s2 + hf1 + j)), 0, cwall)
@ti.func
def draw_tower_level_door(h, size, door_w, door_h):
    s1 = size * 1.5; s2 = size * 0.5; idx = (size - door_w) * 0.5; s_arr = [s2, s1, -s2, -s1, s2]
    for i, j in ti.ndrange(door_w, door_h + 1):
        if ((i == 0 or i == door_w - 1) and j == door_h): continue
        for k in ti.static(range(4)):
            scene.set_voxel(vec3(s_arr[k] + coeff[k,0]*(i + idx), h + 1 + j, 
                                 s_arr[k + 1] + coeff[k,1]*(i + idx)), 0, cwall)
@ti.func
def draw_tower_level_wall(h, wall_h, size, color, mat = 1):
    bOdd = size % 2; size = size - bOdd; s1 = size * 1.5; s2 = size * 0.5; s_arr = [s2, s1, -s2, -s1, s2]
    for i, j in ti.ndrange(size + 1, wall_h):
        for k in ti.static(range(4)):
            scene.set_voxel(vec3(s_arr[k] + coeff[k,0] * i + bOdd * oddadd[k,0], h + 1 + j, 
                                 s_arr[k + 1] + coeff[k,1] * i + bOdd * oddadd[k,1]), mat, color)
            scene.set_voxel(vec3(s_arr[k] + coeff[k,2] * i + bOdd * oddadd[k,2], h + 1 + j, 
                                 s_arr[k + 1] + coeff[k,3] * i + bOdd * oddadd[k,3]), mat, color)
@ti.func
def draw_tower_top(h, size):
    for i in range(size * 0.5 - 1):
        inner_size = size - 4 if i == 0 else size - i * 2 - 2
        draw_tower_level_plane(h + i * 2, size - i * 2, mix_color(cplane, cwall, (i * 2 + 1) / size), 1)
        draw_tower_level_plane(h + i * 2, inner_size, cplane, 0)
    for i in range(3):
        draw_tower_level_plane(h + size - 3 + i, 2, cwall, 1)
        draw_tower_top_square(h  + size - 3 + i, 2, cwall, 0)
        draw_tower_top_square(h  + size + i    , 2, cwall, 1)
        draw_tower_top_square(h  + size + i + 3, 1, cwall, 1)
    draw_tower_top_square(h + size, 1, clight, 2)
@ti.kernel
def draw_tower():
    draw_tower_level_plane(floor_height, outter_size, vec3(0.489, 0.479, 0.449))
    draw_tower_level_wall(floor_height + 1, first_level_height, inner_size, cwall)
    draw_tower_level_light(floor_height + 1, first_level_height, inner_size, clight)
    draw_tower_level_door(floor_height + 1, inner_size, 6, 7)
    for ilevel in range(1, 7):
        height = floor_height + 2 + first_level_height + (ilevel - 1) * (others_level_height + 2)
        draw_tower_level_plane(height, outter_size, cplane)
        draw_tower_level_plane(height, inner_size - 2, cwall, 0)
        draw_tower_level_wall(height + 1, others_level_height, inner_size, cwall)
        draw_tower_level_wall(height + 1, guard_height, inner_size + 2, mix_color(cplane, cwall, 0.85))
        draw_tower_level_wall(height + 1, guard_height, inner_size - 2, mix_color(cplane, cwall, 0.35))
        draw_tower_level_wall( height + 1, guard_height - 1, guard_size + 1, mix_color(cplane, cwall, 0.2))
        draw_tower_level_window(height + 1, inner_size, 2)
        draw_tower_level_door(height + 1, inner_size, 4, 5)
        draw_tower_level_light(height + 1, others_level_height, inner_size, clight)
    draw_tower_top(floor_height + 2 + first_level_height + 6 * (others_level_height + 2), outter_size)
draw_tower()
scene.finish()