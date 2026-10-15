extends StaticBody2D


var col: CollisionShape2D
var shape: RectangleShape2D


func _ready() -> void:
	col = $CollisionShape2D
	assert(col != null)
	shape = col.shape 
	assert(shape != null)


func get_bound_offset_x() -> float:
	return shape.size.x*scale.x*col.scale.x/2


func get_ground_level() -> float:
	return position.y - \
			shape.size.y*scale.y*col.scale.y/2
