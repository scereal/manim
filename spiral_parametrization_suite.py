from manim import *
import numpy as np

config.background_color = "#0f1117"

TITLE_COLOR = "#E6EDF3"
ACCENT = "#58C4DD"
ACCENT2 = "#F4D35E"
ACCENT3 = "#FF7A90"
SOFT = "#9FB3C8"
GRID = "#223042"
SPIRAL = "#7CE38B"
DOTC = "#FFB86B"


def arch_spiral(theta, a=0.35, b=0.16):
    r = a + b * theta
    return np.array([r * np.cos(theta), r * np.sin(theta), 0.0])


def polar_to_cart(theta, r):
    return np.array([r * np.cos(theta), r * np.sin(theta), 0.0])


class SpiralBase(Scene):
    def setup_plane(self):
        plane = NumberPlane(
            x_range=[-5, 5, 1],
            y_range=[-4, 4, 1],
            background_line_style={"stroke_color": GRID, "stroke_opacity": 0.55, "stroke_width": 1},
            axis_config={"color": SOFT, "stroke_width": 2, "include_ticks": False},
        )
        return plane

    def intro_title(self, title, subtitle=None):
        t = Text(title, font_size=40, color=TITLE_COLOR, weight=BOLD).to_edge(UP)
        if subtitle:
            s = Text(subtitle, font_size=22, color=SOFT).next_to(t, DOWN, buff=0.18)
            self.play(FadeIn(t, shift=0.2 * DOWN), FadeIn(s, shift=0.2 * DOWN))
            return VGroup(t, s)
        self.play(FadeIn(t, shift=0.2 * DOWN))
        return VGroup(t)

    def make_spiral(self, tmax=6 * PI, color=SPIRAL, stroke_width=5):
        return ParametricFunction(lambda t: arch_spiral(t), t_range=[0, tmax], color=color, stroke_width=stroke_width)


class SpiralStandard(SpiralBase):
    def construct(self):
        title = self.intro_title(
            "Parametrizing a Spiral",
            "A clean geometric view: angle controls turning, and radius controls outward growth.",
        )
        plane = self.setup_plane()
        self.play(Create(plane), run_time=1.5)

        eq = MathTex(r"r(\theta)=a+b\theta", color=ACCENT).scale(1.0).to_corner(UR).shift(0.2 * LEFT + 0.4 * DOWN)
        eq2 = MathTex(r"x(\theta)=(a+b\theta)\cos\theta", color=TITLE_COLOR).scale(0.82).next_to(eq, DOWN, aligned_edge=RIGHT)
        eq3 = MathTex(r"y(\theta)=(a+b\theta)\sin\theta", color=TITLE_COLOR).scale(0.82).next_to(eq2, DOWN, aligned_edge=RIGHT)
        self.play(Write(eq), Write(eq2), Write(eq3))

        spiral = self.make_spiral()
        tracer = Dot(color=DOTC, radius=0.07)
        radius_line = always_redraw(lambda: Line(ORIGIN, tracer.get_center(), color=ACCENT2, stroke_width=3))
        angle_arc = always_redraw(lambda: Arc(radius=0.75, start_angle=0, angle=np.arctan2(tracer.get_y(), tracer.get_x()), color=ACCENT3, stroke_width=3))

        theta = ValueTracker(0.0)
        tracer.add_updater(lambda m: m.move_to(arch_spiral(theta.get_value())))
        spiral_partial = always_redraw(
            lambda: ParametricFunction(lambda t: arch_spiral(t), t_range=[0, max(0.01, theta.get_value())], color=SPIRAL, stroke_width=5)
        )

        theta_label = always_redraw(lambda: MathTex(r"\theta", color=ACCENT3).scale(0.8).move_to(0.95 * RIGHT + 0.35 * UP))
        r_label = always_redraw(lambda: MathTex(r"r(\theta)", color=ACCENT2).scale(0.8).move_to(radius_line.get_center() + 0.28 * UP))

        self.add(spiral_partial, radius_line, angle_arc, tracer, theta_label, r_label)
        self.play(theta.animate.set_value(6 * PI), run_time=8, rate_func=linear)
        tracer.clear_updaters()

        bullets = VGroup(
            Text("1. \u03b8 tells us how much we have turned.", font_size=24, color=TITLE_COLOR),
            Text("2. r(\u03b8)=a+b\u03b8 tells us how far from the origin we are.", font_size=24, color=TITLE_COLOR),
            Text("3. Converting polar to Cartesian gives x(\u03b8), y(\u03b8).", font_size=24, color=TITLE_COLOR),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).to_corner(DL).shift(0.3 * UP)
        self.play(LaggedStart(*[FadeIn(b, shift=0.2 * RIGHT) for b in bullets], lag_ratio=0.2))
        self.wait(1.5)
        self.play(FadeOut(bullets), FadeOut(title), FadeOut(eq), FadeOut(eq2), FadeOut(eq3), FadeOut(radius_line), FadeOut(angle_arc), FadeOut(theta_label), FadeOut(r_label), FadeOut(tracer), FadeOut(spiral_partial), FadeOut(plane))


