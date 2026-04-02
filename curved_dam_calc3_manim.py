
from manim import *
import numpy as np

config.background_color = "#0f1117"

DAM_COLOR = BLUE_D
WATER_COLOR = TEAL_C
ACCENT = YELLOW
PRESSURE_COLOR = RED_C
RESERVOIR_COLOR = BLUE_E
SURFACE_GRID_COLOR = GREY_B
LABEL_COLOR = GREY_A
VECTOR_COLOR = GREEN_C

def dam_r(u, v):
    R = 3.8
    theta = -0.9 + 1.8 * u
    x = R * np.cos(theta)
    y = 0.65 * R * np.sin(theta) - 1.3
    z = 3.2 * v - 1.6
    return np.array([x, y, z])

def curve_on_dam(t):
    u = 0.15 + 0.7 * t
    v = 0.15 + 0.75 * t
    return dam_r(u, v)

def height_function(x, y):
    return 1.5 + 0.4 * np.cos(0.7 * x) + 0.6 * np.exp(-0.22 * (x**2 + (y+0.5)**2))

def pressure_field(x, z):
    return 1.2 + 0.12 * (x + 1.0)**2 + 1.35 * (1.6 - z)

def pressure_gradient(x, z):
    return np.array([0.24 * (x + 1.0), -1.35, 0.0])

def make_title_block(title, subtitle=None):
    title_text = Text(title, weight=BOLD).scale(0.65)
    if subtitle:
        sub = Text(subtitle, font_size=28, color=LABEL_COLOR)
        block = VGroup(title_text, sub).arrange(DOWN, buff=0.12)
    else:
        block = VGroup(title_text)
    block.to_edge(UP)
    return block

def make_dam_surface(resolution=(20, 12), opacity=0.85):
    return Surface(
        lambda u, v: dam_r(u, v),
        u_range=[0, 1],
        v_range=[0, 1],
        resolution=resolution,
        fill_color=DAM_COLOR,
        fill_opacity=opacity,
        stroke_color=SURFACE_GRID_COLOR,
        stroke_width=1.0,
    )

def make_water_sheet(resolution=(18, 10), opacity=0.4):
    return Surface(
        lambda u, v: dam_r(u, v) + np.array([-0.9, 0.75, 0.0]),
        u_range=[0, 1],
        v_range=[0, 1],
        resolution=resolution,
        fill_color=WATER_COLOR,
        fill_opacity=opacity,
        stroke_color=WATER_COLOR,
        stroke_width=0.6,
    )

def make_axes_3d():
    return ThreeDAxes(
        x_range=[-5, 5, 1],
        y_range=[-5, 4, 1],
        z_range=[-2.5, 3.5, 1],
        x_length=8,
        y_length=6,
        z_length=5,
    )

