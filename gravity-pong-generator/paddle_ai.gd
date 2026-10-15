class_name PaddleAi
extends RefCounted


enum State {
	CHASE,
	RETREAT,
	STRIKE
}


class MovementData:
	var speed: float
	var target_pos: Vector2
	

	static func default() -> MovementData:
		return MovementData.new(0, Vector2.ZERO)


	func _init(spd: float = 0, trgt: Vector2 = Vector2.ZERO) -> void:
		speed = spd
		target_pos = trgt


const TARGET_OFFSET: Vector2 = Vector2(-30, 50)
const STRIKE_RANGE: float = 100
const STRIKE_MOD: float = 2

const TOP_THETA: float = PI
const BOTTOM_THETA: float = -2*PI/3

var BASE_POS: Vector2
var MAX_SPEED: float
var SIDE: int

var state: State = State.CHASE: set = _enter_state


## initializer
func _init(base_pos: Vector2, max_speed: float, side: int) -> void:
	BASE_POS = base_pos
	MAX_SPEED = max_speed
	SIDE = side


## tell an object where to move and how fast to move there
func find_movement_data(position: Vector2) -> MovementData:
	match state:
		State.CHASE:
			return MovementData.new(
				MAX_SPEED,
				_find_chase_position())
		State.RETREAT:
			return MovementData.new(
				MAX_SPEED,
				BASE_POS)
		State.STRIKE:
			return MovementData.new(
				MAX_SPEED*STRIKE_MOD,
				_find_strike_position())
		_:
			return MovementData.default()


## called by paddle to allow state changes where necessary
func update_state(position: Vector2, collision: KinematicCollision2D) -> void:
	if position.distance_to(GameData.get_ball_position()) < STRIKE_RANGE \
			&& _is_angle_acceptable(position) \
			&& state == State.CHASE:
		_enter_state(State.STRIKE)

	if Utilities.is_ball_hit(collision):
		_enter_state(State.RETREAT)
	elif state == State.RETREAT && _is_ball_coming():
		_enter_state(State.CHASE)
	

func _enter_state(new_state: State) -> void:
	state = new_state


func _is_ball_coming() -> bool:
	return sign(_sidify_f(GameData.BALL.linear_velocity.x)) == -1


func _is_angle_acceptable(position: Vector2) -> bool:
	var offset: Vector2 = _find_ball_offset(position)*-1
	var o_norm = offset.normalized()
	o_norm.y *= -1
	return o_norm.y <= sin(TOP_THETA) \
			&& o_norm.y >= sin(BOTTOM_THETA) \
			&& sign(offset.x) == -1


func _find_chase_position() -> Vector2:
	return GameData.get_ball_position() + _sidify_vec(TARGET_OFFSET)


func _find_strike_position() -> Vector2:
	return GameData.get_ball_position()


## returns the offset of a ball from a certain position, adjusted for side
## positive x is towards the goal, and negative x is towards the out zone
func _find_ball_offset(position) -> Vector2:
	var ret: Vector2 = GameData.get_ball_position() - position
	_sidify_vec(ret)
	return ret
	

func _sidify_vec(vec: Vector2) -> Vector2:
	var ret = vec
	ret.x = _sidify_f(vec.x)
	return ret


func _sidify_f(f: float) -> float:
	var ret = f
	if SIDE == SIDE_RIGHT:
		ret *= -1
	return ret
