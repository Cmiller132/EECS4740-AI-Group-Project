extends RigidBody2D


@onready var col: CollisionShape2D = $CollisionShape2D
@onready var shape: CircleShape2D = col.shape


func get_bounding_box_coords() -> Vector2:
	return position - get_bounding_box_dimensions()/2


func get_bounding_box_dimensions() -> Vector2:
	return Vector2(
		scale.x*col.scale.x*shape.radius,
		scale.y*col.scale.y*shape.radius)
