from manimlib import *
from collections import namedtuple

class Coordinate(namedtuple('Coordinate', ('x', 'y', 'z'))):
	__slots__ = ()  # no idea what this does

class UnitTrianglePoints(namedtuple('UnitTrianglePoints', ('bl', 'br', 'tr'))):
	__slots__ = ()  # no idea what this does

class UnitTriangleEdges(namedtuple('UnitTriangleEdges', ('b', 'r', 'tl'))):
	__slots__ = ()  # no idea what this does

class TrigTriangle(Scene):
	def construct(self):
		# triangle value trackers
		angle = ValueTracker(PI/6)
		hypotenuse = ValueTracker(3.7)
		x = ValueTracker(0)
		y = ValueTracker(0)

		def normalize_angle(angle: float):
			return (angle + TAU * math.ceil(angle / TAU)) % TAU

		# returns normalize angle value tracker
		def get_normalized_angle():
			return normalize_angle(angle.get_value())
		

		def get_points():
			bl = x.get_value(), y.get_value(), 0
			br = x.get_value() + math.cos(angle.get_value()) * hypotenuse.get_value(), y.get_value(), 0
			tr = (
				x.get_value() + math.cos(angle.get_value()) * hypotenuse.get_value(),
				y.get_value() + math.sin(angle.get_value()) * hypotenuse.get_value(),
				0,
			)
			return UnitTrianglePoints(Coordinate(*bl), Coordinate(*br), Coordinate(*tr))
		
		def get_dots():
			return UnitTrianglePoints(*(Dot(i) for i in get_points()))
		
		def get_lines():
			points = get_points()
			b = Line(points[0], points[1])
			r = Line(points[1], points[2])
			tl = Line(points[0], points[2])
			return UnitTriangleEdges(b, r, tl)

		always_redraw_lines = [
			always_redraw(lambda: get_lines().b.set_color(BLUE)),
			always_redraw(lambda: get_lines().r.set_color(RED)),
			always_redraw(lambda: get_lines().tl).set_color(GREY),
		]

		def align_mobject_center(mobject: Mobject, point: Iterable[float], rotation: float, normal_angle: float, distance: float):
			pos = (
				point[0] + math.cos(normal_angle) * distance,
				point[1] + math.sin(normal_angle) * distance,
				0,
			)
			return mobject.rotate(rotation).move_to(pos)
		
		def align_mobject_corner(mobject: Mobject, point: Iterable[float], rotation: float, normal_angle: float, distance: float):
			pos = (
				point[0] + math.cos(normal_angle) * distance,
				point[1] + math.sin(normal_angle) * distance,
				0,
			)
			bounding_box_width, bounding_box_height = mobject.get_width(), mobject.get_height()
			normal_angle = normalize_angle(normal_angle)
			if normal_angle < PI/2:
				normal_angle = PI/4
				shift = bounding_box_width / 2, bounding_box_height / 2, 0
			elif normal_angle < PI:
				normal_angle = 3*PI/4
				shift = -bounding_box_width / 2, bounding_box_height / 2, 0
			elif normal_angle < 3*PI/2:
				normal_angle = 5*PI/4
				shift = -bounding_box_width / 2, -bounding_box_height / 2, 0
			else:
				normal_angle = 7*PI/4
				shift = bounding_box_width / 2, -bounding_box_height / 2, 0
			return mobject.rotate(rotation).move_to(pos).shift(shift)
		
		def align_mobject_corner_interpolate(mobject: Mobject, point: Iterable[float], rotation: float, normal_angle: float, distance: float):
			pos = (
				point[0] + math.cos(normal_angle) * distance,
				point[1] + math.sin(normal_angle) * distance,
				0,
			)
			bounding_box_width, bounding_box_height = mobject.get_width(), mobject.get_height()
			normal_angle = normalize_angle(normal_angle)

			def get_shift_val(min_angle: float, max_angle: float, angle: float, max_shift: float):
				return ((angle - min_angle) / (max_angle - min_angle) * 2 - 1) * max_shift

			if normal_angle < PI/4 or normal_angle > 7*PI/4:
				shift = bounding_box_width / 2, get_shift_val(0, PI/2, normalize_angle(normal_angle+PI/4), bounding_box_height / 2), 0
			elif normal_angle < 3*PI/4:
				shift = get_shift_val(PI/4, 3*PI/4, normal_angle, -bounding_box_width / 2), bounding_box_height / 2, 0
			elif normal_angle < 5*PI/4:
				shift = -bounding_box_width / 2, get_shift_val(3*PI/4, 5*PI/4, normal_angle, -bounding_box_height / 2), 0
			else:
				shift = get_shift_val(5*PI/4, 7*PI/4, normal_angle, bounding_box_width / 2), -bounding_box_height / 2, 0
			return mobject.rotate(rotation).move_to(pos).shift(shift)
		
		# edge labels
		edge_label_distance = ValueTracker(0.2)
		edge_label_size = ValueTracker(6)
		always_redraw_labels = [
			always_redraw(lambda: align_mobject_center(Text(f'{round(abs(get_points().br.x - get_points().bl.x) / hypotenuse.get_value(), 2)}', font_size=round(edge_label_size.get_value()*hypotenuse.get_value())), get_lines().b.get_center(), 0, 3*PI/2 if math.sin(angle.get_value()) > 0 else PI/2, edge_label_distance.get_value()).set_color(BLUE)),
			always_redraw(lambda: align_mobject_center(Text(f'{round(abs(get_points().br.y - get_points().tr.y) / hypotenuse.get_value(), 2)}', font_size=round(edge_label_size.get_value()*hypotenuse.get_value())), get_lines().r.get_center(), 3*PI/2 if math.cos(angle.get_value()) > 0 else PI/2, 0 if math.cos(angle.get_value()) > 0 else PI, edge_label_distance.get_value()).set_color(RED)),
			# always_redraw(lambda: redraw_label_function(lambda: f'{round(math.dist(get_points()[0], get_points()[2]) / hypotenuse.get_value(), 2)}', get_lines()[2].get_center(), angle.get_value(), angle.get_value() + PI/2, text_distance)),
		]

		# angle theta
		theta_arc_radius = ValueTracker(0.15)
		theta_label_distance = ValueTracker(0.1)
		theta_label_size = ValueTracker(6)
		theta_arc = always_redraw(lambda: Arc(0, get_normalized_angle(), radius=hypotenuse.get_value() * theta_arc_radius.get_value(), arc_center=get_points()[0]).set_color(GREEN))
		theta_label = always_redraw(lambda: align_mobject_center(Text(f'{round(get_normalized_angle() * 180 / PI)}°', font_size=round(theta_label_size.get_value() * hypotenuse.get_value())), get_points().bl, 0, get_normalized_angle() / 2, (theta_arc_radius.get_value() + theta_label_distance.get_value()) * hypotenuse.get_value()).set_color(GREEN))

		# trying to figure out how bounding boxes work
		# print(tuple(map(tuple, theta_label.get_bounding_box())))
		# # ( left.x, bottom.y, z),
		# # (  top.x,  right.y, z),
		# # (right.x,    top.y, z),
		# # top.x is midpoint between left.x and right.x
		# print('top', theta_label.get_top())
		# print('bottom', theta_label.get_bottom())
		# print('left', theta_label.get_left())
		# print('right', theta_label.get_right())
		# print('width', theta_label.get_width())
		# print('height', theta_label.get_height())

		# unit circle
		circle = always_redraw(lambda: Circle(radius=hypotenuse.get_value(), arc_center=(x.get_value(), y.get_value(), 0)).set_color(GREY))

		# circle point
		circle_point = always_redraw(lambda: get_dots().tr.set_color(PURPLE))
		circle_point_label_distance = ValueTracker(0.04)
		circle_point_label_size = ValueTracker(6)
		circle_point_label = always_redraw(lambda: (x_coord:=str(round(math.cos(angle.get_value()), 2)))and(y_coord:=str(round(math.sin(angle.get_value()), 2)))and align_mobject_corner_interpolate(
			Text(f'({x_coord}, {y_coord})', t2c={y_coord: RED, x_coord+',': BLUE, ',': WHITE}, font_size=round(circle_point_label_size.get_value()*hypotenuse.get_value())),
			get_points().tr,
			0,
			angle.get_value(),
			circle_point_label_distance.get_value() * hypotenuse.get_value()	
		))

		number_plane = always_redraw(lambda: (num_plane:=NumberPlane(
			axis_config={
				'stroke_color': '#AAA',
			},
			background_line_style={
				'stroke_color': '#FFF',
				'stroke_opacity': 0.1,
			},
			faded_line_style={
				'stroke_opacity': 0.1,
				'stroke_width': 0.5,
			},
			faded_line_ratio=9,
		).scale(hypotenuse.get_value()).shift((x.get_value(), y.get_value(), 0))) and num_plane.add_coordinate_labels() and num_plane)
		# explanation for above: .add_coordinate_labels() returns the coordinate labels, but the always_redraw needs the number plane


		self.play(FadeIn(number_plane))
		self.play(ShowCreation(circle))
		self.play(ShowCreation(theta_arc), *(ShowCreation(i) for i in always_redraw_lines), Write(theta_label), ShowCreation(circle_point))
		self.play(*(Write(i) for i in always_redraw_labels), Write(circle_point_label))
		self.play(angle.animate.set_value(PI/3))
		self.play(angle.animate.set_value(13*PI/6), run_time=4)
