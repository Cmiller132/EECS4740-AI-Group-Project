class_name ImageExporter
extends Node


var dataset_path: String = "user://dataset/"
var image_subpath: String = dataset_path + "images/"
var label_subpath: String = dataset_path + "labels/"

var next_id: int = 0


func _ready() -> void:
	for path in [image_subpath, label_subpath]:
		DirAccess.make_dir_recursive_absolute(path)


## generate image and label of current view
func render_data() -> void:
	while FileAccess.file_exists(_generate_image_filename()):
		next_id += 1

	var capture = get_viewport().get_texture().get_image()
	var capture_filepath = _generate_image_filename()

	capture.save_png(capture_filepath)

	var label_file: FileAccess = FileAccess.open(_generate_label_filename(), FileAccess.WRITE)
	label_file.store_string(_generate_label_data())


func _generate_label_data() -> String:
	var ball_pos: Vector2 = GameData.get_ball_position()
	var bb: Rect2 = GameData.BALL.get_bounding_box()
	var data: Dictionary = {
		"frame_id": next_id,
		"ball_center_x": ball_pos.x,
		"ball_center_y": ball_pos.y,
		"ball_bounding_box_x": bb.position.x,
		"ball_bounding_box_y": bb.position.y,
		"ball_bounding_box_width": bb.size.x,
		"ball_bounding_box_height": bb.size.y,
		"ball_visibility": GameData.is_ball_on_screen(),
		"simulation_scenario_id": -1,
	}

	return JSON.stringify(data)


func _generate_image_filename() -> String:
	return image_subpath + str(next_id) + ".png"


func _generate_label_filename() -> String:
	return label_subpath + str(next_id) + ".txt"