class IntroScene(ThreeDScene):
    def construct(self):
        title = make_title_block(
            "Curved Hydroelectric Dam",
            "Using dam design to learn Calculus 3"
        )
        self.add_fixed_in_frame_mobjects(title)
        self.play(FadeIn(title, shift=DOWN), run_time=1.0)

        axes = make_axes_3d()
        dam = make_dam_surface()
        water = make_water_sheet()

        self.set_camera_orientation(phi=68 * DEGREES, theta=-55 * DEGREES, zoom=0.95)
        self.play(Create(axes), run_time=1.2)
        self.play(FadeIn(water), Create(dam), run_time=1.6)

        eq = MathTex(
            r"\mathbf{r}(u,v)=",
            r"\langle",
            r"R\cos(\theta(u)),",
            r"0.65R\sin(\theta(u))-1.3,",
            r"3.2v-1.6",
            r"\rangle"
        ).scale(0.8).to_corner(UL).shift(DOWN*0.8)
        note = Text(
            "The dam wall is a surface traced by two parameters",
            font_size=28,
            color=LABEL_COLOR
        ).next_to(eq, DOWN, aligned_edge=LEFT, buff=0.18)

        self.add_fixed_in_frame_mobjects(eq, note)
        self.play(Write(eq), FadeIn(note, shift=UP), run_time=1.4)

        path = ParametricFunction(
            lambda t: curve_on_dam(t),
            t_range=[0, 1],
            color=ACCENT,
            stroke_width=5
        )
        particle = Sphere(radius=0.10, resolution=(16, 16)).set_color(ACCENT)
        particle.move_to(curve_on_dam(0))

        self.play(Create(path), FadeIn(particle), run_time=1.2)

        t_tracker = ValueTracker(0.0)
        particle.add_updater(lambda m: m.move_to(curve_on_dam(t_tracker.get_value())))

        u_num = DecimalNumber(0, num_decimal_places=2, color=ACCENT)
        v_num = DecimalNumber(0, num_decimal_places=2, color=ACCENT)
        info = VGroup(
            MathTex("u=").scale(0.8), u_num,
            MathTex("v=").scale(0.8), v_num
        ).arrange(RIGHT, buff=0.12)
        info.to_corner(UR).shift(DOWN*0.9)

        u_num.add_updater(lambda m: m.set_value(0.15 + 0.7*t_tracker.get_value()))
        v_num.add_updater(lambda m: m.set_value(0.15 + 0.75*t_tracker.get_value()))

        path_note = Text(
            "A water particle can move along a parametric curve on the wall",
            font_size=26,
            color=LABEL_COLOR
        ).next_to(info, DOWN, aligned_edge=RIGHT, buff=0.18)

        self.add_fixed_in_frame_mobjects(info, path_note)
        self.play(FadeIn(info), FadeIn(path_note, shift=UP), run_time=1.0)

        self.play(t_tracker.animate.set_value(1.0), run_time=4.0, rate_func=smooth)
        self.wait(0.5)

        next_text = Text(
            "Next: how pressure changes along the dam wall",
            font_size=30,
            color=ACCENT
        ).to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(next_text)
        self.play(FadeIn(next_text, shift=UP), run_time=1.0)
        self.wait(1.2)

