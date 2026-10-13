class_name DebugLines
extends Node2D


func _draw() -> void:
	_draw_vert_line(GameData.net_x, Color.GOLD)
	_draw_vert_line(GameData.bound_l, Color.GREEN)
	_draw_vert_line(GameData.bound_r, Color.GREEN)


func _draw_vert_line(pos_x: float, color: Color) -> void:
	var bottom_y = get_viewport().get_visible_rect().size.y

	draw_line(
		Vector2(pos_x, 0),
		Vector2(pos_x, bottom_y),
		color)
