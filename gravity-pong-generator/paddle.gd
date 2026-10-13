extends AnimatableBody2D


var ai: PaddleAi


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	ai = PaddleAi.new(
		position,                        # base_pos
		GameData.generate_max_speed(),   # max_speed
		GameData.get_side_of_net(self))  # side as SIDE_LEFT or SIDE_RIGHT


func _physics_process(delta: float) -> void:
	look_at(GameData.get_ball_position())

	var md: PaddleAi.MovementData = ai.find_movement_data()

	var collision: KinematicCollision2D = _move_towards(
		md.target_pos,
		md.speed*delta)

	if Utilities.is_ball_hit(collision):
		_make_bounce(collision, collision.get_collider(), md.speed)
	
	ai.update_state(position, collision)



func _make_bounce(collision: KinematicCollision2D, body: RigidBody2D, speed: float) -> void:
	var impulse = collision.get_normal().rotated(PI)*speed
	body.apply_impulse(impulse)


func _move_towards(goal: Vector2, speed: float) -> KinematicCollision2D:
	return move_and_collide(position.direction_to(goal)*min(speed, position.distance_to(goal)))