class GradientScene(Scene):
    def construct(self):
        title = make_title_block(
            "Partial Derivatives and the Pressure Gradient",
            "Which way does pressure increase most rapidly?"
        )
        self.play(FadeIn(title, shift=DOWN), run_time=1.0)

        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-2, 3, 1],
            x_length=8.0,
            y_length=5.0,
            axis_config={"include_tip": False, "color": GREY_B},
        ).shift(DOWN*0.4 + LEFT*1.2)

        x_label = axes.get_x_axis_label(MathTex("x"))
        z_label = axes.get_y_axis_label(MathTex("z"))
        self.play(Create(axes), Write(x_label), Write(z_label), run_time=1.1)

        wall = Line(
            axes.c2p(-2.5, -1.4),
            axes.c2p(1.8, 2.0),
            color=DAM_COLOR,
            stroke_width=6
        )
        water_region = Polygon(
            axes.c2p(-4, -2), axes.c2p(-4, 2.4), axes.c2p(-1.2, 2.4),
            axes.c2p(-2.5, -1.4), axes.c2p(-4, -2),
            color=WATER_COLOR, fill_opacity=0.25, stroke_opacity=0
        )

        self.play(FadeIn(water_region), Create(wall), run_time=1.2)

        p_eq = MathTex(
            r"p(x,z)=1.2+0.12(x+1)^2+1.35(1.6-z)"
        ).scale(0.8).to_corner(UR).shift(DOWN*0.6)
        grad_eq = MathTex(
            r"\nabla p(x,z)=\left\langle 0.24(x+1),\,-1.35 \right\rangle"
        ).scale(0.8).next_to(p_eq, DOWN, aligned_edge=LEFT, buff=0.22)
        self.play(Write(p_eq), Write(grad_eq), run_time=1.4)

        vf = ArrowVectorField(
            lambda pos: np.array([
                0.55 * pressure_gradient(pos[0], pos[1])[0],
                0.55 * pressure_gradient(pos[0], pos[1])[1],
                0
            ]),
            x_range=[-3.6, 3.4, 0.9],
            y_range=[-1.8, 2.6, 0.7],
            colors=[BLUE_D, GREEN_C, YELLOW, RED_C],
            length_func=lambda norm: 0.35 + 0.22 * np.tanh(norm),
        )
        self.play(FadeIn(vf), run_time=1.4)

        tracker_x = ValueTracker(-2.6)
        tracker_z = ValueTracker(1.7)

        moving_dot = always_redraw(
            lambda: Dot(
                axes.c2p(tracker_x.get_value(), tracker_z.get_value()),
                color=ACCENT,
                radius=0.08
            )
        )

        pressure_value = DecimalNumber(0, num_decimal_places=2, color=ACCENT)
        pressure_value.add_updater(
            lambda d: d.set_value(pressure_field(tracker_x.get_value(), tracker_z.get_value()))
        )

        grad_mag = DecimalNumber(0, num_decimal_places=2, color=VECTOR_COLOR)
        grad_mag.add_updater(
            lambda d: d.set_value(
                np.linalg.norm(pressure_gradient(tracker_x.get_value(), tracker_z.get_value())[:2])
            )
        )

        readout = VGroup(
            MathTex("p=").scale(0.8), pressure_value,
            MathTex(r"\quad |\nabla p|=").scale(0.8), grad_mag
        ).arrange(RIGHT, buff=0.10)
        readout.next_to(grad_eq, DOWN, aligned_edge=LEFT, buff=0.3)

        self.play(FadeIn(moving_dot), FadeIn(readout), run_time=0.9)

        local_arrow = always_redraw(
            lambda: Arrow(
                start=axes.c2p(tracker_x.get_value(), tracker_z.get_value()),
                end=axes.c2p(
                    tracker_x.get_value() + 0.7 * pressure_gradient(tracker_x.get_value(), tracker_z.get_value())[0],
                    tracker_z.get_value() + 0.7 * pressure_gradient(tracker_x.get_value(), tracker_z.get_value())[1]
                ),
                buff=0,
                color=ACCENT,
                max_tip_length_to_length_ratio=0.18
            )
        )
        self.play(Create(local_arrow), run_time=0.8)

        explanation = Text(
            "The gradient points in the direction of fastest pressure increase.",
            font_size=28,
            color=LABEL_COLOR
        ).to_edge(DOWN)
        self.play(FadeIn(explanation, shift=UP), run_time=1.0)

        self.play(
            tracker_x.animate.set_value(0.4),
            tracker_z.animate.set_value(0.4),
            run_time=3.2,
            rate_func=smooth
        )
        self.play(
            tracker_x.animate.set_value(1.5),
            tracker_z.animate.set_value(-0.8),
            run_time=2.8,
            rate_func=smooth
        )
        self.wait(0.5)

        next_text = Text(
            "Now integrate the water depth to get total volume.",
            font_size=30,
            color=ACCENT
        ).to_edge(DOWN)
        self.play(Transform(explanation, next_text), run_time=1.0)
        self.wait(1.0)

