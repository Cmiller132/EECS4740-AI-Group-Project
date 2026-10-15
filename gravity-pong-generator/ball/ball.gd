extends RigidBody2D


@onready var col: CollisionShape2D = $CollisionShape2D
@onready var shape: CircleShape2D = col.shape


func get_bounding_box() -> Rect2:
	var ret: Rect2
	ret.size = Vector2(
		scale.x*col.scale.x*shape.radius*2,
		scale.y*col.scale.y*shape.radius*2)
	ret.position = position - ret.size/2
	return ret
