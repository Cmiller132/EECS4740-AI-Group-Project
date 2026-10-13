extends Node


var BALL: RigidBody2D
var NET: StaticBody2D
var GROUND: StaticBody2D

var net_x: float
var bound_l: float
var bound_r: float


func _ready() -> void:
	BALL = get_tree().get_nodes_in_group("ball")[0]
	NET = get_tree().get_nodes_in_group("net")[0]
	GROUND = get_tree().get_nodes_in_group("ground")[0]

	BALL.body_entered.connect(_on_ball_body_entered)

	get_tree().root.ready.connect(_on_tree_ready)


func _on_tree_ready() -> void:
	net_x = NET.position.x
	var bound_offset: float = GROUND.get_bound_offset_x()
	bound_l = GROUND.position.x - bound_offset
	bound_r = GROUND.position.x + bound_offset

	get_tree().root.get_child(0).add_child(DebugLines.new())


func get_ball_position() -> Vector2:
	return BALL.position


func get_side_of_net(obj: Node2D) -> int:
	if obj.position.x < NET.position.x:
		return SIDE_LEFT
	else:
		return SIDE_RIGHT


func get_ball_side() -> int:
	return get_side_of_net(BALL)


func generate_max_speed() -> float:
	return randf_range(200.0, 300.0)


func _on_ball_body_entered(body: Node) -> void:
	pass
