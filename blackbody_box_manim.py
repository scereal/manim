
from manim import *
import numpy as np

config.background_color = "#0f1117"

def planck_like_intensity(lam, T):
    c2 = 14388.0
    lam = np.maximum(lam, 1e-3)
    return 1.0 / (lam**5 * (np.exp(c2 / (lam * T)) - 1.0))

def normalized_curve(T, lams):
    y = planck_like_intensity(lams, T)
    y = y / np.max(y)
    return y

def glow_dot(color=WHITE, radius=0.07):
    core = Dot(radius=radius, color=color)
    halo1 = Dot(radius=radius*2.6, color=color, fill_opacity=0.12, stroke_opacity=0)
    halo2 = Dot(radius=radius*4.4, color=color, fill_opacity=0.05, stroke_opacity=0)
    return VGroup(halo2, halo1, core)

def hot_surface_color(T):
    if T < 700:
        return GREY_B
    if T < 1000:
        return RED_E
    if T < 1400:
        return RED_C
    if T < 1800:
        return ORANGE
    if T < 2600:
        return YELLOW
    if T < 4000:
        return WHITE
    return BLUE_B

class BlackbodyBoxExplainer(Scene):
    def construct(self):
        title = Text("Blackbody Irradiation and Why Hot Boxes Change Color", weight=BOLD).scale(0.55)
        subtitle = Text(
            "How temperature shapes the emitted spectrum — and why the outside and inside can look different",
            font_size=26,
            color=GREY_B
        )
        subtitle.next_to(title, DOWN, buff=0.18)
        header = VGroup(title, subtitle).to_edge(UP)
        self.play(FadeIn(header, shift=DOWN), run_time=1.2)
        self.wait(0.3)

        axes = Axes(
            x_range=[0.2, 3.0, 0.4],
            y_range=[0, 1.15, 0.25],
            x_length=6.2,
            y_length=3.8,
            axis_config={"include_tip": False, "color": GREY_B},
        )
        axes_labels = axes.get_axis_labels(
            Text("wavelength  λ", font_size=26),
            Text("relative intensity", font_size=24)
        )

        vis_band = Rectangle(
            width=axes.x_length * (0.7 - 0.4) / (3.0 - 0.2),
            height=axes.y_length,
            stroke_width=0,
            fill_opacity=0.18
        )
        vis_band.set_color_by_gradient(PURPLE_E, BLUE_D, TEAL_C, GREEN_C, YELLOW, ORANGE, RED_C)
        vis_center_x = axes.c2p(0.55, 0)[0]
        vis_band.move_to([vis_center_x, axes.get_center()[1], 0])

        vis_label = Text("visible band", font_size=22, color=GREY_A).next_to(axes, DOWN, buff=0.15)

        plot_group = VGroup(axes, vis_band, axes_labels, vis_label).scale(0.95)
        plot_group.to_edge(LEFT).shift(DOWN*0.4 + RIGHT*0.15)
        self.play(Create(axes), FadeIn(vis_band), Write(axes_labels), FadeIn(vis_label), run_time=1.6)

        lams = np.linspace(0.2, 3.0, 600)
        Ts = [700, 1200, 2000, 3200]
        curve_colors = [RED_E, ORANGE, YELLOW, WHITE]
        curves = VGroup()
        peak_dots = VGroup()
        temp_labels = VGroup()

        for T, c in zip(Ts, curve_colors):
            y = normalized_curve(T, lams)
            graph = axes.plot_line_graph(
                x_values=lams,
                y_values=y,
                add_vertex_dots=False,
                line_color=c,
                stroke_width=5 if T == Ts[-1] else 4
            )
            curves.add(graph)

            peak_idx = int(np.argmax(y))
            peak_lam = lams[peak_idx]
            peak_pt = axes.c2p(peak_lam, y[peak_idx])
            pd = glow_dot(color=c, radius=0.045).move_to(peak_pt)
            peak_dots.add(pd)

            temp_label = MathTex(f"T={T}\\,\\mathrm{{K}}", color=c).scale(0.6)
            temp_label.next_to(graph.get_end(), RIGHT, buff=0.15)
            temp_labels.add(temp_label)

        self.play(
            LaggedStart(*[Create(c) for c in curves], lag_ratio=0.18),
            LaggedStart(*[FadeIn(d) for d in peak_dots], lag_ratio=0.18),
            LaggedStart(*[Write(t) for t in temp_labels], lag_ratio=0.18),
            run_time=2.8
        )

        wien = MathTex(r"\lambda_{\text{peak}} \propto \frac{1}{T}", color=BLUE_B).scale(0.8)
        stefan = MathTex(r"\text{total emitted power} \propto T^4", color=YELLOW).scale(0.8)
        laws = VGroup(wien, stefan).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        laws.next_to(axes, UP, buff=0.22).shift(RIGHT*0.9)

        self.play(Write(wien), run_time=0.9)
        self.play(Write(stefan), run_time=0.9)

        takeaway1 = Text(
            "As temperature rises, the spectrum grows taller\nand its peak shifts toward shorter wavelengths.",
            font_size=26
        ).next_to(plot_group, DOWN, buff=0.45).align_to(plot_group, LEFT)
        self.play(FadeIn(takeaway1, shift=UP), run_time=1.1)
        self.wait(0.7)

        outer = Square(side_length=2.2, color=GREY_C, stroke_width=4)
        inner = Square(side_length=1.15, color=GREY_A, stroke_width=3)
        box = VGroup(outer, inner)
        cavity_label = Text("cavity", font_size=24, color=GREY_A).move_to(inner.get_center())
        outside_label = Text("outer surface", font_size=24, color=GREY_A).next_to(outer, DOWN, buff=0.15)

        box_group = VGroup(box, cavity_label, outside_label).to_edge(RIGHT).shift(LEFT*0.5 + DOWN*0.35)
        self.play(Create(outer), Create(inner), FadeIn(cavity_label), FadeIn(outside_label), run_time=1.4)

        temp_tracker = ValueTracker(700)

        temp_text = always_redraw(
            lambda: MathTex(
                rf"T \approx {int(temp_tracker.get_value())}\,\mathrm{{K}}",
                color=hot_surface_color(temp_tracker.get_value())
            ).scale(0.8).next_to(box_group, UP, buff=0.35)
        )

        exterior_fill = always_redraw(
            lambda: outer.copy()
            .set_stroke(color=hot_surface_color(temp_tracker.get_value()), width=5)
            .set_fill(color=hot_surface_color(temp_tracker.get_value()), opacity=0.35)
        )
        interior_fill = always_redraw(
            lambda: inner.copy()
            .set_stroke(color=hot_surface_color(temp_tracker.get_value()), width=4)
            .set_fill(color=hot_surface_color(temp_tracker.get_value()), opacity=0.75)
        )

        self.add(exterior_fill, interior_fill, temp_text, cavity_label, outside_label)

        def make_rays(n=10, interior=False):
            rays = VGroup()
            center = inner.get_center() if interior else outer.get_center()
            base_r = 0.58 if interior else 1.18
            for k in range(n):
                ang = TAU*k/n + (PI/n if interior else 0)
                start = center + 0.45*np.array([np.cos(ang), np.sin(ang), 0])
                end = center + base_r*np.array([np.cos(ang), np.sin(ang), 0])
                ray = Line(start, end, stroke_width=3)
                rays.add(ray)
            return rays

        exterior_rays = always_redraw(
            lambda: make_rays(n=12, interior=False).set_color(hot_surface_color(temp_tracker.get_value())).set_opacity(0.55)
        )
        interior_rays = always_redraw(
            lambda: make_rays(n=12, interior=True).set_color(hot_surface_color(temp_tracker.get_value())).set_opacity(0.85)
        )

        self.play(FadeIn(exterior_rays), FadeIn(interior_rays), FadeIn(temp_text), run_time=1.2)

        surface_note = Text(
            "A hotter surface emits more radiation.\nIts glow changes from dull red to orange/yellow to white.",
            font_size=25
        ).next_to(box_group, DOWN, buff=0.55)
        surface_note.set_width(4.3)
        self.play(FadeIn(surface_note, shift=UP), run_time=1.0)

        active_curve = curves[0].copy()
        active_dot = peak_dots[0].copy()
        self.play(
            Transform(active_curve, curves[0].copy().set_stroke(width=7)),
            FadeIn(active_dot),
            run_time=0.6
        )
        self.wait(0.3)

        for i, Tnew in enumerate([1200, 2000, 3200]):
            self.play(
                temp_tracker.animate.set_value(Tnew),
                Transform(active_curve, curves[i+1].copy().set_stroke(width=7)),
                Transform(active_dot, peak_dots[i+1].copy()),
                run_time=1.6
            )
            self.wait(0.2)

        divider = Line(UP*2.7, DOWN*2.7, stroke_opacity=0.22).move_to([0.95, -0.2, 0])
        self.play(FadeIn(divider), run_time=0.6)

        cavity_title = Text("Why the interior often looks more intense", weight=BOLD).scale(0.46)
        cavity_title.next_to(box_group, LEFT, buff=0.35).shift(UP*1.55)

        bullets = VGroup(
            Text("1. Radiation emitted inward gets reflected and re-absorbed many times.", font_size=24),
            Text("2. A cavity behaves much more like an ideal blackbody emitter.", font_size=24),
            Text("3. So when you look into the opening, the glow can appear deeper and brighter.", font_size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        bullets.next_to(cavity_title, DOWN, aligned_edge=LEFT, buff=0.25)
        bullets.set_width(5.6)

        self.play(FadeIn(cavity_title, shift=RIGHT), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(b, shift=RIGHT*0.15) for b in bullets], lag_ratio=0.18), run_time=1.5)

        bounce_points = [
            inner.get_corner(UL) + DR*0.18,
            inner.get_corner(UR) + DL*0.18,
            inner.get_corner(DR) + UL*0.18,
            inner.get_corner(DL) + UR*0.18,
            inner.get_corner(UR) + DL*0.18,
        ]
        zig = VMobject(color=WHITE)
        zig.set_points_as_corners(bounce_points).set_stroke(width=4, opacity=0.85)
        zig.set_color(hot_surface_color(temp_tracker.get_value()))

        opening = ArcBetweenPoints(outer.get_top()+LEFT*0.35, outer.get_top()+RIGHT*0.35, angle=-0.6, color=GREY_A)
        opening_label = Text("opening", font_size=22, color=GREY_A).next_to(opening, UP, buff=0.05)

        self.play(Create(opening), FadeIn(opening_label), run_time=0.8)
        self.play(Create(zig), run_time=1.3)

        compare = VGroup(
            Text("Outside surface:", font_size=24, color=GREY_A),
            Text("one emission directly to you", font_size=24),
            Text("Inside cavity:", font_size=24, color=GREY_A),
            Text("many chances for emission / absorption → more blackbody-like glow", font_size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.13)
        compare.next_to(bullets, DOWN, aligned_edge=LEFT, buff=0.35)
        compare.set_width(5.5)

        self.play(FadeIn(compare, shift=UP), run_time=1.1)

        final_box = SurroundingRectangle(
            VGroup(plot_group, box_group),
            buff=0.28,
            corner_radius=0.15,
            color=BLUE_D,
            stroke_opacity=0.35
        )
        final_text = Text(
            "Color change comes from the temperature-dependent spectrum.\n"
            "The interior can look more ideal and more intense because a cavity is a better blackbody emitter.",
            font_size=28
        ).to_edge(DOWN).shift(UP*0.15)

        self.play(Create(final_box), run_time=0.9)
        self.play(FadeIn(final_text, shift=UP), run_time=1.2)
        self.wait(2)

class BlackbodyBoxShort(Scene):
    def construct(self):
        title = Text("Blackbody Radiation in a Heated Box", weight=BOLD).scale(0.65).to_edge(UP)
        self.play(Write(title), run_time=1.0)

        axes = Axes(
            x_range=[0.2, 3.0, 0.4],
            y_range=[0, 1.1, 0.25],
            x_length=6.3,
            y_length=3.7,
            axis_config={"include_tip": False}
        ).to_edge(LEFT).shift(DOWN*0.35)
        band = Rectangle(
            width=axes.x_length*(0.7-0.4)/(3.0-0.2),
            height=axes.y_length,
            stroke_width=0,
            fill_opacity=0.18
        ).set_color_by_gradient(PURPLE_E, BLUE_D, TEAL_C, GREEN_C, YELLOW, ORANGE, RED_C)
        band.move_to([axes.c2p(0.55, 0)[0], axes.get_center()[1], 0])

        self.play(Create(axes), FadeIn(band), run_time=1.1)

        lams = np.linspace(0.2, 3.0, 500)
        Tvals = [800, 1600, 3000]
        cols = [RED_C, ORANGE, WHITE]
        graphs = []
        for T, c in zip(Tvals, cols):
            y = normalized_curve(T, lams)
            g = axes.plot_line_graph(lams, y, add_vertex_dots=False, line_color=c)
            graphs.append(g)

        self.play(LaggedStart(*[Create(g) for g in graphs], lag_ratio=0.18), run_time=2.0)

        law = MathTex(r"\lambda_{\text{peak}} \downarrow \text{ as } T \uparrow,\qquad P \sim T^4").scale(0.78)
        law.next_to(axes, DOWN, buff=0.45)
        self.play(Write(law), run_time=1.0)

        outer = Square(side_length=2.2).set_color(GREY_B).to_edge(RIGHT).shift(LEFT*0.65 + DOWN*0.25)
        inner = Square(side_length=1.2).set_color(GREY_A).move_to(outer)
        inner.set_fill(ORANGE, opacity=0.75)
        outer.set_fill(RED_E, opacity=0.35)

        rays_in = VGroup(*[
            Line(inner.get_center(), inner.get_center() + 0.55*np.array([np.cos(a), np.sin(a), 0]), stroke_width=3, color=YELLOW)
            for a in np.linspace(0, TAU, 10, endpoint=False)
        ])
        rays_out = VGroup(*[
            Line(outer.get_center() + 0.8*np.array([np.cos(a), np.sin(a), 0]),
                 outer.get_center() + 1.2*np.array([np.cos(a), np.sin(a), 0]),
                 stroke_width=3, color=ORANGE)
            for a in np.linspace(0, TAU, 10, endpoint=False)
        ])
        self.play(Create(outer), Create(inner), FadeIn(rays_in), FadeIn(rays_out), run_time=1.4)

        note = Text(
            "As the box gets hotter, the emitted spectrum shifts.\nThe surface glow changes color, and the cavity interior appears especially blackbody-like.",
            font_size=28
        ).to_edge(DOWN)
        self.play(FadeIn(note, shift=UP), run_time=1.0)
        self.wait(2)
