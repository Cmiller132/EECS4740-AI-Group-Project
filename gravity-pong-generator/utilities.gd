@abstract
class_name Utilities
extends Object


static func is_ball_hit(collision: KinematicCollision2D) -> bool:
	return collision != null \
		&& (collision.get_collider() as RigidBody2D) != null \
		&& collision.get_collider().name == "Ball"
