extends StaticBody2D


func get_bound_offset_x() -> float:
	var col = $CollisionShape2D as CollisionShape2D
	assert(col != null)
	var shape = col.shape as RectangleShape2D
	assert(shape != null)
	return shape.size.x*scale.x*col.scale.x/2