class SpiralThreePerspectives(SpiralBase):
    def construct(self):
        title = self.intro_title(
            "One Spiral, Three Ways to Think About It",
            "Geometric, physical, and everyday/hands-on perspectives",
        )

        # Perspective 1: geometric
        plane = self.setup_plane()
        self.play(Create(plane))
        spiral = self.make_spiral(tmax=5 * PI)
        eq = MathTex(r"\theta \mapsto (x(\theta), y(\theta))", color=ACCENT).to_corner(UR)
        subtitle = Text("Perspective 1: The geometry view", font_size=28, color=ACCENT2).to_edge(LEFT).shift(UP * 2.5 + RIGHT * 0.5)
        body = Text("Every moment of parameter \u03b8 picks one point on the curve.", font_size=24, color=TITLE_COLOR).next_to(subtitle, DOWN, aligned_edge=LEFT)
        self.play(Write(subtitle), FadeIn(body), Write(eq), Create(spiral), run_time=2.5)
        dot = Dot(arch_spiral(0), color=DOTC)
        path = TracedPath(dot.get_center, stroke_color=SPIRAL, stroke_width=6)
        self.add(path, dot)
        self.play(MoveAlongPath(dot, spiral), run_time=4, rate_func=linear)
        self.play(FadeOut(VGroup(subtitle, body, eq, dot, path, spiral, plane)))

        # Perspective 2: physical / motion
        title2 = Text("Perspective 2: A turning-and-walking machine", font_size=30, color=ACCENT2).to_edge(UP)
        self.play(FadeIn(title2))
        floor = NumberPlane(
            x_range=[-6, 6, 1], y_range=[-3.5, 3.5, 1],
            background_line_style={"stroke_color": GRID, "stroke_opacity": 0.35, "stroke_width": 1},
            axis_config={"color": SOFT, "include_ticks": False},
        )
        self.play(FadeIn(floor))
        theta = ValueTracker(0.0)
        person = always_redraw(lambda: VGroup(
            Dot(polar_to_cart(theta.get_value(), 0.35 + 0.16 * theta.get_value()), color=DOTC, radius=0.08),
            Arrow(
                polar_to_cart(theta.get_value(), 0.35 + 0.16 * theta.get_value()),
                polar_to_cart(theta.get_value(), 0.35 + 0.16 * theta.get_value()) + 0.5 * np.array([np.cos(theta.get_value()), np.sin(theta.get_value()), 0]),
                buff=0, color=ACCENT3, stroke_width=4, max_tip_length_to_length_ratio=0.25,
            )
        ))
        trace = always_redraw(lambda: ParametricFunction(lambda t: arch_spiral(t), t_range=[0, max(0.01, theta.get_value())], color=SPIRAL, stroke_width=5))
        motion_text = VGroup(
            Text("Imagine this rule:", font_size=25, color=TITLE_COLOR),
            Text("turn a little... then step a little farther out", font_size=25, color=TITLE_COLOR),
            MathTex(r"r = a+b\theta", color=ACCENT),
        ).arrange(DOWN, buff=0.2).to_edge(LEFT).shift(RIGHT * 0.5)
        self.play(FadeIn(motion_text), FadeIn(person), FadeIn(trace))
        self.play(theta.animate.set_value(6 * PI), run_time=6, rate_func=linear)
        self.play(FadeOut(VGroup(title2, floor, motion_text, person, trace)))

        # Perspective 3: tactile / everyday
        title3 = Text("Perspective 3: Like winding tape off a roll", font_size=30, color=ACCENT2).to_edge(UP)
        self.play(FadeIn(title3))
        center = Dot(ORIGIN, color=ACCENT2)
        rings = VGroup(*[Circle(radius=r, color=GRID, stroke_width=2) for r in np.arange(0.5, 3.6, 0.5)])
        self.play(FadeIn(rings), FadeIn(center))
        band = self.make_spiral(tmax=5.5 * PI, color=ACCENT3, stroke_width=8)
        hand = Dot(arch_spiral(0), color=DOTC, radius=0.09)
        band_trace = TracedPath(hand.get_center, stroke_color=ACCENT3, stroke_width=8)
        expl = VGroup(
            Text("As you go around, each lap sits slightly farther out.", font_size=24, color=TITLE_COLOR),
            Text("That steady extra spacing is what b controls.", font_size=24, color=TITLE_COLOR),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).to_edge(DOWN)
        self.play(FadeIn(expl), FadeIn(hand), FadeIn(band_trace))
        self.play(MoveAlongPath(hand, band), run_time=5, rate_func=linear)
        summary = VGroup(
            MathTex(r"\text{turning} \leftrightarrow \theta", color=ACCENT3),
            MathTex(r"\text{distance from center} \leftrightarrow r(\theta)", color=ACCENT2),
            MathTex(r"\text{point in the plane} \leftrightarrow (x(\theta),y(\theta))", color=ACCENT),
        ).arrange(DOWN, buff=0.25).scale(0.9).to_edge(RIGHT).shift(LEFT * 0.4)
        self.play(FadeIn(summary, shift=LEFT))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))


