class_name DebugLines
extends Node2D


var paddles: Array[Node] = []


func _ready() -> void:
	paddles = get_tree().get_nodes_in_group("paddle")


func _draw() -> void:
	_draw_vert_line(GameData.net_x, Color.GOLD)
	_draw_vert_line(GameData.bound_l, Color.GREEN)
	_draw_vert_line(GameData.bound_r, Color.GREEN)
	_draw_hori_line(GameData.ground_level, Color.GREEN)

	for paddle in paddles:
		var pos: Vector2 = paddle.ai.find_movement_data(paddle.position).target_pos
		draw_circle(pos, 20, Color.RED)


func _process(delta: float) -> void:
	queue_redraw()


func _draw_vert_line(pos_x: float, color: Color) -> void:
	var bottom_y = get_viewport().get_visible_rect().size.y

	draw_line(
		Vector2(pos_x, 0),
		Vector2(pos_x, bottom_y),
		color)


func _draw_hori_line(pos_y: float, color: Color) -> void:
	var right_x = get_viewport().get_visible_rect().size.x

	draw_line(
		Vector2(0, pos_y),
		Vector2(right_x, pos_y),
		color)
