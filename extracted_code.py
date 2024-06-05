
from manim import *

# Configure the output directory and file names
config.media_dir = "./custom_media"
config.video_dir = "./custom_media/videos"
config.images_dir = "./custom_media/images"
config.tex_dir = "./custom_media/Tex"
config.frame_rate = 30
config.pixel_height = 1080
config.pixel_width = 1920
config.save_last_frame = False

from manim import *

class AckermannSteering(Scene):
    def construct(self):
        # Introduction
        title = Text("Ackermann Steering Geometry", font_size=48).to_edge(UP)
        self.play(Write(title))

        # Vehicle and Steering Angles
        car_body = Rectangle(width=4, height=2).shift(DOWN)
        rear_wheels = VGroup(Dot(car_body.get_bottom() + LEFT*1.5), Dot(car_body.get_bottom() + RIGHT*1.5))
        front_wheels = VGroup(Dot(car_body.get_top() + LEFT*1.5), Dot(car_body.get_top() + RIGHT*1.5))

        self.play(Create(car_body), Create(rear_wheels), Create(front_wheels))
        self.play(front_wheels[0].animate.shift(LEFT*0.5 + UP*0.5), front_wheels[1].animate.shift(RIGHT*0.5 + UP*0.5))

        # Circles representing turning paths
        inner_circle = Circle(radius=2).move_to(front_wheels[0].get_center())
        outer_circle = Circle(radius=3).move_to(front_wheels[1].get_center())
        self.play(Create(inner_circle), Create(outer_circle))

        # Vehicle following the paths
        path = ArcBetweenPoints(start=inner_circle.point_from_proportion(0), end=outer_circle.point_from_proportion(0.25), angle=PI/6)
        self.play(MoveAlongPath(car_body, path))

        # Mathematical Representation
        formula_1 = MathTex(r"\tan(\theta_{\text{inner}}) = \frac{L}{R + \frac{d}{2}}").next_to(title, DOWN)
        formula_2 = MathTex(r"\tan(\theta_{\text{outer}}) = \frac{L}{R - \frac{d}{2}}").next_to(formula_1, DOWN)
        self.play(Write(formula_1), Write(formula_2))

        # Labels for variables
        l_label = MathTex("L").next_to(car_body, LEFT)
        r_label = MathTex("R").next_to(inner_circle, LEFT)
        d_label = MathTex("d").next_to(front_wheels[0], UP)
        self.play(Write(l_label), Write(r_label), Write(d_label))

        # Cleanup
        self.play(FadeOut(inner_circle), FadeOut(outer_circle), FadeOut(l_label), FadeOut(r_label), FadeOut(d_label))

        # Conclusion
        conclusion = Text("Ensures wheels follow concentric circles, minimizing tire slip.", font_size=24).next_to(formula_2, DOWN)
        self.play(Write(conclusion))
if __name__ == "__main__":
    scene = AckermannSteering()
    scene.render()