class IntegrationScene(ThreeDScene):
    def construct(self):
        title = make_title_block(
            "Multiple Integrals and the Reservoir Volume",
            "Think of the water as a summation of thin columns"
        )
        self.add_fixed_in_frame_mobjects(title)
        self.play(FadeIn(title, shift=DOWN), run_time=1.0)

        axes = ThreeDAxes(
            x_range=[-3.5, 3.5, 1],
            y_range=[-3.5, 2.5, 1],
            z_range=[0, 3.8, 1],
            x_length=7,
            y_length=6,
            z_length=4.2,
        )

        self.set_camera_orientation(phi=70 * DEGREES, theta=-50 * DEGREES, zoom=0.9)
        self.play(Create(axes), run_time=1.1)

        floor = Surface(
            lambda u, v: np.array([u, v, 0]),
            u_range=[-3, 3],
            v_range=[-2.5, 1.8],
            resolution=(12, 10),
            fill_color=GREY_D,
            fill_opacity=0.35,
            stroke_color=GREY_B,
            stroke_width=0.8,
        )

        water_top = Surface(
            lambda u, v: np.array([u, v, height_function(u, v)]),
            u_range=[-3, 3],
            v_range=[-2.5, 1.8],
            resolution=(18, 14),
            fill_color=RESERVOIR_COLOR,
            fill_opacity=0.48,
            stroke_color=BLUE_B,
            stroke_width=0.6,
        )

        self.play(FadeIn(floor), FadeIn(water_top), run_time=1.6)

        x0, y0 = 0.8, -0.6
        h0 = height_function(x0, y0)
        column = Prism(
            dimensions=[0.35, 0.35, h0],
            fill_color=ACCENT,
            fill_opacity=0.75,
            stroke_width=0.8
        )
        column.move_to(np.array([x0, y0, h0/2]))

        patch = Square(side_length=0.35, color=ACCENT, fill_opacity=0.35).move_to(np.array([x0, y0, 0]))
        self.play(FadeIn(column), FadeIn(patch), run_time=1.0)

        vol_eq1 = MathTex(
            r"dV \approx h(x,y)\,dA"
        ).scale(0.95).to_corner(UR).shift(DOWN*0.6)
        vol_eq2 = MathTex(
            r"V=\iint_D h(x,y)\,dA"
        ).scale(1.0).next_to(vol_eq1, DOWN, aligned_edge=LEFT, buff=0.3)
        note = Text(
            "Add many thin columns over the reservoir floor.",
            font_size=28,
            color=LABEL_COLOR
        ).next_to(vol_eq2, DOWN, aligned_edge=LEFT, buff=0.18)

        self.add_fixed_in_frame_mobjects(vol_eq1, vol_eq2, note)
        self.play(Write(vol_eq1), Write(vol_eq2), FadeIn(note, shift=UP), run_time=1.5)

        columns = VGroup()
        xs = np.linspace(-2.4, 2.4, 5)
        ys = np.linspace(-1.8, 1.2, 4)
        for xx in xs:
            for yy in ys:
                hh = height_function(xx, yy)
                c = Prism(
                    dimensions=[0.28, 0.28, hh],
                    fill_color=WATER_COLOR,
                    fill_opacity=0.45,
                    stroke_width=0.4
                )
                c.move_to(np.array([xx, yy, hh/2]))
                columns.add(c)

        self.play(LaggedStart(*[FadeIn(c) for c in columns], lag_ratio=0.05), run_time=2.0)

        area_label = MathTex("D").scale(1.0).move_to(np.array([2.7, 1.4, 0.0]))
        self.play(Write(area_label), run_time=0.8)

        summation_text = Text(
            "The double integral accumulates all these columns into one total volume.",
            font_size=28,
            color=LABEL_COLOR
        ).to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(summation_text)
        self.play(FadeIn(summation_text, shift=UP), run_time=1.0)

        self.begin_ambient_camera_rotation(rate=0.12)
        self.wait(2.2)
        self.stop_ambient_camera_rotation()

        next_text = Text(
            "Finally, use a surface integral to compute total force on the dam.",
            font_size=30,
            color=ACCENT
        ).to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(next_text)
        self.play(Transform(summation_text, next_text), run_time=1.0)
        self.wait(1.0)