class SpiralWow(SpiralBase):
    def construct(self):
        glow_title = Text("Parametrizing a Spiral", font_size=44, color=TITLE_COLOR, weight=BOLD)
        sub = Text("Three lenses. One idea. A cleaner intuition.", font_size=24, color=SOFT)
        VGroup(glow_title, sub).arrange(DOWN, buff=0.18).move_to(ORIGIN)
        self.play(FadeIn(glow_title, scale=0.92), FadeIn(sub, shift=0.15 * DOWN))
        self.wait(0.5)
        self.play(VGroup(glow_title, sub).animate.scale(0.72).to_edge(UP))

        plane = self.setup_plane()
        self.play(Create(plane), run_time=1.3)

        theta = ValueTracker(0.01)
        spiral = always_redraw(lambda: ParametricFunction(lambda t: arch_spiral(t), t_range=[0, theta.get_value()], color=SPIRAL, stroke_width=6))
        dot = always_redraw(lambda: Dot(arch_spiral(theta.get_value()), color=DOTC, radius=0.08))
        radial = always_redraw(lambda: Line(ORIGIN, arch_spiral(theta.get_value()), color=ACCENT2, stroke_width=4))
        tangent = always_redraw(lambda: Arrow(
            arch_spiral(theta.get_value()),
            arch_spiral(theta.get_value()) + 0.8 * np.array([
                np.cos(theta.get_value()) - (0.35 + 0.16 * theta.get_value()) * np.sin(theta.get_value()),
                np.sin(theta.get_value()) + (0.35 + 0.16 * theta.get_value()) * np.cos(theta.get_value()),
                0,
            ]) / np.linalg.norm(np.array([
                np.cos(theta.get_value()) - (0.35 + 0.16 * theta.get_value()) * np.sin(theta.get_value()),
                np.sin(theta.get_value()) + (0.35 + 0.16 * theta.get_value()) * np.cos(theta.get_value()),
                0,
            ])),
            buff=0, color=ACCENT3, stroke_width=4, max_tip_length_to_length_ratio=0.25,
        ))
        eqs = VGroup(
            MathTex(r"r=a+b\theta", color=ACCENT2),
            MathTex(r"x=r\cos\theta", color=ACCENT),
            MathTex(r"y=r\sin\theta", color=ACCENT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UR)
        tag = Text("Lens 1: geometric map", font_size=26, color=ACCENT3).to_edge(LEFT).shift(UP * 2)
        self.play(FadeIn(eqs), FadeIn(tag), FadeIn(spiral), FadeIn(dot), FadeIn(radial), FadeIn(tangent))
        self.play(theta.animate.set_value(6 * PI), run_time=6, rate_func=linear)

        card1 = RoundedRectangle(corner_radius=0.2, width=4.8, height=1.3, stroke_color=ACCENT3, fill_color="#111827", fill_opacity=0.9)
        card1_text = Text("A parameter is like a dial:\nturn the dial, the point moves.", font_size=24, color=TITLE_COLOR).move_to(card1)
        card = VGroup(card1, card1_text).to_edge(DOWN)
        self.play(FadeIn(card, shift=UP * 0.2))
        self.wait(1)
        self.play(FadeOut(card), FadeOut(tag))

        tag2 = Text("Lens 2: choreography", font_size=26, color=ACCENT3).to_edge(LEFT).shift(UP * 2)
        beats = VGroup(*[Dot(point=np.array([-5 + i * 1.1, -3.2, 0]), radius=0.04, color=SOFT) for i in range(10)])
        self.play(FadeIn(tag2), FadeIn(beats))
        captions = VGroup(
            Text("turn", font_size=24, color=ACCENT2),
            Text("step out", font_size=24, color=ACCENT2),
            Text("turn", font_size=24, color=ACCENT2),
            Text("step out", font_size=24, color=ACCENT2),
        ).arrange(RIGHT, buff=0.7).move_to(np.array([0, -3.2, 0]))
        self.play(LaggedStart(*[FadeIn(c, shift=0.1 * UP) for c in captions], lag_ratio=0.2))
        self.wait(1)
        self.play(FadeOut(captions), FadeOut(beats), FadeOut(tag2))

        tag3 = Text("Lens 3: material intuition", font_size=26, color=ACCENT3).to_edge(LEFT).shift(UP * 2)
        rings = VGroup(*[Circle(radius=r, color=GRID, stroke_width=2) for r in np.arange(0.6, 3.8, 0.4)])
        self.play(FadeIn(tag3), FadeIn(rings))
        note = Text("Think of ribbon wrapping outward with steady spacing.", font_size=26, color=TITLE_COLOR).to_edge(DOWN)
        self.play(FadeIn(note))
        pulse = Circle(radius=0.4, color=ACCENT2).move_to(ORIGIN)
        self.play(Indicate(pulse, scale_factor=5.5), run_time=1.5)

        finale = VGroup(
            Text("A spiral parametrization is a rule for motion.", font_size=30, color=TITLE_COLOR),
            MathTex(r"\theta \Rightarrow r(\theta) \Rightarrow (x(\theta), y(\theta))", color=ACCENT),
            Text("Turn. Move out. Place the point.", font_size=28, color=ACCENT2),
        ).arrange(DOWN, buff=0.22).move_to(ORIGIN)
        self.play(FadeOut(note), FadeOut(tag3), FadeOut(rings), FadeOut(radial), FadeOut(tangent), FadeOut(dot), FadeOut(spiral), FadeOut(plane), FadeOut(eqs))
        self.play(FadeIn(finale, shift=0.2 * UP))
        self.wait(2)