class FluxScene(ThreeDScene):
    def construct(self):
        title = make_title_block(
            "Vector Calculus: Flux, Surface Integrals, and Total Force",
            "Normal vectors tell us how the water pushes on the curved wall"
        )
        self.add_fixed_in_frame_mobjects(title)
        self.play(FadeIn(title, shift=DOWN), run_time=1.0)

        axes = make_axes_3d()
        dam = make_dam_surface(resolution=(18, 10), opacity=0.90)
        water = make_water_sheet(resolution=(14, 8), opacity=0.32)

        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES, zoom=0.92)
        self.play(Create(axes), FadeIn(water), Create(dam), run_time=1.6)

        normals = VGroup()
        for u in np.linspace(0.1, 0.9, 5):
            for v in np.linspace(0.12, 0.88, 4):
                p = dam_r(u, v)
                du = 1e-3
                dv = 1e-3
                ru = (dam_r(u + du, v) - dam_r(u - du, v)) / (2 * du)
                rv = (dam_r(u, v + dv) - dam_r(u, v - dv)) / (2 * dv)
                n = np.cross(ru, rv)
                n = n / np.linalg.norm(n)
                if n[1] < 0:
                    n = -n

                arrow = Arrow3D(
                    start=p,
                    end=p + 0.55 * n,
                    color=VECTOR_COLOR,
                    thickness=0.015,
                    resolution=8
                )
                normals.add(arrow)

        self.play(LaggedStart(*[Create(a) for a in normals], lag_ratio=0.05), run_time=2.2)

        eq1 = MathTex(
            r"\mathbf{F}(u,v)=p(u,v)\,\mathbf{n}(u,v)"
        ).scale(0.85).to_corner(UL).shift(DOWN*0.8)
        eq2 = MathTex(
            r"\text{Total force}\;\approx\;\iint_S p\,\mathbf{n}\,dS"
        ).scale(0.95).next_to(eq1, DOWN, aligned_edge=LEFT, buff=0.28)
        eq3 = MathTex(
            r"\text{(surface integral over the dam face)}"
        ).scale(0.75).next_to(eq2, DOWN, aligned_edge=LEFT, buff=0.14)
        self.add_fixed_in_frame_mobjects(eq1, eq2, eq3)
        self.play(Write(eq1), Write(eq2), FadeIn(eq3, shift=UP), run_time=1.6)

        u0, v0 = 0.55, 0.35
        p0 = dam_r(u0, v0)
        du = 1e-3
        dv = 1e-3
        ru = (dam_r(u0 + du, v0) - dam_r(u0 - du, v0)) / (2 * du)
        rv = (dam_r(u0, v0 + dv) - dam_r(u0, v0 - dv)) / (2 * dv)
        n0 = np.cross(ru, rv)
        n0 = n0 / np.linalg.norm(n0)
        if n0[1] < 0:
            n0 = -n0

        local_normal = Arrow3D(start=p0, end=p0 + 0.85*n0, color=ACCENT, thickness=0.024)
        local_force = Arrow3D(start=p0, end=p0 + 1.25*n0, color=PRESSURE_COLOR, thickness=0.028)

        normal_label = MathTex(r"\mathbf{n}").scale(0.75).move_to(p0 + 1.0*n0 + np.array([0.2, 0.2, 0.2]))
        force_label = MathTex(r"p\,\mathbf{n}").scale(0.75).move_to(p0 + 1.45*n0 + np.array([0.2, -0.1, 0.25]))

        self.play(Create(local_normal), Write(normal_label), run_time=1.0)
        self.play(Transform(local_normal.copy(), local_force), Write(force_label), run_time=1.2)

        explanation = Text(
            "Each tiny patch contributes a force in its normal direction. The surface integral adds them all.",
            font_size=28,
            color=LABEL_COLOR
        ).to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(explanation)
        self.play(FadeIn(explanation, shift=UP), run_time=1.0)

        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(2.5)
        self.stop_ambient_camera_rotation()

        next_text = Text(
            "Calculus 3 turns the dam into a complete engineering model.",
            font_size=30,
            color=ACCENT
        ).to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(next_text)
        self.play(Transform(explanation, next_text), run_time=1.0)
        self.wait(1.0)

class OutroScene(Scene):
    def construct(self):
        title = make_title_block(
            "From Curves to Fields to Integrals",
            "A curved dam becomes a Calculus 3 story"
        )
        self.play(FadeIn(title, shift=DOWN), run_time=1.0)

        bullets = VGroup(
            Text("1. Parametric surfaces describe the dam geometry.", font_size=30),
            Text("2. Gradients show where pressure increases fastest.", font_size=30),
            Text("3. Double integrals add water columns to get volume.", font_size=30),
            Text("4. Surface integrals add local forces over the wall.", font_size=30),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).shift(DOWN*0.2)

        box = SurroundingRectangle(bullets, color=BLUE_D, buff=0.35, corner_radius=0.15)
        self.play(LaggedStart(*[FadeIn(b, shift=RIGHT*0.15) for b in bullets], lag_ratio=0.16), run_time=1.8)
        self.play(Create(box), run_time=0.9)

        closing = Text(
            "This is how Calculus 3 helps engineers design structures that interact with the physical world.",
            font_size=30,
            color=LABEL_COLOR
        ).to_edge(DOWN)
        self.play(FadeIn(closing, shift=UP), run_time=1.0)
        self.wait(2.0)
