# Extracted from /Users/hochmax/learn/manim/tests/template_generate_graphical_units_data.py
from __future__ import annotations

from manim import *
from tests.helpers.graphical_units import set_test_scene

# Note: DO NOT COMMIT THIS FILE. The purpose of this template is to produce control data for graphical_units_data. As
# soon as the test data is produced, please revert all changes you made to this file, so this template file will be
# still available for others :)
# More about graphical unit tests: https://github.com/ManimCommunity/manim/wiki/Testing#graphical-unit-test


class YourClassTest(Scene):  # e.g. RoundedRectangleTest
    def construct(self):
        circle = Circle()
        self.play(Animation(circle))


set_test_scene(
    YourClassTest,
    "INSERT_MODULE_NAME",
)  # INSERT_MODULE_NAME can be e.g.  "geometry" or "movements"


# Extracted from /Users/hochmax/learn/manim/tests/test_scene_rendering/simple_scenes.py
from __future__ import annotations

from enum import Enum

from manim import *


class SquareToCircle(Scene):
    def construct(self):
        square = Square()
        circle = Circle()
        self.play(Transform(square, circle))


class SceneWithMultipleCalls(Scene):
    def construct(self):
        number = Integer(0)
        self.add(number)
        for _i in range(10):
            self.play(Animation(Square()))


class SceneWithMultipleWaitCalls(Scene):
    def construct(self):
        self.play(Create(Square()))
        self.wait(1)
        self.play(Create(Square().shift(DOWN)))
        self.wait(1)
        self.play(Create(Square().shift(2 * DOWN)))
        self.wait(1)
        self.play(Create(Square().shift(3 * DOWN)))
        self.wait(1)


class NoAnimations(Scene):
    def construct(self):
        dot = Dot().set_color(GREEN)
        self.add(dot)
        self.wait(0.1)


class SceneWithStaticWait(Scene):
    def construct(self):
        self.add(Square())
        self.wait()


class SceneWithSceneUpdater(Scene):
    def construct(self):
        self.add(Square())
        self.add_updater(lambda dt: 42)
        self.wait()


class SceneForFrozenFrameTests(Scene):
    def construct(self):
        self.mobject_update_count = 0
        self.scene_update_count = 0

        def increment_mobject_update_count(mob, dt):
            self.mobject_update_count += 1

        def increment_scene_update_count(dt):
            self.scene_update_count += 1

        s = Square()
        s.add_updater(increment_mobject_update_count)
        self.add(s)
        self.add_updater(increment_scene_update_count)

        self.wait(frozen_frame=True)


class SceneWithNonStaticWait(Scene):
    def construct(self):
        s = Square()
        # Non static wait are triggered by mobject with time based updaters.
        s.add_updater(lambda mob, dt: None)
        self.add(s)
        self.wait()


class StaticScene(Scene):
    def construct(self):
        dot = Dot().set_color(GREEN)
        self.add(dot)


class InteractiveStaticScene(Scene):
    def construct(self):
        dot = Dot().set_color(GREEN)
        self.add(dot)
        self.interactive_mode = True


class SceneWithSections(Scene):
    def construct(self):
        # this would be defined in a third party application using the segmented video API
        class PresentationSectionType(str, Enum):
            # start, end, wait for continuation by user
            NORMAL = "presentation.normal"
            # start, end, immediately continue to next section
            SKIP = "presentation.skip"
            # start, end, restart, immediately continue to next section when continued by user
            LOOP = "presentation.loop"
            # start, end, restart, finish animation first when user continues
            COMPLETE_LOOP = "presentation.complete_loop"

        # this animation is part of the first, automatically created section
        self.wait()

        self.next_section()
        self.wait(2)

        self.next_section(name="test")
        self.wait()

        self.next_section(
            "Prepare For Unforeseen Consequences.", DefaultSectionType.NORMAL
        )
        self.wait(2)

        self.next_section(type=PresentationSectionType.SKIP)
        self.wait()

        self.next_section(
            name="this section should be removed as it doesn't contain any animations"
        )


class ElaborateSceneWithSections(Scene):
    def construct(self):
        # the first automatically created section should be deleted <- it's empty
        self.next_section("create square")
        square = Square()
        self.play(FadeIn(square))
        self.wait()

        self.next_section("transform to circle")
        circle = Circle()
        self.play(Transform(square, circle))
        self.wait()

        # this section will be entirely skipped
        self.next_section("skipped animations section", skip_animations=True)
        circle = Circle()
        self.play(Transform(square, circle))
        self.wait()

        self.next_section("fade out")
        self.play(FadeOut(square))
        self.wait()


# Extracted from /Users/hochmax/learn/manim/tests/test_scene_rendering/test_play_logic.py
from __future__ import annotations

import sys
from unittest.mock import Mock

import pytest

from manim import *
from manim import config

from .simple_scenes import (
    SceneForFrozenFrameTests,
    SceneWithMultipleCalls,
    SceneWithNonStaticWait,
    SceneWithSceneUpdater,
    SceneWithStaticWait,
    SquareToCircle,
)


@pytest.mark.skipif(
    sys.version_info < (3, 8),
    reason="Mock object has a different implementation in python 3.7, which makes it broken with this logic.",
)
@pytest.mark.parametrize("frame_rate", argvalues=[15, 30, 60])
def test_t_values(using_temp_config, disabling_caching, frame_rate):
    """Test that the framerate corresponds to the number of t values generated"""
    config.frame_rate = frame_rate
    scene = SquareToCircle()
    scene.update_to_time = Mock()
    scene.render()
    assert scene.update_to_time.call_count == config["frame_rate"]
    np.testing.assert_allclose(
        ([call.args[0] for call in scene.update_to_time.call_args_list]),
        np.arange(0, 1, 1 / config["frame_rate"]),
    )


@pytest.mark.skipif(
    sys.version_info < (3, 8),
    reason="Mock object has a different implementation in python 3.7, which makes it broken with this logic.",
)
def test_t_values_with_skip_animations(using_temp_config, disabling_caching):
    """Test the behaviour of scene.skip_animations"""
    scene = SquareToCircle()
    scene.update_to_time = Mock()
    scene.renderer._original_skipping_status = True
    scene.render()
    assert scene.update_to_time.call_count == 1
    np.testing.assert_almost_equal(
        scene.update_to_time.call_args.args[0],
        1.0,
    )


def test_static_wait_detection(using_temp_config, disabling_caching):
    """Test if a static wait (wait that freeze the frame) is correctly detected"""
    scene = SceneWithStaticWait()
    scene.render()
    # Test is is_static_wait of the Wait animation has been set to True by compile_animation_ata
    assert scene.animations[0].is_static_wait
    assert scene.is_current_animation_frozen_frame()


def test_non_static_wait_detection(using_temp_config, disabling_caching):
    scene = SceneWithNonStaticWait()
    scene.render()
    assert not scene.animations[0].is_static_wait
    assert not scene.is_current_animation_frozen_frame()
    scene = SceneWithSceneUpdater()
    scene.render()
    assert not scene.animations[0].is_static_wait
    assert not scene.is_current_animation_frozen_frame()


def test_wait_with_stop_condition(using_temp_config, disabling_caching):
    class TestScene(Scene):
        def construct(self):
            self.wait_until(lambda: self.renderer.time >= 1)
            assert self.renderer.time >= 1
            d = Dot()
            d.add_updater(lambda mobj, dt: self.add(Mobject()))
            self.add(d)
            self.play(Wait(run_time=5, stop_condition=lambda: len(self.mobjects) > 5))
            assert len(self.mobjects) > 5
            assert self.renderer.time < 2

    scene = TestScene()
    scene.render()


def test_frozen_frame(using_temp_config, disabling_caching):
    scene = SceneForFrozenFrameTests()
    scene.render()
    assert scene.mobject_update_count == 0
    assert scene.scene_update_count == 0


def test_t_values_with_cached_data(using_temp_config):
    """Test the proper generation and use of the t values when an animation is cached."""
    scene = SceneWithMultipleCalls()
    # Mocking the file_writer will skip all the writing process.
    scene.renderer.file_writer = Mock(scene.renderer.file_writer)
    scene.renderer.update_skipping_status = Mock()
    # Simulate that all animations are cached.
    scene.renderer.file_writer.is_already_cached.return_value = True
    scene.update_to_time = Mock()

    scene.render()
    assert scene.update_to_time.call_count == 10


def test_t_values_save_last_frame(using_temp_config):
    """Test that there is only one t value handled when only saving the last frame"""
    config.save_last_frame = True
    scene = SquareToCircle()
    scene.update_to_time = Mock()
    scene.render()
    scene.update_to_time.assert_called_once_with(1)


def test_animate_with_changed_custom_attribute(using_temp_config):
    """Test that animating the change of a custom attribute
    using the animate syntax works correctly.
    """

    class CustomAnimateScene(Scene):
        def construct(self):
            vt = ValueTracker(0)
            vt.custom_attribute = "hello"
            self.play(vt.animate.set_value(42).set(custom_attribute="world"))
            assert vt.get_value() == 42
            assert vt.custom_attribute == "world"

    CustomAnimateScene().render()


# Extracted from /Users/hochmax/learn/manim/tests/test_scene_rendering/test_cairo_renderer.py
from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from manim import *

from ..assert_utils import assert_file_exists
from .simple_scenes import *


def test_render(using_temp_config, disabling_caching):
    scene = SquareToCircle()
    renderer = scene.renderer
    renderer.update_frame = Mock(wraps=renderer.update_frame)
    renderer.add_frame = Mock(wraps=renderer.add_frame)
    scene.render()
    assert renderer.add_frame.call_count == config["frame_rate"]
    assert renderer.update_frame.call_count == config["frame_rate"]
    assert_file_exists(config["output_file"])


def test_skipping_status_with_from_to_and_up_to(using_temp_config, disabling_caching):
    """Test if skip_animations is well updated when -n flag is passed"""
    config.from_animation_number = 2
    config.upto_animation_number = 6

    class SceneWithMultipleCalls(Scene):
        def construct(self):
            number = Integer(0)
            self.add(number)
            for i in range(10):
                self.play(Animation(Square()))

                assert ((i >= 2) and (i <= 6)) or self.renderer.skip_animations

    SceneWithMultipleCalls().render()


@pytest.mark.xfail(reason="caching issue")
def test_when_animation_is_cached(using_temp_config):
    partial_movie_files = []
    for _ in range(2):
        # Render several times to generate a cache.
        # In some edgy cases and on some OS, a same scene can produce
        # a (finite, generally 2) number of different hash. In this case, the scene wouldn't be detected as cached, making the test fail.
        scene = SquareToCircle()
        scene.render()
        partial_movie_files.append(scene.renderer.file_writer.partial_movie_files)
    scene = SquareToCircle()
    scene.update_to_time = Mock()
    scene.render()
    assert scene.renderer.file_writer.is_already_cached(
        scene.renderer.animations_hashes[0],
    )
    # Check that the same partial movie files has been used (with he same hash).
    # As there might have been several hashes, a list is used.
    assert scene.renderer.file_writer.partial_movie_files in partial_movie_files
    # Check that manim correctly skipped the animation.
    scene.update_to_time.assert_called_once_with(1)
    # Check that the output video has been generated.
    assert_file_exists(config["output_file"])


def test_hash_logic_is_not_called_when_caching_is_disabled(
    using_temp_config,
    disabling_caching,
):
    with patch("manim.renderer.cairo_renderer.get_hash_from_play_call") as mocked:
        scene = SquareToCircle()
        scene.render()
        mocked.assert_not_called()
        assert_file_exists(config["output_file"])


def test_hash_logic_is_called_when_caching_is_enabled(using_temp_config):
    from manim.renderer.cairo_renderer import get_hash_from_play_call

    with patch(
        "manim.renderer.cairo_renderer.get_hash_from_play_call",
        wraps=get_hash_from_play_call,
    ) as mocked:
        scene = SquareToCircle()
        scene.render()
        mocked.assert_called_once()


# Extracted from /Users/hochmax/learn/manim/tests/test_scene_rendering/opengl/test_play_logic_opengl.py
from __future__ import annotations

import sys
from unittest.mock import Mock

import pytest

from manim import *
from manim import config

from ..simple_scenes import (
    SceneForFrozenFrameTests,
    SceneWithMultipleCalls,
    SceneWithNonStaticWait,
    SceneWithSceneUpdater,
    SceneWithStaticWait,
    SquareToCircle,
)


@pytest.mark.skipif(
    sys.version_info < (3, 8),
    reason="Mock object has a different implementation in python 3.7, which makes it broken with this logic.",
)
@pytest.mark.parametrize("frame_rate", argvalues=[15, 30, 60])
def test_t_values(using_temp_opengl_config, disabling_caching, frame_rate):
    """Test that the framerate corresponds to the number of t values generated"""
    config.frame_rate = frame_rate
    scene = SquareToCircle()
    scene.update_to_time = Mock()
    scene.render()
    assert scene.update_to_time.call_count == config["frame_rate"]
    np.testing.assert_allclose(
        ([call.args[0] for call in scene.update_to_time.call_args_list]),
        np.arange(0, 1, 1 / config["frame_rate"]),
    )


@pytest.mark.skipif(
    sys.version_info < (3, 8),
    reason="Mock object has a different implementation in python 3.7, which makes it broken with this logic.",
)
def test_t_values_with_skip_animations(using_temp_opengl_config, disabling_caching):
    """Test the behaviour of scene.skip_animations"""
    scene = SquareToCircle()
    scene.update_to_time = Mock()
    scene.renderer._original_skipping_status = True
    scene.render()
    assert scene.update_to_time.call_count == 1
    np.testing.assert_almost_equal(
        scene.update_to_time.call_args.args[0],
        1.0,
    )


def test_static_wait_detection(using_temp_opengl_config, disabling_caching):
    """Test if a static wait (wait that freeze the frame) is correctly detected"""
    scene = SceneWithStaticWait()
    scene.render()
    # Test is is_static_wait of the Wait animation has been set to True by compile_animation_ata
    assert scene.animations[0].is_static_wait
    assert scene.is_current_animation_frozen_frame()


def test_non_static_wait_detection(using_temp_opengl_config, disabling_caching):
    scene = SceneWithNonStaticWait()
    scene.render()
    assert not scene.animations[0].is_static_wait
    assert not scene.is_current_animation_frozen_frame()
    scene = SceneWithSceneUpdater()
    scene.render()
    assert not scene.animations[0].is_static_wait
    assert not scene.is_current_animation_frozen_frame()


def test_frozen_frame(using_temp_opengl_config, disabling_caching):
    scene = SceneForFrozenFrameTests()
    scene.render()
    assert scene.mobject_update_count == 0
    assert scene.scene_update_count == 0


@pytest.mark.xfail(reason="Should be fixed in #2133")
def test_t_values_with_cached_data(using_temp_opengl_config):
    """Test the proper generation and use of the t values when an animation is cached."""
    scene = SceneWithMultipleCalls()
    # Mocking the file_writer will skip all the writing process.
    scene.renderer.file_writer = Mock(scene.renderer.file_writer)
    # Simulate that all animations are cached.
    scene.renderer.file_writer.is_already_cached.return_value = True
    scene.update_to_time = Mock()

    scene.render()
    assert scene.update_to_time.call_count == 10


@pytest.mark.xfail(reason="Not currently handled correctly for opengl")
def test_t_values_save_last_frame(using_temp_opengl_config):
    """Test that there is only one t value handled when only saving the last frame"""
    config.save_last_frame = True
    scene = SquareToCircle()
    scene.update_to_time = Mock()
    scene.render()
    scene.update_to_time.assert_called_once_with(1)


def test_animate_with_changed_custom_attribute(using_temp_opengl_config):
    """Test that animating the change of a custom attribute
    using the animate syntax works correctly.
    """

    class CustomAnimateScene(Scene):
        def construct(self):
            vt = ValueTracker(0)
            vt.custom_attribute = "hello"
            self.play(vt.animate.set_value(42).set(custom_attribute="world"))
            assert vt.get_value() == 42
            assert vt.custom_attribute == "world"

    CustomAnimateScene().render()


# Extracted from /Users/hochmax/learn/manim/tests/module/utils/test_file_ops.py
from __future__ import annotations

from pathlib import Path

from manim import *
from tests.assert_utils import assert_dir_exists, assert_file_not_exists
from tests.utils.video_tester import *


def test_guarantee_existence(tmp_path: Path):
    test_dir = tmp_path / "test"
    guarantee_existence(test_dir)
    # test if file dir got created
    assert_dir_exists(test_dir)
    with (test_dir / "test.txt").open("x") as f:
        pass
    # test if file didn't get deleted
    guarantee_existence(test_dir)


def test_guarantee_empty_existence(tmp_path: Path):
    test_dir = tmp_path / "test"
    test_dir.mkdir()
    with (test_dir / "test.txt").open("x"):
        pass

    guarantee_empty_existence(test_dir)
    # test if dir got created
    assert_dir_exists(test_dir)
    # test if dir got cleaned
    assert_file_not_exists(test_dir / "test.txt")


# Extracted from /Users/hochmax/learn/manim/tests/module/scene/test_auto_zoom.py
from __future__ import annotations

from manim import *


def test_zoom():
    s1 = Square()
    s1.set_x(-10)
    s2 = Square()
    s2.set_x(10)

    with tempconfig({"dry_run": True, "quality": "low_quality"}):
        scene = MovingCameraScene()
        scene.add(s1, s2)
        scene.play(scene.camera.auto_zoom([s1, s2]))

    assert scene.camera.frame_width == abs(
        s1.get_left()[0] - s2.get_right()[0],
    ) and scene.camera.frame.get_center()[0] == (
        abs(s1.get_center()[0] + s2.get_center()[0]) / 2
    )


# Extracted from /Users/hochmax/learn/manim/tests/module/mobject/svg/test_svg_mobject.py
from __future__ import annotations

from manim import *
from tests.helpers.path_utils import get_svg_resource


def test_set_fill_color():
    expected_color = "#FF862F"
    svg = SVGMobject(get_svg_resource("heart.svg"), fill_color=expected_color)
    assert svg.fill_color.to_hex() == expected_color


def test_set_stroke_color():
    expected_color = "#FFFDDD"
    svg = SVGMobject(get_svg_resource("heart.svg"), stroke_color=expected_color)
    assert svg.stroke_color.to_hex() == expected_color


def test_set_color_sets_fill_and_stroke():
    expected_color = "#EEE777"
    svg = SVGMobject(get_svg_resource("heart.svg"), color=expected_color)
    assert svg.color.to_hex() == expected_color
    assert svg.fill_color.to_hex() == expected_color
    assert svg.stroke_color.to_hex() == expected_color


def test_set_fill_opacity():
    expected_opacity = 0.5
    svg = SVGMobject(get_svg_resource("heart.svg"), fill_opacity=expected_opacity)
    assert svg.fill_opacity == expected_opacity


def test_stroke_opacity():
    expected_opacity = 0.4
    svg = SVGMobject(get_svg_resource("heart.svg"), stroke_opacity=expected_opacity)
    assert svg.stroke_opacity == expected_opacity


def test_fill_overrides_color():
    expected_color = "#343434"
    svg = SVGMobject(
        get_svg_resource("heart.svg"),
        color="#123123",
        fill_color=expected_color,
    )
    assert svg.fill_color.to_hex() == expected_color


def test_stroke_overrides_color():
    expected_color = "#767676"
    svg = SVGMobject(
        get_svg_resource("heart.svg"),
        color="#334433",
        stroke_color=expected_color,
    )
    assert svg.stroke_color.to_hex() == expected_color


def test_single_path_turns_into_sequence_of_points():
    svg = SVGMobject(
        get_svg_resource("cubic_and_lineto.svg"),
    )
    assert len(svg.points) == 0, svg.points
    assert len(svg.submobjects) == 1, svg.submobjects
    path = svg.submobjects[0]
    np.testing.assert_almost_equal(
        path.points,
        np.array(
            [
                [-0.166666666666666, 0.66666666666666, 0.0],
                [-0.166666666666666, 0.0, 0.0],
                [0.5, 0.66666666666666, 0.0],
                [0.5, 0.0, 0.0],
                [0.5, 0.0, 0.0],
                [-0.16666666666666666, 0.0, 0.0],
                [0.5, -0.6666666666666666, 0.0],
                [-0.166666666666666, -0.66666666666666, 0.0],
                [-0.166666666666666, -0.66666666666666, 0.0],
                [-0.27777777777777, -0.77777777777777, 0.0],
                [-0.38888888888888, -0.88888888888888, 0.0],
                [-0.5, -1.0, 0.0],
                [-0.5, -1.0, 0.0],
                [-0.5, -0.333333333333, 0.0],
                [-0.5, 0.3333333333333, 0.0],
                [-0.5, 1.0, 0.0],
                [-0.5, 1.0, 0.0],
                [-0.38888888888888, 0.8888888888888, 0.0],
                [-0.27777777777777, 0.7777777777777, 0.0],
                [-0.16666666666666, 0.6666666666666, 0.0],
            ]
        ),
        decimal=5,
    )


def test_closed_path_does_not_have_extra_point():
    # This dash.svg is the output of a "-" as generated from LaTex.
    # It ends back where it starts, so we shouldn't see a final line.
    svg = SVGMobject(
        get_svg_resource("dash.svg"),
    )
    assert len(svg.points) == 0, svg.points
    assert len(svg.submobjects) == 1, svg.submobjects
    dash = svg.submobjects[0]
    np.testing.assert_almost_equal(
        dash.points,
        np.array(
            [
                [13.524988331417841, -1.0, 0],
                [14.374988080480586, -1.0, 0],
                [15.274984567359079, -1.0, 0],
                [15.274984567359079, 0.0, 0.0],
                [15.274984567359079, 0.0, 0.0],
                [15.274984567359079, 1.0, 0.0],
                [14.374988080480586, 1.0, 0.0],
                [13.524988331417841, 1.0, 0.0],
                [13.524988331417841, 1.0, 0.0],
                [4.508331116720995, 1.0, 0],
                [-4.508326097975995, 1.0, 0.0],
                [-13.524983312672841, 1.0, 0.0],
                [-13.524983312672841, 1.0, 0.0],
                [-14.374983061735586, 1.0, 0.0],
                [-15.274984567359079, 1.0, 0.0],
                [-15.274984567359079, 0.0, 0.0],
                [-15.274984567359079, 0.0, 0.0],
                [-15.274984567359079, -1.0, 0],
                [-14.374983061735586, -1.0, 0],
                [-13.524983312672841, -1.0, 0],
                [-13.524983312672841, -1.0, 0],
                [-4.508326097975995, -1.0, 0],
                [4.508331116720995, -1.0, 0],
                [13.524988331417841, -1.0, 0],
            ]
        ),
        decimal=5,
    )


def test_close_command_closes_last_move_not_the_starting_one():
    # This A.svg is the output of a Text("A") in some systems
    # It contains a path that moves from the outer boundary of the A
    # to the boundary of the inner triangle, anc then closes the path
    # which should close the inner triangle and not the outer boundary.
    svg = SVGMobject(
        get_svg_resource("A.svg"),
    )
    assert len(svg.points) == 0, svg.points
    assert len(svg.submobjects) == 1, svg.submobjects
    capital_A = svg.submobjects[0]

    # The last point should not be the same as the first point
    assert not all(capital_A.points[0] == capital_A.points[-1])
    np.testing.assert_almost_equal(
        capital_A.points,
        np.array(
            [
                [-0.8380339075214888, -1.0, 1.2246467991473532e-16],
                [-0.6132152047642527, -0.3333333333333336, 4.082155997157847e-17],
                [-0.388396502007016, 0.3333333333333336, -4.082155997157847e-17],
                [-0.16357779924977994, 1.0, -1.2246467991473532e-16],
                [-0.16357779924977994, 1.0, -1.2246467991473532e-16],
                [-0.05425733591657368, 1.0, -1.2246467991473532e-16],
                [0.05506312741663405, 1.0, -1.2246467991473532e-16],
                [0.16438359074984032, 1.0, -1.2246467991473532e-16],
                [0.16438359074984032, 1.0, -1.2246467991473532e-16],
                [0.3889336963403905, 0.3333333333333336, -4.082155997157847e-17],
                [0.6134838019309422, -0.3333333333333336, 4.082155997157847e-17],
                [0.8380339075214923, -1.0, 1.2246467991473532e-16],
                [0.8380339075214923, -1.0, 1.2246467991473532e-16],
                [0.744560897060354, -1.0, 1.2246467991473532e-16],
                [0.6510878865992157, -1.0, 1.2246467991473532e-16],
                [0.5576148761380774, -1.0, 1.2246467991473532e-16],
                [0.5576148761380774, -1.0, 1.2246467991473532e-16],
                [0.49717968849274957, -0.8138597980824822, 9.966907966764229e-17],
                [0.4367445008474217, -0.6277195961649644, 7.687347942054928e-17],
                [0.3763093132020939, -0.4415793942474466, 5.407787917345625e-17],
                [0.3763093132020939, -0.4415793942474466, 5.407787917345625e-17],
                [0.12167600863867864, -0.4415793942474466, 5.407787917345625e-17],
                [-0.13295729592473662, -0.4415793942474466, 5.407787917345625e-17],
                [-0.38759060048815186, -0.4415793942474466, 5.407787917345625e-17],
                [-0.38759060048815186, -0.4415793942474466, 5.407787917345625e-17],
                [-0.4480257881334797, -0.6277195961649644, 7.687347942054928e-17],
                [-0.5084609757788076, -0.8138597980824822, 9.966907966764229e-17],
                [-0.5688961634241354, -1.0, 1.2246467991473532e-16],
                [-0.5688961634241354, -1.0, 1.2246467991473532e-16],
                [-0.6586087447899202, -1.0, 1.2246467991473532e-16],
                [-0.7483213261557048, -1.0, 1.2246467991473532e-16],
                [-0.8380339075214888, -1.0, 1.2246467991473532e-16],
                [0.3021757525699033, -0.21434317946653003, 2.6249468865275272e-17],
                [0.1993017037512583, 0.09991949373745423, -1.2236608817799732e-17],
                [0.09642765493261184, 0.4141821669414385, -5.072268650087473e-17],
                [-0.006446393886033166, 0.7284448401454228, -8.920876418394973e-17],
                [-0.006446393886033166, 0.7284448401454228, -8.920876418394973e-17],
                [-0.10905185929034443, 0.4141821669414385, -5.072268650087473e-17],
                [-0.2116573246946542, 0.09991949373745423, -1.2236608817799732e-17],
                [-0.31426279009896546, -0.21434317946653003, 2.6249468865275272e-17],
                [-0.31426279009896546, -0.21434317946653003, 2.6249468865275272e-17],
                [-0.10878327587600921, -0.21434317946653003, 2.6249468865275272e-17],
                [0.09669623834694704, -0.21434317946653003, 2.6249468865275272e-17],
                [0.3021757525699033, -0.21434317946653003, 2.6249468865275272e-17],
            ]
        ),
        decimal=5,
    )


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_opengl.py
from __future__ import annotations

from manim import *
from manim.renderer.opengl_renderer import OpenGLRenderer
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "opengl"


@frames_comparison(renderer_class=OpenGLRenderer, renderer="opengl")
def test_Circle(scene):
    circle = Circle().set_color(RED)
    scene.add(circle)
    scene.wait()


@frames_comparison(
    renderer_class=OpenGLRenderer,
    renderer="opengl",
)
def test_FixedMobjects3D(scene: Scene):
    scene.renderer.camera.set_euler_angles(phi=75 * DEGREES, theta=-45 * DEGREES)
    circ = Circle(fill_opacity=1).to_edge(LEFT)
    square = Square(fill_opacity=1).to_edge(RIGHT)
    triangle = Triangle(fill_opacity=1).to_corner(UR)
    [i.fix_orientation() for i in (circ, square)]
    triangle.fix_in_frame()


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_indication.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "indication"


@frames_comparison(last_frame=False)
def test_FocusOn(scene):
    square = Square()
    scene.add(square)
    scene.play(FocusOn(square))


@frames_comparison(last_frame=False)
def test_Indicate(scene):
    square = Square()
    scene.add(square)
    scene.play(Indicate(square))


@frames_comparison(last_frame=False)
def test_Flash(scene):
    square = Square()
    scene.add(square)
    scene.play(Flash(ORIGIN))


@frames_comparison(last_frame=False)
def test_Circumscribe(scene):
    square = Square()
    scene.add(square)
    scene.play(Circumscribe(square))
    scene.wait()


@frames_comparison(last_frame=False)
def test_ShowPassingFlash(scene):
    square = Square()
    scene.add(square)
    scene.play(ShowPassingFlash(square.copy()))


@frames_comparison(last_frame=False)
def test_ApplyWave(scene):
    square = Square()
    scene.add(square)
    scene.play(ApplyWave(square))


@frames_comparison(last_frame=False)
def test_Wiggle(scene):
    square = Square()
    scene.add(square)
    scene.play(Wiggle(square))


def test_Wiggle_custom_about_points():
    square = Square()
    wiggle = Wiggle(
        square,
        scale_about_point=[1.0, 2.0, 3.0],
        rotate_about_point=[4.0, 5.0, 6.0],
    )
    assert wiggle.get_scale_about_point() == [1.0, 2.0, 3.0]
    assert wiggle.get_rotate_about_point() == [4.0, 5.0, 6.0]


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_coordinate_systems.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "coordinate_system"


@frames_comparison
def test_number_plane(scene):
    plane = NumberPlane(
        x_range=[-4, 6, 1],
        axis_config={"include_numbers": True},
        x_axis_config={"unit_size": 1.2},
        y_range=[-2, 5],
        y_length=6,
        y_axis_config={"label_direction": UL},
    )

    scene.add(plane)


@frames_comparison
def test_line_graph(scene):
    plane = NumberPlane()
    first_line = plane.plot_line_graph(
        x_values=[-3, 1],
        y_values=[-2, 2],
        line_color=YELLOW,
    )
    second_line = plane.plot_line_graph(
        x_values=[0, 2, 2, 4],
        y_values=[0, 0, 2, 4],
        line_color=RED,
    )

    scene.add(plane, first_line, second_line)


@frames_comparison(base_scene=ThreeDScene)
def test_plot_surface(scene):
    axes = ThreeDAxes(x_range=(-5, 5, 1), y_range=(-5, 5, 1), z_range=(-5, 5, 1))

    def param_trig(u, v):
        x = u
        y = v
        z = 2 * np.sin(x) + 2 * np.cos(y)
        return z

    trig_plane = axes.plot_surface(
        param_trig,
        u_range=(-5, 5),
        v_range=(-5, 5),
        color=BLUE,
    )

    scene.add(axes, trig_plane)


@frames_comparison(base_scene=ThreeDScene)
def test_plot_surface_colorscale(scene):
    axes = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), z_range=(-5, 5, 1))

    def param_trig(u, v):
        x = u
        y = v
        z = 2 * np.sin(x) + 2 * np.cos(y)
        return z

    trig_plane = axes.plot_surface(
        param_trig,
        u_range=(-3, 3),
        v_range=(-3, 3),
        colorscale=[BLUE, GREEN, YELLOW, ORANGE, RED],
    )

    scene.add(axes, trig_plane)


@frames_comparison
def test_implicit_graph(scene):
    ax = Axes()
    graph = ax.plot_implicit_curve(lambda x, y: x**2 + y**2 - 4)
    scene.add(ax, graph)


@frames_comparison
def test_plot_log_x_axis(scene):
    ax = Axes(
        x_range=[-1, 4],
        y_range=[0, 3],
        x_axis_config={"scaling": LogBase()},
    )

    graph = ax.plot(lambda x: 2 if x < 10 else 1, x_range=[-1, 4])
    scene.add(ax, graph)


@frames_comparison
def test_plot_log_x_axis_vectorized(scene):
    ax = Axes(
        x_range=[-1, 4],
        y_range=[0, 3],
        x_axis_config={"scaling": LogBase()},
    )

    graph = ax.plot(
        lambda x: np.where(x < 10, 2, 1), x_range=[-1, 4], use_vectorized=True
    )
    scene.add(ax, graph)


@frames_comparison
def test_number_plane_log(scene):
    """Test that NumberPlane generates its lines properly with a LogBase"""
    # y_axis log
    plane1 = (
        NumberPlane(
            x_range=[0, 8, 1],
            y_range=[-2, 5],
            y_length=6,
            x_length=10,
            y_axis_config={"scaling": LogBase()},
        )
        .add_coordinates()
        .scale(1 / 2)
    )

    # x_axis log
    plane2 = (
        NumberPlane(
            x_range=[0, 8, 1],
            y_range=[-2, 5],
            y_length=6,
            x_length=10,
            x_axis_config={"scaling": LogBase()},
            faded_line_ratio=4,
        )
        .add_coordinates()
        .scale(1 / 2)
    )

    scene.add(VGroup(plane1, plane2).arrange())


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_transform.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "transform"


@frames_comparison(last_frame=False)
def test_Transform(scene):
    square = Square()
    circle = Circle()
    scene.play(Transform(square, circle))


@frames_comparison(last_frame=False)
def test_TransformFromCopy(scene):
    square = Square()
    circle = Circle()
    scene.play(TransformFromCopy(square, circle))


@frames_comparison(last_frame=False)
def test_FullRotation(scene):
    s = VGroup(*(Square() for _ in range(4))).arrange()
    scene.play(
        Rotate(s[0], -2 * TAU),
        Rotate(s[1], -1 * TAU),
        Rotate(s[2], 1 * TAU),
        Rotate(s[3], 2 * TAU),
    )


@frames_comparison(last_frame=False)
def test_ClockwiseTransform(scene):
    square = Square()
    circle = Circle()
    scene.play(ClockwiseTransform(square, circle))


@frames_comparison(last_frame=False)
def test_CounterclockwiseTransform(scene):
    square = Square()
    circle = Circle()
    scene.play(CounterclockwiseTransform(square, circle))


@frames_comparison(last_frame=False)
def test_MoveToTarget(scene):
    square = Square()
    square.generate_target()
    square.target.shift(3 * UP)
    scene.play(MoveToTarget(square))


@frames_comparison(last_frame=False)
def test_ApplyPointwiseFunction(scene):
    square = Square()

    def func(p):
        return np.array([1.0, 1.0, 0.0])

    scene.play(ApplyPointwiseFunction(func, square))


@frames_comparison(last_frame=False)
def test_FadeToColort(scene):
    square = Square()
    scene.play(FadeToColor(square, RED))


@frames_comparison(last_frame=False)
def test_ScaleInPlace(scene):
    square = Square()
    scene.play(ScaleInPlace(square, scale_factor=0.1))


@frames_comparison(last_frame=False)
def test_ShrinkToCenter(scene):
    square = Square()
    scene.play(ShrinkToCenter(square))


@frames_comparison(last_frame=False)
def test_Restore(scene):
    square = Square()
    circle = Circle()
    scene.play(Transform(square, circle))
    square.save_state()
    scene.play(square.animate.shift(UP))
    scene.play(Restore(square))


@frames_comparison
def test_ApplyFunction(scene):
    square = Square()
    scene.add(square)

    def apply_function(mob):
        mob.scale(2)
        mob.to_corner(UR)
        mob.rotate(PI / 4)
        mob.set_color(RED)
        return mob

    scene.play(ApplyFunction(apply_function, square))


@frames_comparison(last_frame=False)
def test_ApplyComplexFunction(scene):
    square = Square()
    scene.play(
        ApplyComplexFunction(
            lambda complex_num: complex_num + 2 * complex(0, 1),
            square,
        ),
    )


@frames_comparison(last_frame=False)
def test_ApplyMatrix(scene):
    square = Square()
    matrice = [[1.0, 0.5], [1.0, 0.0]]
    about_point = np.asarray((-10.0, 5.0, 0.0))
    scene.play(ApplyMatrix(matrice, square, about_point))


@frames_comparison(last_frame=False)
def test_CyclicReplace(scene):
    square = Square()
    circle = Circle()
    circle.shift(3 * UP)
    scene.play(CyclicReplace(square, circle))


@frames_comparison(last_frame=False)
def test_FadeInAndOut(scene):
    square = Square(color=BLUE).shift(2 * UP)
    annotation = Square(color=BLUE)
    scene.add(annotation)
    scene.play(FadeIn(square))

    annotation.become(Square(color=RED).rotate(PI / 4))
    scene.add(annotation)
    scene.play(FadeOut(square))


@frames_comparison
def test_MatchPointsScene(scene):
    circ = Circle(fill_color=RED, fill_opacity=0.8)
    square = Square(fill_color=BLUE, fill_opacity=0.2)
    scene.play(circ.animate.match_points(square))


@frames_comparison(last_frame=False)
def test_AnimationBuilder(scene):
    scene.play(Square().animate.shift(RIGHT).rotate(PI / 4))


@frames_comparison(last_frame=False)
def test_ReplacementTransform(scene):
    yellow = Square(fill_opacity=1.0, fill_color=YELLOW)
    yellow.move_to([0, 0.75, 0])

    green = Square(fill_opacity=1.0, fill_color=GREEN)
    green.move_to([-0.75, 0, 0])

    blue = Square(fill_opacity=1.0, fill_color=BLUE)
    blue.move_to([0.75, 0, 0])

    orange = Square(fill_opacity=1.0, fill_color=ORANGE)
    orange.move_to([0, -0.75, 0])

    scene.add(yellow)
    scene.add(VGroup(green, blue))
    scene.add(orange)

    purple = Circle(fill_opacity=1.0, fill_color=PURPLE)
    purple.move_to(green)

    scene.play(ReplacementTransform(green, purple))
    # This pause is important to verify the purple circle remains behind
    # the blue and orange squares, and the blue square remains behind the
    # orange square after the transform fully completes.
    scene.pause()


@frames_comparison(last_frame=False)
def test_TransformWithPathFunc(scene):
    dots_start = VGroup(*[Dot(LEFT, color=BLUE), Dot(3 * RIGHT, color=RED)])
    dots_end = VGroup(*[Dot(LEFT + 2 * DOWN, color=BLUE), Dot(2 * UP, color=RED)])
    scene.play(Transform(dots_start, dots_end, path_func=clockwise_path()))


@frames_comparison(last_frame=False)
def test_TransformWithPathArcCenters(scene):
    dots_start = VGroup(*[Dot(LEFT, color=BLUE), Dot(3 * RIGHT, color=RED)])
    dots_end = VGroup(*[Dot(LEFT + 2 * DOWN, color=BLUE), Dot(2 * UP, color=RED)])
    scene.play(
        Transform(
            dots_start,
            dots_end,
            path_arc=2 * PI,
            path_arc_centers=ORIGIN,
        )
    )


@frames_comparison(last_frame=False)
def test_TransformWithConflictingPaths(scene):
    dots_start = VGroup(*[Dot(LEFT, color=BLUE), Dot(3 * RIGHT, color=RED)])
    dots_end = VGroup(*[Dot(LEFT + 2 * DOWN, color=BLUE), Dot(2 * UP, color=RED)])
    scene.play(
        Transform(
            dots_start,
            dots_end,
            path_func=clockwise_path(),
            path_arc=2 * PI,
            path_arc_centers=ORIGIN,
        )
    )


@frames_comparison(last_frame=False)
def test_FadeTransformPieces(scene):
    src = VGroup(Square(), Circle().shift(LEFT + UP))
    src.shift(3 * LEFT)

    target = VGroup(Circle(), Triangle().shift(RIGHT + DOWN))
    target.shift(3 * RIGHT)

    scene.add(src)
    scene.play(FadeTransformPieces(src, target))


@frames_comparison(last_frame=False)
def test_FadeTransform(scene):
    src = Square(fill_opacity=1.0)
    src.shift(3 * LEFT)

    target = Circle(fill_opacity=1.0, color=ORANGE)
    target.shift(3 * RIGHT)

    scene.add(src)
    scene.play(FadeTransform(src, target))


@frames_comparison(last_frame=False)
def test_FadeTransform_TargetIsEmpty_FadesOutInPlace(scene):
    # https://github.com/ManimCommunity/manim/issues/2845
    src = Square(fill_opacity=1.0)
    src.shift(3 * LEFT)

    target = VGroup()
    target.shift(3 * RIGHT)

    scene.add(src)
    scene.play(FadeTransform(src, target))


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_mobjects.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "mobjects"


@frames_comparison(base_scene=ThreeDScene)
def test_PointCloudDot(scene):
    p = PointCloudDot()
    scene.add(p)


@frames_comparison
def test_become(scene):
    s = Rectangle(width=2, height=1, color=RED).shift(UP)
    d = Dot()

    s1 = s.copy().become(d, match_width=True).set_opacity(0.25).set_color(BLUE)
    s2 = (
        s.copy()
        .become(d, match_height=True, match_center=True)
        .set_opacity(0.25)
        .set_color(GREEN)
    )
    s3 = s.copy().become(d, stretch=True).set_opacity(0.25).set_color(YELLOW)

    scene.add(s, d, s1, s2, s3)


@frames_comparison
def test_become_no_color_linking(scene):
    a = Circle()
    b = Square()
    scene.add(a)
    scene.add(b)
    b.become(a)
    b.shift(1 * RIGHT)
    b.set_stroke(YELLOW, opacity=1)


@frames_comparison
def test_match_style(scene):
    square = Square(fill_color=[RED, GREEN], fill_opacity=1)
    circle = Circle()
    VGroup(square, circle).arrange()
    circle.match_style(square)
    scene.add(square, circle)


@frames_comparison
def test_vmobject_joint_types(scene):
    angled_line = VMobject(stroke_width=20, color=GREEN).set_points_as_corners(
        [
            np.array([-2, 0, 0]),
            np.array([0, 0, 0]),
            np.array([-2, 1, 0]),
        ]
    )
    lines = VGroup(*[angled_line.copy() for _ in range(len(LineJointType))])
    for line, joint_type in zip(lines, LineJointType):
        line.joint_type = joint_type

    lines.arrange(RIGHT, buff=1)
    scene.add(lines)


@frames_comparison
def test_vmobject_cap_styles(scene):
    arcs = VGroup(
        *[
            Arc(
                radius=1,
                start_angle=0,
                angle=TAU / 4,
                stroke_width=20,
                color=GREEN,
                cap_style=cap_style,
            )
            for cap_style in CapStyleType
        ]
    )
    arcs.arrange(RIGHT, buff=1)
    scene.add(arcs)


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_modifier_methods.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "modifier_methods"


@frames_comparison
def test_Gradient(scene):
    c = Circle(fill_opacity=1).set_color(color=[YELLOW, GREEN])
    scene.add(c)


@frames_comparison
def test_GradientRotation(scene):
    c = Circle(fill_opacity=1).set_color(color=[YELLOW, GREEN]).rotate(PI)
    scene.add(c)


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_tables.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "tables"


@frames_comparison
def test_Table(scene):
    t = Table(
        [["1", "2"], ["3", "4"]],
        row_labels=[Tex("R1"), Tex("R2")],
        col_labels=[Tex("C1"), Tex("C2")],
        top_left_entry=MathTex("TOP"),
        element_to_mobject=Tex,
        include_outer_lines=True,
    )
    scene.add(t)


@frames_comparison
def test_MathTable(scene):
    t = MathTable([[1, 2], [3, 4]])
    scene.add(t)


@frames_comparison
def test_MobjectTable(scene):
    a = Circle().scale(0.5)
    t = MobjectTable([[a.copy(), a.copy()], [a.copy(), a.copy()]])
    scene.add(t)


@frames_comparison
def test_IntegerTable(scene):
    t = IntegerTable(
        np.arange(1, 21).reshape(5, 4),
    )
    scene.add(t)


@frames_comparison
def test_DecimalTable(scene):
    t = DecimalTable(
        np.linspace(0, 0.9, 20).reshape(5, 4),
    )
    scene.add(t)


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_numbers.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "numbers"


@frames_comparison(last_frame=False)
def test_set_value_with_updaters(scene):
    """Test that the position of the decimal updates properly"""
    decimal = DecimalNumber(
        0,
        show_ellipsis=True,
        num_decimal_places=3,
        include_sign=True,
    )
    square = Square().to_edge(UP)

    decimal.add_updater(lambda d: d.next_to(square, RIGHT))
    decimal.add_updater(lambda d: d.set_value(square.get_center()[1]))
    scene.add(square, decimal)
    scene.play(
        square.animate.to_edge(DOWN),
        rate_func=there_and_back,
    )


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_img_and_svg.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

from ..helpers.path_utils import get_svg_resource

__module_test__ = "img_and_svg"

# Tests break down into two kinds: one where the SVG is simple enough to step through
# and ones where the SVG is realistically complex, and the output should be visually inspected.

# First are the simple tests.


@frames_comparison
def test_Line(scene):
    line_demo = SVGMobject(get_svg_resource("line.svg"))
    scene.add(line_demo)
    scene.wait()


@frames_comparison
def test_CubicPath(scene):
    cubic_demo = SVGMobject(get_svg_resource("cubic_demo.svg"))
    scene.add(cubic_demo)
    scene.wait()


@frames_comparison
def test_CubicAndLineto(scene):
    cubic_lineto = SVGMobject(get_svg_resource("cubic_and_lineto.svg"))
    scene.add(cubic_lineto)
    scene.wait()


@frames_comparison
def test_Rhomboid(scene):
    rhomboid = SVGMobject(get_svg_resource("rhomboid.svg")).scale(0.5)
    rhomboid_fill = rhomboid.copy().set_fill(opacity=1).shift(UP * 2)
    rhomboid_no_fill = rhomboid.copy().set_fill(opacity=0).shift(DOWN * 2)
    scene.add(rhomboid, rhomboid_fill, rhomboid_no_fill)
    scene.wait()


@frames_comparison
def test_Inheritance(scene):
    three_arrows = SVGMobject(get_svg_resource("inheritance_test.svg")).scale(0.5)
    scene.add(three_arrows)
    scene.wait()


@frames_comparison
def test_MultiPartPath(scene):
    mpp = SVGMobject(get_svg_resource("multi_part_path.svg"))
    scene.add(mpp)
    scene.wait()


@frames_comparison
def test_QuadraticPath(scene):
    quad = SVGMobject(get_svg_resource("qcurve_demo.svg"))
    scene.add(quad)
    scene.wait()


@frames_comparison
def test_SmoothCurves(scene):
    smooths = SVGMobject(get_svg_resource("smooth_curves.svg"))
    scene.add(smooths)
    scene.wait()


@frames_comparison
def test_WatchTheDecimals(scene):
    def construct(scene):
        decimal = SVGMobject(get_svg_resource("watch_the_decimals.svg"))
        scene.add(decimal)
        scene.wait()


@frames_comparison
def test_UseTagInheritance(scene):
    aabbb = SVGMobject(get_svg_resource("aabbb.svg"))
    scene.add(aabbb)
    scene.wait()


@frames_comparison
def test_HalfEllipse(scene):
    half_ellipse = SVGMobject(get_svg_resource("half_ellipse.svg"))
    scene.add(half_ellipse)
    scene.wait()


@frames_comparison
def test_Heart(scene):
    heart = SVGMobject(get_svg_resource("heart.svg"))
    scene.add(heart)
    scene.wait()


@frames_comparison
def test_Arcs01(scene):
    # See: https://www.w3.org/TR/SVG11/images/paths/arcs01.svg
    arcs = SVGMobject(get_svg_resource("arcs01.svg"))
    scene.add(arcs)
    scene.wait()


@frames_comparison(last_frame=False)
def test_Arcs02(scene):
    # See: https://www.w3.org/TR/SVG11/images/paths/arcs02.svg
    arcs = SVGMobject(get_svg_resource("arcs02.svg"))
    scene.add(arcs)
    scene.wait()


# Second are the visual tests - these are probably too complex to verify step-by-step, so
# these are really more of a spot-check


@frames_comparison(last_frame=False)
def test_WeightSVG(scene):
    path = get_svg_resource("weight.svg")
    svg_obj = SVGMobject(path)
    scene.add(svg_obj)
    scene.wait()


@frames_comparison
def test_BrachistochroneCurve(scene):
    brach_curve = SVGMobject(get_svg_resource("curve.svg"))
    scene.add(brach_curve)
    scene.wait()


@frames_comparison
def test_DesmosGraph1(scene):
    dgraph = SVGMobject(get_svg_resource("desmos-graph_1.svg")).scale(3)
    scene.add(dgraph)
    scene.wait()


@frames_comparison
def test_Penrose(scene):
    penrose = SVGMobject(get_svg_resource("penrose.svg"))
    scene.add(penrose)
    scene.wait()


@frames_comparison
def test_ManimLogo(scene):
    background_rect = Rectangle(color=WHITE, fill_opacity=1).scale(2)
    manim_logo = SVGMobject(get_svg_resource("manim-logo-sidebar.svg"))
    scene.add(background_rect, manim_logo)
    scene.wait()


@frames_comparison
def test_UKFlag(scene):
    uk_flag = SVGMobject(get_svg_resource("united-kingdom.svg"))
    scene.add(uk_flag)
    scene.wait()


@frames_comparison
def test_SingleUSState(scene):
    single_state = SVGMobject(get_svg_resource("single_state.svg"))
    scene.add(single_state)
    scene.wait()


@frames_comparison
def test_ContiguousUSMap(scene):
    states = SVGMobject(get_svg_resource("states_map.svg")).scale(3)
    scene.add(states)
    scene.wait()


@frames_comparison
def test_PixelizedText(scene):
    background_rect = Rectangle(color=WHITE, fill_opacity=1).scale(2)
    rgb_svg = SVGMobject(get_svg_resource("pixelated_text.svg"))
    scene.add(background_rect, rgb_svg)
    scene.wait()


@frames_comparison
def test_VideoIcon(scene):
    video_icon = SVGMobject(get_svg_resource("video_icon.svg"))
    scene.add(video_icon)
    scene.wait()


@frames_comparison
def test_MultipleTransform(scene):
    svg_obj = SVGMobject(get_svg_resource("multiple_transforms.svg"))
    scene.add(svg_obj)
    scene.wait()


@frames_comparison
def test_MatrixTransform(scene):
    svg_obj = SVGMobject(get_svg_resource("matrix.svg"))
    scene.add(svg_obj)
    scene.wait()


@frames_comparison
def test_ScaleTransform(scene):
    svg_obj = SVGMobject(get_svg_resource("scale.svg"))
    scene.add(svg_obj)
    scene.wait()


@frames_comparison
def test_TranslateTransform(scene):
    svg_obj = SVGMobject(get_svg_resource("translate.svg"))
    scene.add(svg_obj)
    scene.wait()


@frames_comparison
def test_SkewXTransform(scene):
    svg_obj = SVGMobject(get_svg_resource("skewX.svg"))
    scene.add(svg_obj)
    scene.wait()


@frames_comparison
def test_SkewYTransform(scene):
    svg_obj = SVGMobject(get_svg_resource("skewY.svg"))
    scene.add(svg_obj)
    scene.wait()


@frames_comparison
def test_RotateTransform(scene):
    svg_obj = SVGMobject(get_svg_resource("rotate.svg"))
    scene.add(svg_obj)
    scene.wait()


@frames_comparison
def test_path_multiple_moves(scene):
    svg_obj = SVGMobject(
        get_svg_resource("path_multiple_moves.svg"),
        fill_color=WHITE,
        stroke_color=WHITE,
        stroke_width=3,
    )
    scene.add(svg_obj)


@frames_comparison
def test_ImageMobject(scene):
    file_path = get_svg_resource("tree_img_640x351.png")
    im1 = ImageMobject(file_path).shift(4 * LEFT + UP)
    im2 = ImageMobject(file_path, scale_to_resolution=1080).shift(4 * LEFT + 2 * DOWN)
    im3 = ImageMobject(file_path, scale_to_resolution=540).shift(4 * RIGHT)
    scene.add(im1, im2, im3)
    scene.wait(1)


@frames_comparison
def test_ImageInterpolation(scene):
    img = ImageMobject(
        np.uint8([[63, 0, 0, 0], [0, 127, 0, 0], [0, 0, 191, 0], [0, 0, 0, 255]]),
    )
    img.height = 2
    img1 = img.copy()
    img2 = img.copy()
    img3 = img.copy()
    img4 = img.copy()
    img5 = img.copy()

    img1.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    img2.set_resampling_algorithm(RESAMPLING_ALGORITHMS["lanczos"])
    img3.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])
    img4.set_resampling_algorithm(RESAMPLING_ALGORITHMS["cubic"])
    img5.set_resampling_algorithm(RESAMPLING_ALGORITHMS["box"])

    scene.add(img1, img2, img3, img4, img5)
    [s.shift(4 * LEFT + pos * 2 * RIGHT) for pos, s in enumerate(scene.mobjects)]
    scene.wait()


def test_ImageMobject_points_length():
    file_path = get_svg_resource("tree_img_640x351.png")
    im1 = ImageMobject(file_path)
    assert len(im1.points) == 4


def test_ImageMobject_rotation():
    # see https://github.com/ManimCommunity/manim/issues/3067
    # rotating an image to and from the same angle should not change the image
    file_path = get_svg_resource("tree_img_640x351.png")
    im1 = ImageMobject(file_path)
    im2 = im1.copy()
    im1.rotate(PI / 2)
    im1.rotate(-PI / 2)
    np.testing.assert_array_equal(im1.points, im2.points)


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_polyhedra.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "polyhedra"


@frames_comparison
def test_Tetrahedron(scene):
    scene.add(Tetrahedron())


@frames_comparison
def test_Octahedron(scene):
    scene.add(Octahedron())


@frames_comparison
def test_Icosahedron(scene):
    scene.add(Icosahedron())


@frames_comparison
def test_Dodecahedron(scene):
    scene.add(Dodecahedron())


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_creation.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "creation"


@frames_comparison(last_frame=False)
def test_create(scene):
    square = Square()
    scene.play(Create(square))


@frames_comparison(last_frame=False)
def test_uncreate(scene):
    square = Square()
    scene.add(square)
    scene.play(Uncreate(square))


@frames_comparison(last_frame=False)
def test_uncreate_rate_func(scene):
    square = Square()
    scene.add(square)
    scene.play(Uncreate(square), rate_func=linear)


@frames_comparison(last_frame=False)
def test_DrawBorderThenFill(scene):
    square = Square(fill_opacity=1)
    scene.play(DrawBorderThenFill(square))


# NOTE : Here should be the Write Test. But for some reasons it appears that this function is untestable (see issue #157)
@frames_comparison(last_frame=False)
def test_FadeOut(scene):
    square = Square()
    scene.add(square)
    scene.play(FadeOut(square))


@frames_comparison(last_frame=False)
def test_FadeIn(scene):
    square = Square()
    scene.play(FadeIn(square))


@frames_comparison(last_frame=False)
def test_GrowFromPoint(scene):
    square = Square()
    scene.play(GrowFromPoint(square, np.array((1, 1, 0))))


@frames_comparison(last_frame=False)
def test_GrowFromCenter(scene):
    square = Square()
    scene.play(GrowFromCenter(square))


@frames_comparison(last_frame=False)
def test_GrowFromEdge(scene):
    square = Square()
    scene.play(GrowFromEdge(square, DOWN))


@frames_comparison(last_frame=False)
def test_SpinInFromNothing(scene):
    square = Square()
    scene.play(SpinInFromNothing(square))


@frames_comparison(last_frame=False)
def test_ShrinkToCenter(scene):
    square = Square()
    scene.play(ShrinkToCenter(square))


@frames_comparison(last_frame=False)
def test_bring_to_back_introducer(scene):
    a = Square(color=RED, fill_opacity=1)
    b = Square(color=BLUE, fill_opacity=1).shift(RIGHT)
    scene.add(a)
    scene.bring_to_back(b)
    scene.play(FadeIn(b))
    scene.wait()


@frames_comparison(last_frame=False)
def test_z_index_introducer(scene):
    a = Circle().set_fill(color=RED, opacity=1.0)
    scene.add(a)
    b = Circle(arc_center=(0.5, 0.5, 0.0), color=GREEN, fill_opacity=1)
    b.set_z_index(-1)
    scene.play(Create(b))
    scene.wait()


@frames_comparison(last_frame=False)
def test_SpiralIn(scene):
    circle = Circle().shift(LEFT)
    square = Square().shift(UP)
    shapes = VGroup(circle, square)
    scene.play(SpiralIn(shapes))


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_composition.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "composition"


@frames_comparison
def test_animationgroup_is_passing_remover_to_animations(scene):
    animation_group = AnimationGroup(Create(Square()), Write(Circle()), remover=True)

    scene.play(animation_group)
    scene.wait(0.1)


@frames_comparison
def test_animationgroup_is_passing_remover_to_nested_animationgroups(scene):
    animation_group = AnimationGroup(
        AnimationGroup(Create(Square()), Create(RegularPolygon(5))),
        Write(Circle(), remover=True),
        remover=True,
    )

    scene.play(animation_group)
    scene.wait(0.1)


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_threed.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "threed"


@frames_comparison(base_scene=ThreeDScene)
def test_AddFixedInFrameMobjects(scene):
    scene.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
    text = Tex("This is a 3D tex")
    scene.add_fixed_in_frame_mobjects(text)


@frames_comparison(base_scene=ThreeDScene)
def test_Cube(scene):
    scene.add(Cube())


@frames_comparison(base_scene=ThreeDScene)
def test_Sphere(scene):
    scene.add(Sphere())


@frames_comparison(base_scene=ThreeDScene)
def test_Dot3D(scene):
    scene.add(Dot3D())


@frames_comparison(base_scene=ThreeDScene)
def test_Cone(scene):
    scene.add(Cone(resolution=16))


@frames_comparison(base_scene=ThreeDScene)
def test_Cylinder(scene):
    scene.add(Cylinder())


@frames_comparison(base_scene=ThreeDScene)
def test_Line3D(scene):
    line1 = Line3D(resolution=16).shift(LEFT * 2)
    line2 = Line3D(resolution=16).shift(RIGHT * 2)
    perp_line = Line3D.perpendicular_to(line1, UP + OUT, resolution=16)
    parallel_line = Line3D.parallel_to(line2, DOWN + IN, resolution=16)
    scene.add(line1, line2, perp_line, parallel_line)


@frames_comparison(base_scene=ThreeDScene)
def test_Arrow3D(scene):
    scene.add(Arrow3D(resolution=16))


@frames_comparison(base_scene=ThreeDScene)
def test_Torus(scene):
    scene.add(Torus())


@frames_comparison(base_scene=ThreeDScene)
def test_Axes(scene):
    scene.add(ThreeDAxes())


@frames_comparison(base_scene=ThreeDScene)
def test_CameraMoveAxes(scene):
    """Tests camera movement to explore varied views of a static scene."""
    axes = ThreeDAxes()
    scene.add(axes)
    scene.add(Dot([1, 2, 3]))
    scene.move_camera(phi=PI / 8, theta=-PI / 8, frame_center=[1, 2, 3], zoom=2)


@frames_comparison(base_scene=ThreeDScene)
def test_CameraMove(scene):
    cube = Cube()
    scene.add(cube)
    scene.move_camera(phi=PI / 4, theta=PI / 4, frame_center=[0, 0, -1], zoom=0.5)


@frames_comparison(base_scene=ThreeDScene)
def test_AmbientCameraMove(scene):
    cube = Cube()
    scene.begin_ambient_camera_rotation(rate=0.5)
    scene.add(cube)
    scene.wait()


@frames_comparison(base_scene=ThreeDScene)
def test_MovingVertices(scene):
    scene.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
    vertices = [1, 2, 3, 4]
    edges = [(1, 2), (2, 3), (3, 4), (1, 3), (1, 4)]
    g = Graph(vertices, edges)
    scene.add(g)
    scene.play(
        g[1].animate.move_to([1, 1, 1]),
        g[2].animate.move_to([-1, 1, 2]),
        g[3].animate.move_to([1, -1, -1]),
        g[4].animate.move_to([-1, -1, 0]),
    )
    scene.wait()


@frames_comparison(base_scene=ThreeDScene)
def test_SurfaceColorscale(scene):
    resolution_fa = 16
    scene.set_camera_orientation(phi=75 * DEGREES, theta=-30 * DEGREES)
    axes = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), z_range=(-4, 4, 1))

    def param_trig(u, v):
        x = u
        y = v
        z = y**2 / 2 - x**2 / 2
        return z

    trig_plane = Surface(
        lambda x, y: axes.c2p(x, y, param_trig(x, y)),
        resolution=(resolution_fa, resolution_fa),
        v_range=[-3, 3],
        u_range=[-3, 3],
    )
    trig_plane.set_fill_by_value(
        axes=axes, colorscale=[BLUE, GREEN, YELLOW, ORANGE, RED]
    )
    scene.add(axes, trig_plane)


@frames_comparison(base_scene=ThreeDScene)
def test_Y_Direction(scene):
    resolution_fa = 16
    scene.set_camera_orientation(phi=75 * DEGREES, theta=-120 * DEGREES)
    axes = ThreeDAxes(x_range=(0, 5, 1), y_range=(0, 5, 1), z_range=(-1, 1, 0.5))

    def param_surface(u, v):
        x = u
        y = v
        z = np.sin(x) * np.cos(y)
        return z

    surface_plane = Surface(
        lambda u, v: axes.c2p(u, v, param_surface(u, v)),
        resolution=(resolution_fa, resolution_fa),
        v_range=[0, 5],
        u_range=[0, 5],
    )
    surface_plane.set_style(fill_opacity=1)
    surface_plane.set_fill_by_value(
        axes=axes, colorscale=[(RED, -0.4), (YELLOW, 0), (GREEN, 0.4)], axis=1
    )
    scene.add(axes, surface_plane)


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_brace.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "brace"


@frames_comparison
def test_brace_sharpness(scene):
    line = Line(LEFT * 3, RIGHT * 3).shift(UP * 4)
    for sharpness in [0, 0.25, 0.5, 0.75, 1, 2, 3, 5]:
        scene.add(Brace(line, sharpness=sharpness))
        line.shift(DOWN)
        scene.wait()


@frames_comparison
def test_braceTip(scene):
    line = Line().shift(LEFT * 3).rotate(PI / 2)
    steps = 8
    for _i in range(steps):
        brace = Brace(line, direction=line.copy().rotate(PI / 2).get_unit_vector())
        dot = Dot()
        brace.put_at_tip(dot)
        line.rotate_about_origin(TAU / steps)
        scene.add(brace, dot)
        scene.wait()


@frames_comparison
def test_arcBrace(scene):
    scene.play(Animation(ArcBrace()))


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_functions.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "functions"


@frames_comparison
def test_FunctionGraph(scene):
    graph = FunctionGraph(lambda x: 2 * np.cos(0.5 * x), x_range=[-PI, PI], color=BLUE)
    scene.add(graph)


@frames_comparison
def test_ImplicitFunction(scene):
    graph = ImplicitFunction(lambda x, y: x**2 + y**2 - 9)
    scene.add(graph)


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_movements.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "movements"


@frames_comparison(last_frame=False)
def test_Homotopy(scene):
    def func(x, y, z, t):
        norm = np.linalg.norm([x, y])
        tau = interpolate(5, -5, t) + norm / config["frame_x_radius"]
        alpha = sigmoid(tau)
        return [x, y + 0.5 * np.sin(2 * np.pi * alpha) - t * SMALL_BUFF / 2, z]

    square = Square()
    scene.play(Homotopy(func, square))


@frames_comparison(last_frame=False)
def test_PhaseFlow(scene):
    square = Square()

    def func(t):
        return t * 0.5 * UP

    scene.play(PhaseFlow(func, square))


@frames_comparison(last_frame=False)
def test_MoveAlongPath(scene):
    square = Square()
    dot = Dot()
    scene.play(MoveAlongPath(dot, square))


@frames_comparison(last_frame=False)
def test_Rotate(scene):
    square = Square()
    scene.play(Rotate(square, PI))


@frames_comparison(last_frame=False)
def test_MoveTo(scene):
    square = Square()
    scene.play(square.animate.move_to(np.array([1.0, 1.0, 0.0])))


@frames_comparison(last_frame=False)
def test_Shift(scene):
    square = Square()
    scene.play(square.animate.shift(UP))


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_transform_matching_parts.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "transform_matching_parts"


@frames_comparison(last_frame=True)
def test_TransformMatchingLeavesOneObject(scene):
    square = Square()
    circle = Circle().shift(RIGHT)
    scene.add(square)
    scene.play(TransformMatchingShapes(square, circle))
    assert len(scene.mobjects) == 1 and isinstance(scene.mobjects[0], Circle)


@frames_comparison(last_frame=False)
def test_TransformMatchingDisplaysCorrect(scene):
    square = Square()
    circle = Circle().shift(RIGHT)
    scene.add(square)
    scene.play(TransformMatchingShapes(square, circle))
    # Wait to make sure object isn't missing in-between animations
    scene.wait(0.5)
    # Shift to make sure object isn't duplicated if moved
    scene.play(circle.animate.shift(DOWN))


@frames_comparison(last_frame=False)
def test_TransformMatchingTex(scene):
    start = MathTex("A", "+", "B", "=", "C")
    end = MathTex("C", "=", "B", "-", "A")

    scene.add(start)
    scene.play(TransformMatchingTex(start, end))


@frames_comparison(last_frame=False)
def test_TransformMatchingTex_FadeTransformMismatches(scene):
    start = MathTex("A", "+", "B", "=", "C")
    end = MathTex("C", "=", "B", "-", "A")

    scene.add(start)
    scene.play(TransformMatchingTex(start, end, fade_transform_mismatches=True))


@frames_comparison(last_frame=False)
def test_TransformMatchingTex_TransformMismatches(scene):
    start = MathTex("A", "+", "B", "=", "C")
    end = MathTex("C", "=", "B", "-", "A")

    scene.add(start)
    scene.play(TransformMatchingTex(start, end, transform_mismatches=True))


@frames_comparison(last_frame=False)
def test_TransformMatchingTex_FadeTransformMismatches_NothingToFade(scene):
    # https://github.com/ManimCommunity/manim/issues/2845
    start = MathTex("A", r"\to", "B")
    end = MathTex("B", r"\to", "A")

    scene.add(start)
    scene.play(TransformMatchingTex(start, end, fade_transform_mismatches=True))


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_speed.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "speed"


@frames_comparison(last_frame=False)
def test_SpeedModifier(scene):
    a = Dot().shift(LEFT * 2 + 0.5 * UP)
    b = Dot().shift(LEFT * 2 + 0.5 * DOWN)
    c = Dot().shift(2 * RIGHT)
    ChangeSpeed.add_updater(c, lambda x, dt: x.rotate_about_origin(PI / 3.7 * dt))
    scene.add(a, b, c)
    scene.play(ChangeSpeed(Wait(0.5), speedinfo={0.3: 1, 0.4: 0.1, 0.6: 0.1, 1: 1}))
    scene.play(
        ChangeSpeed(
            AnimationGroup(
                a.animate(run_time=0.5, rate_func=linear).shift(RIGHT * 4),
                b.animate(run_time=0.5, rate_func=rush_from).shift(RIGHT * 4),
            ),
            speedinfo={0.3: 1, 0.4: 0.1, 0.6: 0.1, 1: 1},
            affects_speed_updaters=False,
        ),
    )
    scene.play(
        ChangeSpeed(
            AnimationGroup(
                a.animate(run_time=0.5, rate_func=linear).shift(LEFT * 4),
                b.animate(run_time=0.5, rate_func=rush_into).shift(LEFT * 4),
            ),
            speedinfo={0.3: 1, 0.4: 0.1, 0.6: 0.1, 1: 1},
            rate_func=there_and_back,
        ),
    )


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_tex_mobject.py
from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "tex_mobject"


@frames_comparison
def test_color_inheritance(scene):
    """Test that Text and MarkupText correctly inherit colour from
    their parent class."""

    VMobject.set_default(color=RED)
    tex = Tex("test color inheritance")
    mathtex = MathTex("test color inheritance")
    vgr = VGroup(tex, mathtex).arrange()
    VMobject.set_default()

    scene.add(vgr)


@frames_comparison
def test_set_opacity_by_tex(scene):
    """Test that set_opacity_by_tex works correctly."""
    tex = MathTex("f(x) = y", substrings_to_isolate=["f(x)"])
    tex.set_opacity_by_tex("f(x)", 0.2, 0.5)
    scene.add(tex)


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_updaters.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "updaters"


@frames_comparison(last_frame=False)
def test_Updater(scene):
    dot = Dot()
    square = Square()
    scene.add(dot, square)
    square.add_updater(lambda m: m.next_to(dot, RIGHT, buff=SMALL_BUFF))
    scene.add(square)
    scene.play(dot.animate.shift(UP * 2))
    square.clear_updaters()


@frames_comparison
def test_ValueTracker(scene):
    theta = ValueTracker(PI / 2)
    line = Line(ORIGIN, RIGHT)
    line.rotate(theta.get_value(), about_point=ORIGIN)
    scene.add(line)


@frames_comparison(last_frame=False)
def test_UpdateSceneDuringAnimation(scene):
    def f(mob):
        scene.add(Square())

    s = Circle().add_updater(f)
    scene.play(Create(s))


@frames_comparison(last_frame=False)
def test_LastFrameWhenCleared(scene):
    dot = Dot()
    square = Square()
    square.add_updater(lambda m: m.move_to(dot, UL))
    scene.add(square)
    scene.play(dot.animate.shift(UP * 2), rate_func=linear)
    square.clear_updaters()
    scene.wait()


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_axes.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "plot"


@frames_comparison
def test_axes(scene):
    graph = Axes(
        x_range=[-10, 10, 1],
        y_range=[-10, 10, 1],
        x_length=6,
        y_length=6,
        color=WHITE,
        y_axis_config={"tip_shape": StealthTip},
    )
    labels = graph.get_axis_labels()
    scene.add(graph, labels)


@frames_comparison
def test_plot_functions(scene, use_vectorized):
    ax = Axes(x_range=(-10, 10.3), y_range=(-1.5, 1.5))
    graph = ax.plot(lambda x: x**2, use_vectorized=use_vectorized)
    scene.add(ax, graph)


@frames_comparison
def test_custom_coordinates(scene):
    ax = Axes(x_range=[0, 10])

    ax.add_coordinates(
        dict(zip(list(range(1, 10)), [Tex("str") for _ in range(1, 10)])),
    )
    scene.add(ax)


@frames_comparison
def test_get_axis_labels(scene):
    ax = Axes()
    labels = ax.get_axis_labels(Tex("$x$-axis").scale(0.7), Tex("$y$-axis").scale(0.45))
    scene.add(ax, labels)


@frames_comparison
def test_get_x_axis_label(scene):
    ax = Axes(x_range=(0, 8), y_range=(0, 5), x_length=8, y_length=5)
    x_label = ax.get_x_axis_label(
        Tex("$x$-values").scale(0.65),
        edge=DOWN,
        direction=DOWN,
        buff=0.5,
    )
    scene.add(ax, x_label)


@frames_comparison
def test_get_y_axis_label(scene):
    ax = Axes(x_range=(0, 8), y_range=(0, 5), x_length=8, y_length=5)
    y_label = ax.get_y_axis_label(
        Tex("$y$-values").scale(0.65).rotate(90 * DEGREES),
        edge=LEFT,
        direction=LEFT,
        buff=0.3,
    )
    scene.add(ax, y_label)


@frames_comparison
def test_axis_tip_default_width_height(scene):
    ax = Axes(
        x_range=(0, 4),
        y_range=(0, 4),
        axis_config={"include_numbers": True, "include_tip": True},
    )

    scene.add(ax)


@frames_comparison
def test_axis_tip_custom_width_height(scene):
    ax = Axes(
        x_range=(0, 4),
        y_range=(0, 4),
        axis_config={"include_numbers": True, "include_tip": True},
        x_axis_config={"tip_width": 1, "tip_height": 0.1},
        y_axis_config={"tip_width": 0.1, "tip_height": 1},
    )

    scene.add(ax)


@frames_comparison
def test_plot_derivative_graph(scene, use_vectorized):
    ax = NumberPlane(y_range=[-1, 7], background_line_style={"stroke_opacity": 0.4})

    curve_1 = ax.plot(lambda x: x**2, color=PURPLE_B, use_vectorized=use_vectorized)
    curve_2 = ax.plot_derivative_graph(curve_1, use_vectorized=use_vectorized)
    curve_3 = ax.plot_antiderivative_graph(curve_1, use_vectorized=use_vectorized)
    curves = VGroup(curve_1, curve_2, curve_3)
    scene.add(ax, curves)


@frames_comparison
def test_plot(scene, use_vectorized):
    # construct the axes
    ax_1 = Axes(
        x_range=[0.001, 6],
        y_range=[-8, 2],
        x_length=5,
        y_length=3,
        tips=False,
    )
    ax_2 = ax_1.copy()
    ax_3 = ax_1.copy()

    # position the axes
    ax_1.to_corner(UL)
    ax_2.to_corner(UR)
    ax_3.to_edge(DOWN)
    axes = VGroup(ax_1, ax_2, ax_3)

    # create the logarithmic curves
    def log_func(x):
        return np.log(x)

    # a curve without adjustments; poor interpolation.
    curve_1 = ax_1.plot(log_func, color=PURE_RED, use_vectorized=use_vectorized)

    # disabling interpolation makes the graph look choppy as not enough
    # inputs are available
    curve_2 = ax_2.plot(
        log_func, use_smoothing=False, color=ORANGE, use_vectorized=use_vectorized
    )

    # taking more inputs of the curve by specifying a step for the
    # x_range yields expected results, but increases rendering time.
    curve_3 = ax_3.plot(
        log_func,
        x_range=(0.001, 6, 0.001),
        color=PURE_GREEN,
        use_vectorized=use_vectorized,
    )

    curves = VGroup(curve_1, curve_2, curve_3)

    scene.add(axes, curves)


@frames_comparison
def test_get_graph_label(scene):
    ax = Axes()
    sin = ax.plot(lambda x: np.sin(x), color=PURPLE_B)
    label = ax.get_graph_label(
        graph=sin,
        label=MathTex(r"\frac{\pi}{2}"),
        x_val=PI / 2,
        dot=True,
        dot_config={"radius": 0.04},
        direction=UR,
    )

    scene.add(ax, sin, label)


@frames_comparison
def test_get_lines_to_point(scene):
    ax = Axes()
    circ = Circle(radius=0.5).move_to([-4, -1.5, 0])

    lines_1 = ax.get_lines_to_point(circ.get_right(), color=GREEN_B)
    lines_2 = ax.get_lines_to_point(circ.get_corner(DL), color=BLUE_B)
    scene.add(ax, lines_1, lines_2, circ)


@frames_comparison
def test_plot_line_graph(scene):
    plane = NumberPlane(
        x_range=(0, 7),
        y_range=(0, 5),
        x_length=7,
        axis_config={"include_numbers": True},
    )

    line_graph = plane.plot_line_graph(
        x_values=[0, 1.5, 2, 2.8, 4, 6.25],
        y_values=[1, 3, 2.25, 4, 2.5, 1.75],
        line_color=GOLD_E,
        vertex_dot_style={"stroke_width": 3, "fill_color": PURPLE},
        vertex_dot_radius=0.04,
        stroke_width=4,
    )
    # test that the line and dots can be accessed afterwards
    line_graph["line_graph"].set_stroke(width=2)
    line_graph["vertex_dots"].scale(2)
    scene.add(plane, line_graph)


@frames_comparison
def test_t_label(scene):
    # defines the axes and linear function
    axes = Axes(x_range=[-1, 10], y_range=[-1, 10], x_length=9, y_length=6)
    func = axes.plot(lambda x: x, color=BLUE)
    # creates the T_label
    t_label = axes.get_T_label(x_val=4, graph=func, label=Tex("$x$-value"))
    scene.add(axes, func, t_label)


@frames_comparison
def test_get_area(scene):
    ax = Axes().add_coordinates()
    curve1 = ax.plot(
        lambda x: 2 * np.sin(x),
        x_range=[-5, ax.x_range[1]],
        color=DARK_BLUE,
    )
    curve2 = ax.plot(lambda x: (x + 4) ** 2 - 2, x_range=[-5, -2], color=RED)
    area1 = ax.get_area(
        curve1,
        x_range=(PI / 2, 3 * PI / 2),
        color=(GREEN_B, GREEN_D),
        opacity=1,
    )
    area2 = ax.get_area(
        curve1,
        x_range=(-4.5, -2),
        color=(RED, YELLOW),
        opacity=0.2,
        bounded_graph=curve2,
    )

    scene.add(ax, curve1, curve2, area1, area2)


@frames_comparison
def test_get_area_with_boundary_and_few_plot_points(scene):
    ax = Axes(x_range=[-2, 2], y_range=[-2, 2], color=WHITE)
    f1 = ax.plot(lambda t: t, [-1, 1, 0.5])
    f2 = ax.plot(lambda t: 1, [-1, 1, 0.5])
    a1 = ax.get_area(f1, [-1, 0.75], color=RED)
    a2 = ax.get_area(f1, [-0.75, 1], bounded_graph=f2, color=GREEN)

    scene.add(ax, f1, f2, a1, a2)


@frames_comparison
def test_get_riemann_rectangles(scene, use_vectorized):
    ax = Axes(y_range=[-2, 10])
    quadratic = ax.plot(lambda x: 0.5 * x**2 - 0.5, use_vectorized=use_vectorized)

    # the rectangles are constructed from their top right corner.
    # passing an iterable to `color` produces a gradient
    rects_right = ax.get_riemann_rectangles(
        quadratic,
        x_range=[-4, -3],
        dx=0.25,
        color=(TEAL, BLUE_B, DARK_BLUE),
        input_sample_type="right",
    )

    # the colour of rectangles below the x-axis is inverted
    # due to show_signed_area
    rects_left = ax.get_riemann_rectangles(
        quadratic,
        x_range=[-1.5, 1.5],
        dx=0.15,
        color=YELLOW,
    )

    bounding_line = ax.plot(lambda x: 1.5 * x, color=BLUE_B, x_range=[3.3, 6])
    bounded_rects = ax.get_riemann_rectangles(
        bounding_line,
        bounded_graph=quadratic,
        dx=0.15,
        x_range=[4, 5],
        show_signed_area=False,
        color=(MAROON_A, RED_B, PURPLE_D),
    )

    scene.add(ax, bounding_line, quadratic, rects_right, rects_left, bounded_rects)


@frames_comparison(base_scene=ThreeDScene)
def test_get_z_axis_label(scene):
    ax = ThreeDAxes()
    lab = ax.get_z_axis_label(Tex("$z$-label"))
    scene.set_camera_orientation(phi=2 * PI / 5, theta=PI / 5)
    scene.add(ax, lab)


@frames_comparison
def test_polar_graph(scene):
    polar = PolarPlane()

    def r(theta):
        return 4 * np.sin(theta * 4)

    polar_graph = polar.plot_polar_graph(r)
    scene.add(polar, polar_graph)


@frames_comparison
def test_log_scaling_graph(scene):
    ax = Axes(
        x_range=[0, 8],
        y_range=[-2, 4],
        x_length=10,
        y_axis_config={"scaling": LogBase()},
    )
    ax.add_coordinates()

    gr = ax.plot(lambda x: x, use_smoothing=False, x_range=[0.01, 8])

    scene.add(ax, gr)


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_specialized.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "specialized"


@frames_comparison(last_frame=False)
def test_Broadcast(scene):
    circle = Circle()
    scene.play(Broadcast(circle))


# Extracted from /Users/hochmax/learn/manim/tests/test_graphical_units/test_geometry.py
from __future__ import annotations

from manim import *
from manim.utils.testing.frames_comparison import frames_comparison

__module_test__ = "geometry"


@frames_comparison(last_frame=True)
def test_Coordinates(scene):
    dots = [Dot(np.array([x, y, 0])) for x in range(-7, 8) for y in range(-4, 5)]
    scene.add(VGroup(*dots))


@frames_comparison
def test_Arc(scene):
    a = Arc(radius=1, start_angle=PI)
    scene.add(a)


@frames_comparison
def test_ArcBetweenPoints(scene):
    a = ArcBetweenPoints(np.array([1, 1, 0]), np.array([2, 2, 0]))
    scene.add(a)


@frames_comparison
def test_CurvedArrow(scene):
    a = CurvedArrow(np.array([1, 1, 0]), np.array([2, 2, 0]))
    scene.add(a)


@frames_comparison
def test_CustomDoubleArrow(scene):
    a = DoubleArrow(
        np.array([-1, -1, 0]),
        np.array([1, 1, 0]),
        tip_shape_start=ArrowCircleTip,
        tip_shape_end=ArrowSquareFilledTip,
    )
    scene.add(a)


@frames_comparison
def test_Circle(scene):
    circle = Circle()
    scene.add(circle)


@frames_comparison
def test_CirclePoints(scene):
    circle = Circle.from_three_points(LEFT, LEFT + UP, UP * 2)
    scene.add(circle)


@frames_comparison
def test_Dot(scene):
    dot = Dot()
    scene.add(dot)


@frames_comparison
def test_DashedVMobject(scene):
    circle = DashedVMobject(Circle(), 12, 0.9, dash_offset=0.1)
    line = DashedLine(dash_length=0.5)
    scene.add(circle, line)


@frames_comparison
def test_AnnotationDot(scene):
    adot = AnnotationDot()
    scene.add(adot)


@frames_comparison
def test_Ellipse(scene):
    e = Ellipse()
    scene.add(e)


@frames_comparison
def test_Sector(scene):
    e = Sector()
    scene.add(e)


@frames_comparison
def test_Annulus(scene):
    a = Annulus()
    scene.add(a)


@frames_comparison
def test_AnnularSector(scene):
    a = AnnularSector()
    scene.add(a)


@frames_comparison
def test_Line(scene):
    a = Line(np.array([1, 1, 0]), np.array([2, 2, 0]))
    scene.add(a)


@frames_comparison
def test_Elbow(scene):
    a = Elbow()
    scene.add(a)


@frames_comparison
def test_DoubleArrow(scene):
    a = DoubleArrow()
    scene.add(a)


@frames_comparison
def test_Vector(scene):
    a = Vector(UP)
    scene.add(a)


@frames_comparison
def test_Polygon(scene):
    a = Polygon(*[np.array([1, 1, 0]), np.array([2, 2, 0]), np.array([2, 3, 0])])
    scene.add(a)


@frames_comparison
def test_Rectangle(scene):
    a = Rectangle()
    scene.add(a)


@frames_comparison
def test_RoundedRectangle(scene):
    a = RoundedRectangle()
    scene.add(a)


@frames_comparison
def test_Arrange(scene):
    s1 = Square()
    s2 = Square()
    x = VGroup(s1, s2).set_x(0).arrange(buff=1.4)
    scene.add(x)


@frames_comparison(last_frame=False)
def test_ZIndex(scene):
    circle = Circle().set_fill(RED, opacity=1)
    square = Square(side_length=1.7).set_fill(BLUE, opacity=1)
    triangle = Triangle().set_fill(GREEN, opacity=1)
    square.z_index = 0
    triangle.z_index = 1
    circle.z_index = 2

    scene.play(FadeIn(VGroup(circle, square, triangle)))
    scene.play(ApplyMethod(circle.shift, UP))
    scene.play(ApplyMethod(triangle.shift, 2 * UP))


@frames_comparison
def test_Angle(scene):
    l1 = Line(ORIGIN, RIGHT)
    l2 = Line(ORIGIN, UP)
    a = Angle(l1, l2)
    scene.add(a)


@frames_comparison
def test_three_points_Angle(scene):
    # acute angle
    acute = Angle.from_three_points(
        np.array([10, 0, 0]), np.array([0, 0, 0]), np.array([10, 10, 0])
    )
    # obtuse angle
    obtuse = Angle.from_three_points(
        np.array([-10, 1, 0]), np.array([0, 0, 0]), np.array([10, 1, 0])
    )
    # quadrant 1 angle
    q1 = Angle.from_three_points(
        np.array([10, 10, 0]), np.array([0, 0, 0]), np.array([10, 1, 0])
    )
    # quadrant 2 angle
    q2 = Angle.from_three_points(
        np.array([-10, 1, 0]), np.array([0, 0, 0]), np.array([-1, 10, 0])
    )
    # quadrant 3 angle
    q3 = Angle.from_three_points(
        np.array([-10, -1, 0]), np.array([0, 0, 0]), np.array([-1, -10, 0])
    )
    # quadrant 4 angle
    q4 = Angle.from_three_points(
        np.array([10, -1, 0]), np.array([0, 0, 0]), np.array([1, -10, 0])
    )
    scene.add(VGroup(acute, obtuse, q1, q2, q3, q4).arrange(RIGHT))


@frames_comparison
def test_RightAngle(scene):
    l1 = Line(ORIGIN, RIGHT)
    l2 = Line(ORIGIN, UP)
    a = RightAngle(l1, l2)
    scene.add(a)


@frames_comparison
def test_Polygram(scene):
    hexagram = Polygram(
        [[0, 2, 0], [-np.sqrt(3), -1, 0], [np.sqrt(3), -1, 0]],
        [[-np.sqrt(3), 1, 0], [0, -2, 0], [np.sqrt(3), 1, 0]],
    )
    scene.add(hexagram)


@frames_comparison
def test_RegularPolygram(scene):
    pentagram = RegularPolygram(5, radius=2)
    octagram = RegularPolygram(8, radius=2)
    scene.add(VGroup(pentagram, octagram).arrange(RIGHT))


@frames_comparison
def test_Star(scene):
    star = Star(outer_radius=2)
    scene.add(star)


@frames_comparison
def test_AngledArrowTip(scene):
    arrow = Arrow(start=ORIGIN, end=UP + RIGHT + OUT)
    scene.add(arrow)


@frames_comparison
def test_CurvedArrowCustomTip(scene):
    arrow = CurvedArrow(
        LEFT,
        RIGHT,
        tip_shape=ArrowCircleTip,
    )
    double_arrow = CurvedDoubleArrow(
        LEFT,
        RIGHT,
        tip_shape_start=ArrowCircleTip,
        tip_shape_end=ArrowSquareFilledTip,
    )
    scene.add(arrow, double_arrow)


@frames_comparison
def test_LabeledLine(scene):
    line = LabeledLine(
        label="0.5",
        label_position=0.8,
        font_size=20,
        label_color=WHITE,
        label_frame=True,
        start=LEFT + DOWN,
        end=RIGHT + UP,
    )
    scene.add(line)


@frames_comparison
def test_LabeledArrow(scene):
    l_arrow = LabeledArrow(
        "0.5", start=LEFT * 3, end=RIGHT * 3 + UP * 2, label_position=0.5, font_size=15
    )
    scene.add(l_arrow)


# Extracted from /Users/hochmax/learn/manim/tests/test_plugins/simple_scenes.py
from __future__ import annotations

from manim import *


class SquareToCircle(Scene):
    def construct(self):
        square = Square()
        circle = Circle()
        self.play(Transform(square, circle))


# Extracted from /Users/hochmax/learn/manim/tests/test_plugins/test_plugins.py
from __future__ import annotations

import random
import string
import textwrap
from pathlib import Path

import pytest

from manim import capture

plugin_pyproject_template = textwrap.dedent(
    """\
    [tool.poetry]
    name = "{plugin_name}"
    authors = ["ManimCE Test Suite"]
    version = "0.1.0"
    description = ""

    [tool.poetry.dependencies]
    python = "^3.7"

    [tool.poetry.plugins."manim.plugins"]
    "{plugin_name}" = "{plugin_entrypoint}"

    [build-system]
    requires = ["poetry-core>=1.0.0"]
    build-backend = "poetry.core.masonry.api"
    """,
)

plugin_init_template = textwrap.dedent(
    """\
    from manim import *
    {all_dec}
    class {class_name}(VMobject):
        def __init__(self):
            super().__init__()
            dot1 = Dot(fill_color=GREEN).shift(LEFT)
            dot2 = Dot(fill_color=BLUE)
            dot3 = Dot(fill_color=RED).shift(RIGHT)
            self.dotgrid = VGroup(dot1, dot2, dot3)
            self.add(self.dotgrid)

        def update_dot(self):
            self.dotgrid.become(self.dotgrid.shift(UP))
    def {function_name}():
        return [{class_name}]
    """,
)

cfg_file_contents = textwrap.dedent(
    """\
        [CLI]
        plugins = {plugin_name}
    """,
)


@pytest.fixture
def simple_scenes_path():
    yield Path(__file__).parent / "simple_scenes.py"


def cfg_file_create(cfg_file_contents, path):
    file_loc = (path / "manim.cfg").absolute()
    file_loc.write_text(cfg_file_contents)
    return file_loc


@pytest.fixture
def random_string():
    all_letters = string.ascii_lowercase
    a = random.Random()
    final_letters = [a.choice(all_letters) for _ in range(8)]
    yield "".join(final_letters)


def test_plugin_warning(tmp_path, python_version, simple_scenes_path):
    cfg_file = cfg_file_create(
        cfg_file_contents.format(plugin_name="DNEplugin"),
        tmp_path,
    )
    scene_name = "SquareToCircle"
    command = [
        python_version,
        "-m",
        "manim",
        "-ql",
        "--media_dir",
        str(cfg_file.parent),
        "--config_file",
        str(cfg_file),
        str(simple_scenes_path),
        scene_name,
    ]
    out, err, exit_code = capture(command, cwd=str(cfg_file.parent))
    assert exit_code == 0, err
    assert "Missing Plugins" in out, "Missing Plugins isn't in Output."


@pytest.fixture
def create_plugin(tmp_path, python_version, random_string):
    plugin_dir = tmp_path / "plugin_dir"
    plugin_name = random_string

    def _create_plugin(entry_point, class_name, function_name, all_dec=""):
        entry_point = entry_point.format(plugin_name=plugin_name)
        module_dir = plugin_dir / plugin_name
        module_dir.mkdir(parents=True)
        (module_dir / "__init__.py").write_text(
            plugin_init_template.format(
                class_name=class_name,
                function_name=function_name,
                all_dec=all_dec,
            ),
        )
        (plugin_dir / "pyproject.toml").write_text(
            plugin_pyproject_template.format(
                plugin_name=plugin_name,
                plugin_entrypoint=entry_point,
            ),
        )
        command = [
            python_version,
            "-m",
            "pip",
            "install",
            str(plugin_dir.absolute()),
        ]
        out, err, exit_code = capture(command, cwd=str(plugin_dir))
        print(out)
        assert exit_code == 0, err
        return {
            "module_dir": module_dir,
            "plugin_name": plugin_name,
        }

    yield _create_plugin
    command = [python_version, "-m", "pip", "uninstall", plugin_name, "-y"]
    out, err, exit_code = capture(command)
    print(out)
    assert exit_code == 0, err


# Extracted from /Users/hochmax/learn/manim/tests/test_logging/basic_scenes_write_stuff.py
from __future__ import annotations

from manim import *

# This module is used in the CLI tests in tests_CLi.py.


class WriteStuff(Scene):
    def construct(self):
        example_text = Tex("This is a some text", tex_to_color_map={"text": YELLOW})
        example_tex = MathTex(
            "\\sum_{k=1}^\\infty {1 \\over k^2} = {\\pi^2 \\over 6}",
        )
        group = VGroup(example_text, example_tex)
        group.arrange(DOWN)
        group.width = config["frame_width"] - 2 * LARGE_BUFF

        self.play(Write(example_text))


# Extracted from /Users/hochmax/learn/manim/tests/test_logging/basic_scenes_square_to_circle.py
from __future__ import annotations

from manim import *

# This module is used in the CLI tests in tests_CLi.py.


class SquareToCircle(Scene):
    def construct(self):
        self.play(Transform(Square(), Circle()))


# Extracted from /Users/hochmax/learn/manim/tests/test_logging/basic_scenes_error.py
from __future__ import annotations

from manim import *

# This module is intended to raise an error.


class Error(Scene):
    def construct(self):
        raise Exception("An error has occurred")


# Extracted from /Users/hochmax/learn/manim/tests/opengl/test_svg_mobject_opengl.py
from __future__ import annotations

from manim import *
from tests.helpers.path_utils import get_svg_resource


def test_set_fill_color(using_opengl_renderer):
    expected_color = "#FF862F"
    svg = SVGMobject(get_svg_resource("heart.svg"), fill_color=expected_color)
    assert svg.fill_color.to_hex() == expected_color


def test_set_stroke_color(using_opengl_renderer):
    expected_color = "#FFFDDD"
    svg = SVGMobject(get_svg_resource("heart.svg"), stroke_color=expected_color)
    assert svg.stroke_color.to_hex() == expected_color


def test_set_color_sets_fill_and_stroke(using_opengl_renderer):
    expected_color = "#EEE777"
    svg = SVGMobject(get_svg_resource("heart.svg"), color=expected_color)
    assert svg.color.to_hex() == expected_color
    assert svg.fill_color.to_hex() == expected_color
    assert svg.stroke_color.to_hex() == expected_color


def test_set_fill_opacity(using_opengl_renderer):
    expected_opacity = 0.5
    svg = SVGMobject(get_svg_resource("heart.svg"), fill_opacity=expected_opacity)
    assert svg.fill_opacity == expected_opacity


def test_stroke_opacity(using_opengl_renderer):
    expected_opacity = 0.4
    svg = SVGMobject(get_svg_resource("heart.svg"), stroke_opacity=expected_opacity)
    assert svg.stroke_opacity == expected_opacity


def test_fill_overrides_color(using_opengl_renderer):
    expected_color = "#343434"
    svg = SVGMobject(
        get_svg_resource("heart.svg"),
        color="#123123",
        fill_color=expected_color,
    )
    assert svg.fill_color.to_hex() == expected_color


def test_stroke_overrides_color(using_opengl_renderer):
    expected_color = "#767676"
    svg = SVGMobject(
        get_svg_resource("heart.svg"),
        color="#334433",
        stroke_color=expected_color,
    )
    assert svg.stroke_color.to_hex() == expected_color


# Extracted from /Users/hochmax/learn/manim/manim/utils/ipython_magic.py
"""Utilities for using Manim with IPython (in particular: Jupyter notebooks)"""

from __future__ import annotations

import mimetypes
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from manim import config, logger, tempconfig
from manim.__main__ import main
from manim.renderer.shader import shader_program_cache

from ..constants import RendererType

__all__ = ["ManimMagic"]

try:
    from IPython import get_ipython
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.core.magic import (
        Magics,
        line_cell_magic,
        magics_class,
        needs_local_scope,
    )
    from IPython.display import Image, Video, display
except ImportError:
    pass
else:

    @magics_class
    class ManimMagic(Magics):
        def __init__(self, shell: InteractiveShell) -> None:
            super().__init__(shell)
            self.rendered_files = {}

        @needs_local_scope
        @line_cell_magic
        def manim(
            self,
            line: str,
            cell: str = None,
            local_ns: dict[str, Any] = None,
        ) -> None:
            r"""Render Manim scenes contained in IPython cells.
            Works as a line or cell magic.

            .. hint::

                This line and cell magic works best when used in a JupyterLab
                environment: while all of the functionality is available for
                classic Jupyter notebooks as well, it is possible that videos
                sometimes don't update on repeated execution of the same cell
                if the scene name stays the same.

                This problem does not occur when using JupyterLab.

            Please refer to `<https://jupyter.org/>`_ for more information about JupyterLab
            and Jupyter notebooks.

            Usage in line mode::

                %manim [CLI options] MyAwesomeScene

            Usage in cell mode::

                %%manim [CLI options] MyAwesomeScene

                class MyAweseomeScene(Scene):
                    def construct(self):
                        ...

            Run ``%manim --help`` and ``%manim render --help`` for possible command line interface options.

            .. note::

                The maximal width of the rendered videos that are displayed in the notebook can be
                configured via the ``media_width`` configuration option. The default is set to ``25vw``,
                which is 25% of your current viewport width. To allow the output to become as large
                as possible, set ``config.media_width = "100%"``.

                The ``media_embed`` option will embed the image/video output in the notebook. This is
                generally undesirable as it makes the notebooks very large, but is required on some
                platforms (notably Google's CoLab, where it is automatically enabled unless suppressed
                by ``config.embed = False``) and needed in cases when the notebook (or converted HTML
                file) will be moved relative to the video locations. Use-cases include building
                documentation with Sphinx and JupyterBook. See also the :mod:`manim directive for Sphinx
                <manim.utils.docbuild.manim_directive>`.

            Examples
            --------

            First make sure to put ``import manim``, or even ``from manim import *``
            in a cell and evaluate it. Then, a typical Jupyter notebook cell for Manim
            could look as follows::

                %%manim -v WARNING --disable_caching -qm BannerExample

                config.media_width = "75%"
                config.media_embed = True

                class BannerExample(Scene):
                    def construct(self):
                        self.camera.background_color = "#ece6e2"
                        banner_large = ManimBanner(dark_theme=False).scale(0.7)
                        self.play(banner_large.create())
                        self.play(banner_large.expand())

            Evaluating this cell will render and display the ``BannerExample`` scene defined in the body of the cell.

            .. note::

                In case you want to hide the red box containing the output progress bar, the ``progress_bar`` config
                option should be set to ``None``. This can also be done by passing ``--progress_bar None`` as a
                CLI flag.

            """
            if cell:
                exec(cell, local_ns)

            args = line.split()
            if not len(args) or "-h" in args or "--help" in args or "--version" in args:
                main(args, standalone_mode=False, prog_name="manim")
                return

            modified_args = self.add_additional_args(args)
            args = main(modified_args, standalone_mode=False, prog_name="manim")
            with tempconfig(local_ns.get("config", {})):
                config.digest_args(args)

                renderer = None
                if config.renderer == RendererType.OPENGL:
                    from manim.renderer.opengl_renderer import OpenGLRenderer

                    renderer = OpenGLRenderer()

                try:
                    SceneClass = local_ns[config["scene_names"][0]]
                    scene = SceneClass(renderer=renderer)
                    scene.render()
                finally:
                    # Shader cache becomes invalid as the context is destroyed
                    shader_program_cache.clear()

                    # Close OpenGL window here instead of waiting for the main thread to
                    # finish causing the window to stay open and freeze
                    if renderer is not None and renderer.window is not None:
                        renderer.window.close()

                if config["output_file"] is None:
                    logger.info("No output file produced")
                    return

                local_path = Path(config["output_file"]).relative_to(Path.cwd())
                tmpfile = (
                    Path(config["media_dir"])
                    / "jupyter"
                    / f"{_generate_file_name()}{local_path.suffix}"
                )

                if local_path in self.rendered_files:
                    self.rendered_files[local_path].unlink()
                self.rendered_files[local_path] = tmpfile
                tmpfile.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(local_path, tmpfile)

                file_type = mimetypes.guess_type(config["output_file"])[0]
                embed = config["media_embed"]
                if embed is None:
                    # videos need to be embedded when running in google colab.
                    # do this automatically in case config.media_embed has not been
                    # set explicitly.
                    embed = "google.colab" in str(get_ipython())

                if file_type.startswith("image"):
                    result = Image(filename=config["output_file"])
                else:
                    result = Video(
                        tmpfile,
                        html_attributes=f'controls autoplay loop style="max-width: {config["media_width"]};"',
                        embed=embed,
                    )

                display(result)

        def add_additional_args(self, args: list[str]) -> list[str]:
            additional_args = ["--jupyter"]
            # Use webm to support transparency
            if "-t" in args and "--format" not in args:
                additional_args += ["--format", "webm"]
            return additional_args + args[:-1] + [""] + [args[-1]]


def _generate_file_name() -> str:
    return config["scene_names"][0] + "@" + datetime.now().strftime("%Y-%m-%d@%H-%M-%S")


# Extracted from /Users/hochmax/learn/manim/manim/utils/file_ops.py
"""Utility functions for interacting with the file system."""

from __future__ import annotations

__all__ = [
    "add_extension_if_not_present",
    "guarantee_existence",
    "guarantee_empty_existence",
    "seek_full_path_from_defaults",
    "modify_atime",
    "open_file",
    "is_mp4_format",
    "is_gif_format",
    "is_png_format",
    "is_webm_format",
    "is_mov_format",
    "write_to_movie",
    "ensure_executable",
]

import os
import platform
import shutil
import subprocess as sp
import time
from pathlib import Path
from shutil import copyfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..scene.scene_file_writer import SceneFileWriter

from manim import __version__, config, logger

from .. import console


def is_mp4_format() -> bool:
    """
    Determines if output format is .mp4

    Returns
    -------
    class:`bool`
        ``True`` if format is set as mp4

    """
    return config["format"] == "mp4"


def is_gif_format() -> bool:
    """
    Determines if output format is .gif

    Returns
    -------
    class:`bool`
        ``True`` if format is set as gif

    """
    return config["format"] == "gif"


def is_webm_format() -> bool:
    """
    Determines if output format is .webm

    Returns
    -------
    class:`bool`
        ``True`` if format is set as webm

    """
    return config["format"] == "webm"


def is_mov_format() -> bool:
    """
    Determines if output format is .mov

    Returns
    -------
    class:`bool`
        ``True`` if format is set as mov

    """
    return config["format"] == "mov"


def is_png_format() -> bool:
    """
    Determines if output format is .png

    Returns
    -------
    class:`bool`
        ``True`` if format is set as png

    """
    return config["format"] == "png"


def write_to_movie() -> bool:
    """
    Determines from config if the output is a video format such as mp4 or gif, if the --format is set as 'png'
    then it will take precedence event if the write_to_movie flag is set

    Returns
    -------
    class:`bool`
        ``True`` if the output should be written in a movie format

    """
    if is_png_format():
        return False
    return (
        config["write_to_movie"]
        or is_mp4_format()
        or is_gif_format()
        or is_webm_format()
        or is_mov_format()
    )


def ensure_executable(path_to_exe: Path) -> bool:
    if path_to_exe.parent == Path("."):
        executable = shutil.which(path_to_exe.stem)
        if executable is None:
            return False
    else:
        executable = path_to_exe
    return os.access(executable, os.X_OK)


def add_extension_if_not_present(file_name: Path, extension: str) -> Path:
    if file_name.suffix != extension:
        return file_name.with_suffix(file_name.suffix + extension)
    else:
        return file_name


def add_version_before_extension(file_name: Path) -> Path:
    return file_name.with_name(
        f"{file_name.stem}_ManimCE_v{__version__}{file_name.suffix}"
    )


def guarantee_existence(path: Path) -> Path:
    if not path.exists():
        path.mkdir(parents=True)
    return path.resolve(strict=True)


def guarantee_empty_existence(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(str(path))
    path.mkdir(parents=True)
    return path.resolve(strict=True)


def seek_full_path_from_defaults(
    file_name: str, default_dir: Path, extensions: list[str]
) -> Path:
    possible_paths = [Path(file_name).expanduser()]
    possible_paths += [
        Path(default_dir) / f"{file_name}{extension}" for extension in ["", *extensions]
    ]
    for path in possible_paths:
        if path.exists():
            return path
    error = (
        f"From: {Path.cwd()}, could not find {file_name} at either "
        f"of these locations: {list(map(str, possible_paths))}"
    )
    raise OSError(error)


def modify_atime(file_path: str) -> None:
    """Will manually change the accessed time (called `atime`) of the file, as on a lot of OS the accessed time refresh is disabled by default.

    Parameters
    ----------
    file_path
        The path of the file.
    """
    os.utime(file_path, times=(time.time(), Path(file_path).stat().st_mtime))


def open_file(file_path, in_browser=False):
    current_os = platform.system()
    if current_os == "Windows":
        os.startfile(file_path if not in_browser else file_path.parent)
    else:
        if current_os == "Linux":
            commands = ["xdg-open"]
            file_path = file_path if not in_browser else file_path.parent
        elif current_os.startswith("CYGWIN"):
            commands = ["cygstart"]
            file_path = file_path if not in_browser else file_path.parent
        elif current_os == "Darwin":
            commands = ["open"] if not in_browser else ["open", "-R"]
        else:
            raise OSError("Unable to identify your operating system...")

        # check after so that file path is set correctly
        if config.preview_command:
            commands = [config.preview_command]
        commands.append(file_path)
        sp.run(commands)


def open_media_file(file_writer: SceneFileWriter) -> None:
    file_paths = []

    if config["save_last_frame"]:
        file_paths.append(file_writer.image_file_path)
    if write_to_movie() and not is_gif_format():
        file_paths.append(file_writer.movie_file_path)
    if write_to_movie() and is_gif_format():
        file_paths.append(file_writer.gif_file_path)

    for file_path in file_paths:
        if config["show_in_file_browser"]:
            open_file(file_path, True)
        if config["preview"]:
            open_file(file_path, False)

            logger.info(f"Previewed File at: '{file_path}'")


def get_template_names() -> list[str]:
    """Returns template names from the templates directory.

    Returns
    -------
        :class:`list`
    """
    template_path = Path.resolve(Path(__file__).parent.parent / "templates")
    return [template_name.stem for template_name in template_path.glob("*.mtp")]


def get_template_path() -> Path:
    """Returns the Path of templates directory.

    Returns
    -------
        :class:`Path`
    """
    return Path.resolve(Path(__file__).parent.parent / "templates")


def add_import_statement(file: Path):
    """Prepends an import statement in a file

    Parameters
    ----------
        file
    """
    with file.open("r+") as f:
        import_line = "from manim import *"
        content = f.read()
        f.seek(0)
        f.write(import_line + "\n" + content)


def copy_template_files(
    project_dir: Path = Path("."), template_name: str = "Default"
) -> None:
    """Copies template files from templates dir to project_dir.

    Parameters
    ----------
        project_dir
            Path to project directory.
        template_name
            Name of template.
    """
    template_cfg_path = Path.resolve(
        Path(__file__).parent.parent / "templates/template.cfg",
    )
    template_scene_path = Path.resolve(
        Path(__file__).parent.parent / f"templates/{template_name}.mtp",
    )

    if not template_cfg_path.exists():
        raise FileNotFoundError(f"{template_cfg_path} : file does not exist")
    if not template_scene_path.exists():
        raise FileNotFoundError(f"{template_scene_path} : file does not exist")

    copyfile(template_cfg_path, Path.resolve(project_dir / "manim.cfg"))
    console.print("\n\t[green]copied[/green] [blue]manim.cfg[/blue]\n")
    copyfile(template_scene_path, Path.resolve(project_dir / "main.py"))
    console.print("\n\t[green]copied[/green] [blue]main.py[/blue]\n")
    add_import_statement(Path.resolve(project_dir / "main.py"))


# Extracted from /Users/hochmax/learn/manim/manim/utils/module_ops.py
from __future__ import annotations

import importlib.util
import inspect
import re
import sys
import types
import warnings
from pathlib import Path

from .. import config, console, constants, logger
from ..scene.scene_file_writer import SceneFileWriter

__all__ = ["scene_classes_from_file"]


def get_module(file_name: Path):
    if str(file_name) == "-":
        module = types.ModuleType("input_scenes")
        logger.info(
            "Enter the animation's code & end with an EOF (CTRL+D on Linux/Unix, CTRL+Z on Windows):",
        )
        code = sys.stdin.read()
        if not code.startswith("from manim import"):
            logger.warning(
                "Didn't find an import statement for Manim. Importing automatically...",
            )
            code = "from manim import *\n" + code
        logger.info("Rendering animation from typed code...")
        try:
            exec(code, module.__dict__)
            return module
        except Exception as e:
            logger.error(f"Failed to render scene: {str(e)}")
            sys.exit(2)
    else:
        if file_name.exists():
            ext = file_name.suffix
            if ext != ".py":
                raise ValueError(f"{file_name} is not a valid Manim python script.")
            module_name = ".".join(file_name.with_suffix("").parts)

            warnings.filterwarnings(
                "default",
                category=DeprecationWarning,
                module=module_name,
            )

            spec = importlib.util.spec_from_file_location(module_name, file_name)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            sys.path.insert(0, str(file_name.parent.absolute()))
            spec.loader.exec_module(module)
            return module
        else:
            raise FileNotFoundError(f"{file_name} not found")


def get_scene_classes_from_module(module):
    from ..scene.scene import Scene

    def is_child_scene(obj, module):
        return (
            inspect.isclass(obj)
            and issubclass(obj, Scene)
            and obj != Scene
            and obj.__module__.startswith(module.__name__)
        )

    return [
        member[1]
        for member in inspect.getmembers(module, lambda x: is_child_scene(x, module))
    ]


def get_scenes_to_render(scene_classes):
    if not scene_classes:
        logger.error(constants.NO_SCENE_MESSAGE)
        return []
    if config["write_all"]:
        return scene_classes
    result = []
    for scene_name in config["scene_names"]:
        found = False
        for scene_class in scene_classes:
            if scene_class.__name__ == scene_name:
                result.append(scene_class)
                found = True
                break
        if not found and (scene_name != ""):
            logger.error(constants.SCENE_NOT_FOUND_MESSAGE.format(scene_name))
    if result:
        return result
    if len(scene_classes) == 1:
        config["scene_names"] = [scene_classes[0].__name__]
        return [scene_classes[0]]
    return prompt_user_for_choice(scene_classes)


def prompt_user_for_choice(scene_classes):
    num_to_class = {}
    SceneFileWriter.force_output_as_scene_name = True
    for count, scene_class in enumerate(scene_classes, 1):
        name = scene_class.__name__
        console.print(f"{count}: {name}", style="logging.level.info")
        num_to_class[count] = scene_class
    try:
        user_input = console.input(
            f"[log.message] {constants.CHOOSE_NUMBER_MESSAGE} [/log.message]",
        )
        scene_classes = [
            num_to_class[int(num_str)]
            for num_str in re.split(r"\s*,\s*", user_input.strip())
        ]
        config["scene_names"] = [scene_class.__name__ for scene_class in scene_classes]
        return scene_classes
    except KeyError:
        logger.error(constants.INVALID_NUMBER_MESSAGE)
        sys.exit(2)
    except EOFError:
        sys.exit(1)
    except ValueError:
        logger.error("No scenes were selected. Exiting.")
        sys.exit(1)


def scene_classes_from_file(
    file_path: Path, require_single_scene=False, full_list=False
):
    module = get_module(file_path)
    all_scene_classes = get_scene_classes_from_module(module)
    if full_list:
        return all_scene_classes
    scene_classes_to_render = get_scenes_to_render(all_scene_classes)
    if require_single_scene:
        assert len(scene_classes_to_render) == 1
        return scene_classes_to_render[0]
    return scene_classes_to_render


# Extracted from /Users/hochmax/learn/manim/manim/utils/docbuild/manim_directive.py
r"""
A directive for including Manim videos in a Sphinx document
===========================================================

When rendering the HTML documentation, the ``.. manim::`` directive
implemented here allows to include rendered videos.

Its basic usage that allows processing **inline content**
looks as follows::

    .. manim:: MyScene

        class MyScene(Scene):
            def construct(self):
                ...

It is required to pass the name of the class representing the
scene to be rendered to the directive.

As a second application, the directive can also be used to
render scenes that are defined within doctests, for example::

    .. manim:: DirectiveDoctestExample
        :ref_classes: Dot

        >>> from manim import Create, Dot, RED, Scene
        >>> dot = Dot(color=RED)
        >>> dot.color
        ManimColor('#FC6255')
        >>> class DirectiveDoctestExample(Scene):
        ...     def construct(self):
        ...         self.play(Create(dot))


Options
-------

Options can be passed as follows::

    .. manim:: <Class name>
        :<option name>: <value>

The following configuration options are supported by the
directive:

    hide_source
        If this flag is present without argument,
        the source code is not displayed above the rendered video.

    no_autoplay
        If this flag is present without argument,
        the video will not autoplay.

    quality : {'low', 'medium', 'high', 'fourk'}
        Controls render quality of the video, in analogy to
        the corresponding command line flags.

    save_as_gif
        If this flag is present without argument,
        the scene is rendered as a gif.

    save_last_frame
        If this flag is present without argument,
        an image representing the last frame of the scene will
        be rendered and displayed, instead of a video.

    ref_classes
        A list of classes, separated by spaces, that is
        rendered in a reference block after the source code.

    ref_functions
        A list of functions, separated by spaces,
        that is rendered in a reference block after the source code.

    ref_methods
        A list of methods, separated by spaces,
        that is rendered in a reference block after the source code.

"""

from __future__ import annotations

import csv
import itertools as it
import re
import shutil
import sys
import textwrap
from pathlib import Path
from timeit import timeit
from typing import TYPE_CHECKING, Any

import jinja2
from docutils import nodes
from docutils.parsers.rst import Directive, directives  # type: ignore
from docutils.statemachine import StringList

from manim import QUALITIES
from manim import __version__ as manim_version

if TYPE_CHECKING:
    from sphinx.application import Sphinx

__all__ = ["ManimDirective"]


classnamedict: dict[str, int] = {}


class SkipManimNode(nodes.Admonition, nodes.Element):
    """Auxiliary node class that is used when the ``skip-manim`` tag is present
    or ``.pot`` files are being built.

    Skips rendering the manim directive and outputs a placeholder instead.
    """

    pass


def visit(self: SkipManimNode, node: nodes.Element, name: str = "") -> None:
    self.visit_admonition(node, name)
    if not isinstance(node[0], nodes.title):
        node.insert(0, nodes.title("skip-manim", "Example Placeholder"))


def depart(self: SkipManimNode, node: nodes.Element) -> None:
    self.depart_admonition(node)


def process_name_list(option_input: str, reference_type: str) -> list[str]:
    r"""Reformats a string of space separated class names
    as a list of strings containing valid Sphinx references.

    Tests
    -----

    ::

        >>> process_name_list("Tex TexTemplate", "class")
        [':class:`~.Tex`', ':class:`~.TexTemplate`']
        >>> process_name_list("Scene.play Mobject.rotate", "func")
        [':func:`~.Scene.play`', ':func:`~.Mobject.rotate`']
    """
    return [f":{reference_type}:`~.{name}`" for name in option_input.split()]


class ManimDirective(Directive):
    r"""The manim directive, rendering videos while building
    the documentation.

    See the module docstring for documentation.
    """

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "hide_source": bool,
        "no_autoplay": bool,
        "quality": lambda arg: directives.choice(
            arg,
            ("low", "medium", "high", "fourk"),
        ),
        "save_as_gif": bool,
        "save_last_frame": bool,
        "ref_modules": lambda arg: process_name_list(arg, "mod"),
        "ref_classes": lambda arg: process_name_list(arg, "class"),
        "ref_functions": lambda arg: process_name_list(arg, "func"),
        "ref_methods": lambda arg: process_name_list(arg, "meth"),
    }
    final_argument_whitespace = True

    def run(self) -> list[nodes.Element]:
        # Rendering is skipped if the tag skip-manim is present,
        # or if we are making the pot-files
        should_skip = (
            "skip-manim" in self.state.document.settings.env.app.builder.tags.tags
            or self.state.document.settings.env.app.builder.name == "gettext"
        )
        if should_skip:
            clsname = self.arguments[0]
            node = SkipManimNode()
            self.state.nested_parse(
                StringList(
                    [
                        f"Placeholder block for ``{clsname}``.",
                        "",
                        ".. code-block:: python",
                        "",
                    ]
                    + ["    " + line for line in self.content]
                    + [
                        "",
                        ".. raw:: html",
                        "",
                        f'    <pre data-manim-binder data-manim-classname="{clsname}">',
                    ]
                    + ["    " + line for line in self.content]
                    + ["    </pre>"],
                ),
                self.content_offset,
                node,
            )
            return [node]

        from manim import config, tempconfig

        global classnamedict

        clsname = self.arguments[0]
        if clsname not in classnamedict:
            classnamedict[clsname] = 1
        else:
            classnamedict[clsname] += 1

        hide_source = "hide_source" in self.options
        no_autoplay = "no_autoplay" in self.options
        save_as_gif = "save_as_gif" in self.options
        save_last_frame = "save_last_frame" in self.options
        assert not (save_as_gif and save_last_frame)

        ref_content = (
            self.options.get("ref_modules", [])
            + self.options.get("ref_classes", [])
            + self.options.get("ref_functions", [])
            + self.options.get("ref_methods", [])
        )
        if ref_content:
            ref_block = "References: " + " ".join(ref_content)

        else:
            ref_block = ""

        if "quality" in self.options:
            quality = f'{self.options["quality"]}_quality'
        else:
            quality = "example_quality"
        frame_rate = QUALITIES[quality]["frame_rate"]
        pixel_height = QUALITIES[quality]["pixel_height"]
        pixel_width = QUALITIES[quality]["pixel_width"]

        state_machine = self.state_machine
        document = state_machine.document

        source_file_name = Path(document.attributes["source"])
        source_rel_name = source_file_name.relative_to(setup.confdir)
        source_rel_dir = source_rel_name.parents[0]
        dest_dir = Path(setup.app.builder.outdir, source_rel_dir).absolute()
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True, exist_ok=True)

        source_block = [
            ".. code-block:: python",
            "",
            "    from manim import *\n",
            *("    " + line for line in self.content),
            "",
            ".. raw:: html",
            "",
            f'    <pre data-manim-binder data-manim-classname="{clsname}">',
            *("    " + line for line in self.content),
            "",
            "    </pre>",
        ]
        source_block = "\n".join(source_block)

        config.media_dir = (Path(setup.confdir) / "media").absolute()
        config.images_dir = "{media_dir}/images"
        config.video_dir = "{media_dir}/videos/{quality}"
        output_file = f"{clsname}-{classnamedict[clsname]}"
        config.assets_dir = Path("_static")
        config.progress_bar = "none"
        config.verbosity = "WARNING"

        example_config = {
            "frame_rate": frame_rate,
            "no_autoplay": no_autoplay,
            "pixel_height": pixel_height,
            "pixel_width": pixel_width,
            "save_last_frame": save_last_frame,
            "write_to_movie": not save_last_frame,
            "output_file": output_file,
        }
        if save_last_frame:
            example_config["format"] = None
        if save_as_gif:
            example_config["format"] = "gif"

        user_code = self.content
        if user_code[0].startswith(">>> "):  # check whether block comes from doctest
            user_code = [
                line[4:] for line in user_code if line.startswith((">>> ", "... "))
            ]

        code = [
            "from manim import *",
            *user_code,
            f"{clsname}().render()",
        ]

        try:
            with tempconfig(example_config):
                run_time = timeit(lambda: exec("\n".join(code), globals()), number=1)
                video_dir = config.get_dir("video_dir")
                images_dir = config.get_dir("images_dir")
        except Exception as e:
            raise RuntimeError(f"Error while rendering example {clsname}") from e

        _write_rendering_stats(
            clsname,
            run_time,
            self.state.document.settings.env.docname,
        )

        # copy video file to output directory
        if not (save_as_gif or save_last_frame):
            filename = f"{output_file}.mp4"
            filesrc = video_dir / filename
            destfile = Path(dest_dir, filename)
            shutil.copyfile(filesrc, destfile)
        elif save_as_gif:
            filename = f"{output_file}.gif"
            filesrc = video_dir / filename
        elif save_last_frame:
            filename = f"{output_file}.png"
            filesrc = images_dir / filename
        else:
            raise ValueError("Invalid combination of render flags received.")
        rendered_template = jinja2.Template(TEMPLATE).render(
            clsname=clsname,
            clsname_lowercase=clsname.lower(),
            hide_source=hide_source,
            filesrc_rel=Path(filesrc).relative_to(setup.confdir).as_posix(),
            no_autoplay=no_autoplay,
            output_file=output_file,
            save_last_frame=save_last_frame,
            save_as_gif=save_as_gif,
            source_block=source_block,
            ref_block=ref_block,
        )
        state_machine.insert_input(
            rendered_template.split("\n"),
            source=document.attributes["source"],
        )

        return []


rendering_times_file_path = Path("../rendering_times.csv")


def _write_rendering_stats(scene_name: str, run_time: str, file_name: str) -> None:
    with rendering_times_file_path.open("a") as file:
        csv.writer(file).writerow(
            [
                re.sub(r"^(reference\/)|(manim\.)", "", file_name),
                scene_name,
                "%.3f" % run_time,
            ],
        )


def _log_rendering_times(*args: tuple[Any]) -> None:
    if rendering_times_file_path.exists():
        with rendering_times_file_path.open() as file:
            data = list(csv.reader(file))
        if len(data) == 0:
            sys.exit()

        print("\nRendering Summary\n-----------------\n")

        # filter out empty lists caused by csv reader
        data = [row for row in data if row]

        max_file_length = max(len(row[0]) for row in data)
        for key, group in it.groupby(data, key=lambda row: row[0]):
            key = key.ljust(max_file_length + 1, ".")
            group = list(group)
            if len(group) == 1:
                row = group[0]
                print(f"{key}{row[2].rjust(7, '.')}s {row[1]}")
                continue
            time_sum = sum(float(row[2]) for row in group)
            print(
                f"{key}{f'{time_sum:.3f}'.rjust(7, '.')}s  => {len(group)} EXAMPLES",
            )
            for row in group:
                print(f"{' ' * max_file_length} {row[2].rjust(7)}s {row[1]}")
        print("")


def _delete_rendering_times(*args: tuple[Any]) -> None:
    if rendering_times_file_path.exists():
        rendering_times_file_path.unlink()


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_node(SkipManimNode, html=(visit, depart))

    setup.app = app
    setup.config = app.config
    setup.confdir = app.confdir

    app.add_directive("manim", ManimDirective)

    app.connect("builder-inited", _delete_rendering_times)
    app.connect("build-finished", _log_rendering_times)

    app.add_js_file("manim-binder.min.js")
    app.add_js_file(
        None,
        body=textwrap.dedent(
            f"""\
                window.initManimBinder({{branch: "v{manim_version}"}})
            """
        ).strip(),
    )

    metadata = {"parallel_read_safe": False, "parallel_write_safe": True}
    return metadata


TEMPLATE = r"""
{% if not hide_source %}
.. raw:: html

    <div id="{{ clsname_lowercase }}" class="admonition admonition-manim-example">
    <p class="admonition-title">Example: {{ clsname }} <a class="headerlink" href="#{{ clsname_lowercase }}">¶</a></p>

{% endif %}

{% if not (save_as_gif or save_last_frame) %}
.. raw:: html

    <video
        class="manim-video"
        controls
        loop
        {{ '' if no_autoplay else 'autoplay' }}
        src="./{{ output_file }}.mp4">
    </video>

{% elif save_as_gif %}
.. image:: /{{ filesrc_rel }}
    :align: center

{% elif save_last_frame %}
.. image:: /{{ filesrc_rel }}
    :align: center

{% endif %}
{% if not hide_source %}
{{ source_block }}

{{ ref_block }}

.. raw:: html

    </div>

{% endif %}
"""


# Extracted from /Users/hochmax/learn/manim/manim/mobject/mobject.py
"""Base classes for objects that can be displayed."""

from __future__ import annotations

__all__ = ["Mobject", "Group", "override_animate"]


import copy
import inspect
import itertools as it
import math
import operator as op
import random
import sys
import types
import warnings
from collections.abc import Iterable
from functools import partialmethod, reduce
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Literal

import numpy as np

from manim.mobject.opengl.opengl_compatibility import ConvertToOpenGL

from .. import config, logger
from ..constants import *
from ..utils.color import (
    BLACK,
    WHITE,
    YELLOW_C,
    ManimColor,
    ParsableManimColor,
    color_gradient,
    interpolate_color,
)
from ..utils.exceptions import MultiAnimationOverrideException
from ..utils.iterables import list_update, remove_list_redundancies
from ..utils.paths import straight_path
from ..utils.space_ops import angle_between_vectors, normalize, rotation_matrix

if TYPE_CHECKING:
    from typing_extensions import Self, TypeAlias

    from manim.typing import (
        FunctionOverride,
        Image,
        ManimFloat,
        ManimInt,
        MappingFunction,
        PathFuncType,
        Point3D,
        Point3D_Array,
        Vector3D,
    )

    from ..animation.animation import Animation

    TimeBasedUpdater: TypeAlias = Callable[["Mobject", float], object]
    NonTimeBasedUpdater: TypeAlias = Callable[["Mobject"], object]
    Updater: TypeAlias = NonTimeBasedUpdater | TimeBasedUpdater


class Mobject:
    """Mathematical Object: base class for objects that can be displayed on screen.

    There is a compatibility layer that allows for
    getting and setting generic attributes with ``get_*``
    and ``set_*`` methods. See :meth:`set` for more details.

    Attributes
    ----------
    submobjects : List[:class:`Mobject`]
        The contained objects.
    points : :class:`numpy.ndarray`
        The points of the objects.

        .. seealso::

            :class:`~.VMobject`

    """

    animation_overrides = {}

    @classmethod
    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        cls.animation_overrides: dict[
            type[Animation],
            FunctionOverride,
        ] = {}
        cls._add_intrinsic_animation_overrides()
        cls._original__init__ = cls.__init__

    def __init__(
        self,
        color: ParsableManimColor | list[ParsableManimColor] = WHITE,
        name: str | None = None,
        dim: int = 3,
        target=None,
        z_index: float = 0,
    ) -> None:
        self.name = self.__class__.__name__ if name is None else name
        self.dim = dim
        self.target = target
        self.z_index = z_index
        self.point_hash = None
        self.submobjects = []
        self.updaters: list[Updater] = []
        self.updating_suspended = False
        self.color = ManimColor.parse(color)

        self.reset_points()
        self.generate_points()
        self.init_colors()

    def _assert_valid_submobjects(self, submobjects: Iterable[Mobject]) -> Self:
        """Check that all submobjects are actually instances of
        :class:`Mobject`, and that none of them is ``self`` (a
        :class:`Mobject` cannot contain itself).

        This is an auxiliary function called when adding Mobjects to the
        :attr:`submobjects` list.

        This function is intended to be overridden by subclasses such as
        :class:`VMobject`, which should assert that only other VMobjects
        may be added into it.

        Parameters
        ----------
        submobjects
            The list containing values to validate.

        Returns
        -------
        :class:`Mobject`
            The Mobject itself.

        Raises
        ------
        TypeError
            If any of the values in `submobjects` is not a :class:`Mobject`.
        ValueError
            If there was an attempt to add a :class:`Mobject` as its own
            submobject.
        """
        return self._assert_valid_submobjects_internal(submobjects, Mobject)

    def _assert_valid_submobjects_internal(
        self, submobjects: list[Mobject], mob_class: type[Mobject]
    ) -> Self:
        for i, submob in enumerate(submobjects):
            if not isinstance(submob, mob_class):
                error_message = (
                    f"Only values of type {mob_class.__name__} can be added "
                    f"as submobjects of {type(self).__name__}, but the value "
                    f"{submob} (at index {i}) is of type "
                    f"{type(submob).__name__}."
                )
                # Intended for subclasses such as VMobject, which
                # cannot have regular Mobjects as submobjects
                if isinstance(submob, Mobject):
                    error_message += (
                        " You can try adding this value into a Group instead."
                    )
                raise TypeError(error_message)
            if submob is self:
                raise ValueError(
                    f"Cannot add {type(self).__name__} as a submobject of "
                    f"itself (at index {i})."
                )
        return self

    @classmethod
    def animation_override_for(
        cls,
        animation_class: type[Animation],
    ) -> FunctionOverride | None:
        """Returns the function defining a specific animation override for this class.

        Parameters
        ----------
        animation_class
            The animation class for which the override function should be returned.

        Returns
        -------
        Optional[Callable[[Mobject, ...], Animation]]
            The function returning the override animation or ``None`` if no such animation
            override is defined.
        """
        if animation_class in cls.animation_overrides:
            return cls.animation_overrides[animation_class]

        return None

    @classmethod
    def _add_intrinsic_animation_overrides(cls) -> None:
        """Initializes animation overrides marked with the :func:`~.override_animation`
        decorator.
        """
        for method_name in dir(cls):
            # Ignore dunder methods
            if method_name.startswith("__"):
                continue

            method = getattr(cls, method_name)
            if hasattr(method, "_override_animation"):
                animation_class = method._override_animation
                cls.add_animation_override(animation_class, method)

    @classmethod
    def add_animation_override(
        cls,
        animation_class: type[Animation],
        override_func: FunctionOverride,
    ) -> None:
        """Add an animation override.

        This does not apply to subclasses.

        Parameters
        ----------
        animation_class
            The animation type to be overridden
        override_func
            The function returning an animation replacing the default animation. It gets
            passed the parameters given to the animation constructor.

        Raises
        ------
        MultiAnimationOverrideException
            If the overridden animation was already overridden.
        """
        if animation_class not in cls.animation_overrides:
            cls.animation_overrides[animation_class] = override_func
        else:
            raise MultiAnimationOverrideException(
                f"The animation {animation_class.__name__} for "
                f"{cls.__name__} is overridden by more than one method: "
                f"{cls.animation_overrides[animation_class].__qualname__} and "
                f"{override_func.__qualname__}.",
            )

    @classmethod
    def set_default(cls, **kwargs) -> None:
        """Sets the default values of keyword arguments.

        If this method is called without any additional keyword
        arguments, the original default values of the initialization
        method of this class are restored.

        Parameters
        ----------

        kwargs
            Passing any keyword argument will update the default
            values of the keyword arguments of the initialization
            function of this class.

        Examples
        --------

        ::

            >>> from manim import Square, GREEN
            >>> Square.set_default(color=GREEN, fill_opacity=0.25)
            >>> s = Square(); s.color, s.fill_opacity
            (ManimColor('#83C167'), 0.25)
            >>> Square.set_default()
            >>> s = Square(); s.color, s.fill_opacity
            (ManimColor('#FFFFFF'), 0.0)

        .. manim:: ChangedDefaultTextcolor
            :save_last_frame:

            config.background_color = WHITE

            class ChangedDefaultTextcolor(Scene):
                def construct(self):
                    Text.set_default(color=BLACK)
                    self.add(Text("Changing default values is easy!"))

                    # we revert the colour back to the default to prevent a bug in the docs.
                    Text.set_default(color=WHITE)

        """
        if kwargs:
            cls.__init__ = partialmethod(cls.__init__, **kwargs)
        else:
            cls.__init__ = cls._original__init__

    @property
    def animate(self) -> _AnimationBuilder | Self:
        """Used to animate the application of any method of :code:`self`.

        Any method called on :code:`animate` is converted to an animation of applying
        that method on the mobject itself.

        For example, :code:`square.set_fill(WHITE)` sets the fill color of a square,
        while :code:`square.animate.set_fill(WHITE)` animates this action.

        Multiple methods can be put in a single animation once via chaining:

        ::

            self.play(my_mobject.animate.shift(RIGHT).rotate(PI))

        .. warning::

            Passing multiple animations for the same :class:`Mobject` in one
            call to :meth:`~.Scene.play` is discouraged and will most likely
            not work properly. Instead of writing an animation like

            ::

                self.play(my_mobject.animate.shift(RIGHT), my_mobject.animate.rotate(PI))

            make use of method chaining.

        Keyword arguments that can be passed to :meth:`.Scene.play` can be passed
        directly after accessing ``.animate``, like so::

            self.play(my_mobject.animate(rate_func=linear).shift(RIGHT))

        This is especially useful when animating simultaneous ``.animate`` calls that
        you want to behave differently::

            self.play(
                mobject1.animate(run_time=2).rotate(PI),
                mobject2.animate(rate_func=there_and_back).shift(RIGHT),
            )

        .. seealso::

            :func:`override_animate`


        Examples
        --------

        .. manim:: AnimateExample

            class AnimateExample(Scene):
                def construct(self):
                    s = Square()
                    self.play(Create(s))
                    self.play(s.animate.shift(RIGHT))
                    self.play(s.animate.scale(2))
                    self.play(s.animate.rotate(PI / 2))
                    self.play(Uncreate(s))


        .. manim:: AnimateChainExample

            class AnimateChainExample(Scene):
                def construct(self):
                    s = Square()
                    self.play(Create(s))
                    self.play(s.animate.shift(RIGHT).scale(2).rotate(PI / 2))
                    self.play(Uncreate(s))

        .. manim:: AnimateWithArgsExample

            class AnimateWithArgsExample(Scene):
                def construct(self):
                    s = Square()
                    c = Circle()

                    VGroup(s, c).arrange(RIGHT, buff=2)
                    self.add(s, c)

                    self.play(
                        s.animate(run_time=2).rotate(PI / 2),
                        c.animate(rate_func=there_and_back).shift(RIGHT),
                    )

        .. warning::

            ``.animate``
             will interpolate the :class:`~.Mobject` between its points prior to
             ``.animate`` and its points after applying ``.animate`` to it. This may
             result in unexpected behavior when attempting to interpolate along paths,
             or rotations.
             If you want animations to consider the points between, consider using
             :class:`~.ValueTracker` with updaters instead.

        """
        return _AnimationBuilder(self)

    def __deepcopy__(self, clone_from_id) -> Self:
        cls = self.__class__
        result = cls.__new__(cls)
        clone_from_id[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, clone_from_id))
        result.original_id = str(id(self))
        return result

    def __repr__(self) -> str:
        return str(self.name)

    def reset_points(self) -> None:
        """Sets :attr:`points` to be an empty array."""
        self.points = np.zeros((0, self.dim))

    def init_colors(self) -> None:
        """Initializes the colors.

        Gets called upon creation. This is an empty method that can be implemented by
        subclasses.
        """

    def generate_points(self) -> None:
        """Initializes :attr:`points` and therefore the shape.

        Gets called upon creation. This is an empty method that can be implemented by
        subclasses.
        """

    def add(self, *mobjects: Mobject) -> Self:
        """Add mobjects as submobjects.

        The mobjects are added to :attr:`submobjects`.

        Subclasses of mobject may implement ``+`` and ``+=`` dunder methods.

        Parameters
        ----------
        mobjects
            The mobjects to add.

        Returns
        -------
        :class:`Mobject`
            ``self``

        Raises
        ------
        :class:`ValueError`
            When a mobject tries to add itself.
        :class:`TypeError`
            When trying to add an object that is not an instance of :class:`Mobject`.


        Notes
        -----
        A mobject cannot contain itself, and it cannot contain a submobject
        more than once.  If the parent mobject is displayed, the newly-added
        submobjects will also be displayed (i.e. they are automatically added
        to the parent Scene).

        See Also
        --------
        :meth:`remove`
        :meth:`add_to_back`

        Examples
        --------
        ::

            >>> outer = Mobject()
            >>> inner = Mobject()
            >>> outer = outer.add(inner)

        Duplicates are not added again::

            >>> outer = outer.add(inner)
            >>> len(outer.submobjects)
            1

        Only Mobjects can be added::

            >>> outer.add(3)
            Traceback (most recent call last):
            ...
            TypeError: Only values of type Mobject can be added as submobjects of Mobject, but the value 3 (at index 0) is of type int.

        Adding an object to itself raises an error::

            >>> outer.add(outer)
            Traceback (most recent call last):
            ...
            ValueError: Cannot add Mobject as a submobject of itself (at index 0).

        A given mobject cannot be added as a submobject
        twice to some parent::

            >>> parent = Mobject(name="parent")
            >>> child = Mobject(name="child")
            >>> parent.add(child, child)
            [...] WARNING  ...
            parent
            >>> parent.submobjects
            [child]

        """
        self._assert_valid_submobjects(mobjects)
        unique_mobjects = remove_list_redundancies(mobjects)
        if len(mobjects) != len(unique_mobjects):
            logger.warning(
                "Attempted adding some Mobject as a child more than once, "
                "this is not possible. Repetitions are ignored.",
            )

        self.submobjects = list_update(self.submobjects, unique_mobjects)
        return self

    def insert(self, index: int, mobject: Mobject) -> None:
        """Inserts a mobject at a specific position into self.submobjects

        Effectively just calls  ``self.submobjects.insert(index, mobject)``,
        where ``self.submobjects`` is a list.

        Highly adapted from ``Mobject.add``.

        Parameters
        ----------
        index
            The index at which
        mobject
            The mobject to be inserted.
        """
        self._assert_valid_submobjects([mobject])
        self.submobjects.insert(index, mobject)

    def __add__(self, mobject: Mobject):
        raise NotImplementedError

    def __iadd__(self, mobject: Mobject):
        raise NotImplementedError

    def add_to_back(self, *mobjects: Mobject) -> Self:
        """Add all passed mobjects to the back of the submobjects.

        If :attr:`submobjects` already contains the given mobjects, they just get moved
        to the back instead.

        Parameters
        ----------
        mobjects
            The mobjects to add.

        Returns
        -------
        :class:`Mobject`
            ``self``


        .. note::

            Technically, this is done by adding (or moving) the mobjects to
            the head of :attr:`submobjects`. The head of this list is rendered
            first, which places the corresponding mobjects behind the
            subsequent list members.

        Raises
        ------
        :class:`ValueError`
            When a mobject tries to add itself.
        :class:`TypeError`
            When trying to add an object that is not an instance of :class:`Mobject`.

        Notes
        -----
        A mobject cannot contain itself, and it cannot contain a submobject
        more than once.  If the parent mobject is displayed, the newly-added
        submobjects will also be displayed (i.e. they are automatically added
        to the parent Scene).

        See Also
        --------
        :meth:`remove`
        :meth:`add`

        """
        self._assert_valid_submobjects(mobjects)
        self.remove(*mobjects)
        # dict.fromkeys() removes duplicates while maintaining order
        self.submobjects = list(dict.fromkeys(mobjects)) + self.submobjects
        return self

    def remove(self, *mobjects: Mobject) -> Self:
        """Remove :attr:`submobjects`.

        The mobjects are removed from :attr:`submobjects`, if they exist.

        Subclasses of mobject may implement ``-`` and ``-=`` dunder methods.

        Parameters
        ----------
        mobjects
            The mobjects to remove.

        Returns
        -------
        :class:`Mobject`
            ``self``

        See Also
        --------
        :meth:`add`

        """
        for mobject in mobjects:
            if mobject in self.submobjects:
                self.submobjects.remove(mobject)
        return self

    def __sub__(self, other):
        raise NotImplementedError

    def __isub__(self, other):
        raise NotImplementedError

    def set(self, **kwargs) -> Self:
        """Sets attributes.

        I.e. ``my_mobject.set(foo=1)`` applies ``my_mobject.foo = 1``.

        This is a convenience to be used along with :attr:`animate` to
        animate setting attributes.

        In addition to this method, there is a compatibility
        layer that allows ``get_*`` and ``set_*`` methods to
        get and set generic attributes. For instance::

            >>> mob = Mobject()
            >>> mob.set_foo(0)
            Mobject
            >>> mob.get_foo()
            0
            >>> mob.foo
            0

        This compatibility layer does not interfere with any
        ``get_*`` or ``set_*`` methods that are explicitly
        defined.

        .. warning::

            This compatibility layer is for backwards compatibility
            and is not guaranteed to stay around. Where applicable,
            please prefer getting/setting attributes normally or with
            the :meth:`set` method.

        Parameters
        ----------
        **kwargs
            The attributes and corresponding values to set.

        Returns
        -------
        :class:`Mobject`
            ``self``

        Examples
        --------
        ::

            >>> mob = Mobject()
            >>> mob.set(foo=0)
            Mobject
            >>> mob.foo
            0
        """

        for attr, value in kwargs.items():
            setattr(self, attr, value)

        return self

    def __getattr__(self, attr: str) -> types.MethodType:
        # Add automatic compatibility layer
        # between properties and get_* and set_*
        # methods.
        #
        # In python 3.9+ we could change this
        # logic to use str.remove_prefix instead.

        if attr.startswith("get_"):
            # Remove the "get_" prefix
            to_get = attr[4:]

            def getter(self):
                warnings.warn(
                    "This method is not guaranteed to stay around. Please prefer "
                    "getting the attribute normally.",
                    DeprecationWarning,
                    stacklevel=2,
                )

                return getattr(self, to_get)

            # Return a bound method
            return types.MethodType(getter, self)

        if attr.startswith("set_"):
            # Remove the "set_" prefix
            to_set = attr[4:]

            def setter(self, value):
                warnings.warn(
                    "This method is not guaranteed to stay around. Please prefer "
                    "setting the attribute normally or with Mobject.set().",
                    DeprecationWarning,
                    stacklevel=2,
                )

                setattr(self, to_set, value)

                return self

            # Return a bound method
            return types.MethodType(setter, self)

        # Unhandled attribute, therefore error
        raise AttributeError(f"{type(self).__name__} object has no attribute '{attr}'")

    @property
    def width(self) -> float:
        """The width of the mobject.

        Returns
        -------
        :class:`float`

        Examples
        --------
        .. manim:: WidthExample

            class WidthExample(Scene):
                def construct(self):
                    decimal = DecimalNumber().to_edge(UP)
                    rect = Rectangle(color=BLUE)
                    rect_copy = rect.copy().set_stroke(GRAY, opacity=0.5)

                    decimal.add_updater(lambda d: d.set_value(rect.width))

                    self.add(rect_copy, rect, decimal)
                    self.play(rect.animate.set(width=7))
                    self.wait()

        See also
        --------
        :meth:`length_over_dim`

        """

        # Get the length across the X dimension
        return self.length_over_dim(0)

    @width.setter
    def width(self, value: float):
        self.scale_to_fit_width(value)

    @property
    def height(self) -> float:
        """The height of the mobject.

        Returns
        -------
        :class:`float`

        Examples
        --------
        .. manim:: HeightExample

            class HeightExample(Scene):
                def construct(self):
                    decimal = DecimalNumber().to_edge(UP)
                    rect = Rectangle(color=BLUE)
                    rect_copy = rect.copy().set_stroke(GRAY, opacity=0.5)

                    decimal.add_updater(lambda d: d.set_value(rect.height))

                    self.add(rect_copy, rect, decimal)
                    self.play(rect.animate.set(height=5))
                    self.wait()

        See also
        --------
        :meth:`length_over_dim`

        """

        # Get the length across the Y dimension
        return self.length_over_dim(1)

    @height.setter
    def height(self, value: float):
        self.scale_to_fit_height(value)

    @property
    def depth(self) -> float:
        """The depth of the mobject.

        Returns
        -------
        :class:`float`

        See also
        --------
        :meth:`length_over_dim`

        """

        # Get the length across the Z dimension
        return self.length_over_dim(2)

    @depth.setter
    def depth(self, value: float):
        self.scale_to_fit_depth(value)

    # Can't be staticmethod because of point_cloud_mobject.py
    def get_array_attrs(self) -> list[Literal["points"]]:
        return ["points"]

    def apply_over_attr_arrays(self, func: MappingFunction) -> Self:
        for attr in self.get_array_attrs():
            setattr(self, attr, func(getattr(self, attr)))
        return self

    # Displaying

    def get_image(self, camera=None) -> Image:
        if camera is None:
            from ..camera.camera import Camera

            camera = Camera()
        camera.capture_mobject(self)
        return camera.get_image()

    def show(self, camera=None) -> None:
        self.get_image(camera=camera).show()

    def save_image(self, name: str | None = None) -> None:
        """Saves an image of only this :class:`Mobject` at its position to a png
        file."""
        self.get_image().save(
            Path(config.get_dir("video_dir")).joinpath((name or str(self)) + ".png"),
        )

    def copy(self) -> Self:
        """Create and return an identical copy of the :class:`Mobject` including all
        :attr:`submobjects`.

        Returns
        -------
        :class:`Mobject`
            The copy.

        Note
        ----
        The clone is initially not visible in the Scene, even if the original was.
        """
        return copy.deepcopy(self)

    def generate_target(self, use_deepcopy: bool = False) -> Self:
        self.target = None  # Prevent unbounded linear recursion
        if use_deepcopy:
            self.target = copy.deepcopy(self)
        else:
            self.target = self.copy()
        return self.target

    # Updating

    def update(self, dt: float = 0, recursive: bool = True) -> Self:
        """Apply all updaters.

        Does nothing if updating is suspended.

        Parameters
        ----------
        dt
            The parameter ``dt`` to pass to the update functions. Usually this is the
            time in seconds since the last call of ``update``.
        recursive
            Whether to recursively update all submobjects.

        Returns
        -------
        :class:`Mobject`
            ``self``

        See Also
        --------
        :meth:`add_updater`
        :meth:`get_updaters`

        """
        if self.updating_suspended:
            return self
        for updater in self.updaters:
            if "dt" in inspect.signature(updater).parameters:
                updater(self, dt)
            else:
                updater(self)
        if recursive:
            for submob in self.submobjects:
                submob.update(dt, recursive)
        return self

    def get_time_based_updaters(self) -> list[TimeBasedUpdater]:
        """Return all updaters using the ``dt`` parameter.

        The updaters use this parameter as the input for difference in time.

        Returns
        -------
        List[:class:`Callable`]
            The list of time based updaters.

        See Also
        --------
        :meth:`get_updaters`
        :meth:`has_time_based_updater`

        """
        return [
            updater
            for updater in self.updaters
            if "dt" in inspect.signature(updater).parameters
        ]

    def has_time_based_updater(self) -> bool:
        """Test if ``self`` has a time based updater.

        Returns
        -------
        :class:`bool`
            ``True`` if at least one updater uses the ``dt`` parameter, ``False``
            otherwise.

        See Also
        --------
        :meth:`get_time_based_updaters`

        """
        return any(
            "dt" in inspect.signature(updater).parameters for updater in self.updaters
        )

    def get_updaters(self) -> list[Updater]:
        """Return all updaters.

        Returns
        -------
        List[:class:`Callable`]
            The list of updaters.

        See Also
        --------
        :meth:`add_updater`
        :meth:`get_time_based_updaters`

        """
        return self.updaters

    def get_family_updaters(self) -> list[Updater]:
        return list(it.chain(*(sm.get_updaters() for sm in self.get_family())))

    def add_updater(
        self,
        update_function: Updater,
        index: int | None = None,
        call_updater: bool = False,
    ) -> Self:
        """Add an update function to this mobject.

        Update functions, or updaters in short, are functions that are applied to the
        Mobject in every frame.

        Parameters
        ----------
        update_function
            The update function to be added.
            Whenever :meth:`update` is called, this update function gets called using
            ``self`` as the first parameter.
            The updater can have a second parameter ``dt``. If it uses this parameter,
            it gets called using a second value ``dt``, usually representing the time
            in seconds since the last call of :meth:`update`.
        index
            The index at which the new updater should be added in ``self.updaters``.
            In case ``index`` is ``None`` the updater will be added at the end.
        call_updater
            Whether or not to call the updater initially. If ``True``, the updater will
            be called using ``dt=0``.

        Returns
        -------
        :class:`Mobject`
            ``self``

        Examples
        --------
        .. manim:: NextToUpdater

            class NextToUpdater(Scene):
                def construct(self):
                    def dot_position(mobject):
                        mobject.set_value(dot.get_center()[0])
                        mobject.next_to(dot)

                    dot = Dot(RIGHT*3)
                    label = DecimalNumber()
                    label.add_updater(dot_position)
                    self.add(dot, label)

                    self.play(Rotating(dot, about_point=ORIGIN, angle=TAU, run_time=TAU, rate_func=linear))

        .. manim:: DtUpdater

            class DtUpdater(Scene):
                def construct(self):
                    square = Square()

                    #Let the square rotate 90° per second
                    square.add_updater(lambda mobject, dt: mobject.rotate(dt*90*DEGREES))
                    self.add(square)
                    self.wait(2)

        See also
        --------
        :meth:`get_updaters`
        :meth:`remove_updater`
        :class:`~.UpdateFromFunc`
        """

        if index is None:
            self.updaters.append(update_function)
        else:
            self.updaters.insert(index, update_function)
        if call_updater:
            parameters = inspect.signature(update_function).parameters
            if "dt" in parameters:
                update_function(self, 0)
            else:
                update_function(self)
        return self

    def remove_updater(self, update_function: Updater) -> Self:
        """Remove an updater.

        If the same updater is applied multiple times, every instance gets removed.

        Parameters
        ----------
        update_function
            The update function to be removed.


        Returns
        -------
        :class:`Mobject`
            ``self``

        See also
        --------
        :meth:`clear_updaters`
        :meth:`add_updater`
        :meth:`get_updaters`

        """
        while update_function in self.updaters:
            self.updaters.remove(update_function)
        return self

    def clear_updaters(self, recursive: bool = True) -> Self:
        """Remove every updater.

        Parameters
        ----------
        recursive
            Whether to recursively call ``clear_updaters`` on all submobjects.

        Returns
        -------
        :class:`Mobject`
            ``self``

        See also
        --------
        :meth:`remove_updater`
        :meth:`add_updater`
        :meth:`get_updaters`

        """
        self.updaters = []
        if recursive:
            for submob in self.submobjects:
                submob.clear_updaters()
        return self

    def match_updaters(self, mobject: Mobject) -> Self:
        """Match the updaters of the given mobject.

        Parameters
        ----------
        mobject
            The mobject whose updaters get matched.

        Returns
        -------
        :class:`Mobject`
            ``self``

        Note
        ----
        All updaters from submobjects are removed, but only updaters of the given
        mobject are matched, not those of it's submobjects.

        See also
        --------
        :meth:`add_updater`
        :meth:`clear_updaters`

        """

        self.clear_updaters()
        for updater in mobject.get_updaters():
            self.add_updater(updater)
        return self

    def suspend_updating(self, recursive: bool = True) -> Self:
        """Disable updating from updaters and animations.


        Parameters
        ----------
        recursive
            Whether to recursively suspend updating on all submobjects.

        Returns
        -------
        :class:`Mobject`
            ``self``

        See also
        --------
        :meth:`resume_updating`
        :meth:`add_updater`

        """

        self.updating_suspended = True
        if recursive:
            for submob in self.submobjects:
                submob.suspend_updating(recursive)
        return self

    def resume_updating(self, recursive: bool = True) -> Self:
        """Enable updating from updaters and animations.

        Parameters
        ----------
        recursive
            Whether to recursively enable updating on all submobjects.

        Returns
        -------
        :class:`Mobject`
            ``self``

        See also
        --------
        :meth:`suspend_updating`
        :meth:`add_updater`

        """
        self.updating_suspended = False
        if recursive:
            for submob in self.submobjects:
                submob.resume_updating(recursive)
        self.update(dt=0, recursive=recursive)
        return self

    # Transforming operations

    def apply_to_family(self, func: Callable[[Mobject], None]) -> None:
        """Apply a function to ``self`` and every submobject with points recursively.

        Parameters
        ----------
        func
            The function to apply to each mobject. ``func`` gets passed the respective
            (sub)mobject as parameter.

        Returns
        -------
        :class:`Mobject`
            ``self``

        See also
        --------
        :meth:`family_members_with_points`

        """
        for mob in self.family_members_with_points():
            func(mob)

    def shift(self, *vectors: Vector3D) -> Self:
        """Shift by the given vectors.

        Parameters
        ----------
        vectors
            Vectors to shift by. If multiple vectors are given, they are added
            together.

        Returns
        -------
        :class:`Mobject`
            ``self``

        See also
        --------
        :meth:`move_to`
        """

        total_vector = reduce(op.add, vectors)
        for mob in self.family_members_with_points():
            mob.points = mob.points.astype("float")
            mob.points += total_vector

        return self

    def scale(self, scale_factor: float, **kwargs) -> Self:
        r"""Scale the size by a factor.

        Default behavior is to scale about the center of the mobject.

        Parameters
        ----------
        scale_factor
            The scaling factor :math:`\alpha`. If :math:`0 < |\alpha| < 1`, the mobject
            will shrink, and for :math:`|\alpha| > 1` it will grow. Furthermore,
            if :math:`\alpha < 0`, the mobject is also flipped.
        kwargs
            Additional keyword arguments passed to
            :meth:`apply_points_function_about_point`.

        Returns
        -------
        :class:`Mobject`
            ``self``

        Examples
        --------

        .. manim:: MobjectScaleExample
            :save_last_frame:

            class MobjectScaleExample(Scene):
                def construct(self):
                    f1 = Text("F")
                    f2 = Text("F").scale(2)
                    f3 = Text("F").scale(0.5)
                    f4 = Text("F").scale(-1)

                    vgroup = VGroup(f1, f2, f3, f4).arrange(6 * RIGHT)
                    self.add(vgroup)

        See also
        --------
        :meth:`move_to`

        """
        self.apply_points_function_about_point(
            lambda points: scale_factor * points, **kwargs
        )
        return self

    def rotate_about_origin(self, angle: float, axis: Vector3D = OUT, axes=[]) -> Self:
        """Rotates the :class:`~.Mobject` about the ORIGIN, which is at [0,0,0]."""
        return self.rotate(angle, axis, about_point=ORIGIN)

    def rotate(
        self,
        angle: float,
        axis: Vector3D = OUT,
        about_point: Point3D | None = None,
        **kwargs,
    ) -> Self:
        """Rotates the :class:`~.Mobject` about a certain point."""
        rot_matrix = rotation_matrix(angle, axis)
        self.apply_points_function_about_point(
            lambda points: np.dot(points, rot_matrix.T), about_point, **kwargs
        )
        return self

    def flip(self, axis: Vector3D = UP, **kwargs) -> Self:
        """Flips/Mirrors an mobject about its center.

        Examples
        --------

        .. manim:: FlipExample
            :save_last_frame:

            class FlipExample(Scene):
                def construct(self):
                    s= Line(LEFT, RIGHT+UP).shift(4*LEFT)
                    self.add(s)
                    s2= s.copy().flip()
                    self.add(s2)

        """
        return self.rotate(TAU / 2, axis, **kwargs)

    def stretch(self, factor: float, dim: int, **kwargs) -> Self:
        def func(points):
            points[:, dim] *= factor
            return points

        self.apply_points_function_about_point(func, **kwargs)
        return self

    def apply_function(self, function: MappingFunction, **kwargs) -> Self:
        # Default to applying matrix about the origin, not mobjects center
        if len(kwargs) == 0:
            kwargs["about_point"] = ORIGIN
        self.apply_points_function_about_point(
            lambda points: np.apply_along_axis(function, 1, points), **kwargs
        )
        return self

    def apply_function_to_position(self, function: MappingFunction) -> Self:
        self.move_to(function(self.get_center()))
        return self

    def apply_function_to_submobject_positions(self, function: MappingFunction) -> Self:
        for submob in self.submobjects:
            submob.apply_function_to_position(function)
        return self

    def apply_matrix(self, matrix, **kwargs) -> Self:
        # Default to applying matrix about the origin, not mobjects center
        if ("about_point" not in kwargs) and ("about_edge" not in kwargs):
            kwargs["about_point"] = ORIGIN
        full_matrix = np.identity(self.dim)
        matrix = np.array(matrix)
        full_matrix[: matrix.shape[0], : matrix.shape[1]] = matrix
        self.apply_points_function_about_point(
            lambda points: np.dot(points, full_matrix.T), **kwargs
        )
        return self

    def apply_complex_function(
        self, function: Callable[[complex], complex], **kwargs
    ) -> Self:
        """Applies a complex function to a :class:`Mobject`.
        The x and y Point3Ds correspond to the real and imaginary parts respectively.

        Example
        -------

        .. manim:: ApplyFuncExample

            class ApplyFuncExample(Scene):
                def construct(self):
                    circ = Circle().scale(1.5)
                    circ_ref = circ.copy()
                    circ.apply_complex_function(
                        lambda x: np.exp(x*1j)
                    )
                    t = ValueTracker(0)
                    circ.add_updater(
                        lambda x: x.become(circ_ref.copy().apply_complex_function(
                            lambda x: np.exp(x+t.get_value()*1j)
                        )).set_color(BLUE)
                    )
                    self.add(circ_ref)
                    self.play(TransformFromCopy(circ_ref, circ))
                    self.play(t.animate.set_value(TAU), run_time=3)
        """

        def R3_func(point):
            x, y, z = point
            xy_complex = function(complex(x, y))
            return [xy_complex.real, xy_complex.imag, z]

        return self.apply_function(R3_func)

    def reverse_points(self) -> Self:
        for mob in self.family_members_with_points():
            mob.apply_over_attr_arrays(lambda arr: np.array(list(reversed(arr))))
        return self

    def repeat(self, count: int) -> Self:
        """This can make transition animations nicer"""

        def repeat_array(array):
            return reduce(lambda a1, a2: np.append(a1, a2, axis=0), [array] * count)

        for mob in self.family_members_with_points():
            mob.apply_over_attr_arrays(repeat_array)
        return self

    # In place operations.
    # Note, much of these are now redundant with default behavior of
    # above methods

    def apply_points_function_about_point(
        self,
        func: MappingFunction,
        about_point: Point3D = None,
        about_edge=None,
    ) -> Self:
        if about_point is None:
            if about_edge is None:
                about_edge = ORIGIN
            about_point = self.get_critical_point(about_edge)
        for mob in self.family_members_with_points():
            mob.points -= about_point
            mob.points = func(mob.points)
            mob.points += about_point
        return self

    def pose_at_angle(self, **kwargs):
        self.rotate(TAU / 14, RIGHT + UP, **kwargs)
        return self

    # Positioning methods

    def center(self) -> Self:
        """Moves the center of the mobject to the center of the scene.

        Returns
        -------
        :class:`.Mobject`
            The centered mobject.
        """
        self.shift(-self.get_center())
        return self

    def align_on_border(
        self, direction: Vector3D, buff: float = DEFAULT_MOBJECT_TO_EDGE_BUFFER
    ) -> Self:
        """Direction just needs to be a vector pointing towards side or
        corner in the 2d plane.
        """
        target_point = np.sign(direction) * (
            config["frame_x_radius"],
            config["frame_y_radius"],
            0,
        )
        point_to_align = self.get_critical_point(direction)
        shift_val = target_point - point_to_align - buff * np.array(direction)
        shift_val = shift_val * abs(np.sign(direction))
        self.shift(shift_val)
        return self

    def to_corner(
        self, corner: Vector3D = DL, buff: float = DEFAULT_MOBJECT_TO_EDGE_BUFFER
    ) -> Self:
        """Moves this :class:`~.Mobject` to the given corner of the screen.

        Returns
        -------
        :class:`.Mobject`
            The newly positioned mobject.

        Examples
        --------

        .. manim:: ToCornerExample
            :save_last_frame:

            class ToCornerExample(Scene):
                def construct(self):
                    c = Circle()
                    c.to_corner(UR)
                    t = Tex("To the corner!")
                    t2 = MathTex("x^3").shift(DOWN)
                    self.add(c,t,t2)
                    t.to_corner(DL, buff=0)
                    t2.to_corner(UL, buff=1.5)
        """
        return self.align_on_border(corner, buff)

    def to_edge(
        self, edge: Vector3D = LEFT, buff: float = DEFAULT_MOBJECT_TO_EDGE_BUFFER
    ) -> Self:
        """Moves this :class:`~.Mobject` to the given edge of the screen,
        without affecting its position in the other dimension.

        Returns
        -------
        :class:`.Mobject`
            The newly positioned mobject.

        Examples
        --------

        .. manim:: ToEdgeExample
            :save_last_frame:

            class ToEdgeExample(Scene):
                def construct(self):
                    tex_top = Tex("I am at the top!")
                    tex_top.to_edge(UP)
                    tex_side = Tex("I am moving to the side!")
                    c = Circle().shift(2*DOWN)
                    self.add(tex_top, tex_side)
                    tex_side.to_edge(LEFT)
                    c.to_edge(RIGHT, buff=0)

        """
        return self.align_on_border(edge, buff)

    def next_to(
        self,
        mobject_or_point: Mobject | Point3D,
        direction: Vector3D = RIGHT,
        buff: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
        aligned_edge: Vector3D = ORIGIN,
        submobject_to_align: Mobject | None = None,
        index_of_submobject_to_align: int | None = None,
        coor_mask: Vector3D = np.array([1, 1, 1]),
    ) -> Self:
        """Move this :class:`~.Mobject` next to another's :class:`~.Mobject` or Point3D.

        Examples
        --------

        .. manim:: GeometricShapes
            :save_last_frame:

            class GeometricShapes(Scene):
                def construct(self):
                    d = Dot()
                    c = Circle()
                    s = Square()
                    t = Triangle()
                    d.next_to(c, RIGHT)
                    s.next_to(c, LEFT)
                    t.next_to(c, DOWN)
                    self.add(d, c, s, t)

        """
        if isinstance(mobject_or_point, Mobject):
            mob = mobject_or_point
            if index_of_submobject_to_align is not None:
                target_aligner = mob[index_of_submobject_to_align]
            else:
                target_aligner = mob
            target_point = target_aligner.get_critical_point(aligned_edge + direction)
        else:
            target_point = mobject_or_point
        if submobject_to_align is not None:
            aligner = submobject_to_align
        elif index_of_submobject_to_align is not None:
            aligner = self[index_of_submobject_to_align]
        else:
            aligner = self
        point_to_align = aligner.get_critical_point(aligned_edge - direction)
        self.shift((target_point - point_to_align + buff * direction) * coor_mask)
        return self

    def shift_onto_screen(self, **kwargs) -> Self:
        space_lengths = [config["frame_x_radius"], config["frame_y_radius"]]
        for vect in UP, DOWN, LEFT, RIGHT:
            dim = np.argmax(np.abs(vect))
            buff = kwargs.get("buff", DEFAULT_MOBJECT_TO_EDGE_BUFFER)
            max_val = space_lengths[dim] - buff
            edge_center = self.get_edge_center(vect)
            if np.dot(edge_center, vect) > max_val:
                self.to_edge(vect, **kwargs)
        return self

    def is_off_screen(self):
        if self.get_left()[0] > config["frame_x_radius"]:
            return True
        if self.get_right()[0] < -config["frame_x_radius"]:
            return True
        if self.get_bottom()[1] > config["frame_y_radius"]:
            return True
        if self.get_top()[1] < -config["frame_y_radius"]:
            return True
        return False

    def stretch_about_point(self, factor: float, dim: int, point: Point3D) -> Self:
        return self.stretch(factor, dim, about_point=point)

    def rescale_to_fit(
        self, length: float, dim: int, stretch: bool = False, **kwargs
    ) -> Self:
        old_length = self.length_over_dim(dim)
        if old_length == 0:
            return self
        if stretch:
            self.stretch(length / old_length, dim, **kwargs)
        else:
            self.scale(length / old_length, **kwargs)
        return self

    def scale_to_fit_width(self, width: float, **kwargs) -> Self:
        """Scales the :class:`~.Mobject` to fit a width while keeping height/depth proportional.

        Returns
        -------
        :class:`Mobject`
            ``self``

        Examples
        --------
        ::

            >>> from manim import *
            >>> sq = Square()
            >>> sq.height
            2.0
            >>> sq.scale_to_fit_width(5)
            Square
            >>> sq.width
            5.0
            >>> sq.height
            5.0
        """

        return self.rescale_to_fit(width, 0, stretch=False, **kwargs)

    def stretch_to_fit_width(self, width: float, **kwargs) -> Self:
        """Stretches the :class:`~.Mobject` to fit a width, not keeping height/depth proportional.

        Returns
        -------
        :class:`Mobject`
            ``self``

        Examples
        --------
        ::

            >>> from manim import *
            >>> sq = Square()
            >>> sq.height
            2.0
            >>> sq.stretch_to_fit_width(5)
            Square
            >>> sq.width
            5.0
            >>> sq.height
            2.0
        """

        return self.rescale_to_fit(width, 0, stretch=True, **kwargs)

    def scale_to_fit_height(self, height: float, **kwargs) -> Self:
        """Scales the :class:`~.Mobject` to fit a height while keeping width/depth proportional.

        Returns
        -------
        :class:`Mobject`
            ``self``

        Examples
        --------
        ::

            >>> from manim import *
            >>> sq = Square()
            >>> sq.width
            2.0
            >>> sq.scale_to_fit_height(5)
            Square
            >>> sq.height
            5.0
            >>> sq.width
            5.0
        """

        return self.rescale_to_fit(height, 1, stretch=False, **kwargs)

    def stretch_to_fit_height(self, height: float, **kwargs) -> Self:
        """Stretches the :class:`~.Mobject` to fit a height, not keeping width/depth proportional.

        Returns
        -------
        :class:`Mobject`
            ``self``

        Examples
        --------
        ::

            >>> from manim import *
            >>> sq = Square()
            >>> sq.width
            2.0
            >>> sq.stretch_to_fit_height(5)
            Square
            >>> sq.height
            5.0
            >>> sq.width
            2.0
        """

        return self.rescale_to_fit(height, 1, stretch=True, **kwargs)

    def scale_to_fit_depth(self, depth: float, **kwargs) -> Self:
        """Scales the :class:`~.Mobject` to fit a depth while keeping width/height proportional."""

        return self.rescale_to_fit(depth, 2, stretch=False, **kwargs)

    def stretch_to_fit_depth(self, depth: float, **kwargs) -> Self:
        """Stretches the :class:`~.Mobject` to fit a depth, not keeping width/height proportional."""

        return self.rescale_to_fit(depth, 2, stretch=True, **kwargs)

    def set_coord(self, value, dim: int, direction: Vector3D = ORIGIN) -> Self:
        curr = self.get_coord(dim, direction)
        shift_vect = np.zeros(self.dim)
        shift_vect[dim] = value - curr
        self.shift(shift_vect)
        return self

    def set_x(self, x: float, direction: Vector3D = ORIGIN) -> Self:
        """Set x value of the center of the :class:`~.Mobject` (``int`` or ``float``)"""
        return self.set_coord(x, 0, direction)

    def set_y(self, y: float, direction: Vector3D = ORIGIN) -> Self:
        """Set y value of the center of the :class:`~.Mobject` (``int`` or ``float``)"""
        return self.set_coord(y, 1, direction)

    def set_z(self, z: float, direction: Vector3D = ORIGIN) -> Self:
        """Set z value of the center of the :class:`~.Mobject` (``int`` or ``float``)"""
        return self.set_coord(z, 2, direction)

    def space_out_submobjects(self, factor: float = 1.5, **kwargs) -> Self:
        self.scale(factor, **kwargs)
        for submob in self.submobjects:
            submob.scale(1.0 / factor)
        return self

    def move_to(
        self,
        point_or_mobject: Point3D | Mobject,
        aligned_edge: Vector3D = ORIGIN,
        coor_mask: Vector3D = np.array([1, 1, 1]),
    ) -> Self:
        """Move center of the :class:`~.Mobject` to certain Point3D."""
        if isinstance(point_or_mobject, Mobject):
            target = point_or_mobject.get_critical_point(aligned_edge)
        else:
            target = point_or_mobject
        point_to_align = self.get_critical_point(aligned_edge)
        self.shift((target - point_to_align) * coor_mask)
        return self

    def replace(
        self, mobject: Mobject, dim_to_match: int = 0, stretch: bool = False
    ) -> Self:
        if not mobject.get_num_points() and not mobject.submobjects:
            raise Warning("Attempting to replace mobject with no points")
        if stretch:
            self.stretch_to_fit_width(mobject.width)
            self.stretch_to_fit_height(mobject.height)
        else:
            self.rescale_to_fit(
                mobject.length_over_dim(dim_to_match),
                dim_to_match,
                stretch=False,
            )
        self.shift(mobject.get_center() - self.get_center())
        return self

    def surround(
        self,
        mobject: Mobject,
        dim_to_match: int = 0,
        stretch: bool = False,
        buff: float = MED_SMALL_BUFF,
    ) -> Self:
        self.replace(mobject, dim_to_match, stretch)
        length = mobject.length_over_dim(dim_to_match)
        self.scale((length + buff) / length)
        return self

    def put_start_and_end_on(self, start: Point3D, end: Point3D) -> Self:
        curr_start, curr_end = self.get_start_and_end()
        curr_vect = curr_end - curr_start
        if np.all(curr_vect == 0):
            self.points = start
            return self
        target_vect = np.array(end) - np.array(start)
        axis = (
            normalize(np.cross(curr_vect, target_vect))
            if np.linalg.norm(np.cross(curr_vect, target_vect)) != 0
            else OUT
        )
        self.scale(
            np.linalg.norm(target_vect) / np.linalg.norm(curr_vect),
            about_point=curr_start,
        )
        self.rotate(
            angle_between_vectors(curr_vect, target_vect),
            about_point=curr_start,
            axis=axis,
        )
        self.shift(start - curr_start)
        return self

    # Background rectangle
    def add_background_rectangle(
        self, color: ParsableManimColor | None = None, opacity: float = 0.75, **kwargs
    ) -> Self:
        """Add a BackgroundRectangle as submobject.

        The BackgroundRectangle is added behind other submobjects.

        This can be used to increase the mobjects visibility in front of a noisy background.

        Parameters
        ----------
        color
            The color of the BackgroundRectangle
        opacity
            The opacity of the BackgroundRectangle
        kwargs
            Additional keyword arguments passed to the BackgroundRectangle constructor


        Returns
        -------
        :class:`Mobject`
            ``self``

        See Also
        --------
        :meth:`add_to_back`
        :class:`~.BackgroundRectangle`

        """

        # TODO, this does not behave well when the mobject has points,
        # since it gets displayed on top
        from manim.mobject.geometry.shape_matchers import BackgroundRectangle

        self.background_rectangle = BackgroundRectangle(
            self, color=color, fill_opacity=opacity, **kwargs
        )
        self.add_to_back(self.background_rectangle)
        return self

    def add_background_rectangle_to_submobjects(self, **kwargs) -> Self:
        for submobject in self.submobjects:
            submobject.add_background_rectangle(**kwargs)
        return self

    def add_background_rectangle_to_family_members_with_points(self, **kwargs) -> Self:
        for mob in self.family_members_with_points():
            mob.add_background_rectangle(**kwargs)
        return self

    # Color functions

    def set_color(
        self, color: ParsableManimColor = YELLOW_C, family: bool = True
    ) -> Self:
        """Condition is function which takes in one arguments, (x, y, z).
        Here it just recurses to submobjects, but in subclasses this
        should be further implemented based on the the inner workings
        of color
        """
        if family:
            for submob in self.submobjects:
                submob.set_color(color, family=family)

        self.color = ManimColor.parse(color)
        return self

    def set_color_by_gradient(self, *colors: ParsableManimColor) -> Self:
        """
        Parameters
        ----------
        colors
            The colors to use for the gradient. Use like `set_color_by_gradient(RED, BLUE, GREEN)`.

        self.color = ManimColor.parse(color)
        return self
        """
        self.set_submobject_colors_by_gradient(*colors)
        return self

    def set_colors_by_radial_gradient(
        self,
        center: Point3D | None = None,
        radius: float = 1,
        inner_color: ParsableManimColor = WHITE,
        outer_color: ParsableManimColor = BLACK,
    ) -> Self:
        self.set_submobject_colors_by_radial_gradient(
            center,
            radius,
            inner_color,
            outer_color,
        )
        return self

    def set_submobject_colors_by_gradient(self, *colors: Iterable[ParsableManimColor]):
        if len(colors) == 0:
            raise ValueError("Need at least one color")
        elif len(colors) == 1:
            return self.set_color(*colors)

        mobs = self.family_members_with_points()
        new_colors = color_gradient(colors, len(mobs))

        for mob, color in zip(mobs, new_colors):
            mob.set_color(color, family=False)
        return self

    def set_submobject_colors_by_radial_gradient(
        self,
        center: Point3D | None = None,
        radius: float = 1,
        inner_color: ParsableManimColor = WHITE,
        outer_color: ParsableManimColor = BLACK,
    ) -> Self:
        if center is None:
            center = self.get_center()

        for mob in self.family_members_with_points():
            t = np.linalg.norm(mob.get_center() - center) / radius
            t = min(t, 1)
            mob_color = interpolate_color(inner_color, outer_color, t)
            mob.set_color(mob_color, family=False)

        return self

    def to_original_color(self) -> Self:
        self.set_color(self.color)
        return self

    def fade_to(
        self, color: ParsableManimColor, alpha: float, family: bool = True
    ) -> Self:
        if self.get_num_points() > 0:
            new_color = interpolate_color(self.get_color(), color, alpha)
            self.set_color(new_color, family=False)
        if family:
            for submob in self.submobjects:
                submob.fade_to(color, alpha)
        return self

    def fade(self, darkness: float = 0.5, family: bool = True) -> Self:
        if family:
            for submob in self.submobjects:
                submob.fade(darkness, family)
        return self

    def get_color(self) -> ManimColor:
        """Returns the color of the :class:`~.Mobject`

        Examples
        --------
        ::

            >>> from manim import Square, RED
            >>> Square(color=RED).get_color() == RED
            True

        """
        return self.color

    ##

    def save_state(self) -> Self:
        """Save the current state (position, color & size). Can be restored with :meth:`~.Mobject.restore`."""
        if hasattr(self, "saved_state"):
            # Prevent exponential growth of data
            self.saved_state = None
        self.saved_state = self.copy()

        return self

    def restore(self) -> Self:
        """Restores the state that was previously saved with :meth:`~.Mobject.save_state`."""
        if not hasattr(self, "saved_state") or self.save_state is None:
            raise Exception("Trying to restore without having saved")
        self.become(self.saved_state)
        return self

    def reduce_across_dimension(self, reduce_func: Callable, dim: int):
        """Find the min or max value from a dimension across all points in this and submobjects."""
        assert dim >= 0 and dim <= 2
        if len(self.submobjects) == 0 and len(self.points) == 0:
            # If we have no points and no submobjects, return 0 (e.g. center)
            return 0

        # If we do not have points (but do have submobjects)
        # use only the points from those.
        if len(self.points) == 0:
            rv = None
        else:
            # Otherwise, be sure to include our own points
            rv = reduce_func(self.points[:, dim])
        # Recursively ask submobjects (if any) for the biggest/
        # smallest dimension they have and compare it to the return value.
        for mobj in self.submobjects:
            value = mobj.reduce_across_dimension(reduce_func, dim)
            if rv is None:
                rv = value
            else:
                rv = reduce_func([value, rv])
        return rv

    def nonempty_submobjects(self) -> list[Self]:
        return [
            submob
            for submob in self.submobjects
            if len(submob.submobjects) != 0 or len(submob.points) != 0
        ]

    def get_merged_array(self, array_attr: str) -> np.ndarray:
        """Return all of a given attribute from this mobject and all submobjects.

        May contain duplicates; the order is in a depth-first (pre-order)
        traversal of the submobjects.
        """
        result = getattr(self, array_attr)
        for submob in self.submobjects:
            result = np.append(result, submob.get_merged_array(array_attr), axis=0)
        return result

    def get_all_points(self) -> Point3D_Array:
        """Return all points from this mobject and all submobjects.

        May contain duplicates; the order is in a depth-first (pre-order)
        traversal of the submobjects.
        """
        return self.get_merged_array("points")

    # Getters

    def get_points_defining_boundary(self) -> Point3D_Array:
        return self.get_all_points()

    def get_num_points(self) -> int:
        return len(self.points)

    def get_extremum_along_dim(
        self, points: Point3D_Array | None = None, dim: int = 0, key: int = 0
    ) -> np.ndarray | float:
        if points is None:
            points = self.get_points_defining_boundary()
        values = points[:, dim]
        if key < 0:
            return np.min(values)
        elif key == 0:
            return (np.min(values) + np.max(values)) / 2
        else:
            return np.max(values)

    def get_critical_point(self, direction: Vector3D) -> Point3D:
        """Picture a box bounding the :class:`~.Mobject`.  Such a box has
        9 'critical points': 4 corners, 4 edge center, the
        center. This returns one of them, along the given direction.

        ::

            sample = Arc(start_angle=PI / 7, angle=PI / 5)

            # These are all equivalent
            max_y_1 = sample.get_top()[1]
            max_y_2 = sample.get_critical_point(UP)[1]
            max_y_3 = sample.get_extremum_along_dim(dim=1, key=1)

        """
        result = np.zeros(self.dim)
        all_points = self.get_points_defining_boundary()
        if len(all_points) == 0:
            return result
        for dim in range(self.dim):
            result[dim] = self.get_extremum_along_dim(
                all_points,
                dim=dim,
                key=direction[dim],
            )
        return result

    # Pseudonyms for more general get_critical_point method

    def get_edge_center(self, direction: Vector3D) -> Point3D:
        """Get edge Point3Ds for certain direction."""
        return self.get_critical_point(direction)

    def get_corner(self, direction: Vector3D) -> Point3D:
        """Get corner Point3Ds for certain direction."""
        return self.get_critical_point(direction)

    def get_center(self) -> Point3D:
        """Get center Point3Ds"""
        return self.get_critical_point(np.zeros(self.dim))

    def get_center_of_mass(self) -> Point3D:
        return np.apply_along_axis(np.mean, 0, self.get_all_points())

    def get_boundary_point(self, direction: Vector3D) -> Point3D:
        all_points = self.get_points_defining_boundary()
        index = np.argmax(np.dot(all_points, np.array(direction).T))
        return all_points[index]

    def get_midpoint(self) -> Point3D:
        """Get Point3Ds of the middle of the path that forms the  :class:`~.Mobject`.

        Examples
        --------

        .. manim:: AngleMidPoint
            :save_last_frame:

            class AngleMidPoint(Scene):
                def construct(self):
                    line1 = Line(ORIGIN, 2*RIGHT)
                    line2 = Line(ORIGIN, 2*RIGHT).rotate_about_origin(80*DEGREES)

                    a = Angle(line1, line2, radius=1.5, other_angle=False)
                    d = Dot(a.get_midpoint()).set_color(RED)

                    self.add(line1, line2, a, d)
                    self.wait()

        """
        return self.point_from_proportion(0.5)

    def get_top(self) -> Point3D:
        """Get top Point3Ds of a box bounding the :class:`~.Mobject`"""
        return self.get_edge_center(UP)

    def get_bottom(self) -> Point3D:
        """Get bottom Point3Ds of a box bounding the :class:`~.Mobject`"""
        return self.get_edge_center(DOWN)

    def get_right(self) -> Point3D:
        """Get right Point3Ds of a box bounding the :class:`~.Mobject`"""
        return self.get_edge_center(RIGHT)

    def get_left(self) -> Point3D:
        """Get left Point3Ds of a box bounding the :class:`~.Mobject`"""
        return self.get_edge_center(LEFT)

    def get_zenith(self) -> Point3D:
        """Get zenith Point3Ds of a box bounding a 3D :class:`~.Mobject`."""
        return self.get_edge_center(OUT)

    def get_nadir(self) -> Point3D:
        """Get nadir (opposite the zenith) Point3Ds of a box bounding a 3D :class:`~.Mobject`."""
        return self.get_edge_center(IN)

    def length_over_dim(self, dim: int) -> float:
        """Measure the length of an :class:`~.Mobject` in a certain direction."""
        return self.reduce_across_dimension(
            max,
            dim,
        ) - self.reduce_across_dimension(min, dim)

    def get_coord(self, dim: int, direction: Vector3D = ORIGIN):
        """Meant to generalize ``get_x``, ``get_y`` and ``get_z``"""
        return self.get_extremum_along_dim(dim=dim, key=direction[dim])

    def get_x(self, direction: Vector3D = ORIGIN) -> ManimFloat:
        """Returns x Point3D of the center of the :class:`~.Mobject` as ``float``"""
        return self.get_coord(0, direction)

    def get_y(self, direction: Vector3D = ORIGIN) -> ManimFloat:
        """Returns y Point3D of the center of the :class:`~.Mobject` as ``float``"""
        return self.get_coord(1, direction)

    def get_z(self, direction: Vector3D = ORIGIN) -> ManimFloat:
        """Returns z Point3D of the center of the :class:`~.Mobject` as ``float``"""
        return self.get_coord(2, direction)

    def get_start(self) -> Point3D:
        """Returns the point, where the stroke that surrounds the :class:`~.Mobject` starts."""
        self.throw_error_if_no_points()
        return np.array(self.points[0])

    def get_end(self) -> Point3D:
        """Returns the point, where the stroke that surrounds the :class:`~.Mobject` ends."""
        self.throw_error_if_no_points()
        return np.array(self.points[-1])

    def get_start_and_end(self) -> tuple[Point3D, Point3D]:
        """Returns starting and ending point of a stroke as a ``tuple``."""
        return self.get_start(), self.get_end()

    def point_from_proportion(self, alpha: float) -> Point3D:
        raise NotImplementedError("Please override in a child class.")

    def proportion_from_point(self, point: Point3D) -> float:
        raise NotImplementedError("Please override in a child class.")

    def get_pieces(self, n_pieces: float) -> Group:
        template = self.copy()
        template.submobjects = []
        alphas = np.linspace(0, 1, n_pieces + 1)
        return Group(
            *(
                template.copy().pointwise_become_partial(self, a1, a2)
                for a1, a2 in zip(alphas[:-1], alphas[1:])
            )
        )

    def get_z_index_reference_point(self) -> Point3D:
        # TODO, better place to define default z_index_group?
        z_index_group = getattr(self, "z_index_group", self)
        return z_index_group.get_center()

    def has_points(self) -> bool:
        """Check if :class:`~.Mobject` contains points."""
        return len(self.points) > 0

    def has_no_points(self) -> bool:
        """Check if :class:`~.Mobject` *does not* contains points."""
        return not self.has_points()

    # Match other mobject properties

    def match_color(self, mobject: Mobject) -> Self:
        """Match the color with the color of another :class:`~.Mobject`."""
        return self.set_color(mobject.get_color())

    def match_dim_size(self, mobject: Mobject, dim: int, **kwargs) -> Self:
        """Match the specified dimension with the dimension of another :class:`~.Mobject`."""
        return self.rescale_to_fit(mobject.length_over_dim(dim), dim, **kwargs)

    def match_width(self, mobject: Mobject, **kwargs) -> Self:
        """Match the width with the width of another :class:`~.Mobject`."""
        return self.match_dim_size(mobject, 0, **kwargs)

    def match_height(self, mobject: Mobject, **kwargs) -> Self:
        """Match the height with the height of another :class:`~.Mobject`."""
        return self.match_dim_size(mobject, 1, **kwargs)

    def match_depth(self, mobject: Mobject, **kwargs) -> Self:
        """Match the depth with the depth of another :class:`~.Mobject`."""
        return self.match_dim_size(mobject, 2, **kwargs)

    def match_coord(
        self, mobject: Mobject, dim: int, direction: Vector3D = ORIGIN
    ) -> Self:
        """Match the Point3Ds with the Point3Ds of another :class:`~.Mobject`."""
        return self.set_coord(
            mobject.get_coord(dim, direction),
            dim=dim,
            direction=direction,
        )

    def match_x(self, mobject: Mobject, direction=ORIGIN) -> Self:
        """Match x coord. to the x coord. of another :class:`~.Mobject`."""
        return self.match_coord(mobject, 0, direction)

    def match_y(self, mobject: Mobject, direction=ORIGIN) -> Self:
        """Match y coord. to the x coord. of another :class:`~.Mobject`."""
        return self.match_coord(mobject, 1, direction)

    def match_z(self, mobject: Mobject, direction=ORIGIN) -> Self:
        """Match z coord. to the x coord. of another :class:`~.Mobject`."""
        return self.match_coord(mobject, 2, direction)

    def align_to(
        self,
        mobject_or_point: Mobject | Point3D,
        direction: Vector3D = ORIGIN,
    ) -> Self:
        """Aligns mobject to another :class:`~.Mobject` in a certain direction.

        Examples:
        mob1.align_to(mob2, UP) moves mob1 vertically so that its
        top edge lines ups with mob2's top edge.
        """
        if isinstance(mobject_or_point, Mobject):
            point = mobject_or_point.get_critical_point(direction)
        else:
            point = mobject_or_point

        for dim in range(self.dim):
            if direction[dim] != 0:
                self.set_coord(point[dim], dim, direction)
        return self

    # Family matters

    def __getitem__(self, value):
        self_list = self.split()
        if isinstance(value, slice):
            GroupClass = self.get_group_class()
            return GroupClass(*self_list.__getitem__(value))
        return self_list.__getitem__(value)

    def __iter__(self):
        return iter(self.split())

    def __len__(self):
        return len(self.split())

    def get_group_class(self) -> type[Group]:
        return Group

    @staticmethod
    def get_mobject_type_class() -> type[Mobject]:
        """Return the base class of this mobject type."""
        return Mobject

    def split(self) -> list[Self]:
        result = [self] if len(self.points) > 0 else []
        return result + self.submobjects

    def get_family(self, recurse: bool = True) -> list[Self]:
        sub_families = [x.get_family() for x in self.submobjects]
        all_mobjects = [self] + list(it.chain(*sub_families))
        return remove_list_redundancies(all_mobjects)

    def family_members_with_points(self) -> list[Self]:
        return [m for m in self.get_family() if m.get_num_points() > 0]

    def arrange(
        self,
        direction: Vector3D = RIGHT,
        buff: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
        center: bool = True,
        **kwargs,
    ) -> Self:
        """Sorts :class:`~.Mobject` next to each other on screen.

        Examples
        --------

        .. manim:: Example
            :save_last_frame:

            class Example(Scene):
                def construct(self):
                    s1 = Square()
                    s2 = Square()
                    s3 = Square()
                    s4 = Square()
                    x = VGroup(s1, s2, s3, s4).set_x(0).arrange(buff=1.0)
                    self.add(x)
        """
        for m1, m2 in zip(self.submobjects, self.submobjects[1:]):
            m2.next_to(m1, direction, buff, **kwargs)
        if center:
            self.center()
        return self

    def arrange_in_grid(
        self,
        rows: int | None = None,
        cols: int | None = None,
        buff: float | tuple[float, float] = MED_SMALL_BUFF,
        cell_alignment: Vector3D = ORIGIN,
        row_alignments: str | None = None,  # "ucd"
        col_alignments: str | None = None,  # "lcr"
        row_heights: Iterable[float | None] | None = None,
        col_widths: Iterable[float | None] | None = None,
        flow_order: str = "rd",
        **kwargs,
    ) -> Self:
        """Arrange submobjects in a grid.

        Parameters
        ----------
        rows
            The number of rows in the grid.
        cols
            The number of columns in the grid.
        buff
            The gap between grid cells. To specify a different buffer in the horizontal and
            vertical directions, a tuple of two values can be given - ``(row, col)``.
        cell_alignment
            The way each submobject is aligned in its grid cell.
        row_alignments
            The vertical alignment for each row (top to bottom). Accepts the following characters: ``"u"`` -
            up, ``"c"`` - center, ``"d"`` - down.
        col_alignments
            The horizontal alignment for each column (left to right). Accepts the following characters ``"l"`` - left,
            ``"c"`` - center, ``"r"`` - right.
        row_heights
            Defines a list of heights for certain rows (top to bottom). If the list contains
            ``None``, the corresponding row will fit its height automatically based
            on the highest element in that row.
        col_widths
            Defines a list of widths for certain columns (left to right). If the list contains ``None``, the
            corresponding column will fit its width automatically based on the widest element in that column.
        flow_order
            The order in which submobjects fill the grid. Can be one of the following values:
            "rd", "dr", "ld", "dl", "ru", "ur", "lu", "ul". ("rd" -> fill rightwards then downwards)

        Returns
        -------
        :class:`Mobject`
            ``self``

        Raises
        ------
        ValueError
            If ``rows`` and ``cols`` are too small to fit all submobjects.
        ValueError
            If :code:`cols`, :code:`col_alignments` and :code:`col_widths` or :code:`rows`,
            :code:`row_alignments` and :code:`row_heights` have mismatching sizes.

        Notes
        -----
        If only one of ``cols`` and ``rows`` is set implicitly, the other one will be chosen big
        enough to fit all submobjects. If neither is set, they will be chosen to be about the same,
        tending towards ``cols`` > ``rows`` (simply because videos are wider than they are high).

        If both ``cell_alignment`` and ``row_alignments`` / ``col_alignments`` are
        defined, the latter has higher priority.

        Examples
        --------
        .. manim:: ExampleBoxes
            :save_last_frame:

            class ExampleBoxes(Scene):
                def construct(self):
                    boxes=VGroup(*[Square() for s in range(0,6)])
                    boxes.arrange_in_grid(rows=2, buff=0.1)
                    self.add(boxes)


        .. manim:: ArrangeInGrid
            :save_last_frame:

            class ArrangeInGrid(Scene):
                def construct(self):
                    boxes = VGroup(*[
                        Rectangle(WHITE, 0.5, 0.5).add(Text(str(i+1)).scale(0.5))
                        for i in range(24)
                    ])
                    self.add(boxes)

                    boxes.arrange_in_grid(
                        buff=(0.25,0.5),
                        col_alignments="lccccr",
                        row_alignments="uccd",
                        col_widths=[1, *[None]*4, 1],
                        row_heights=[1, None, None, 1],
                        flow_order="dr"
                    )


        """
        from manim.mobject.geometry.line import Line

        mobs = self.submobjects.copy()
        start_pos = self.get_center()

        # get cols / rows values if given (implicitly)
        def init_size(num, alignments, sizes):
            if num is not None:
                return num
            if alignments is not None:
                return len(alignments)
            if sizes is not None:
                return len(sizes)

        cols = init_size(cols, col_alignments, col_widths)
        rows = init_size(rows, row_alignments, row_heights)

        # calculate rows cols
        if rows is None and cols is None:
            cols = math.ceil(math.sqrt(len(mobs)))
            # make the grid as close to quadratic as possible.
            # choosing cols first can results in cols>rows.
            # This is favored over rows>cols since in general
            # the sceene is wider than high.
        if rows is None:
            rows = math.ceil(len(mobs) / cols)
        if cols is None:
            cols = math.ceil(len(mobs) / rows)
        if rows * cols < len(mobs):
            raise ValueError("Too few rows and columns to fit all submobjetcs.")
        # rows and cols are now finally valid.

        if isinstance(buff, tuple):
            buff_x = buff[0]
            buff_y = buff[1]
        else:
            buff_x = buff_y = buff

        # Initialize alignments correctly
        def init_alignments(alignments, num, mapping, name, dir):
            if alignments is None:
                # Use cell_alignment as fallback
                return [cell_alignment * dir] * num
            if len(alignments) != num:
                raise ValueError(f"{name}_alignments has a mismatching size.")
            alignments = list(alignments)
            for i in range(num):
                alignments[i] = mapping[alignments[i]]
            return alignments

        row_alignments = init_alignments(
            row_alignments,
            rows,
            {"u": UP, "c": ORIGIN, "d": DOWN},
            "row",
            RIGHT,
        )
        col_alignments = init_alignments(
            col_alignments,
            cols,
            {"l": LEFT, "c": ORIGIN, "r": RIGHT},
            "col",
            UP,
        )
        # Now row_alignment[r] + col_alignment[c] is the alignment in cell [r][c]

        mapper = {
            "dr": lambda r, c: (rows - r - 1) + c * rows,
            "dl": lambda r, c: (rows - r - 1) + (cols - c - 1) * rows,
            "ur": lambda r, c: r + c * rows,
            "ul": lambda r, c: r + (cols - c - 1) * rows,
            "rd": lambda r, c: (rows - r - 1) * cols + c,
            "ld": lambda r, c: (rows - r - 1) * cols + (cols - c - 1),
            "ru": lambda r, c: r * cols + c,
            "lu": lambda r, c: r * cols + (cols - c - 1),
        }
        if flow_order not in mapper:
            raise ValueError(
                'flow_order must be one of the following values: "dr", "rd", "ld" "dl", "ru", "ur", "lu", "ul".',
            )
        flow_order = mapper[flow_order]

        # Reverse row_alignments and row_heights. Necessary since the
        # grid filling is handled bottom up for simplicity reasons.
        def reverse(maybe_list):
            if maybe_list is not None:
                maybe_list = list(maybe_list)
                maybe_list.reverse()
                return maybe_list

        row_alignments = reverse(row_alignments)
        row_heights = reverse(row_heights)

        placeholder = Mobject()
        # Used to fill up the grid temporarily, doesn't get added to the scene.
        # In this case a Mobject is better than None since it has width and height
        # properties of 0.

        mobs.extend([placeholder] * (rows * cols - len(mobs)))
        grid = [[mobs[flow_order(r, c)] for c in range(cols)] for r in range(rows)]

        measured_heigths = [
            max(grid[r][c].height for c in range(cols)) for r in range(rows)
        ]
        measured_widths = [
            max(grid[r][c].width for r in range(rows)) for c in range(cols)
        ]

        # Initialize row_heights / col_widths correctly using measurements as fallback
        def init_sizes(sizes, num, measures, name):
            if sizes is None:
                sizes = [None] * num
            if len(sizes) != num:
                raise ValueError(f"{name} has a mismatching size.")
            return [
                sizes[i] if sizes[i] is not None else measures[i] for i in range(num)
            ]

        heights = init_sizes(row_heights, rows, measured_heigths, "row_heights")
        widths = init_sizes(col_widths, cols, measured_widths, "col_widths")

        x, y = 0, 0
        for r in range(rows):
            x = 0
            for c in range(cols):
                if grid[r][c] is not placeholder:
                    alignment = row_alignments[r] + col_alignments[c]
                    line = Line(
                        x * RIGHT + y * UP,
                        (x + widths[c]) * RIGHT + (y + heights[r]) * UP,
                    )
                    # Use a mobject to avoid rewriting align inside
                    # box code that Mobject.move_to(Mobject) already
                    # includes.

                    grid[r][c].move_to(line, alignment)
                x += widths[c] + buff_x
            y += heights[r] + buff_y

        self.move_to(start_pos)
        return self

    def sort(
        self,
        point_to_num_func: Callable[[Point3D], ManimInt] = lambda p: p[0],
        submob_func: Callable[[Mobject], ManimInt] | None = None,
    ) -> Self:
        """Sorts the list of :attr:`submobjects` by a function defined by ``submob_func``."""
        if submob_func is None:

            def submob_func(m: Mobject):
                return point_to_num_func(m.get_center())

        self.submobjects.sort(key=submob_func)
        return self

    def shuffle(self, recursive: bool = False) -> None:
        """Shuffles the list of :attr:`submobjects`."""
        if recursive:
            for submob in self.submobjects:
                submob.shuffle(recursive=True)
        random.shuffle(self.submobjects)

    def invert(self, recursive: bool = False) -> None:
        """Inverts the list of :attr:`submobjects`.

        Parameters
        ----------
        recursive
            If ``True``, all submobject lists of this mobject's family are inverted.

        Examples
        --------

        .. manim:: InvertSumobjectsExample

            class InvertSumobjectsExample(Scene):
                def construct(self):
                    s = VGroup(*[Dot().shift(i*0.1*RIGHT) for i in range(-20,20)])
                    s2 = s.copy()
                    s2.invert()
                    s2.shift(DOWN)
                    self.play(Write(s), Write(s2))
        """
        if recursive:
            for submob in self.submobjects:
                submob.invert(recursive=True)
        self.submobjects.reverse()

    # Just here to keep from breaking old scenes.
    def arrange_submobjects(self, *args, **kwargs) -> Self:
        """Arrange the position of :attr:`submobjects` with a small buffer.

        Examples
        --------

        .. manim:: ArrangeSumobjectsExample
            :save_last_frame:

            class ArrangeSumobjectsExample(Scene):
                def construct(self):
                    s= VGroup(*[Dot().shift(i*0.1*RIGHT*np.random.uniform(-1,1)+UP*np.random.uniform(-1,1)) for i in range(0,15)])
                    s.shift(UP).set_color(BLUE)
                    s2= s.copy().set_color(RED)
                    s2.arrange_submobjects()
                    s2.shift(DOWN)
                    self.add(s,s2)

        """
        return self.arrange(*args, **kwargs)

    def sort_submobjects(self, *args, **kwargs) -> Self:
        """Sort the :attr:`submobjects`"""
        return self.sort(*args, **kwargs)

    def shuffle_submobjects(self, *args, **kwargs) -> None:
        """Shuffles the order of :attr:`submobjects`

        Examples
        --------

        .. manim:: ShuffleSubmobjectsExample

            class ShuffleSubmobjectsExample(Scene):
                def construct(self):
                    s= VGroup(*[Dot().shift(i*0.1*RIGHT) for i in range(-20,20)])
                    s2= s.copy()
                    s2.shuffle_submobjects()
                    s2.shift(DOWN)
                    self.play(Write(s), Write(s2))
        """
        return self.shuffle(*args, **kwargs)

    # Alignment
    def align_data(self, mobject: Mobject, skip_point_alignment: bool = False) -> None:
        """Aligns the data of this mobject with another mobject.

        Afterwards, the two mobjects will have the same number of submobjects
        (see :meth:`.align_submobjects`), the same parent structure (see
        :meth:`.null_point_align`). If ``skip_point_alignment`` is false,
        they will also have the same number of points (see :meth:`.align_points`).

        Parameters
        ----------
        mobject
            The other mobject this mobject should be aligned to.
        skip_point_alignment
            Controls whether or not the computationally expensive
            point alignment is skipped (default: False).
        """
        self.null_point_align(mobject)
        self.align_submobjects(mobject)
        if not skip_point_alignment:
            self.align_points(mobject)
        # Recurse
        for m1, m2 in zip(self.submobjects, mobject.submobjects):
            m1.align_data(m2)

    def get_point_mobject(self, center=None):
        """The simplest :class:`~.Mobject` to be transformed to or from self.
        Should by a point of the appropriate type
        """
        msg = f"get_point_mobject not implemented for {self.__class__.__name__}"
        raise NotImplementedError(msg)

    def align_points(self, mobject: Mobject) -> Self:
        count1 = self.get_num_points()
        count2 = mobject.get_num_points()
        if count1 < count2:
            self.align_points_with_larger(mobject)
        elif count2 < count1:
            mobject.align_points_with_larger(self)
        return self

    def align_points_with_larger(self, larger_mobject: Mobject):
        raise NotImplementedError("Please override in a child class.")

    def align_submobjects(self, mobject: Mobject) -> Self:
        mob1 = self
        mob2 = mobject
        n1 = len(mob1.submobjects)
        n2 = len(mob2.submobjects)
        mob1.add_n_more_submobjects(max(0, n2 - n1))
        mob2.add_n_more_submobjects(max(0, n1 - n2))
        return self

    def null_point_align(self, mobject: Mobject):
        """If a :class:`~.Mobject` with points is being aligned to
        one without, treat both as groups, and push
        the one with points into its own submobjects
        list.

        Returns
        -------
        :class:`Mobject`
            ``self``
        """
        for m1, m2 in (self, mobject), (mobject, self):
            if m1.has_no_points() and m2.has_points():
                m2.push_self_into_submobjects()
        return self

    def push_self_into_submobjects(self) -> Self:
        copy = self.copy()
        copy.submobjects = []
        self.reset_points()
        self.add(copy)
        return self

    def add_n_more_submobjects(self, n: int) -> Self | None:
        if n == 0:
            return None

        curr = len(self.submobjects)
        if curr == 0:
            # If empty, simply add n point mobjects
            self.submobjects = [self.get_point_mobject() for k in range(n)]
            return None

        target = curr + n
        # TODO, factor this out to utils so as to reuse
        # with VMobject.insert_n_curves
        repeat_indices = (np.arange(target) * curr) // target
        split_factors = [sum(repeat_indices == i) for i in range(curr)]
        new_submobs = []
        for submob, sf in zip(self.submobjects, split_factors):
            new_submobs.append(submob)
            for _ in range(1, sf):
                new_submobs.append(submob.copy().fade(1))
        self.submobjects = new_submobs
        return self

    def repeat_submobject(self, submob: Mobject) -> Self:
        return submob.copy()

    def interpolate(
        self,
        mobject1: Mobject,
        mobject2: Mobject,
        alpha: float,
        path_func: PathFuncType = straight_path(),
    ) -> Self:
        """Turns this :class:`~.Mobject` into an interpolation between ``mobject1``
        and ``mobject2``.

        Examples
        --------

        .. manim:: DotInterpolation
            :save_last_frame:

            class DotInterpolation(Scene):
                def construct(self):
                    dotR = Dot(color=DARK_GREY)
                    dotR.shift(2 * RIGHT)
                    dotL = Dot(color=WHITE)
                    dotL.shift(2 * LEFT)

                    dotMiddle = VMobject().interpolate(dotL, dotR, alpha=0.3)

                    self.add(dotL, dotR, dotMiddle)
        """
        self.points = path_func(mobject1.points, mobject2.points, alpha)
        self.interpolate_color(mobject1, mobject2, alpha)
        return self

    def interpolate_color(self, mobject1: Mobject, mobject2: Mobject, alpha: float):
        raise NotImplementedError("Please override in a child class.")

    def become(
        self,
        mobject: Mobject,
        match_height: bool = False,
        match_width: bool = False,
        match_depth: bool = False,
        match_center: bool = False,
        stretch: bool = False,
    ) -> Self:
        """Edit points, colors and submobjects to be identical
        to another :class:`~.Mobject`

        .. note::

            If both match_height and match_width are ``True`` then the transformed :class:`~.Mobject`
            will match the height first and then the width.

        Parameters
        ----------
        match_height
            Whether or not to preserve the height of the original
            :class:`~.Mobject`.
        match_width
            Whether or not to preserve the width of the original
            :class:`~.Mobject`.
        match_depth
            Whether or not to preserve the depth of the original
            :class:`~.Mobject`.
        match_center
            Whether or not to preserve the center of the original
            :class:`~.Mobject`.
        stretch
            Whether or not to stretch the target mobject to match the
            the proportions of the original :class:`~.Mobject`.

        Examples
        --------
        .. manim:: BecomeScene

            class BecomeScene(Scene):
                def construct(self):
                    circ = Circle(fill_color=RED, fill_opacity=0.8)
                    square = Square(fill_color=BLUE, fill_opacity=0.2)
                    self.add(circ)
                    self.wait(0.5)
                    circ.become(square)
                    self.wait(0.5)


        The following examples illustrate how mobject measurements
        change when using the ``match_...`` and ``stretch`` arguments.
        We start with a rectangle that is 2 units high and 4 units wide,
        which we want to turn into a circle of radius 3::

            >>> from manim import Rectangle, Circle
            >>> import numpy as np
            >>> rect = Rectangle(height=2, width=4)
            >>> circ = Circle(radius=3)

        With ``stretch=True``, the target circle is deformed to match
        the proportions of the rectangle, which results in the target
        mobject being an ellipse with height 2 and width 4. We can
        check that the resulting points satisfy the ellipse equation
        :math:`x^2/a^2 + y^2/b^2 = 1` with :math:`a = 4/2` and :math:`b = 2/2`
        being the semi-axes::

            >>> result = rect.copy().become(circ, stretch=True)
            >>> result.height, result.width
            (2.0, 4.0)
            >>> ellipse_points = np.array(result.get_anchors())
            >>> ellipse_eq = np.sum(ellipse_points**2 * [1/4, 1, 0], axis=1)
            >>> np.allclose(ellipse_eq, 1)
            True

        With ``match_height=True`` and ``match_width=True`` the circle is
        scaled such that the height or the width of the rectangle will
        be preserved, respectively.
        The points of the resulting mobject satisfy the circle equation
        :math:`x^2 + y^2 = r^2` for the corresponding radius :math:`r`::

            >>> result = rect.copy().become(circ, match_height=True)
            >>> result.height, result.width
            (2.0, 2.0)
            >>> circle_points = np.array(result.get_anchors())
            >>> circle_eq = np.sum(circle_points**2, axis=1)
            >>> np.allclose(circle_eq, 1)
            True
            >>> result = rect.copy().become(circ, match_width=True)
            >>> result.height, result.width
            (4.0, 4.0)
            >>> circle_points = np.array(result.get_anchors())
            >>> circle_eq = np.sum(circle_points**2, axis=1)
            >>> np.allclose(circle_eq, 2**2)
            True

        With ``match_center=True``, the resulting mobject is moved such that
        its center is the same as the center of the original mobject::

            >>> rect = rect.shift(np.array([0, 1, 0]))
            >>> np.allclose(rect.get_center(), circ.get_center())
            False
            >>> result = rect.copy().become(circ, match_center=True)
            >>> np.allclose(rect.get_center(), result.get_center())
            True
        """
        mobject = mobject.copy()
        if stretch:
            mobject.stretch_to_fit_height(self.height)
            mobject.stretch_to_fit_width(self.width)
            mobject.stretch_to_fit_depth(self.depth)
        else:
            if match_height:
                mobject.match_height(self)
            if match_width:
                mobject.match_width(self)
            if match_depth:
                mobject.match_depth(self)

        if match_center:
            mobject.move_to(self.get_center())

        self.align_data(mobject, skip_point_alignment=True)
        for sm1, sm2 in zip(self.get_family(), mobject.get_family()):
            sm1.points = np.array(sm2.points)
            sm1.interpolate_color(sm1, sm2, 1)
        return self

    def match_points(self, mobject: Mobject, copy_submobjects: bool = True) -> Self:
        """Edit points, positions, and submobjects to be identical
        to another :class:`~.Mobject`, while keeping the style unchanged.

        Examples
        --------
        .. manim:: MatchPointsScene

            class MatchPointsScene(Scene):
                def construct(self):
                    circ = Circle(fill_color=RED, fill_opacity=0.8)
                    square = Square(fill_color=BLUE, fill_opacity=0.2)
                    self.add(circ)
                    self.wait(0.5)
                    self.play(circ.animate.match_points(square))
                    self.wait(0.5)
        """
        for sm1, sm2 in zip(self.get_family(), mobject.get_family()):
            sm1.points = np.array(sm2.points)
        return self

    # Errors
    def throw_error_if_no_points(self) -> None:
        if self.has_no_points():
            caller_name = sys._getframe(1).f_code.co_name
            raise Exception(
                f"Cannot call Mobject.{caller_name} for a Mobject with no points",
            )

    # About z-index
    def set_z_index(
        self,
        z_index_value: float,
        family: bool = True,
    ) -> Self:
        """Sets the :class:`~.Mobject`'s :attr:`z_index` to the value specified in `z_index_value`.

        Parameters
        ----------
        z_index_value
            The new value of :attr:`z_index` set.
        family
            If ``True``, the :attr:`z_index` value of all submobjects is also set.

        Returns
        -------
        :class:`Mobject`
            The Mobject itself, after :attr:`z_index` is set. For chaining purposes. (Returns `self`.)

        Examples
        --------
        .. manim:: SetZIndex
            :save_last_frame:

            class SetZIndex(Scene):
                def construct(self):
                    text = Text('z_index = 3', color = PURE_RED).shift(UP).set_z_index(3)
                    square = Square(2, fill_opacity=1).set_z_index(2)
                    tex = Tex(r'zIndex = 1', color = PURE_BLUE).shift(DOWN).set_z_index(1)
                    circle = Circle(radius = 1.7, color = GREEN, fill_opacity = 1) # z_index = 0

                    # Displaying order is now defined by z_index values
                    self.add(text)
                    self.add(square)
                    self.add(tex)
                    self.add(circle)
        """
        if family:
            for submob in self.submobjects:
                submob.set_z_index(z_index_value, family=family)
        self.z_index = z_index_value
        return self

    def set_z_index_by_z_Point3D(self) -> Self:
        """Sets the :class:`~.Mobject`'s z Point3D to the value of :attr:`z_index`.

        Returns
        -------
        :class:`Mobject`
            The Mobject itself, after :attr:`z_index` is set. (Returns `self`.)
        """
        z_coord = self.get_center()[-1]
        self.set_z_index(z_coord)
        return self


class Group(Mobject, metaclass=ConvertToOpenGL):
    """Groups together multiple :class:`Mobjects <.Mobject>`.

    Notes
    -----
    When adding the same mobject more than once, repetitions are ignored.
    Use :meth:`.Mobject.copy` to create a separate copy which can then
    be added to the group.
    """

    def __init__(self, *mobjects, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add(*mobjects)


class _AnimationBuilder:
    def __init__(self, mobject) -> None:
        self.mobject = mobject
        self.mobject.generate_target()

        self.overridden_animation = None
        self.is_chaining = False
        self.methods = []

        # Whether animation args can be passed
        self.cannot_pass_args = False
        self.anim_args = {}

    def __call__(self, **kwargs) -> Self:
        if self.cannot_pass_args:
            raise ValueError(
                "Animation arguments must be passed before accessing methods and can only be passed once",
            )

        self.anim_args = kwargs
        self.cannot_pass_args = True

        return self

    def __getattr__(self, method_name) -> types.MethodType:
        method = getattr(self.mobject.target, method_name)
        has_overridden_animation = hasattr(method, "_override_animate")

        if (self.is_chaining and has_overridden_animation) or self.overridden_animation:
            raise NotImplementedError(
                "Method chaining is currently not supported for "
                "overridden animations",
            )

        def update_target(*method_args, **method_kwargs):
            if has_overridden_animation:
                self.overridden_animation = method._override_animate(
                    self.mobject,
                    *method_args,
                    anim_args=self.anim_args,
                    **method_kwargs,
                )
            else:
                self.methods.append([method, method_args, method_kwargs])
                method(*method_args, **method_kwargs)
            return self

        self.is_chaining = True
        self.cannot_pass_args = True

        return update_target

    def build(self) -> Animation:
        from ..animation.transform import (  # is this to prevent circular import?
            _MethodAnimation,
        )

        if self.overridden_animation:
            anim = self.overridden_animation
        else:
            anim = _MethodAnimation(self.mobject, self.methods)

        for attr, value in self.anim_args.items():
            setattr(anim, attr, value)

        return anim


def override_animate(method) -> types.FunctionType:
    r"""Decorator for overriding method animations.

    This allows to specify a method (returning an :class:`~.Animation`)
    which is called when the decorated method is used with the ``.animate`` syntax
    for animating the application of a method.

    .. seealso::

        :attr:`Mobject.animate`

    .. note::

        Overridden methods cannot be combined with normal or other overridden
        methods using method chaining with the ``.animate`` syntax.


    Examples
    --------

    .. manim:: AnimationOverrideExample

        class CircleWithContent(VGroup):
            def __init__(self, content):
                super().__init__()
                self.circle = Circle()
                self.content = content
                self.add(self.circle, content)
                content.move_to(self.circle.get_center())

            def clear_content(self):
                self.remove(self.content)
                self.content = None

            @override_animate(clear_content)
            def _clear_content_animation(self, anim_args=None):
                if anim_args is None:
                    anim_args = {}
                anim = Uncreate(self.content, **anim_args)
                self.clear_content()
                return anim

        class AnimationOverrideExample(Scene):
            def construct(self):
                t = Text("hello!")
                my_mobject = CircleWithContent(t)
                self.play(Create(my_mobject))
                self.play(my_mobject.animate.clear_content())
                self.wait()

    """

    def decorator(animation_method):
        method._override_animate = animation_method
        return animation_method

    return decorator


# Extracted from /Users/hochmax/learn/manim/manim/mobject/types/vectorized_mobject.py
"""Mobjects that use vector graphics."""

from __future__ import annotations

__all__ = [
    "VMobject",
    "VGroup",
    "VDict",
    "VectorizedPoint",
    "CurvesAsSubmobjects",
    "DashedVMobject",
]


import itertools as it
import sys
from collections.abc import Generator, Hashable, Iterable, Mapping, Sequence
from typing import TYPE_CHECKING, Callable, Literal

import numpy as np
from PIL.Image import Image

from manim import config
from manim.constants import *
from manim.mobject.mobject import Mobject
from manim.mobject.opengl.opengl_compatibility import ConvertToOpenGL
from manim.mobject.opengl.opengl_vectorized_mobject import OpenGLVMobject
from manim.mobject.three_d.three_d_utils import (
    get_3d_vmob_gradient_start_and_end_points,
)
from manim.utils.bezier import (
    bezier,
    bezier_remap,
    get_smooth_handle_points,
    integer_interpolate,
    interpolate,
    partial_bezier_points,
    proportions_along_bezier_curve_for_point,
)
from manim.utils.color import BLACK, WHITE, ManimColor, ParsableManimColor
from manim.utils.iterables import (
    make_even,
    resize_array,
    stretch_array_to_length,
    tuplify,
)
from manim.utils.space_ops import rotate_vector, shoelace_direction

if TYPE_CHECKING:
    import numpy.typing as npt
    from typing_extensions import Self

    from manim.typing import (
        BezierPoints,
        CubicBezierPoints,
        ManimFloat,
        MappingFunction,
        Point2D,
        Point3D,
        Point3D_Array,
        QuadraticBezierPoints,
        RGBA_Array_Float,
        Vector3D,
        Zeros,
    )

# TODO
# - Change cubic curve groups to have 4 points instead of 3
# - Change sub_path idea accordingly
# - No more mark_paths_closed, instead have the camera test
#   if last point in close to first point
# - Think about length of self.points.  Always 0 or 1 mod 4?
#   That's kind of weird.

__all__ = [
    "VMobject",
    "VGroup",
    "VDict",
    "VectorizedPoint",
    "CurvesAsSubmobjects",
    "VectorizedPoint",
    "DashedVMobject",
]


class VMobject(Mobject):
    """A vectorized mobject.

    Parameters
    ----------
    background_stroke_color
        The purpose of background stroke is to have something
        that won't overlap fill, e.g.  For text against some
        textured background.
    sheen_factor
        When a color c is set, there will be a second color
        computed based on interpolating c to WHITE by with
        sheen_factor, and the display will gradient to this
        secondary color in the direction of sheen_direction.
    close_new_points
        Indicates that it will not be displayed, but
        that it should count in parent mobject's path
    tolerance_for_point_equality
        This is within a pixel
    joint_type
        The line joint type used to connect the curve segments
        of this vectorized mobject. See :class:`.LineJointType`
        for options.
    """

    sheen_factor = 0.0

    def __init__(
        self,
        fill_color: ParsableManimColor | None = None,
        fill_opacity: float = 0.0,
        stroke_color: ParsableManimColor | None = None,
        stroke_opacity: float = 1.0,
        stroke_width: float = DEFAULT_STROKE_WIDTH,
        background_stroke_color: ParsableManimColor | None = BLACK,
        background_stroke_opacity: float = 1.0,
        background_stroke_width: float = 0,
        sheen_factor: float = 0.0,
        joint_type: LineJointType | None = None,
        sheen_direction: Vector3D = UL,
        close_new_points: bool = False,
        pre_function_handle_to_anchor_scale_factor: float = 0.01,
        make_smooth_after_applying_functions: bool = False,
        background_image: Image | str | None = None,
        shade_in_3d: bool = False,
        # TODO, do we care about accounting for varying zoom levels?
        tolerance_for_point_equality: float = 1e-6,
        n_points_per_cubic_curve: int = 4,
        cap_style: CapStyleType = CapStyleType.AUTO,
        **kwargs,
    ):
        self.fill_opacity = fill_opacity
        self.stroke_opacity = stroke_opacity
        self.stroke_width = stroke_width
        if background_stroke_color is not None:
            self.background_stroke_color: ManimColor = ManimColor(
                background_stroke_color
            )
        self.background_stroke_opacity: float = background_stroke_opacity
        self.background_stroke_width: float = background_stroke_width
        self.sheen_factor: float = sheen_factor
        self.joint_type: LineJointType = (
            LineJointType.AUTO if joint_type is None else joint_type
        )
        self.sheen_direction: Vector3D = sheen_direction
        self.close_new_points: bool = close_new_points
        self.pre_function_handle_to_anchor_scale_factor: float = (
            pre_function_handle_to_anchor_scale_factor
        )
        self.make_smooth_after_applying_functions: bool = (
            make_smooth_after_applying_functions
        )
        self.background_image: Image | str | None = background_image
        self.shade_in_3d: bool = shade_in_3d
        self.tolerance_for_point_equality: float = tolerance_for_point_equality
        self.n_points_per_cubic_curve: int = n_points_per_cubic_curve
        self._bezier_t_values: npt.NDArray[float] = np.linspace(
            0, 1, n_points_per_cubic_curve
        )
        self.cap_style: CapStyleType = cap_style
        super().__init__(**kwargs)
        self.submobjects: list[VMobject]

        # TODO: Find where color overwrites are happening and remove the color doubling
        # if "color" in kwargs:
        #     fill_color = kwargs["color"]
        #     stroke_color = kwargs["color"]
        if fill_color is not None:
            self.fill_color = ManimColor.parse(fill_color)
        if stroke_color is not None:
            self.stroke_color = ManimColor.parse(stroke_color)

    def _assert_valid_submobjects(self, submobjects: Iterable[VMobject]) -> Self:
        return self._assert_valid_submobjects_internal(submobjects, VMobject)

    # OpenGL compatibility
    @property
    def n_points_per_curve(self) -> int:
        return self.n_points_per_cubic_curve

    def get_group_class(self) -> type[VGroup]:
        return VGroup

    @staticmethod
    def get_mobject_type_class() -> type[VMobject]:
        return VMobject

    # Colors
    def init_colors(self, propagate_colors: bool = True) -> Self:
        self.set_fill(
            color=self.fill_color,
            opacity=self.fill_opacity,
            family=propagate_colors,
        )
        self.set_stroke(
            color=self.stroke_color,
            width=self.stroke_width,
            opacity=self.stroke_opacity,
            family=propagate_colors,
        )
        self.set_background_stroke(
            color=self.background_stroke_color,
            width=self.background_stroke_width,
            opacity=self.background_stroke_opacity,
            family=propagate_colors,
        )
        self.set_sheen(
            factor=self.sheen_factor,
            direction=self.sheen_direction,
            family=propagate_colors,
        )

        if not propagate_colors:
            for submobject in self.submobjects:
                submobject.init_colors(propagate_colors=False)

        return self

    def generate_rgbas_array(
        self, color: ManimColor | list[ManimColor], opacity: float | Iterable[float]
    ) -> RGBA_Array_Float:
        """
        First arg can be either a color, or a tuple/list of colors.
        Likewise, opacity can either be a float, or a tuple of floats.
        If self.sheen_factor is not zero, and only
        one color was passed in, a second slightly light color
        will automatically be added for the gradient
        """
        colors: list[ManimColor] = [
            ManimColor(c) if (c is not None) else BLACK for c in tuplify(color)
        ]
        opacities: list[float] = [
            o if (o is not None) else 0.0 for o in tuplify(opacity)
        ]
        rgbas: npt.NDArray[RGBA_Array_Float] = np.array(
            [c.to_rgba_with_alpha(o) for c, o in zip(*make_even(colors, opacities))],
        )

        sheen_factor = self.get_sheen_factor()
        if sheen_factor != 0 and len(rgbas) == 1:
            light_rgbas = np.array(rgbas)
            light_rgbas[:, :3] += sheen_factor
            np.clip(light_rgbas, 0, 1, out=light_rgbas)
            rgbas = np.append(rgbas, light_rgbas, axis=0)
        return rgbas

    def update_rgbas_array(
        self,
        array_name: str,
        color: ManimColor | None = None,
        opacity: float | None = None,
    ) -> Self:
        rgbas = self.generate_rgbas_array(color, opacity)
        if not hasattr(self, array_name):
            setattr(self, array_name, rgbas)
            return self
        # Match up current rgbas array with the newly calculated
        # one. 99% of the time they'll be the same.
        curr_rgbas = getattr(self, array_name)
        if len(curr_rgbas) < len(rgbas):
            curr_rgbas = stretch_array_to_length(curr_rgbas, len(rgbas))
            setattr(self, array_name, curr_rgbas)
        elif len(rgbas) < len(curr_rgbas):
            rgbas = stretch_array_to_length(rgbas, len(curr_rgbas))
        # Only update rgb if color was not None, and only
        # update alpha channel if opacity was passed in
        if color is not None:
            curr_rgbas[:, :3] = rgbas[:, :3]
        if opacity is not None:
            curr_rgbas[:, 3] = rgbas[:, 3]
        return self

    def set_fill(
        self,
        color: ParsableManimColor | None = None,
        opacity: float | None = None,
        family: bool = True,
    ) -> Self:
        """Set the fill color and fill opacity of a :class:`VMobject`.

        Parameters
        ----------
        color
            Fill color of the :class:`VMobject`.
        opacity
            Fill opacity of the :class:`VMobject`.
        family
            If ``True``, the fill color of all submobjects is also set.

        Returns
        -------
        :class:`VMobject`
            ``self``

        Examples
        --------
        .. manim:: SetFill
            :save_last_frame:

            class SetFill(Scene):
                def construct(self):
                    square = Square().scale(2).set_fill(WHITE,1)
                    circle1 = Circle().set_fill(GREEN,0.8)
                    circle2 = Circle().set_fill(YELLOW) # No fill_opacity
                    circle3 = Circle().set_fill(color = '#FF2135', opacity = 0.2)
                    group = Group(circle1,circle2,circle3).arrange()
                    self.add(square)
                    self.add(group)

        See Also
        --------
        :meth:`~.VMobject.set_style`
        """
        if family:
            for submobject in self.submobjects:
                submobject.set_fill(color, opacity, family)
        self.update_rgbas_array("fill_rgbas", color, opacity)
        self.fill_rgbas: RGBA_Array_Float
        if opacity is not None:
            self.fill_opacity = opacity
        return self

    def set_stroke(
        self,
        color: ParsableManimColor = None,
        width: float | None = None,
        opacity: float | None = None,
        background=False,
        family: bool = True,
    ) -> Self:
        if family:
            for submobject in self.submobjects:
                submobject.set_stroke(color, width, opacity, background, family)
        if background:
            array_name = "background_stroke_rgbas"
            width_name = "background_stroke_width"
            opacity_name = "background_stroke_opacity"
        else:
            array_name = "stroke_rgbas"
            width_name = "stroke_width"
            opacity_name = "stroke_opacity"
        self.update_rgbas_array(array_name, color, opacity)
        if width is not None:
            setattr(self, width_name, width)
        if opacity is not None:
            setattr(self, opacity_name, opacity)
        if color is not None and background:
            if isinstance(color, (list, tuple)):
                self.background_stroke_color = ManimColor.parse(color)
            else:
                self.background_stroke_color = ManimColor(color)
        return self

    def set_cap_style(self, cap_style: CapStyleType) -> Self:
        """
        Sets the cap style of the :class:`VMobject`.

        Parameters
        ----------
        cap_style
            The cap style to be set. See :class:`.CapStyleType` for options.

        Returns
        -------
        :class:`VMobject`
            ``self``

        Examples
        --------
        .. manim:: CapStyleExample
            :save_last_frame:

            class CapStyleExample(Scene):
                def construct(self):
                    line = Line(LEFT, RIGHT, color=YELLOW, stroke_width=20)
                    line.set_cap_style(CapStyleType.ROUND)
                    self.add(line)
        """
        self.cap_style = cap_style
        return self

    def set_background_stroke(self, **kwargs) -> Self:
        kwargs["background"] = True
        self.set_stroke(**kwargs)
        return self

    def set_style(
        self,
        fill_color: ParsableManimColor | None = None,
        fill_opacity: float | None = None,
        stroke_color: ParsableManimColor | None = None,
        stroke_width: float | None = None,
        stroke_opacity: float | None = None,
        background_stroke_color: ParsableManimColor | None = None,
        background_stroke_width: float | None = None,
        background_stroke_opacity: float | None = None,
        sheen_factor: float | None = None,
        sheen_direction: Vector3D | None = None,
        background_image: Image | str | None = None,
        family: bool = True,
    ) -> Self:
        self.set_fill(color=fill_color, opacity=fill_opacity, family=family)
        self.set_stroke(
            color=stroke_color,
            width=stroke_width,
            opacity=stroke_opacity,
            family=family,
        )
        self.set_background_stroke(
            color=background_stroke_color,
            width=background_stroke_width,
            opacity=background_stroke_opacity,
            family=family,
        )
        if sheen_factor:
            self.set_sheen(
                factor=sheen_factor,
                direction=sheen_direction,
                family=family,
            )
        if background_image:
            self.color_using_background_image(background_image)
        return self

    def get_style(self, simple: bool = False) -> dict:
        ret = {
            "stroke_opacity": self.get_stroke_opacity(),
            "stroke_width": self.get_stroke_width(),
        }

        # TODO: FIX COLORS HERE
        if simple:
            ret["fill_color"] = self.get_fill_color()
            ret["fill_opacity"] = self.get_fill_opacity()
            ret["stroke_color"] = self.get_stroke_color()
        else:
            ret["fill_color"] = self.get_fill_colors()
            ret["fill_opacity"] = self.get_fill_opacities()
            ret["stroke_color"] = self.get_stroke_colors()
            ret["background_stroke_color"] = self.get_stroke_colors(background=True)
            ret["background_stroke_width"] = self.get_stroke_width(background=True)
            ret["background_stroke_opacity"] = self.get_stroke_opacity(background=True)
            ret["sheen_factor"] = self.get_sheen_factor()
            ret["sheen_direction"] = self.get_sheen_direction()
            ret["background_image"] = self.get_background_image()

        return ret

    def match_style(self, vmobject: VMobject, family: bool = True) -> Self:
        self.set_style(**vmobject.get_style(), family=False)

        if family:
            # Does its best to match up submobject lists, and
            # match styles accordingly
            submobs1, submobs2 = self.submobjects, vmobject.submobjects
            if len(submobs1) == 0:
                return self
            elif len(submobs2) == 0:
                submobs2 = [vmobject]
            for sm1, sm2 in zip(*make_even(submobs1, submobs2)):
                sm1.match_style(sm2)
        return self

    def set_color(self, color: ParsableManimColor, family: bool = True) -> Self:
        self.set_fill(color, family=family)
        self.set_stroke(color, family=family)
        return self

    def set_opacity(self, opacity: float, family: bool = True) -> Self:
        self.set_fill(opacity=opacity, family=family)
        self.set_stroke(opacity=opacity, family=family)
        self.set_stroke(opacity=opacity, family=family, background=True)
        return self

    def fade(self, darkness: float = 0.5, family: bool = True) -> Self:
        factor = 1.0 - darkness
        self.set_fill(opacity=factor * self.get_fill_opacity(), family=False)
        self.set_stroke(opacity=factor * self.get_stroke_opacity(), family=False)
        self.set_background_stroke(
            opacity=factor * self.get_stroke_opacity(background=True),
            family=False,
        )
        super().fade(darkness, family)
        return self

    def get_fill_rgbas(self) -> RGBA_Array_Float | Zeros:
        try:
            return self.fill_rgbas
        except AttributeError:
            return np.zeros((1, 4))

    def get_fill_color(self) -> ManimColor:
        """
        If there are multiple colors (for gradient)
        this returns the first one
        """
        return self.get_fill_colors()[0]

    fill_color = property(get_fill_color, set_fill)

    def get_fill_opacity(self) -> ManimFloat:
        """
        If there are multiple opacities, this returns the
        first
        """
        return self.get_fill_opacities()[0]

    # TODO: Does this just do a copy?
    # TODO: I have the feeling that this function should not return None, does that have any usage ?
    def get_fill_colors(self) -> list[ManimColor | None]:
        return [
            ManimColor(rgba[:3]) if rgba.any() else None
            for rgba in self.get_fill_rgbas()
        ]

    def get_fill_opacities(self) -> npt.NDArray[ManimFloat]:
        return self.get_fill_rgbas()[:, 3]

    def get_stroke_rgbas(self, background: bool = False) -> RGBA_Array_float | Zeros:
        try:
            if background:
                self.background_stroke_rgbas: RGBA_Array_Float
                rgbas = self.background_stroke_rgbas
            else:
                self.stroke_rgbas: RGBA_Array_Float
                rgbas = self.stroke_rgbas
            return rgbas
        except AttributeError:
            return np.zeros((1, 4))

    def get_stroke_color(self, background: bool = False) -> ManimColor | None:
        return self.get_stroke_colors(background)[0]

    stroke_color = property(get_stroke_color, set_stroke)

    def get_stroke_width(self, background: bool = False) -> float:
        if background:
            self.background_stroke_width: float
            width = self.background_stroke_width
        else:
            width = self.stroke_width
            if isinstance(width, str):
                width = int(width)
        return max(0.0, width)

    def get_stroke_opacity(self, background: bool = False) -> ManimFloat:
        return self.get_stroke_opacities(background)[0]

    def get_stroke_colors(self, background: bool = False) -> list[ManimColor | None]:
        return [
            ManimColor(rgba[:3]) if rgba.any() else None
            for rgba in self.get_stroke_rgbas(background)
        ]

    def get_stroke_opacities(self, background: bool = False) -> npt.NDArray[ManimFloat]:
        return self.get_stroke_rgbas(background)[:, 3]

    def get_color(self) -> ManimColor:
        if np.all(self.get_fill_opacities() == 0):
            return self.get_stroke_color()
        return self.get_fill_color()

    color = property(get_color, set_color)

    def set_sheen_direction(self, direction: Vector3D, family: bool = True) -> Self:
        """Sets the direction of the applied sheen.

        Parameters
        ----------
        direction
            Direction from where the gradient is applied.

        Examples
        --------
        Normal usage::

            Circle().set_sheen_direction(UP)

        See Also
        --------
        :meth:`~.VMobject.set_sheen`
        :meth:`~.VMobject.rotate_sheen_direction`
        """

        direction = np.array(direction)
        if family:
            for submob in self.get_family():
                submob.sheen_direction = direction
        else:
            self.sheen_direction: Vector3D = direction
        return self

    def rotate_sheen_direction(
        self, angle: float, axis: Vector3D = OUT, family: bool = True
    ) -> Self:
        """Rotates the direction of the applied sheen.

        Parameters
        ----------
        angle
            Angle by which the direction of sheen is rotated.
        axis
            Axis of rotation.

        Examples
        --------
        Normal usage::

            Circle().set_sheen_direction(UP).rotate_sheen_direction(PI)

        See Also
        --------
        :meth:`~.VMobject.set_sheen_direction`
        """
        if family:
            for submob in self.get_family():
                submob.sheen_direction = rotate_vector(
                    submob.sheen_direction,
                    angle,
                    axis,
                )
        else:
            self.sheen_direction = rotate_vector(self.sheen_direction, angle, axis)
        return self

    def set_sheen(
        self, factor: float, direction: Vector3D | None = None, family: bool = True
    ) -> Self:
        """Applies a color gradient from a direction.

        Parameters
        ----------
        factor
            The extent of lustre/gradient to apply. If negative, the gradient
            starts from black, if positive the gradient starts from white and
            changes to the current color.
        direction
            Direction from where the gradient is applied.

        Examples
        --------
        .. manim:: SetSheen
            :save_last_frame:

            class SetSheen(Scene):
                def construct(self):
                    circle = Circle(fill_opacity=1).set_sheen(-0.3, DR)
                    self.add(circle)
        """

        if family:
            for submob in self.submobjects:
                submob.set_sheen(factor, direction, family)
        self.sheen_factor: float = factor
        if direction is not None:
            # family set to false because recursion will
            # already be handled above
            self.set_sheen_direction(direction, family=False)
        # Reset color to put sheen_factor into effect
        if factor != 0:
            self.set_stroke(self.get_stroke_color(), family=family)
            self.set_fill(self.get_fill_color(), family=family)
        return self

    def get_sheen_direction(self) -> Vector3D:
        return np.array(self.sheen_direction)

    def get_sheen_factor(self) -> float:
        return self.sheen_factor

    def get_gradient_start_and_end_points(self) -> tuple[Point3D, Point3D]:
        if self.shade_in_3d:
            return get_3d_vmob_gradient_start_and_end_points(self)
        else:
            direction = self.get_sheen_direction()
            c = self.get_center()
            bases = np.array(
                [self.get_edge_center(vect) - c for vect in [RIGHT, UP, OUT]],
            ).transpose()
            offset = np.dot(bases, direction)
            return (c - offset, c + offset)

    def color_using_background_image(self, background_image: Image | str) -> Self:
        self.background_image: Image | str = background_image
        self.set_color(WHITE)
        for submob in self.submobjects:
            submob.color_using_background_image(background_image)
        return self

    def get_background_image(self) -> Image | str:
        return self.background_image

    def match_background_image(self, vmobject: VMobject) -> Self:
        self.color_using_background_image(vmobject.get_background_image())
        return self

    def set_shade_in_3d(
        self, value: bool = True, z_index_as_group: bool = False
    ) -> Self:
        for submob in self.get_family():
            submob.shade_in_3d = value
            if z_index_as_group:
                submob.z_index_group = self
        return self

    def set_points(self, points: Point3D_Array) -> Self:
        self.points: Point3D_Array = np.array(points)
        return self

    def resize_points(
        self,
        new_length: int,
        resize_func: Callable[[Point3D, int], Point3D] = resize_array,
    ) -> Self:
        """Resize the array of anchor points and handles to have
        the specified size.

        Parameters
        ----------
        new_length
            The new (total) number of points.
        resize_func
            A function mapping a Numpy array (the points) and an integer
            (the target size) to a Numpy array. The default implementation
            is based on Numpy's ``resize`` function.
        """
        if new_length != len(self.points):
            self.points = resize_func(self.points, new_length)
        return self

    def set_anchors_and_handles(
        self,
        anchors1: CubicBezierPoints,
        handles1: CubicBezierPoints,
        handles2: CubicBezierPoints,
        anchors2: CubicBezierPoints,
    ) -> Self:
        """Given two sets of anchors and handles, process them to set them as anchors
        and handles of the VMobject.

        anchors1[i], handles1[i], handles2[i] and anchors2[i] define the i-th bezier
        curve of the vmobject. There are four hardcoded parameters and this is a
        problem as it makes the number of points per cubic curve unchangeable from 4
        (two anchors and two handles).

        Returns
        -------
        :class:`VMobject`
            ``self``
        """
        assert len(anchors1) == len(handles1) == len(handles2) == len(anchors2)
        nppcc = self.n_points_per_cubic_curve  # 4
        total_len = nppcc * len(anchors1)
        self.points = np.empty((total_len, self.dim))
        # the following will, from the four sets, dispatch them in points such that
        # self.points = [
        #     anchors1[0], handles1[0], handles2[0], anchors1[0], anchors1[1],
        #     handles1[1], ...
        # ]
        arrays = [anchors1, handles1, handles2, anchors2]
        for index, array in enumerate(arrays):
            self.points[index::nppcc] = array
        return self

    def clear_points(self) -> None:
        # TODO: shouldn't this return self instead of None?
        self.points = np.zeros((0, self.dim))

    def append_points(self, new_points: Point3D_Array) -> Self:
        """Append the given ``new_points`` to the end of
        :attr:`VMobject.points`.

        Parameters
        ----------
        new_points
            An array of 3D points to append.

        Returns
        -------
        :class:`VMobject`
            The VMobject itself, after appending ``new_points``.
        """
        # TODO, check that number new points is a multiple of 4?
        # or else that if len(self.points) % 4 == 1, then
        # len(new_points) % 4 == 3?
        n = len(self.points)
        points = np.empty((n + len(new_points), self.dim))
        points[:n] = self.points
        points[n:] = new_points
        self.points = points
        return self

    def start_new_path(self, point: Point3D) -> Self:
        """Append a ``point`` to the :attr:`VMobject.points`, which will be the
        beginning of a new Bézier curve in the path given by the points. If
        there's an unfinished curve at the end of :attr:`VMobject.points`,
        complete it by appending the last Bézier curve's start anchor as many
        times as needed.

        Parameters
        ----------
        point
            A 3D point to append to :attr:`VMobject.points`.

        Returns
        -------
        :class:`VMobject`
            The VMobject itself, after appending ``point`` and starting a new
            curve.
        """
        n_points = len(self.points)
        nppc = self.n_points_per_curve
        if n_points % nppc != 0:
            # close the open path by appending the last
            # start anchor sufficiently often
            last_anchor = self.get_start_anchors()[-1]
            closure = [last_anchor] * (nppc - (n_points % nppc))
            self.append_points(closure + [point])
        else:
            self.append_points([point])
        return self

    def add_cubic_bezier_curve(
        self,
        anchor1: CubicBezierPoints,
        handle1: CubicBezierPoints,
        handle2: CubicBezierPoints,
        anchor2: CubicBezierPoints,
    ) -> None:
        # TODO, check the len(self.points) % 4 == 0?
        self.append_points([anchor1, handle1, handle2, anchor2])

    # what type is curves?
    def add_cubic_bezier_curves(self, curves) -> None:
        self.append_points(curves.flatten())

    def add_cubic_bezier_curve_to(
        self,
        handle1: CubicBezierPoints,
        handle2: CubicBezierPoints,
        anchor: CubicBezierPoints,
    ) -> Self:
        """Add cubic bezier curve to the path.

        NOTE : the first anchor is not a parameter as by default the end of the last sub-path!

        Parameters
        ----------
        handle1
            first handle
        handle2
            second handle
        anchor
            anchor

        Returns
        -------
        :class:`VMobject`
            ``self``
        """
        self.throw_error_if_no_points()
        new_points = [handle1, handle2, anchor]
        if self.has_new_path_started():
            self.append_points(new_points)
        else:
            self.append_points([self.get_last_point()] + new_points)
        return self

    def add_quadratic_bezier_curve_to(
        self,
        handle: QuadraticBezierPoints,
        anchor: QuadraticBezierPoints,
    ) -> Self:
        """Add Quadratic bezier curve to the path.

        Returns
        -------
        :class:`VMobject`
            ``self``
        """
        # How does one approximate a quadratic with a cubic?
        # refer to the Wikipedia page on Bezier curves
        # https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Degree_elevation, accessed Jan 20, 2021
        # 1. Copy the end points, and then
        # 2. Place the 2 middle control points 2/3 along the line segments
        # from the end points to the quadratic curve's middle control point.
        # I think that's beautiful.
        self.add_cubic_bezier_curve_to(
            2 / 3 * handle + 1 / 3 * self.get_last_point(),
            2 / 3 * handle + 1 / 3 * anchor,
            anchor,
        )
        return self

    def add_line_to(self, point: Point3D) -> Self:
        """Add a straight line from the last point of VMobject to the given point.

        Parameters
        ----------

        point
            The end of the straight line.

        Returns
        -------
        :class:`VMobject`
            ``self``
        """
        self.add_cubic_bezier_curve_to(
            *(
                interpolate(self.get_last_point(), point, t)
                for t in self._bezier_t_values[1:]
            )
        )
        return self

    def add_smooth_curve_to(self, *points: Point3D) -> Self:
        """Creates a smooth curve from given points and add it to the VMobject. If two points are passed in, the first is interpreted
        as a handle, the second as an anchor.

        Parameters
        ----------
        points
            Points (anchor and handle, or just anchor) to add a smooth curve from

        Returns
        -------
        :class:`VMobject`
            ``self``

        Raises
        ------
        ValueError
            If 0 or more than 2 points are given.
        """
        # TODO remove the value error and just add two parameters with one optional
        if len(points) == 1:
            handle2 = None
            new_anchor = points[0]
        elif len(points) == 2:
            handle2, new_anchor = points
        else:
            name = sys._getframe(0).f_code.co_name
            raise ValueError(f"Only call {name} with 1 or 2 points")

        if self.has_new_path_started():
            self.add_line_to(new_anchor)
        else:
            self.throw_error_if_no_points()
            last_h2, last_a2 = self.points[-2:]
            last_tangent = last_a2 - last_h2
            handle1 = last_a2 + last_tangent
            if handle2 is None:
                to_anchor_vect = new_anchor - last_a2
                new_tangent = rotate_vector(last_tangent, PI, axis=to_anchor_vect)
                handle2 = new_anchor - new_tangent
            self.append_points([last_a2, handle1, handle2, new_anchor])
        return self

    def has_new_path_started(self) -> bool:
        nppcc = self.n_points_per_cubic_curve  # 4
        # A new path starting is defined by a control point which is not part of a bezier subcurve.
        return len(self.points) % nppcc == 1

    def get_last_point(self) -> Point3D:
        return self.points[-1]

    def is_closed(self) -> bool:
        # TODO use consider_points_equals_2d ?
        return self.consider_points_equals(self.points[0], self.points[-1])

    def close_path(self) -> None:
        if not self.is_closed():
            self.add_line_to(self.get_subpaths()[-1][0])

    def add_points_as_corners(self, points: Iterable[Point3D]) -> Iterable[Point3D]:
        """Append multiple straight lines at the end of
        :attr:`VMobject.points`, which connect the given ``points`` in order
        starting from the end of the current path. These ``points`` would be
        therefore the corners of the new polyline appended to the path.

        Parameters
        ----------
        points
            An array of 3D points representing the corners of the polyline to
            append to :attr:`VMobject.points`.

        Returns
        -------
        :class:`VMobject`
            The VMobject itself, after appending the straight lines to its
            path.
        """
        points = np.asarray(points).reshape(-1, self.dim)
        if self.has_new_path_started():
            # Pop the last point from self.points and
            # add it to start_corners
            start_corners = np.empty((len(points), self.dim))
            start_corners[0] = self.points[-1]
            start_corners[1:] = points[:-1]
            end_corners = points
            self.points = self.points[:-1]
        else:
            start_corners = points[:-1]
            end_corners = points[1:]

        nppcc = self.n_points_per_cubic_curve
        new_points = np.empty((nppcc * start_corners.shape[0], self.dim))
        new_points[::nppcc] = start_corners
        new_points[nppcc - 1 :: nppcc] = end_corners
        for i, t in enumerate(self._bezier_t_values):
            new_points[i::nppcc] = interpolate(start_corners, end_corners, t)

        self.append_points(new_points)
        # TODO: shouldn't this method return self instead of points?
        return points

    def set_points_as_corners(self, points: Point3D_Array) -> Self:
        """Given an array of points, set them as corners of the
        :class:`VMobject`.

        To achieve that, this algorithm sets handles aligned with the anchors
        such that the resultant Bézier curve will be the segment between the
        two anchors.

        Parameters
        ----------
        points
            Array of points that will be set as corners.

        Returns
        -------
        :class:`VMobject`
            The VMobject itself, after setting the new points as corners.


        Examples
        --------
        .. manim:: PointsAsCornersExample
            :save_last_frame:

            class PointsAsCornersExample(Scene):
                def construct(self):
                    corners = (
                        # create square
                        UR, UL,
                        DL, DR,
                        UR,
                        # create crosses
                        DL, UL,
                        DR
                    )
                    vmob = VMobject(stroke_color=RED)
                    vmob.set_points_as_corners(corners).scale(2)
                    self.add(vmob)
        """
        points = np.array(points)
        # This will set the handles aligned with the anchors.
        # Id est, a bezier curve will be the segment from the two anchors such that the handles belongs to this segment.
        self.set_anchors_and_handles(
            *(interpolate(points[:-1], points[1:], t) for t in self._bezier_t_values)
        )
        return self

    def set_points_smoothly(self, points: Point3D_Array) -> Self:
        self.set_points_as_corners(points)
        self.make_smooth()
        return self

    def change_anchor_mode(self, mode: Literal["jagged", "smooth"]) -> Self:
        """Changes the anchor mode of the bezier curves. This will modify the handles.

        There can be only two modes, "jagged", and "smooth".

        Returns
        -------
        :class:`VMobject`
            ``self``
        """
        assert mode in ["jagged", "smooth"], 'mode must be either "jagged" or "smooth"'
        nppcc = self.n_points_per_cubic_curve
        for submob in self.family_members_with_points():
            subpaths = submob.get_subpaths()
            submob.clear_points()
            # A subpath can be composed of several bezier curves.
            for subpath in subpaths:
                # This will retrieve the anchors of the subpath, by selecting every n element in the array subpath
                # The append is needed as the last element is not reached when slicing with numpy.
                anchors = np.append(subpath[::nppcc], subpath[-1:], 0)
                if mode == "smooth":
                    h1, h2 = get_smooth_handle_points(anchors)
                else:  # mode == "jagged"
                    # The following will make the handles aligned with the anchors, thus making the bezier curve a segment
                    a1 = anchors[:-1]
                    a2 = anchors[1:]
                    h1 = interpolate(a1, a2, 1.0 / 3)
                    h2 = interpolate(a1, a2, 2.0 / 3)
                new_subpath = np.array(subpath)
                new_subpath[1::nppcc] = h1
                new_subpath[2::nppcc] = h2
                submob.append_points(new_subpath)
        return self

    def make_smooth(self) -> Self:
        return self.change_anchor_mode("smooth")

    def make_jagged(self) -> Self:
        return self.change_anchor_mode("jagged")

    def add_subpath(self, points: Point3D_Array) -> Self:
        assert len(points) % 4 == 0
        self.append_points(points)
        return self

    def append_vectorized_mobject(self, vectorized_mobject: VMobject) -> None:
        if self.has_new_path_started():
            # Remove last point, which is starting
            # a new path
            self.points = self.points[:-1]
        self.append_points(vectorized_mobject.points)

    def apply_function(self, function: MappingFunction) -> Self:
        factor = self.pre_function_handle_to_anchor_scale_factor
        self.scale_handle_to_anchor_distances(factor)
        super().apply_function(function)
        self.scale_handle_to_anchor_distances(1.0 / factor)
        if self.make_smooth_after_applying_functions:
            self.make_smooth()
        return self

    def rotate(
        self,
        angle: float,
        axis: Vector3D = OUT,
        about_point: Point3D | None = None,
        **kwargs,
    ) -> Self:
        self.rotate_sheen_direction(angle, axis)
        super().rotate(angle, axis, about_point, **kwargs)
        return self

    def scale_handle_to_anchor_distances(self, factor: float) -> Self:
        """If the distance between a given handle point H and its associated
        anchor point A is d, then it changes H to be a distances factor*d
        away from A, but so that the line from A to H doesn't change.
        This is mostly useful in the context of applying a (differentiable)
        function, to preserve tangency properties.  One would pull all the
        handles closer to their anchors, apply the function then push them out
        again.

        Parameters
        ----------
        factor
            The factor used for scaling.

        Returns
        -------
        :class:`VMobject`
            ``self``
        """
        for submob in self.family_members_with_points():
            if len(submob.points) < self.n_points_per_cubic_curve:
                # The case that a bezier quad is not complete (there is no bezier curve as there is not enough control points.)
                continue
            a1, h1, h2, a2 = submob.get_anchors_and_handles()
            a1_to_h1 = h1 - a1
            a2_to_h2 = h2 - a2
            new_h1 = a1 + factor * a1_to_h1
            new_h2 = a2 + factor * a2_to_h2
            submob.set_anchors_and_handles(a1, new_h1, new_h2, a2)
        return self

    #
    def consider_points_equals(self, p0: Point3D, p1: Point3D) -> bool:
        return np.allclose(p0, p1, atol=self.tolerance_for_point_equality)

    def consider_points_equals_2d(self, p0: Point2D, p1: Point2D) -> bool:
        """Determine if two points are close enough to be considered equal.

        This uses the algorithm from np.isclose(), but expanded here for the
        2D point case. NumPy is overkill for such a small question.
        Parameters
        ----------
        p0
            first point
        p1
            second point

        Returns
        -------
        bool
            whether two points considered close.
        """
        rtol = 1.0e-5  # default from np.isclose()
        atol = self.tolerance_for_point_equality
        if abs(p0[0] - p1[0]) > atol + rtol * abs(p1[0]):
            return False
        if abs(p0[1] - p1[1]) > atol + rtol * abs(p1[1]):
            return False
        return True

    # Information about line
    def get_cubic_bezier_tuples_from_points(
        self, points: Point3D_Array
    ) -> npt.NDArray[Point3D_Array]:
        return np.array(self.gen_cubic_bezier_tuples_from_points(points))

    def gen_cubic_bezier_tuples_from_points(
        self, points: Point3D_Array
    ) -> tuple[Point3D_Array]:
        """Returns the bezier tuples from an array of points.

        self.points is a list of the anchors and handles of the bezier curves of the mobject (ie [anchor1, handle1, handle2, anchor2, anchor3 ..])
        This algorithm basically retrieve them by taking an element every n, where n is the number of control points
        of the bezier curve.


        Parameters
        ----------
        points
            Points from which control points will be extracted.

        Returns
        -------
        tuple
            Bezier control points.
        """
        nppcc = self.n_points_per_cubic_curve
        remainder = len(points) % nppcc
        points = points[: len(points) - remainder]
        # Basically take every nppcc element.
        return tuple(points[i : i + nppcc] for i in range(0, len(points), nppcc))

    def get_cubic_bezier_tuples(self) -> npt.NDArray[Point3D_Array]:
        return self.get_cubic_bezier_tuples_from_points(self.points)

    def _gen_subpaths_from_points(
        self,
        points: Point3D_Array,
        filter_func: Callable[[int], bool],
    ) -> Generator[Point3D_Array]:
        """Given an array of points defining the bezier curves of the vmobject, return subpaths formed by these points.
        Here, Two bezier curves form a path if at least two of their anchors are evaluated True by the relation defined by filter_func.

        The algorithm every bezier tuple (anchors and handles) in ``self.points`` (by regrouping each n elements, where
        n is the number of points per cubic curve)), and evaluate the relation between two anchors with filter_func.
        NOTE : The filter_func takes an int n as parameter, and will evaluate the relation between points[n] and points[n - 1]. This should probably be changed so
        the function takes two points as parameters.

        Parameters
        ----------
        points
            points defining the bezier curve.
        filter_func
            Filter-func defining the relation.

        Returns
        -------
        Generator[Point3D_Array]
            subpaths formed by the points.
        """
        nppcc = self.n_points_per_cubic_curve
        filtered = filter(filter_func, range(nppcc, len(points), nppcc))
        split_indices = [0] + list(filtered) + [len(points)]
        return (
            points[i1:i2]
            for i1, i2 in zip(split_indices, split_indices[1:])
            if (i2 - i1) >= nppcc
        )

    def get_subpaths_from_points(self, points: Point3D_Array) -> list[Point3D_Array]:
        return list(
            self._gen_subpaths_from_points(
                points,
                lambda n: not self.consider_points_equals(points[n - 1], points[n]),
            ),
        )

    def gen_subpaths_from_points_2d(
        self, points: Point3D_Array
    ) -> Generator[Point3D_Array]:
        return self._gen_subpaths_from_points(
            points,
            lambda n: not self.consider_points_equals_2d(points[n - 1], points[n]),
        )

    def get_subpaths(self) -> list[Point3D_Array]:
        """Returns subpaths formed by the curves of the VMobject.

        Subpaths are ranges of curves with each pair of consecutive curves having their end/start points coincident.

        Returns
        -------
        list[Point3D_Array]
            subpaths.
        """
        return self.get_subpaths_from_points(self.points)

    def get_nth_curve_points(self, n: int) -> Point3D_Array:
        """Returns the points defining the nth curve of the vmobject.

        Parameters
        ----------
        n
            index of the desired bezier curve.

        Returns
        -------
        Point3D_Array
            points defining the nth bezier curve (anchors, handles)
        """
        assert n < self.get_num_curves()
        nppcc = self.n_points_per_cubic_curve
        return self.points[nppcc * n : nppcc * (n + 1)]

    def get_nth_curve_function(self, n: int) -> Callable[[float], Point3D]:
        """Returns the expression of the nth curve.

        Parameters
        ----------
        n
            index of the desired curve.

        Returns
        -------
        Callable[float, Point3D]
            expression of the nth bezier curve.
        """
        return bezier(self.get_nth_curve_points(n))

    def get_nth_curve_length_pieces(
        self,
        n: int,
        sample_points: int | None = None,
    ) -> npt.NDArray[ManimFloat]:
        """Returns the array of short line lengths used for length approximation.

        Parameters
        ----------
        n
            The index of the desired curve.
        sample_points
            The number of points to sample to find the length.

        Returns
        -------
            The short length-pieces of the nth curve.
        """
        if sample_points is None:
            sample_points = 10

        curve = self.get_nth_curve_function(n)
        points = np.array([curve(a) for a in np.linspace(0, 1, sample_points)])
        diffs = points[1:] - points[:-1]
        norms = np.linalg.norm(diffs, axis=1)

        return norms

    def get_nth_curve_length(
        self,
        n: int,
        sample_points: int | None = None,
    ) -> float:
        """Returns the (approximate) length of the nth curve.

        Parameters
        ----------
        n
            The index of the desired curve.
        sample_points
            The number of points to sample to find the length.

        Returns
        -------
        length : :class:`float`
            The length of the nth curve.
        """

        _, length = self.get_nth_curve_function_with_length(n, sample_points)

        return length

    def get_nth_curve_function_with_length(
        self,
        n: int,
        sample_points: int | None = None,
    ) -> tuple[Callable[[float], Point3D], float]:
        """Returns the expression of the nth curve along with its (approximate) length.

        Parameters
        ----------
        n
            The index of the desired curve.
        sample_points
            The number of points to sample to find the length.

        Returns
        -------
        curve : Callable[[float], Point3D]
            The function for the nth curve.
        length : :class:`float`
            The length of the nth curve.
        """

        curve = self.get_nth_curve_function(n)
        norms = self.get_nth_curve_length_pieces(n, sample_points=sample_points)
        length = np.sum(norms)

        return curve, length

    def get_num_curves(self) -> int:
        """Returns the number of curves of the vmobject.

        Returns
        -------
        int
            number of curves of the vmobject.
        """
        nppcc = self.n_points_per_cubic_curve
        return len(self.points) // nppcc

    def get_curve_functions(
        self,
    ) -> Generator[Callable[[float], Point3D]]:
        """Gets the functions for the curves of the mobject.

        Returns
        -------
        Generator[Callable[[float], Point3D]]
            The functions for the curves.
        """

        num_curves = self.get_num_curves()

        for n in range(num_curves):
            yield self.get_nth_curve_function(n)

    def get_curve_functions_with_lengths(
        self, **kwargs
    ) -> Generator[tuple[Callable[[float], Point3D], float]]:
        """Gets the functions and lengths of the curves for the mobject.

        Parameters
        ----------
        **kwargs
            The keyword arguments passed to :meth:`get_nth_curve_function_with_length`

        Returns
        -------
        Generator[tuple[Callable[[float], Point3D], float]]
            The functions and lengths of the curves.
        """

        num_curves = self.get_num_curves()

        for n in range(num_curves):
            yield self.get_nth_curve_function_with_length(n, **kwargs)

    def point_from_proportion(self, alpha: float) -> Point3D:
        """Gets the point at a proportion along the path of the :class:`VMobject`.

        Parameters
        ----------
        alpha
            The proportion along the the path of the :class:`VMobject`.

        Returns
        -------
        :class:`numpy.ndarray`
            The point on the :class:`VMobject`.

        Raises
        ------
        :exc:`ValueError`
            If ``alpha`` is not between 0 and 1.
        :exc:`Exception`
            If the :class:`VMobject` has no points.

        Example
        -------
        .. manim:: PointFromProportion
            :save_last_frame:

            class PointFromProportion(Scene):
                def construct(self):
                    line = Line(2*DL, 2*UR)
                    self.add(line)
                    colors = (RED, BLUE, YELLOW)
                    proportions = (1/4, 1/2, 3/4)
                    for color, proportion in zip(colors, proportions):
                        self.add(Dot(color=color).move_to(
                                line.point_from_proportion(proportion)
                        ))
        """

        if alpha < 0 or alpha > 1:
            raise ValueError(f"Alpha {alpha} not between 0 and 1.")

        self.throw_error_if_no_points()
        if alpha == 1:
            return self.points[-1]

        curves_and_lengths = tuple(self.get_curve_functions_with_lengths())

        target_length = alpha * sum(length for _, length in curves_and_lengths)
        current_length = 0

        for curve, length in curves_and_lengths:
            if current_length + length >= target_length:
                if length != 0:
                    residue = (target_length - current_length) / length
                else:
                    residue = 0

                return curve(residue)

            current_length += length
        raise Exception(
            "Not sure how you reached here, please file a bug report at https://github.com/ManimCommunity/manim/issues/new/choose"
        )

    def proportion_from_point(
        self,
        point: Iterable[float | int],
    ) -> float:
        """Returns the proportion along the path of the :class:`VMobject`
        a particular given point is at.

        Parameters
        ----------
        point
            The Cartesian coordinates of the point which may or may not lie on the :class:`VMobject`

        Returns
        -------
        float
            The proportion along the path of the :class:`VMobject`.

        Raises
        ------
        :exc:`ValueError`
            If ``point`` does not lie on the curve.
        :exc:`Exception`
            If the :class:`VMobject` has no points.
        """
        self.throw_error_if_no_points()

        # Iterate over each bezier curve that the ``VMobject`` is composed of, checking
        # if the point lies on that curve. If it does not lie on that curve, add
        # the whole length of the curve to ``target_length`` and move onto the next
        # curve. If the point does lie on the curve, add how far along the curve
        # the point is to ``target_length``.
        # Then, divide ``target_length`` by the total arc length of the shape to get
        # the proportion along the ``VMobject`` the point is at.

        num_curves = self.get_num_curves()
        total_length = self.get_arc_length()
        target_length = 0
        for n in range(num_curves):
            control_points = self.get_nth_curve_points(n)
            length = self.get_nth_curve_length(n)
            proportions_along_bezier = proportions_along_bezier_curve_for_point(
                point,
                control_points,
            )
            if len(proportions_along_bezier) > 0:
                proportion_along_nth_curve = max(proportions_along_bezier)
                target_length += length * proportion_along_nth_curve
                break
            target_length += length
        else:
            raise ValueError(f"Point {point} does not lie on this curve.")

        alpha = target_length / total_length

        return alpha

    def get_anchors_and_handles(self) -> list[Point3D_Array]:
        """Returns anchors1, handles1, handles2, anchors2,
        where (anchors1[i], handles1[i], handles2[i], anchors2[i])
        will be four points defining a cubic bezier curve
        for any i in range(0, len(anchors1))

        Returns
        -------
        `list[Point3D_Array]`
            Iterable of the anchors and handles.
        """
        nppcc = self.n_points_per_cubic_curve
        return [self.points[i::nppcc] for i in range(nppcc)]

    def get_start_anchors(self) -> Point3D_Array:
        """Returns the start anchors of the bezier curves.

        Returns
        -------
        Point3D_Array
            Starting anchors
        """
        return self.points[:: self.n_points_per_cubic_curve]

    def get_end_anchors(self) -> Point3D_Array:
        """Return the end anchors of the bezier curves.

        Returns
        -------
        Point3D_Array
            Starting anchors
        """
        nppcc = self.n_points_per_cubic_curve
        return self.points[nppcc - 1 :: nppcc]

    def get_anchors(self) -> Point3D_Array:
        """Returns the anchors of the curves forming the VMobject.

        Returns
        -------
        Point3D_Array
            The anchors.
        """
        if self.points.shape[0] == 1:
            return self.points

        s = self.get_start_anchors()
        e = self.get_end_anchors()
        return list(it.chain.from_iterable(zip(s, e)))

    def get_points_defining_boundary(self) -> Point3D_Array:
        # Probably returns all anchors, but this is weird regarding  the name of the method.
        return np.array(
            tuple(it.chain(*(sm.get_anchors() for sm in self.get_family())))
        )

    def get_arc_length(self, sample_points_per_curve: int | None = None) -> float:
        """Return the approximated length of the whole curve.

        Parameters
        ----------
        sample_points_per_curve
            Number of sample points per curve used to approximate the length. More points result in a better approximation.

        Returns
        -------
        float
            The length of the :class:`VMobject`.
        """

        return sum(
            length
            for _, length in self.get_curve_functions_with_lengths(
                sample_points=sample_points_per_curve,
            )
        )

    # Alignment
    def align_points(self, vmobject: VMobject) -> Self:
        """Adds points to self and vmobject so that they both have the same number of subpaths, with
        corresponding subpaths each containing the same number of points.

        Points are added either by subdividing curves evenly along the subpath, or by creating new subpaths consisting
        of a single point repeated.

        Parameters
        ----------
        vmobject
            The object to align points with.

        Returns
        -------
        :class:`VMobject`
           ``self``
        """
        self.align_rgbas(vmobject)
        # TODO: This shortcut can be a bit over eager. What if they have the same length, but different subpath lengths?
        if self.get_num_points() == vmobject.get_num_points():
            return

        for mob in self, vmobject:
            # If there are no points, add one to
            # wherever the "center" is
            if mob.has_no_points():
                mob.start_new_path(mob.get_center())
            # If there's only one point, turn it into
            # a null curve
            if mob.has_new_path_started():
                mob.add_line_to(mob.get_last_point())

        # Figure out what the subpaths are
        subpaths1 = self.get_subpaths()
        subpaths2 = vmobject.get_subpaths()
        n_subpaths = max(len(subpaths1), len(subpaths2))
        # Start building new ones
        new_path1 = np.zeros((0, self.dim))
        new_path2 = np.zeros((0, self.dim))

        nppcc = self.n_points_per_cubic_curve

        def get_nth_subpath(path_list, n):
            if n >= len(path_list):
                # Create a null path at the very end
                return [path_list[-1][-1]] * nppcc
            path = path_list[n]
            # Check for useless points at the end of the path and remove them
            # https://github.com/ManimCommunity/manim/issues/1959
            while len(path) > nppcc:
                # If the last nppc points are all equal to the preceding point
                if self.consider_points_equals(path[-nppcc:], path[-nppcc - 1]):
                    path = path[:-nppcc]
                else:
                    break
            return path

        for n in range(n_subpaths):
            # For each pair of subpaths, add points until they are the same length
            sp1 = get_nth_subpath(subpaths1, n)
            sp2 = get_nth_subpath(subpaths2, n)
            diff1 = max(0, (len(sp2) - len(sp1)) // nppcc)
            diff2 = max(0, (len(sp1) - len(sp2)) // nppcc)
            sp1 = self.insert_n_curves_to_point_list(diff1, sp1)
            sp2 = self.insert_n_curves_to_point_list(diff2, sp2)
            new_path1 = np.append(new_path1, sp1, axis=0)
            new_path2 = np.append(new_path2, sp2, axis=0)
        self.set_points(new_path1)
        vmobject.set_points(new_path2)
        return self

    def insert_n_curves(self, n: int) -> Self:
        """Inserts n curves to the bezier curves of the vmobject.

        Parameters
        ----------
        n
            Number of curves to insert.

        Returns
        -------
        :class:`VMobject`
            ``self``
        """
        new_path_point = None
        if self.has_new_path_started():
            new_path_point = self.get_last_point()

        new_points = self.insert_n_curves_to_point_list(n, self.points)
        self.set_points(new_points)

        if new_path_point is not None:
            self.append_points([new_path_point])
        return self

    def insert_n_curves_to_point_list(
        self, n: int, points: Point3D_Array
    ) -> npt.NDArray[BezierPoints]:
        """Given an array of k points defining a bezier curves (anchors and handles), returns points defining exactly k + n bezier curves.

        Parameters
        ----------
        n
            Number of desired curves.
        points
            Starting points.

        Returns
        -------
            Points generated.
        """

        if len(points) == 1:
            nppcc = self.n_points_per_cubic_curve
            return np.repeat(points, nppcc * n, 0)
        bezier_tuples = self.get_cubic_bezier_tuples_from_points(points)
        current_number_of_curves = len(bezier_tuples)
        new_number_of_curves = current_number_of_curves + n
        new_bezier_tuples = bezier_remap(bezier_tuples, new_number_of_curves)
        new_points = new_bezier_tuples.reshape(-1, 3)
        return new_points

    def align_rgbas(self, vmobject: VMobject) -> Self:
        attrs = ["fill_rgbas", "stroke_rgbas", "background_stroke_rgbas"]
        for attr in attrs:
            a1 = getattr(self, attr)
            a2 = getattr(vmobject, attr)
            if len(a1) > len(a2):
                new_a2 = stretch_array_to_length(a2, len(a1))
                setattr(vmobject, attr, new_a2)
            elif len(a2) > len(a1):
                new_a1 = stretch_array_to_length(a1, len(a2))
                setattr(self, attr, new_a1)
        return self

    def get_point_mobject(self, center: Point3D | None = None) -> VectorizedPoint:
        if center is None:
            center = self.get_center()
        point = VectorizedPoint(center)
        point.match_style(self)
        return point

    def interpolate_color(
        self, mobject1: VMobject, mobject2: VMobject, alpha: float
    ) -> None:
        attrs = [
            "fill_rgbas",
            "stroke_rgbas",
            "background_stroke_rgbas",
            "stroke_width",
            "background_stroke_width",
            "sheen_direction",
            "sheen_factor",
        ]
        for attr in attrs:
            setattr(
                self,
                attr,
                interpolate(getattr(mobject1, attr), getattr(mobject2, attr), alpha),
            )
            if alpha == 1.0:
                val = getattr(mobject2, attr)
                if isinstance(val, np.ndarray):
                    val = val.copy()
                setattr(self, attr, val)

    def pointwise_become_partial(
        self,
        vmobject: VMobject,
        a: float,
        b: float,
    ) -> Self:
        """Given two bounds a and b, transforms the points of the self vmobject into the points of the vmobject
        passed as parameter with respect to the bounds. Points here stand for control points of the bezier curves (anchors and handles)

        Parameters
        ----------
        vmobject
            The vmobject that will serve as a model.
        a
            upper-bound.
        b
            lower-bound

        Returns
        -------
        :class:`VMobject`
            ``self``
        """
        assert isinstance(vmobject, VMobject)
        # Partial curve includes three portions:
        # - A middle section, which matches the curve exactly
        # - A start, which is some ending portion of an inner cubic
        # - An end, which is the starting portion of a later inner cubic
        if a <= 0 and b >= 1:
            self.set_points(vmobject.points)
            return self
        bezier_quads = vmobject.get_cubic_bezier_tuples()
        num_cubics = len(bezier_quads)

        # The following two lines will compute which bezier curves of the given mobject need to be processed.
        # The residue basically indicates de proportion of the selected bezier curve that have to be selected.
        # Ex : if lower_index is 3, and lower_residue is 0.4, then the algorithm will append to the points 0.4 of the third bezier curve
        lower_index, lower_residue = integer_interpolate(0, num_cubics, a)
        upper_index, upper_residue = integer_interpolate(0, num_cubics, b)

        self.clear_points()
        if num_cubics == 0:
            return self
        if lower_index == upper_index:
            self.append_points(
                partial_bezier_points(
                    bezier_quads[lower_index],
                    lower_residue,
                    upper_residue,
                ),
            )
        else:
            self.append_points(
                partial_bezier_points(bezier_quads[lower_index], lower_residue, 1),
            )
            for quad in bezier_quads[lower_index + 1 : upper_index]:
                self.append_points(quad)
            self.append_points(
                partial_bezier_points(bezier_quads[upper_index], 0, upper_residue),
            )
        return self

    def get_subcurve(self, a: float, b: float) -> Self:
        """Returns the subcurve of the VMobject between the interval [a, b].
        The curve is a VMobject itself.

        Parameters
        ----------

        a
            The lower bound.
        b
            The upper bound.

        Returns
        -------
        VMobject
            The subcurve between of [a, b]
        """
        if self.is_closed() and a > b:
            vmob = self.copy()
            vmob.pointwise_become_partial(self, a, 1)
            vmob2 = self.copy()
            vmob2.pointwise_become_partial(self, 0, b)
            vmob.append_vectorized_mobject(vmob2)
        else:
            vmob = self.copy()
            vmob.pointwise_become_partial(self, a, b)
        return vmob

    def get_direction(self) -> Literal["CW", "CCW"]:
        """Uses :func:`~.space_ops.shoelace_direction` to calculate the direction.
        The direction of points determines in which direction the
        object is drawn, clockwise or counterclockwise.

        Examples
        --------
        The default direction of a :class:`~.Circle` is counterclockwise::

            >>> from manim import Circle
            >>> Circle().get_direction()
            'CCW'

        Returns
        -------
        :class:`str`
            Either ``"CW"`` or ``"CCW"``.
        """
        return shoelace_direction(self.get_start_anchors())

    def reverse_direction(self) -> Self:
        """Reverts the point direction by inverting the point order.

        Returns
        -------
        :class:`VMobject`
            Returns self.

        Examples
        --------
        .. manim:: ChangeOfDirection

            class ChangeOfDirection(Scene):
                def construct(self):
                    ccw = RegularPolygon(5)
                    ccw.shift(LEFT)
                    cw = RegularPolygon(5)
                    cw.shift(RIGHT).reverse_direction()

                    self.play(Create(ccw), Create(cw),
                    run_time=4)
        """
        self.points = self.points[::-1]
        return self

    def force_direction(self, target_direction: Literal["CW", "CCW"]) -> Self:
        """Makes sure that points are either directed clockwise or
        counterclockwise.

        Parameters
        ----------
        target_direction
            Either ``"CW"`` or ``"CCW"``.
        """
        if target_direction not in ("CW", "CCW"):
            raise ValueError('Invalid input for force_direction. Use "CW" or "CCW"')
        if self.get_direction() != target_direction:
            # Since we already assured the input is CW or CCW,
            # and the directions don't match, we just reverse
            self.reverse_direction()
        return self


class VGroup(VMobject, metaclass=ConvertToOpenGL):
    """A group of vectorized mobjects.

    This can be used to group multiple :class:`~.VMobject` instances together
    in order to scale, move, ... them together.

    Notes
    -----
    When adding the same mobject more than once, repetitions are ignored.
    Use :meth:`.Mobject.copy` to create a separate copy which can then
    be added to the group.

    Examples
    --------

    To add :class:`~.VMobject`s to a :class:`~.VGroup`, you can either use the
    :meth:`~.VGroup.add` method, or use the `+` and `+=` operators. Similarly, you
    can subtract elements of a VGroup via :meth:`~.VGroup.remove` method, or
    `-` and `-=` operators:

        >>> from manim import Triangle, Square, VGroup
        >>> vg = VGroup()
        >>> triangle, square = Triangle(), Square()
        >>> vg.add(triangle)
        VGroup(Triangle)
        >>> vg + square  # a new VGroup is constructed
        VGroup(Triangle, Square)
        >>> vg  # not modified
        VGroup(Triangle)
        >>> vg += square
        >>> vg  # modifies vg
        VGroup(Triangle, Square)
        >>> vg.remove(triangle)
        VGroup(Square)
        >>> vg - square  # a new VGroup is constructed
        VGroup()
        >>> vg  # not modified
        VGroup(Square)
        >>> vg -= square
        >>> vg  # modifies vg
        VGroup()

    .. manim:: ArcShapeIris
        :save_last_frame:

        class ArcShapeIris(Scene):
            def construct(self):
                colors = [DARK_BROWN, BLUE_E, BLUE_D, BLUE_A, TEAL_B, GREEN_B, YELLOW_E]
                radius = [1 + rad * 0.1 for rad in range(len(colors))]

                circles_group = VGroup()

                # zip(radius, color) makes the iterator [(radius[i], color[i]) for i in range(radius)]
                circles_group.add(*[Circle(radius=rad, stroke_width=10, color=col)
                                    for rad, col in zip(radius, colors)])
                self.add(circles_group)

    """

    def __init__(self, *vmobjects, **kwargs):
        super().__init__(**kwargs)
        self.add(*vmobjects)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({", ".join(str(mob) for mob in self.submobjects)})'

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__} of {len(self.submobjects)} "
            f"submobject{'s' if len(self.submobjects) > 0 else ''}"
        )

    def add(self, *vmobjects: VMobject) -> Self:
        """Checks if all passed elements are an instance of VMobject and then add them to submobjects

        Parameters
        ----------
        vmobjects
            List of VMobject to add

        Returns
        -------
        :class:`VGroup`

        Raises
        ------
        TypeError
            If one element of the list is not an instance of VMobject

        Examples
        --------
        .. manim:: AddToVGroup

            class AddToVGroup(Scene):
                def construct(self):
                    circle_red = Circle(color=RED)
                    circle_green = Circle(color=GREEN)
                    circle_blue = Circle(color=BLUE)
                    circle_red.shift(LEFT)
                    circle_blue.shift(RIGHT)
                    gr = VGroup(circle_red, circle_green)
                    gr2 = VGroup(circle_blue) # Constructor uses add directly
                    self.add(gr,gr2)
                    self.wait()
                    gr += gr2 # Add group to another
                    self.play(
                        gr.animate.shift(DOWN),
                    )
                    gr -= gr2 # Remove group
                    self.play( # Animate groups separately
                        gr.animate.shift(LEFT),
                        gr2.animate.shift(UP),
                    )
                    self.play( #Animate groups without modification
                        (gr+gr2).animate.shift(RIGHT)
                    )
                    self.play( # Animate group without component
                        (gr-circle_red).animate.shift(RIGHT)
                    )
        """
        return super().add(*vmobjects)

    def __add__(self, vmobject: VMobject) -> Self:
        return VGroup(*self.submobjects, vmobject)

    def __iadd__(self, vmobject: VMobject) -> Self:
        return self.add(vmobject)

    def __sub__(self, vmobject: VMobject) -> Self:
        copy = VGroup(*self.submobjects)
        copy.remove(vmobject)
        return copy

    def __isub__(self, vmobject: VMobject) -> Self:
        return self.remove(vmobject)

    def __setitem__(self, key: int, value: VMobject | Sequence[VMobject]) -> None:
        """Override the [] operator for item assignment.

        Parameters
        ----------
        key
            The index of the submobject to be assigned
        value
            The vmobject value to assign to the key

        Returns
        -------
        None

        Tests
        -----
        Check that item assignment does not raise error::
            >>> vgroup = VGroup(VMobject())
            >>> new_obj = VMobject()
            >>> vgroup[0] = new_obj
        """
        self._assert_valid_submobjects(tuplify(value))
        self.submobjects[key] = value


class VDict(VMobject, metaclass=ConvertToOpenGL):
    """A VGroup-like class, also offering submobject access by
    key, like a python dict

    Parameters
    ----------
    mapping_or_iterable
            The parameter specifying the key-value mapping of keys and mobjects.
    show_keys
            Whether to also display the key associated with
            the mobject. This might be useful when debugging,
            especially when there are a lot of mobjects in the
            :class:`VDict`. Defaults to False.
    kwargs
            Other arguments to be passed to `Mobject`.

    Attributes
    ----------
    show_keys : :class:`bool`
            Whether to also display the key associated with
            the mobject. This might be useful when debugging,
            especially when there are a lot of mobjects in the
            :class:`VDict`. When displayed, the key is towards
            the left of the mobject.
            Defaults to False.
    submob_dict : :class:`dict`
            Is the actual python dictionary that is used to bind
            the keys to the mobjects.

    Examples
    --------

    .. manim:: ShapesWithVDict

        class ShapesWithVDict(Scene):
            def construct(self):
                square = Square().set_color(RED)
                circle = Circle().set_color(YELLOW).next_to(square, UP)

                # create dict from list of tuples each having key-mobject pair
                pairs = [("s", square), ("c", circle)]
                my_dict = VDict(pairs, show_keys=True)

                # display it just like a VGroup
                self.play(Create(my_dict))
                self.wait()

                text = Tex("Some text").set_color(GREEN).next_to(square, DOWN)

                # add a key-value pair by wrapping it in a single-element list of tuple
                # after attrs branch is merged, it will be easier like `.add(t=text)`
                my_dict.add([("t", text)])
                self.wait()

                rect = Rectangle().next_to(text, DOWN)
                # can also do key assignment like a python dict
                my_dict["r"] = rect

                # access submobjects like a python dict
                my_dict["t"].set_color(PURPLE)
                self.play(my_dict["t"].animate.scale(3))
                self.wait()

                # also supports python dict styled reassignment
                my_dict["t"] = Tex("Some other text").set_color(BLUE)
                self.wait()

                # remove submobject by key
                my_dict.remove("t")
                self.wait()

                self.play(Uncreate(my_dict["s"]))
                self.wait()

                self.play(FadeOut(my_dict["c"]))
                self.wait()

                self.play(FadeOut(my_dict["r"], shift=DOWN))
                self.wait()

                # you can also make a VDict from an existing dict of mobjects
                plain_dict = {
                    1: Integer(1).shift(DOWN),
                    2: Integer(2).shift(2 * DOWN),
                    3: Integer(3).shift(3 * DOWN),
                }

                vdict_from_plain_dict = VDict(plain_dict)
                vdict_from_plain_dict.shift(1.5 * (UP + LEFT))
                self.play(Create(vdict_from_plain_dict))

                # you can even use zip
                vdict_using_zip = VDict(zip(["s", "c", "r"], [Square(), Circle(), Rectangle()]))
                vdict_using_zip.shift(1.5 * RIGHT)
                self.play(Create(vdict_using_zip))
                self.wait()
    """

    def __init__(
        self,
        mapping_or_iterable: (
            Mapping[Hashable, VMobject] | Iterable[tuple[Hashable, VMobject]]
        ) = {},
        show_keys: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.show_keys = show_keys
        self.submob_dict = {}
        self.add(mapping_or_iterable)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self.submob_dict)})"

    def add(
        self,
        mapping_or_iterable: (
            Mapping[Hashable, VMobject] | Iterable[tuple[Hashable, VMobject]]
        ),
    ) -> Self:
        """Adds the key-value pairs to the :class:`VDict` object.

        Also, it internally adds the value to the `submobjects` :class:`list`
        of :class:`~.Mobject`, which is responsible for actual on-screen display.

        Parameters
        ---------
        mapping_or_iterable
            The parameter specifying the key-value mapping of keys and mobjects.

        Returns
        -------
        :class:`VDict`
            Returns the :class:`VDict` object on which this method was called.

        Examples
        --------
        Normal usage::

            square_obj = Square()
            my_dict.add([("s", square_obj)])
        """
        for key, value in dict(mapping_or_iterable).items():
            self.add_key_value_pair(key, value)

        return self

    def remove(self, key: Hashable) -> Self:
        """Removes the mobject from the :class:`VDict` object having the key `key`

        Also, it internally removes the mobject from the `submobjects` :class:`list`
        of :class:`~.Mobject`, (which is responsible for removing it from the screen)

        Parameters
        ----------
        key
            The key of the submoject to be removed.

        Returns
        -------
        :class:`VDict`
            Returns the :class:`VDict` object on which this method was called.

        Examples
        --------
        Normal usage::

            my_dict.remove("square")
        """
        if key not in self.submob_dict:
            raise KeyError("The given key '%s' is not present in the VDict" % str(key))
        super().remove(self.submob_dict[key])
        del self.submob_dict[key]
        return self

    def __getitem__(self, key: Hashable):
        """Override the [] operator for item retrieval.

        Parameters
        ----------
        key
           The key of the submoject to be accessed

        Returns
        -------
        :class:`VMobject`
           The submobject corresponding to the key `key`

        Examples
        --------
        Normal usage::

           self.play(Create(my_dict["s"]))
        """
        submob = self.submob_dict[key]
        return submob

    def __setitem__(self, key: Hashable, value: VMobject) -> None:
        """Override the [] operator for item assignment.

        Parameters
        ----------
        key
            The key of the submoject to be assigned
        value
            The submobject to bind the key to

        Returns
        -------
        None

        Examples
        --------
        Normal usage::

            square_obj = Square()
            my_dict["sq"] = square_obj
        """
        if key in self.submob_dict:
            self.remove(key)
        self.add([(key, value)])

    def __delitem__(self, key: Hashable):
        """Override the del operator for deleting an item.

        Parameters
        ----------
        key
            The key of the submoject to be deleted

        Returns
        -------
        None

        Examples
        --------
        ::

            >>> from manim import *
            >>> my_dict = VDict({'sq': Square()})
            >>> 'sq' in my_dict
            True
            >>> del my_dict['sq']
            >>> 'sq' in my_dict
            False

        Notes
        -----
        Removing an item from a VDict does not remove that item from any Scene
        that the VDict is part of.

        """
        del self.submob_dict[key]

    def __contains__(self, key: Hashable):
        """Override the in operator.

        Parameters
        ----------
        key
            The key to check membership of.

        Returns
        -------
        :class:`bool`

        Examples
        --------
        ::

            >>> from manim import *
            >>> my_dict = VDict({'sq': Square()})
            >>> 'sq' in my_dict
            True

        """
        return key in self.submob_dict

    def get_all_submobjects(self) -> list[list]:
        """To get all the submobjects associated with a particular :class:`VDict` object

        Returns
        -------
        :class:`dict_values`
            All the submobjects associated with the :class:`VDict` object

        Examples
        --------
        Normal usage::

            for submob in my_dict.get_all_submobjects():
                self.play(Create(submob))
        """
        submobjects = self.submob_dict.values()
        return submobjects

    def add_key_value_pair(self, key: Hashable, value: VMobject) -> None:
        """A utility function used by :meth:`add` to add the key-value pair
        to :attr:`submob_dict`. Not really meant to be used externally.

        Parameters
        ----------
        key
            The key of the submobject to be added.
        value
            The mobject associated with the key

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If the value is not an instance of VMobject

        Examples
        --------
        Normal usage::

            square_obj = Square()
            self.add_key_value_pair("s", square_obj)

        """
        self._assert_valid_submobjects([value])
        mob = value
        if self.show_keys:
            # This import is here and not at the top to avoid circular import
            from manim.mobject.text.tex_mobject import Tex

            key_text = Tex(str(key)).next_to(value, LEFT)
            mob.add(key_text)

        self.submob_dict[key] = mob
        super().add(value)


class VectorizedPoint(VMobject, metaclass=ConvertToOpenGL):
    def __init__(
        self,
        location: Point3D = ORIGIN,
        color: ManimColor = BLACK,
        fill_opacity: float = 0,
        stroke_width: float = 0,
        artificial_width: float = 0.01,
        artificial_height: float = 0.01,
        **kwargs,
    ) -> None:
        self.artificial_width = artificial_width
        self.artificial_height = artificial_height
        super().__init__(
            color=color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
            **kwargs,
        )
        self.set_points(np.array([location]))

    basecls = OpenGLVMobject if config.renderer == RendererType.OPENGL else VMobject

    @basecls.width.getter
    def width(self) -> float:
        return self.artificial_width

    @basecls.height.getter
    def height(self) -> float:
        return self.artificial_height

    def get_location(self) -> Point3D:
        return np.array(self.points[0])

    def set_location(self, new_loc: Point3D):
        self.set_points(np.array([new_loc]))


class CurvesAsSubmobjects(VGroup):
    """Convert a curve's elements to submobjects.

    Examples
    --------
    .. manim:: LineGradientExample
        :save_last_frame:

        class LineGradientExample(Scene):
            def construct(self):
                curve = ParametricFunction(lambda t: [t, np.sin(t), 0], t_range=[-PI, PI, 0.01], stroke_width=10)
                new_curve = CurvesAsSubmobjects(curve)
                new_curve.set_color_by_gradient(BLUE, RED)
                self.add(new_curve.shift(UP), curve)

    """

    def __init__(self, vmobject: VMobject, **kwargs) -> None:
        super().__init__(**kwargs)
        tuples = vmobject.get_cubic_bezier_tuples()
        for tup in tuples:
            part = VMobject()
            part.set_points(tup)
            part.match_style(vmobject)
            self.add(part)

    def point_from_proportion(self, alpha: float) -> Point3D:
        """Gets the point at a proportion along the path of the :class:`CurvesAsSubmobjects`.

        Parameters
        ----------
        alpha
            The proportion along the the path of the :class:`CurvesAsSubmobjects`.

        Returns
        -------
        :class:`numpy.ndarray`
            The point on the :class:`CurvesAsSubmobjects`.

        Raises
        ------
        :exc:`ValueError`
            If ``alpha`` is not between 0 and 1.
        :exc:`Exception`
            If the :class:`CurvesAsSubmobjects` has no submobjects, or no submobject has points.
        """
        if alpha < 0 or alpha > 1:
            raise ValueError(f"Alpha {alpha} not between 0 and 1.")

        self._throw_error_if_no_submobjects()
        submobjs_with_pts = self._get_submobjects_with_points()

        if alpha == 1:
            return submobjs_with_pts[-1].points[-1]

        submobjs_arc_lengths = tuple(
            part.get_arc_length() for part in submobjs_with_pts
        )

        total_length = sum(submobjs_arc_lengths)
        target_length = alpha * total_length
        current_length = 0

        for i, part in enumerate(submobjs_with_pts):
            part_length = submobjs_arc_lengths[i]
            if current_length + part_length >= target_length:
                residue = (target_length - current_length) / part_length
                return part.point_from_proportion(residue)

            current_length += part_length

    def _throw_error_if_no_submobjects(self):
        if len(self.submobjects) == 0:
            caller_name = sys._getframe(1).f_code.co_name
            raise Exception(
                f"Cannot call CurvesAsSubmobjects. {caller_name} for a CurvesAsSubmobject with no submobjects"
            )

    def _get_submobjects_with_points(self):
        submobjs_with_pts = tuple(
            part for part in self.submobjects if len(part.points) > 0
        )
        if len(submobjs_with_pts) == 0:
            caller_name = sys._getframe(1).f_code.co_name
            raise Exception(
                f"Cannot call CurvesAsSubmobjects. {caller_name} for a CurvesAsSubmobject whose submobjects have no points"
            )
        return submobjs_with_pts


class DashedVMobject(VMobject, metaclass=ConvertToOpenGL):
    """A :class:`VMobject` composed of dashes instead of lines.

    Parameters
    ----------
        vmobject
            The object that will get dashed
        num_dashes
            Number of dashes to add.
        dashed_ratio
            Ratio of dash to empty space.
        dash_offset
            Shifts the starting point of dashes along the
            path. Value 1 shifts by one full dash length.
        equal_lengths
            If ``True``, dashes will be (approximately) equally long.
            If ``False``, dashes will be split evenly in the curve's
            input t variable (legacy behavior).

    Examples
    --------
    .. manim:: DashedVMobjectExample
        :save_last_frame:

        class DashedVMobjectExample(Scene):
            def construct(self):
                r = 0.5

                top_row = VGroup()  # Increasing num_dashes
                for dashes in range(1, 12):
                    circ = DashedVMobject(Circle(radius=r, color=WHITE), num_dashes=dashes)
                    top_row.add(circ)

                middle_row = VGroup()  # Increasing dashed_ratio
                for ratio in np.arange(1 / 11, 1, 1 / 11):
                    circ = DashedVMobject(
                        Circle(radius=r, color=WHITE), dashed_ratio=ratio
                    )
                    middle_row.add(circ)

                func1 = FunctionGraph(lambda t: t**5,[-1,1],color=WHITE)
                func_even = DashedVMobject(func1,num_dashes=6,equal_lengths=True)
                func_stretched = DashedVMobject(func1, num_dashes=6, equal_lengths=False)
                bottom_row = VGroup(func_even,func_stretched)


                top_row.arrange(buff=0.3)
                middle_row.arrange()
                bottom_row.arrange(buff=1)
                everything = VGroup(top_row, middle_row, bottom_row).arrange(DOWN, buff=1)
                self.add(everything)

    """

    def __init__(
        self,
        vmobject: VMobject,
        num_dashes: int = 15,
        dashed_ratio: float = 0.5,
        dash_offset: float = 0,
        color: ManimColor = WHITE,
        equal_lengths: bool = True,
        **kwargs,
    ) -> None:
        self.dashed_ratio = dashed_ratio
        self.num_dashes = num_dashes
        super().__init__(color=color, **kwargs)
        r = self.dashed_ratio
        n = self.num_dashes
        if n > 0:
            # Assuming total length is 1
            dash_len = r / n
            if vmobject.is_closed():
                void_len = (1 - r) / n
            else:
                if n == 1:
                    void_len = 1 - r
                else:
                    void_len = (1 - r) / (n - 1)

            period = dash_len + void_len
            phase_shift = (dash_offset % 1) * period

            if vmobject.is_closed():
                # closed curves have equal amount of dashes and voids
                pattern_len = 1
            else:
                # open curves start and end with a dash, so the whole dash pattern with the last void is longer
                pattern_len = 1 + void_len

            dash_starts = [((i * period + phase_shift) % pattern_len) for i in range(n)]
            dash_ends = [
                ((i * period + dash_len + phase_shift) % pattern_len) for i in range(n)
            ]

            # closed shapes can handle overflow at the 0-point
            # open shapes need special treatment for it
            if not vmobject.is_closed():
                # due to phase shift being [0...1] range, always the last dash element needs attention for overflow
                # if an entire dash moves out of the shape end:
                if dash_ends[-1] > 1 and dash_starts[-1] > 1:
                    # remove the last element since it is out-of-bounds
                    dash_ends.pop()
                    dash_starts.pop()
                elif dash_ends[-1] < dash_len:  # if it overflowed
                    if (
                        dash_starts[-1] < 1
                    ):  # if the beginning of the piece is still in range
                        dash_starts.append(0)
                        dash_ends.append(dash_ends[-1])
                        dash_ends[-2] = 1
                    else:
                        dash_starts[-1] = 0
                elif dash_starts[-1] > (1 - dash_len):
                    dash_ends[-1] = 1

            if equal_lengths:
                # calculate the entire length by adding up short line-pieces
                norms = np.array(0)
                for k in range(vmobject.get_num_curves()):
                    norms = np.append(norms, vmobject.get_nth_curve_length_pieces(k))
                # add up length-pieces in array form
                length_vals = np.cumsum(norms)
                ref_points = np.linspace(0, 1, length_vals.size)
                curve_length = length_vals[-1]
                self.add(
                    *(
                        vmobject.get_subcurve(
                            np.interp(
                                dash_starts[i] * curve_length,
                                length_vals,
                                ref_points,
                            ),
                            np.interp(
                                dash_ends[i] * curve_length,
                                length_vals,
                                ref_points,
                            ),
                        )
                        for i in range(len(dash_starts))
                    )
                )
            else:
                self.add(
                    *(
                        vmobject.get_subcurve(
                            dash_starts[i],
                            dash_ends[i],
                        )
                        for i in range(len(dash_starts))
                    )
                )
        # Family is already taken care of by get_subcurve
        # implementation
        if config.renderer == RendererType.OPENGL:
            self.match_style(vmobject, recurse=False)
        else:
            self.match_style(vmobject, family=False)


# Extracted from /Users/hochmax/learn/manim/manim/mobject/opengl/opengl_mobject.py
from __future__ import annotations

import copy
import inspect
import itertools as it
import random
import sys
from collections.abc import Iterable, Sequence
from functools import partialmethod, wraps
from math import ceil

import moderngl
import numpy as np

from manim import config, logger
from manim.constants import *
from manim.renderer.shader_wrapper import get_colormap_code
from manim.utils.bezier import integer_interpolate, interpolate
from manim.utils.color import (
    WHITE,
    ManimColor,
    ParsableManimColor,
    color_gradient,
    color_to_rgb,
    rgb_to_hex,
)
from manim.utils.config_ops import _Data, _Uniforms

# from ..utils.iterables import batch_by_property
from manim.utils.iterables import (
    batch_by_property,
    list_update,
    listify,
    make_even,
    resize_array,
    resize_preserving_order,
    resize_with_interpolation,
    uniq_chain,
)
from manim.utils.paths import straight_path
from manim.utils.space_ops import (
    angle_between_vectors,
    normalize,
    rotation_matrix_transpose,
)


def affects_shader_info_id(func):
    @wraps(func)
    def wrapper(self):
        for mob in self.get_family():
            func(mob)
            mob.refresh_shader_wrapper_id()
        return self

    return wrapper


__all__ = ["OpenGLMobject", "OpenGLGroup", "OpenGLPoint", "_AnimationBuilder"]


class OpenGLMobject:
    """Mathematical Object: base class for objects that can be displayed on screen.

    Attributes
    ----------
    submobjects : List[:class:`OpenGLMobject`]
        The contained objects.
    points : :class:`numpy.ndarray`
        The points of the objects.

        .. seealso::

            :class:`~.OpenGLVMobject`

    """

    shader_dtype = [
        ("point", np.float32, (3,)),
    ]
    shader_folder = ""

    # _Data and _Uniforms are set as class variables to tell manim how to handle setting/getting these attributes later.
    points = _Data()
    bounding_box = _Data()
    rgbas = _Data()

    is_fixed_in_frame = _Uniforms()
    is_fixed_orientation = _Uniforms()
    fixed_orientation_center = _Uniforms()  # for fixed orientation reference
    gloss = _Uniforms()
    shadow = _Uniforms()

    def __init__(
        self,
        color=WHITE,
        opacity=1,
        dim=3,  # TODO, get rid of this
        # Lighting parameters
        # Positive gloss up to 1 makes it reflect the light.
        gloss=0.0,
        # Positive shadow up to 1 makes a side opposite the light darker
        shadow=0.0,
        # For shaders
        render_primitive=moderngl.TRIANGLES,
        texture_paths=None,
        depth_test=False,
        # If true, the mobject will not get rotated according to camera position
        is_fixed_in_frame=False,
        is_fixed_orientation=False,
        # Must match in attributes of vert shader
        # Event listener
        listen_to_events=False,
        model_matrix=None,
        should_render=True,
        name: str | None = None,
        **kwargs,
    ):
        self.name = self.__class__.__name__ if name is None else name
        # getattr in case data/uniforms are already defined in parent classes.
        self.data = getattr(self, "data", {})
        self.uniforms = getattr(self, "uniforms", {})

        self.opacity = opacity
        self.dim = dim  # TODO, get rid of this
        # Lighting parameters
        # Positive gloss up to 1 makes it reflect the light.
        self.gloss = gloss
        # Positive shadow up to 1 makes a side opposite the light darker
        self.shadow = shadow
        # For shaders
        self.render_primitive = render_primitive
        self.texture_paths = texture_paths
        self.depth_test = depth_test
        # If true, the mobject will not get rotated according to camera position
        self.is_fixed_in_frame = float(is_fixed_in_frame)
        self.is_fixed_orientation = float(is_fixed_orientation)
        self.fixed_orientation_center = (0, 0, 0)
        # Must match in attributes of vert shader
        # Event listener
        self.listen_to_events = listen_to_events

        self._submobjects = []
        self.parents = []
        self.parent = None
        self.family = [self]
        self.locked_data_keys = set()
        self.needs_new_bounding_box = True
        if model_matrix is None:
            self.model_matrix = np.eye(4)
        else:
            self.model_matrix = model_matrix

        self.init_data()
        self.init_updaters()
        # self.init_event_listners()
        self.init_points()
        self.color = ManimColor.parse(color)
        self.init_colors()

        self.shader_indices = None

        if self.depth_test:
            self.apply_depth_test()

        self.should_render = should_render

    def _assert_valid_submobjects(self, submobjects: Iterable[OpenGLMobject]) -> Self:
        """Check that all submobjects are actually instances of
        :class:`OpenGLMobject`, and that none of them is
        ``self`` (an :class:`OpenGLMobject` cannot contain itself).

        This is an auxiliary function called when adding OpenGLMobjects to the
        :attr:`submobjects` list.

        This function is intended to be overridden by subclasses such as
        :class:`OpenGLVMobject`, which should assert that only other
        OpenGLVMobjects may be added into it.

        Parameters
        ----------
        submobjects
            The list containing values to validate.

        Returns
        -------
        :class:`OpenGLMobject`
            The OpenGLMobject itself.

        Raises
        ------
        TypeError
            If any of the values in `submobjects` is not an
            :class:`OpenGLMobject`.
        ValueError
            If there was an attempt to add an :class:`OpenGLMobject` as its own
            submobject.
        """
        return self._assert_valid_submobjects_internal(submobjects, OpenGLMobject)

    def _assert_valid_submobjects_internal(
        self, submobjects: list[OpenGLMobject], mob_class: type[OpenGLMobject]
    ) -> Self:
        for i, submob in enumerate(submobjects):
            if not isinstance(submob, mob_class):
                error_message = (
                    f"Only values of type {mob_class.__name__} can be added "
                    f"as submobjects of {type(self).__name__}, but the value "
                    f"{submob} (at index {i}) is of type "
                    f"{type(submob).__name__}."
                )
                # Intended for subclasses such as OpenGLVMobject, which
                # cannot have regular OpenGLMobjects as submobjects
                if isinstance(submob, OpenGLMobject):
                    error_message += (
                        " You can try adding this value into a Group instead."
                    )
                raise TypeError(error_message)
            if submob is self:
                raise ValueError(
                    f"Cannot add {type(self).__name__} as a submobject of "
                    f"itself (at index {i})."
                )
        return self

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._original__init__ = cls.__init__

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self.name)

    def __sub__(self, other):
        return NotImplemented

    def __isub__(self, other):
        return NotImplemented

    def __add__(self, mobject):
        return NotImplemented

    def __iadd__(self, mobject):
        return NotImplemented

    @classmethod
    def set_default(cls, **kwargs):
        """Sets the default values of keyword arguments.

        If this method is called without any additional keyword
        arguments, the original default values of the initialization
        method of this class are restored.

        Parameters
        ----------

        kwargs
            Passing any keyword argument will update the default
            values of the keyword arguments of the initialization
            function of this class.

        Examples
        --------

        ::

            >>> from manim import Square, GREEN
            >>> Square.set_default(color=GREEN, fill_opacity=0.25)
            >>> s = Square(); s.color, s.fill_opacity
            (ManimColor('#83C167'), 0.25)
            >>> Square.set_default()
            >>> s = Square(); s.color, s.fill_opacity
            (ManimColor('#FFFFFF'), 0.0)

        .. manim:: ChangedDefaultTextcolor
            :save_last_frame:

            config.background_color = WHITE

            class ChangedDefaultTextcolor(Scene):
                def construct(self):
                    Text.set_default(color=BLACK)
                    self.add(Text("Changing default values is easy!"))

                    # we revert the colour back to the default to prevent a bug in the docs.
                    Text.set_default(color=WHITE)

        """
        if kwargs:
            cls.__init__ = partialmethod(cls.__init__, **kwargs)
        else:
            cls.__init__ = cls._original__init__

    def init_data(self):
        """Initializes the ``points``, ``bounding_box`` and ``rgbas`` attributes and groups them into self.data.
        Subclasses can inherit and overwrite this method to extend `self.data`."""
        self.points = np.zeros((0, 3))
        self.bounding_box = np.zeros((3, 3))
        self.rgbas = np.zeros((1, 4))

    def init_colors(self):
        """Initializes the colors.

        Gets called upon creation"""
        self.set_color(self.color, self.opacity)

    def init_points(self):
        """Initializes :attr:`points` and therefore the shape.

        Gets called upon creation. This is an empty method that can be implemented by
        subclasses."""
        # Typically implemented in subclass, unless purposefully left blank
        pass

    def set(self, **kwargs) -> OpenGLMobject:
        """Sets attributes.

        Mainly to be used along with :attr:`animate` to
        animate setting attributes.

        Examples
        --------
        ::

            >>> mob = OpenGLMobject()
            >>> mob.set(foo=0)
            OpenGLMobject
            >>> mob.foo
            0

        Parameters
        ----------
        **kwargs
            The attributes and corresponding values to set.

        Returns
        -------
        :class:`OpenGLMobject`
            ``self``


        """

        for attr, value in kwargs.items():
            setattr(self, attr, value)

        return self

    def set_data(self, data):
        for key in data:
            self.data[key] = data[key].copy()
        return self

    def set_uniforms(self, uniforms):
        for key in uniforms:
            self.uniforms[key] = uniforms[key]  # Copy?
        return self

    @property
    def animate(self):
        """Used to animate the application of a method.

        .. warning::

            Passing multiple animations for the same :class:`OpenGLMobject` in one
            call to :meth:`~.Scene.play` is discouraged and will most likely
            not work properly. Instead of writing an animation like

            ::

                self.play(my_mobject.animate.shift(RIGHT), my_mobject.animate.rotate(PI))

            make use of method chaining for ``animate``, meaning::

                self.play(my_mobject.animate.shift(RIGHT).rotate(PI))

        Keyword arguments that can be passed to :meth:`.Scene.play` can be passed
        directly after accessing ``.animate``, like so::

            self.play(my_mobject.animate(rate_func=linear).shift(RIGHT))

        This is especially useful when animating simultaneous ``.animate`` calls that
        you want to behave differently::

            self.play(
                mobject1.animate(run_time=2).rotate(PI),
                mobject2.animate(rate_func=there_and_back).shift(RIGHT),
            )

        .. seealso::

            :func:`override_animate`


        Examples
        --------

        .. manim:: AnimateExample

            class AnimateExample(Scene):
                def construct(self):
                    s = Square()
                    self.play(Create(s))
                    self.play(s.animate.shift(RIGHT))
                    self.play(s.animate.scale(2))
                    self.play(s.animate.rotate(PI / 2))
                    self.play(Uncreate(s))


        .. manim:: AnimateChainExample

            class AnimateChainExample(Scene):
                def construct(self):
                    s = Square()
                    self.play(Create(s))
                    self.play(s.animate.shift(RIGHT).scale(2).rotate(PI / 2))
                    self.play(Uncreate(s))

        .. manim:: AnimateWithArgsExample

            class AnimateWithArgsExample(Scene):
                def construct(self):
                    s = Square()
                    c = Circle()

                    VGroup(s, c).arrange(RIGHT, buff=2)
                    self.add(s, c)

                    self.play(
                        s.animate(run_time=2).rotate(PI / 2),
                        c.animate(rate_func=there_and_back).shift(RIGHT),
                    )

        .. warning::

            ``.animate``
             will interpolate the :class:`~.OpenGLMobject` between its points prior to
             ``.animate`` and its points after applying ``.animate`` to it. This may
             result in unexpected behavior when attempting to interpolate along paths,
             or rotations.
             If you want animations to consider the points between, consider using
             :class:`~.ValueTracker` with updaters instead.

        """
        return _AnimationBuilder(self)

    @property
    def width(self):
        """The width of the mobject.

        Returns
        -------
        :class:`float`

        Examples
        --------
        .. manim:: WidthExample

            class WidthExample(Scene):
                def construct(self):
                    decimal = DecimalNumber().to_edge(UP)
                    rect = Rectangle(color=BLUE)
                    rect_copy = rect.copy().set_stroke(GRAY, opacity=0.5)

                    decimal.add_updater(lambda d: d.set_value(rect.width))

                    self.add(rect_copy, rect, decimal)
                    self.play(rect.animate.set(width=7))
                    self.wait()

        See also
        --------
        :meth:`length_over_dim`

        """

        # Get the length across the X dimension
        return self.length_over_dim(0)

    # Only these methods should directly affect points
    @width.setter
    def width(self, value):
        self.rescale_to_fit(value, 0, stretch=False)

    @property
    def height(self):
        """The height of the mobject.

        Returns
        -------
        :class:`float`

        Examples
        --------
        .. manim:: HeightExample

            class HeightExample(Scene):
                def construct(self):
                    decimal = DecimalNumber().to_edge(UP)
                    rect = Rectangle(color=BLUE)
                    rect_copy = rect.copy().set_stroke(GRAY, opacity=0.5)

                    decimal.add_updater(lambda d: d.set_value(rect.height))

                    self.add(rect_copy, rect, decimal)
                    self.play(rect.animate.set(height=5))
                    self.wait()

        See also
        --------
        :meth:`length_over_dim`

        """

        # Get the length across the Y dimension
        return self.length_over_dim(1)

    @height.setter
    def height(self, value):
        self.rescale_to_fit(value, 1, stretch=False)

    @property
    def depth(self):
        """The depth of the mobject.

        Returns
        -------
        :class:`float`

        See also
        --------
        :meth:`length_over_dim`

        """

        # Get the length across the Z dimension
        return self.length_over_dim(2)

    @depth.setter
    def depth(self, value):
        self.rescale_to_fit(value, 2, stretch=False)

    def resize_points(self, new_length, resize_func=resize_array):
        if new_length != len(self.points):
            self.points = resize_func(self.points, new_length)
        self.refresh_bounding_box()
        return self

    def set_points(self, points):
        if len(points) == len(self.points):
            self.points[:] = points
        elif isinstance(points, np.ndarray):
            self.points = points.copy()
        else:
            self.points = np.array(points)
        self.refresh_bounding_box()
        return self

    def apply_over_attr_arrays(self, func):
        for attr in self.get_array_attrs():
            setattr(self, attr, func(getattr(self, attr)))
        return self

    def append_points(self, new_points):
        self.points = np.vstack([self.points, new_points])
        self.refresh_bounding_box()
        return self

    def reverse_points(self):
        for mob in self.get_family():
            for key in mob.data:
                mob.data[key] = mob.data[key][::-1]
        return self

    def get_midpoint(self) -> np.ndarray:
        """Get coordinates of the middle of the path that forms the  :class:`~.OpenGLMobject`.

        Examples
        --------

        .. manim:: AngleMidPoint
            :save_last_frame:

            class AngleMidPoint(Scene):
                def construct(self):
                    line1 = Line(ORIGIN, 2*RIGHT)
                    line2 = Line(ORIGIN, 2*RIGHT).rotate_about_origin(80*DEGREES)

                    a = Angle(line1, line2, radius=1.5, other_angle=False)
                    d = Dot(a.get_midpoint()).set_color(RED)

                    self.add(line1, line2, a, d)
                    self.wait()

        """
        return self.point_from_proportion(0.5)

    def apply_points_function(
        self,
        func,
        about_point=None,
        about_edge=ORIGIN,
        works_on_bounding_box=False,
    ):
        if about_point is None and about_edge is not None:
            about_point = self.get_bounding_box_point(about_edge)

        for mob in self.get_family():
            arrs = []
            if mob.has_points():
                arrs.append(mob.points)
            if works_on_bounding_box:
                arrs.append(mob.get_bounding_box())

            for arr in arrs:
                if about_point is None:
                    arr[:] = func(arr)
                else:
                    arr[:] = func(arr - about_point) + about_point

        if not works_on_bounding_box:
            self.refresh_bounding_box(recurse_down=True)
        else:
            for parent in self.parents:
                parent.refresh_bounding_box()
        return self

    # Others related to points

    def match_points(self, mobject):
        """Edit points, positions, and submobjects to be identical
        to another :class:`~.OpenGLMobject`, while keeping the style unchanged.

        Examples
        --------
        .. manim:: MatchPointsScene

            class MatchPointsScene(Scene):
                def construct(self):
                    circ = Circle(fill_color=RED, fill_opacity=0.8)
                    square = Square(fill_color=BLUE, fill_opacity=0.2)
                    self.add(circ)
                    self.wait(0.5)
                    self.play(circ.animate.match_points(square))
                    self.wait(0.5)
        """
        self.set_points(mobject.points)

    def clear_points(self):
        self.points = np.empty((0, 3))

    def get_num_points(self):
        return len(self.points)

    def get_all_points(self):
        if self.submobjects:
            return np.vstack([sm.points for sm in self.get_family()])
        else:
            return self.points

    def has_points(self):
        return self.get_num_points() > 0

    def get_bounding_box(self):
        if self.needs_new_bounding_box:
            self.bounding_box = self.compute_bounding_box()
            self.needs_new_bounding_box = False
        return self.bounding_box

    def compute_bounding_box(self):
        all_points = np.vstack(
            [
                self.points,
                *(
                    mob.get_bounding_box()
                    for mob in self.get_family()[1:]
                    if mob.has_points()
                ),
            ],
        )
        if len(all_points) == 0:
            return np.zeros((3, self.dim))
        else:
            # Lower left and upper right corners
            mins = all_points.min(0)
            maxs = all_points.max(0)
            mids = (mins + maxs) / 2
            return np.array([mins, mids, maxs])

    def refresh_bounding_box(self, recurse_down=False, recurse_up=True):
        for mob in self.get_family(recurse_down):
            mob.needs_new_bounding_box = True
        if recurse_up:
            for parent in self.parents:
                parent.refresh_bounding_box()
        return self

    def is_point_touching(self, point, buff=MED_SMALL_BUFF):
        bb = self.get_bounding_box()
        mins = bb[0] - buff
        maxs = bb[2] + buff
        return (point >= mins).all() and (point <= maxs).all()

    # Family matters

    def __getitem__(self, value):
        if isinstance(value, slice):
            GroupClass = self.get_group_class()
            return GroupClass(*self.split().__getitem__(value))
        return self.split().__getitem__(value)

    def __iter__(self):
        return iter(self.split())

    def __len__(self):
        return len(self.split())

    def split(self):
        return self.submobjects

    def assemble_family(self):
        sub_families = (sm.get_family() for sm in self.submobjects)
        self.family = [self, *uniq_chain(*sub_families)]
        self.refresh_has_updater_status()
        self.refresh_bounding_box()
        for parent in self.parents:
            parent.assemble_family()
        return self

    def get_family(self, recurse=True):
        if recurse and hasattr(self, "family"):
            return self.family
        else:
            return [self]

    def family_members_with_points(self):
        return [m for m in self.get_family() if m.has_points()]

    def add(
        self, *mobjects: OpenGLMobject, update_parent: bool = False
    ) -> OpenGLMobject:
        """Add mobjects as submobjects.

        The mobjects are added to :attr:`submobjects`.

        Subclasses of mobject may implement ``+`` and ``+=`` dunder methods.

        Parameters
        ----------
        mobjects
            The mobjects to add.

        Returns
        -------
        :class:`OpenGLMobject`
            ``self``

        Raises
        ------
        :class:`ValueError`
            When a mobject tries to add itself.
        :class:`TypeError`
            When trying to add an object that is not an instance of :class:`OpenGLMobject`.


        Notes
        -----
        A mobject cannot contain itself, and it cannot contain a submobject
        more than once.  If the parent mobject is displayed, the newly-added
        submobjects will also be displayed (i.e. they are automatically added
        to the parent Scene).

        See Also
        --------
        :meth:`remove`
        :meth:`add_to_back`

        Examples
        --------
        ::

            >>> outer = OpenGLMobject()
            >>> inner = OpenGLMobject()
            >>> outer = outer.add(inner)

        Duplicates are not added again::

            >>> outer = outer.add(inner)
            >>> len(outer.submobjects)
            1

        Only OpenGLMobjects can be added::

            >>> outer.add(3)
            Traceback (most recent call last):
            ...
            TypeError: Only values of type OpenGLMobject can be added as submobjects of OpenGLMobject, but the value 3 (at index 0) is of type int.

        Adding an object to itself raises an error::

            >>> outer.add(outer)
            Traceback (most recent call last):
            ...
            ValueError: Cannot add OpenGLMobject as a submobject of itself (at index 0).

        """
        if update_parent:
            assert len(mobjects) == 1, "Can't set multiple parents."
            mobjects[0].parent = self

        self._assert_valid_submobjects(mobjects)

        if any(mobjects.count(elem) > 1 for elem in mobjects):
            logger.warning(
                "Attempted adding some Mobject as a child more than once, "
                "this is not possible. Repetitions are ignored.",
            )
        for mobject in mobjects:
            if mobject not in self.submobjects:
                self.submobjects.append(mobject)
            if self not in mobject.parents:
                mobject.parents.append(self)
        self.assemble_family()
        return self

    def insert(self, index: int, mobject: OpenGLMobject, update_parent: bool = False):
        """Inserts a mobject at a specific position into self.submobjects

        Effectively just calls  ``self.submobjects.insert(index, mobject)``,
        where ``self.submobjects`` is a list.

        Highly adapted from ``OpenGLMobject.add``.

        Parameters
        ----------
        index
            The index at which
        mobject
            The mobject to be inserted.
        update_parent
            Whether or not to set ``mobject.parent`` to ``self``.
        """

        if update_parent:
            mobject.parent = self

        self._assert_valid_submobjects([mobject])

        if mobject not in self.submobjects:
            self.submobjects.insert(index, mobject)

        if self not in mobject.parents:
            mobject.parents.append(self)

        self.assemble_family()
        return self

    def remove(
        self, *mobjects: OpenGLMobject, update_parent: bool = False
    ) -> OpenGLMobject:
        """Remove :attr:`submobjects`.

        The mobjects are removed from :attr:`submobjects`, if they exist.

        Subclasses of mobject may implement ``-`` and ``-=`` dunder methods.

        Parameters
        ----------
        mobjects
            The mobjects to remove.

        Returns
        -------
        :class:`OpenGLMobject`
            ``self``

        See Also
        --------
        :meth:`add`

        """
        if update_parent:
            assert len(mobjects) == 1, "Can't remove multiple parents."
            mobjects[0].parent = None

        for mobject in mobjects:
            if mobject in self.submobjects:
                self.submobjects.remove(mobject)
            if self in mobject.parents:
                mobject.parents.remove(self)
        self.assemble_family()
        return self

    def add_to_back(self, *mobjects: OpenGLMobject) -> OpenGLMobject:
        # NOTE: is the note true OpenGLMobjects?
        """Add all passed mobjects to the back of the submobjects.

        If :attr:`submobjects` already contains the given mobjects, they just get moved
        to the back instead.

        Parameters
        ----------
        mobjects
            The mobjects to add.

        Returns
        -------
        :class:`OpenGLMobject`
            ``self``


        .. note::

            Technically, this is done by adding (or moving) the mobjects to
            the head of :attr:`submobjects`. The head of this list is rendered
            first, which places the corresponding mobjects behind the
            subsequent list members.

        Raises
        ------
        :class:`ValueError`
            When a mobject tries to add itself.
        :class:`TypeError`
            When trying to add an object that is not an instance of :class:`OpenGLMobject`.

        Notes
        -----
        A mobject cannot contain itself, and it cannot contain a submobject
        more than once.  If the parent mobject is displayed, the newly-added
        submobjects will also be displayed (i.e. they are automatically added
        to the parent Scene).

        See Also
        --------
        :meth:`remove`
        :meth:`add`

        """
        self._assert_valid_submobjects(mobjects)
        self.submobjects = list_update(mobjects, self.submobjects)
        return self

    def replace_submobject(self, index, new_submob):
        self._assert_valid_submobjects([new_submob])
        old_submob = self.submobjects[index]
        if self in old_submob.parents:
            old_submob.parents.remove(self)
        self.submobjects[index] = new_submob
        self.assemble_family()
        return self

    # Submobject organization

    def arrange(self, direction=RIGHT, center=True, **kwargs):
        """Sorts :class:`~.OpenGLMobject` next to each other on screen.

        Examples
        --------

        .. manim:: Example
            :save_last_frame:

            class Example(Scene):
                def construct(self):
                    s1 = Square()
                    s2 = Square()
                    s3 = Square()
                    s4 = Square()
                    x = OpenGLVGroup(s1, s2, s3, s4).set_x(0).arrange(buff=1.0)
                    self.add(x)
        """
        for m1, m2 in zip(self.submobjects, self.submobjects[1:]):
            m2.next_to(m1, direction, **kwargs)
        if center:
            self.center()
        return self

    def arrange_in_grid(
        self,
        rows: int | None = None,
        cols: int | None = None,
        buff: float | tuple[float, float] = MED_SMALL_BUFF,
        cell_alignment: np.ndarray = ORIGIN,
        row_alignments: str | None = None,  # "ucd"
        col_alignments: str | None = None,  # "lcr"
        row_heights: Iterable[float | None] | None = None,
        col_widths: Iterable[float | None] | None = None,
        flow_order: str = "rd",
        **kwargs,
    ) -> OpenGLMobject:
        """Arrange submobjects in a grid.

        Parameters
        ----------
        rows
            The number of rows in the grid.
        cols
            The number of columns in the grid.
        buff
            The gap between grid cells. To specify a different buffer in the horizontal and
            vertical directions, a tuple of two values can be given - ``(row, col)``.
        cell_alignment
            The way each submobject is aligned in its grid cell.
        row_alignments
            The vertical alignment for each row (top to bottom). Accepts the following characters: ``"u"`` -
            up, ``"c"`` - center, ``"d"`` - down.
        col_alignments
            The horizontal alignment for each column (left to right). Accepts the following characters ``"l"`` - left,
            ``"c"`` - center, ``"r"`` - right.
        row_heights
            Defines a list of heights for certain rows (top to bottom). If the list contains
            ``None``, the corresponding row will fit its height automatically based
            on the highest element in that row.
        col_widths
            Defines a list of widths for certain columns (left to right). If the list contains ``None``, the
            corresponding column will fit its width automatically based on the widest element in that column.
        flow_order
            The order in which submobjects fill the grid. Can be one of the following values:
            "rd", "dr", "ld", "dl", "ru", "ur", "lu", "ul". ("rd" -> fill rightwards then downwards)

        Returns
        -------
        OpenGLMobject
            The mobject.

        NOTES
        -----

        If only one of ``cols`` and ``rows`` is set implicitly, the other one will be chosen big
        enough to fit all submobjects. If neither is set, they will be chosen to be about the same,
        tending towards ``cols`` > ``rows`` (simply because videos are wider than they are high).

        If both ``cell_alignment`` and ``row_alignments`` / ``col_alignments`` are
        defined, the latter has higher priority.


        Raises
        ------
        ValueError
            If ``rows`` and ``cols`` are too small to fit all submobjects.
        ValueError
            If :code:`cols`, :code:`col_alignments` and :code:`col_widths` or :code:`rows`,
            :code:`row_alignments` and :code:`row_heights` have mismatching sizes.

        Examples
        --------
        .. manim:: ExampleBoxes
            :save_last_frame:

            class ExampleBoxes(Scene):
                def construct(self):
                    boxes=VGroup(*[Square() for s in range(0,6)])
                    boxes.arrange_in_grid(rows=2, buff=0.1)
                    self.add(boxes)


        .. manim:: ArrangeInGrid
            :save_last_frame:

            class ArrangeInGrid(Scene):
                def construct(self):
                    #Add some numbered boxes:
                    np.random.seed(3)
                    boxes = VGroup(*[
                        Rectangle(WHITE, np.random.random()+.5, np.random.random()+.5).add(Text(str(i+1)).scale(0.5))
                        for i in range(22)
                    ])
                    self.add(boxes)

                    boxes.arrange_in_grid(
                        buff=(0.25,0.5),
                        col_alignments="lccccr",
                        row_alignments="uccd",
                        col_widths=[2, *[None]*4, 2],
                        flow_order="dr"
                    )


        """
        from manim.mobject.geometry.line import Line

        mobs = self.submobjects.copy()
        start_pos = self.get_center()

        # get cols / rows values if given (implicitly)
        def init_size(num, alignments, sizes):
            if num is not None:
                return num
            if alignments is not None:
                return len(alignments)
            if sizes is not None:
                return len(sizes)

        cols = init_size(cols, col_alignments, col_widths)
        rows = init_size(rows, row_alignments, row_heights)

        # calculate rows cols
        if rows is None and cols is None:
            cols = ceil(np.sqrt(len(mobs)))
            # make the grid as close to quadratic as possible.
            # choosing cols first can results in cols>rows.
            # This is favored over rows>cols since in general
            # the sceene is wider than high.
        if rows is None:
            rows = ceil(len(mobs) / cols)
        if cols is None:
            cols = ceil(len(mobs) / rows)
        if rows * cols < len(mobs):
            raise ValueError("Too few rows and columns to fit all submobjetcs.")
        # rows and cols are now finally valid.

        if isinstance(buff, tuple):
            buff_x = buff[0]
            buff_y = buff[1]
        else:
            buff_x = buff_y = buff

        # Initialize alignments correctly
        def init_alignments(alignments, num, mapping, name, dir):
            if alignments is None:
                # Use cell_alignment as fallback
                return [cell_alignment * dir] * num
            if len(alignments) != num:
                raise ValueError(f"{name}_alignments has a mismatching size.")
            alignments = list(alignments)
            for i in range(num):
                alignments[i] = mapping[alignments[i]]
            return alignments

        row_alignments = init_alignments(
            row_alignments,
            rows,
            {"u": UP, "c": ORIGIN, "d": DOWN},
            "row",
            RIGHT,
        )
        col_alignments = init_alignments(
            col_alignments,
            cols,
            {"l": LEFT, "c": ORIGIN, "r": RIGHT},
            "col",
            UP,
        )
        # Now row_alignment[r] + col_alignment[c] is the alignment in cell [r][c]

        mapper = {
            "dr": lambda r, c: (rows - r - 1) + c * rows,
            "dl": lambda r, c: (rows - r - 1) + (cols - c - 1) * rows,
            "ur": lambda r, c: r + c * rows,
            "ul": lambda r, c: r + (cols - c - 1) * rows,
            "rd": lambda r, c: (rows - r - 1) * cols + c,
            "ld": lambda r, c: (rows - r - 1) * cols + (cols - c - 1),
            "ru": lambda r, c: r * cols + c,
            "lu": lambda r, c: r * cols + (cols - c - 1),
        }
        if flow_order not in mapper:
            raise ValueError(
                'flow_order must be one of the following values: "dr", "rd", "ld" "dl", "ru", "ur", "lu", "ul".',
            )
        flow_order = mapper[flow_order]

        # Reverse row_alignments and row_heights. Necessary since the
        # grid filling is handled bottom up for simplicity reasons.
        def reverse(maybe_list):
            if maybe_list is not None:
                maybe_list = list(maybe_list)
                maybe_list.reverse()
                return maybe_list

        row_alignments = reverse(row_alignments)
        row_heights = reverse(row_heights)

        placeholder = OpenGLMobject()
        # Used to fill up the grid temporarily, doesn't get added to the scene.
        # In this case a Mobject is better than None since it has width and height
        # properties of 0.

        mobs.extend([placeholder] * (rows * cols - len(mobs)))
        grid = [[mobs[flow_order(r, c)] for c in range(cols)] for r in range(rows)]

        measured_heigths = [
            max(grid[r][c].height for c in range(cols)) for r in range(rows)
        ]
        measured_widths = [
            max(grid[r][c].width for r in range(rows)) for c in range(cols)
        ]

        # Initialize row_heights / col_widths correctly using measurements as fallback
        def init_sizes(sizes, num, measures, name):
            if sizes is None:
                sizes = [None] * num
            if len(sizes) != num:
                raise ValueError(f"{name} has a mismatching size.")
            return [
                sizes[i] if sizes[i] is not None else measures[i] for i in range(num)
            ]

        heights = init_sizes(row_heights, rows, measured_heigths, "row_heights")
        widths = init_sizes(col_widths, cols, measured_widths, "col_widths")

        x, y = 0, 0
        for r in range(rows):
            x = 0
            for c in range(cols):
                if grid[r][c] is not placeholder:
                    alignment = row_alignments[r] + col_alignments[c]
                    line = Line(
                        x * RIGHT + y * UP,
                        (x + widths[c]) * RIGHT + (y + heights[r]) * UP,
                    )
                    # Use a mobject to avoid rewriting align inside
                    # box code that Mobject.move_to(Mobject) already
                    # includes.

                    grid[r][c].move_to(line, alignment)
                x += widths[c] + buff_x
            y += heights[r] + buff_y

        self.move_to(start_pos)
        return self

    def get_grid(self, n_rows, n_cols, height=None, **kwargs):
        """
        Returns a new mobject containing multiple copies of this one
        arranged in a grid
        """
        grid = self.duplicate(n_rows * n_cols)
        grid.arrange_in_grid(n_rows, n_cols, **kwargs)
        if height is not None:
            grid.set_height(height)
        return grid

    def duplicate(self, n: int):
        """Returns an :class:`~.OpenGLVGroup` containing ``n`` copies of the mobject."""
        return self.get_group_class()(*[self.copy() for _ in range(n)])

    def sort(self, point_to_num_func=lambda p: p[0], submob_func=None):
        """Sorts the list of :attr:`submobjects` by a function defined by ``submob_func``."""
        if submob_func is not None:
            self.submobjects.sort(key=submob_func)
        else:
            self.submobjects.sort(key=lambda m: point_to_num_func(m.get_center()))
        return self

    def shuffle(self, recurse=False):
        """Shuffles the order of :attr:`submobjects`

        Examples
        --------

        .. manim:: ShuffleSubmobjectsExample

            class ShuffleSubmobjectsExample(Scene):
                def construct(self):
                    s= OpenGLVGroup(*[Dot().shift(i*0.1*RIGHT) for i in range(-20,20)])
                    s2= s.copy()
                    s2.shuffle()
                    s2.shift(DOWN)
                    self.play(Write(s), Write(s2))
        """
        if recurse:
            for submob in self.submobjects:
                submob.shuffle(recurse=True)
        random.shuffle(self.submobjects)
        self.assemble_family()
        return self

    def invert(self, recursive=False):
        """Inverts the list of :attr:`submobjects`.

        Parameters
        ----------
        recursive
            If ``True``, all submobject lists of this mobject's family are inverted.

        Examples
        --------

        .. manim:: InvertSumobjectsExample

            class InvertSumobjectsExample(Scene):
                def construct(self):
                    s = VGroup(*[Dot().shift(i*0.1*RIGHT) for i in range(-20,20)])
                    s2 = s.copy()
                    s2.invert()
                    s2.shift(DOWN)
                    self.play(Write(s), Write(s2))
        """
        if recursive:
            for submob in self.submobjects:
                submob.invert(recursive=True)
        self.submobjects.reverse()
        # Is there supposed to be an assemble_family here?

    # Copying

    def copy(self, shallow: bool = False):
        """Create and return an identical copy of the :class:`OpenGLMobject` including all
        :attr:`submobjects`.

        Returns
        -------
        :class:`OpenGLMobject`
            The copy.

        Parameters
        ----------
        shallow
            Controls whether a shallow copy is returned.

        Note
        ----
        The clone is initially not visible in the Scene, even if the original was.
        """
        if not shallow:
            return self.deepcopy()

        # TODO, either justify reason for shallow copy, or
        # remove this redundancy everywhere
        # return self.deepcopy()

        parents = self.parents
        self.parents = []
        copy_mobject = copy.copy(self)
        self.parents = parents

        copy_mobject.data = dict(self.data)
        for key in self.data:
            copy_mobject.data[key] = self.data[key].copy()

        # TODO, are uniforms ever numpy arrays?
        copy_mobject.uniforms = dict(self.uniforms)

        copy_mobject.submobjects = []
        copy_mobject.add(*(sm.copy() for sm in self.submobjects))
        copy_mobject.match_updaters(self)

        copy_mobject.needs_new_bounding_box = self.needs_new_bounding_box

        # Make sure any mobject or numpy array attributes are copied
        family = self.get_family()
        for attr, value in list(self.__dict__.items()):
            if (
                isinstance(value, OpenGLMobject)
                and value in family
                and value is not self
            ):
                setattr(copy_mobject, attr, value.copy())
            if isinstance(value, np.ndarray):
                setattr(copy_mobject, attr, value.copy())
            # if isinstance(value, ShaderWrapper):
            #     setattr(copy_mobject, attr, value.copy())
        return copy_mobject

    def deepcopy(self):
        parents = self.parents
        self.parents = []
        result = copy.deepcopy(self)
        self.parents = parents
        return result

    def generate_target(self, use_deepcopy: bool = False):
        self.target = None  # Prevent exponential explosion
        if use_deepcopy:
            self.target = self.deepcopy()
        else:
            self.target = self.copy()
        return self.target

    def save_state(self, use_deepcopy: bool = False):
        """Save the current state (position, color & size). Can be restored with :meth:`~.OpenGLMobject.restore`."""
        if hasattr(self, "saved_state"):
            # Prevent exponential growth of data
            self.saved_state = None
        if use_deepcopy:
            self.saved_state = self.deepcopy()
        else:
            self.saved_state = self.copy()
        return self

    def restore(self):
        """Restores the state that was previously saved with :meth:`~.OpenGLMobject.save_state`."""
        if not hasattr(self, "saved_state") or self.save_state is None:
            raise Exception("Trying to restore without having saved")
        self.become(self.saved_state)
        return self

    # Updating

    def init_updaters(self):
        self.time_based_updaters = []
        self.non_time_updaters = []
        self.has_updaters = False
        self.updating_suspended = False

    def update(self, dt=0, recurse=True):
        if not self.has_updaters or self.updating_suspended:
            return self
        for updater in self.time_based_updaters:
            updater(self, dt)
        for updater in self.non_time_updaters:
            updater(self)
        if recurse:
            for submob in self.submobjects:
                submob.update(dt, recurse)
        return self

    def get_time_based_updaters(self):
        return self.time_based_updaters

    def has_time_based_updater(self):
        return len(self.time_based_updaters) > 0

    def get_updaters(self):
        return self.time_based_updaters + self.non_time_updaters

    def get_family_updaters(self):
        return list(it.chain(*(sm.get_updaters() for sm in self.get_family())))

    def add_updater(self, update_function, index=None, call_updater=False):
        if "dt" in inspect.signature(update_function).parameters:
            updater_list = self.time_based_updaters
        else:
            updater_list = self.non_time_updaters

        if index is None:
            updater_list.append(update_function)
        else:
            updater_list.insert(index, update_function)

        self.refresh_has_updater_status()
        if call_updater:
            self.update()
        return self

    def remove_updater(self, update_function):
        for updater_list in [self.time_based_updaters, self.non_time_updaters]:
            while update_function in updater_list:
                updater_list.remove(update_function)
        self.refresh_has_updater_status()
        return self

    def clear_updaters(self, recurse=True):
        self.time_based_updaters = []
        self.non_time_updaters = []
        self.refresh_has_updater_status()
        if recurse:
            for submob in self.submobjects:
                submob.clear_updaters()
        return self

    def match_updaters(self, mobject):
        self.clear_updaters()
        for updater in mobject.get_updaters():
            self.add_updater(updater)
        return self

    def suspend_updating(self, recurse=True):
        self.updating_suspended = True
        if recurse:
            for submob in self.submobjects:
                submob.suspend_updating(recurse)
        return self

    def resume_updating(self, recurse=True, call_updater=True):
        self.updating_suspended = False
        if recurse:
            for submob in self.submobjects:
                submob.resume_updating(recurse)
        for parent in self.parents:
            parent.resume_updating(recurse=False, call_updater=False)
        if call_updater:
            self.update(dt=0, recurse=recurse)
        return self

    def refresh_has_updater_status(self):
        self.has_updaters = any(mob.get_updaters() for mob in self.get_family())
        return self

    # Transforming operations

    def shift(self, vector):
        self.apply_points_function(
            lambda points: points + vector,
            about_edge=None,
            works_on_bounding_box=True,
        )
        return self

    def scale(
        self,
        scale_factor: float,
        about_point: Sequence[float] | None = None,
        about_edge: Sequence[float] = ORIGIN,
        **kwargs,
    ) -> OpenGLMobject:
        r"""Scale the size by a factor.

        Default behavior is to scale about the center of the mobject.
        The argument about_edge can be a vector, indicating which side of
        the mobject to scale about, e.g., mob.scale(about_edge = RIGHT)
        scales about mob.get_right().

        Otherwise, if about_point is given a value, scaling is done with
        respect to that point.

        Parameters
        ----------
        scale_factor
            The scaling factor :math:`\alpha`. If :math:`0 < |\alpha| < 1`, the mobject
            will shrink, and for :math:`|\alpha| > 1` it will grow. Furthermore,
            if :math:`\alpha < 0`, the mobject is also flipped.
        kwargs
            Additional keyword arguments passed to
            :meth:`apply_points_function_about_point`.

        Returns
        -------
        OpenGLMobject
            The scaled mobject.

        Examples
        --------

        .. manim:: MobjectScaleExample
            :save_last_frame:

            class MobjectScaleExample(Scene):
                def construct(self):
                    f1 = Text("F")
                    f2 = Text("F").scale(2)
                    f3 = Text("F").scale(0.5)
                    f4 = Text("F").scale(-1)

                    vgroup = VGroup(f1, f2, f3, f4).arrange(6 * RIGHT)
                    self.add(vgroup)

        See also
        --------
        :meth:`move_to`

        """
        self.apply_points_function(
            lambda points: scale_factor * points,
            about_point=about_point,
            about_edge=about_edge,
            works_on_bounding_box=True,
            **kwargs,
        )
        return self

    def stretch(self, factor, dim, **kwargs):
        def func(points):
            points[:, dim] *= factor
            return points

        self.apply_points_function(func, works_on_bounding_box=True, **kwargs)
        return self

    def rotate_about_origin(self, angle, axis=OUT):
        return self.rotate(angle, axis, about_point=ORIGIN)

    def rotate(
        self,
        angle,
        axis=OUT,
        about_point: Sequence[float] | None = None,
        **kwargs,
    ):
        """Rotates the :class:`~.OpenGLMobject` about a certain point."""
        rot_matrix_T = rotation_matrix_transpose(angle, axis)
        self.apply_points_function(
            lambda points: np.dot(points, rot_matrix_T),
            about_point=about_point,
            **kwargs,
        )
        return self

    def flip(self, axis=UP, **kwargs):
        """Flips/Mirrors an mobject about its center.

        Examples
        --------

        .. manim:: FlipExample
            :save_last_frame:

            class FlipExample(Scene):
                def construct(self):
                    s= Line(LEFT, RIGHT+UP).shift(4*LEFT)
                    self.add(s)
                    s2= s.copy().flip()
                    self.add(s2)

        """
        return self.rotate(TAU / 2, axis, **kwargs)

    def apply_function(self, function, **kwargs):
        # Default to applying matrix about the origin, not mobjects center
        if len(kwargs) == 0:
            kwargs["about_point"] = ORIGIN
        self.apply_points_function(
            lambda points: np.array([function(p) for p in points]), **kwargs
        )
        return self

    def apply_function_to_position(self, function):
        self.move_to(function(self.get_center()))
        return self

    def apply_function_to_submobject_positions(self, function):
        for submob in self.submobjects:
            submob.apply_function_to_position(function)
        return self

    def apply_matrix(self, matrix, **kwargs):
        # Default to applying matrix about the origin, not mobjects center
        if ("about_point" not in kwargs) and ("about_edge" not in kwargs):
            kwargs["about_point"] = ORIGIN
        full_matrix = np.identity(self.dim)
        matrix = np.array(matrix)
        full_matrix[: matrix.shape[0], : matrix.shape[1]] = matrix
        self.apply_points_function(
            lambda points: np.dot(points, full_matrix.T), **kwargs
        )
        return self

    def apply_complex_function(self, function, **kwargs):
        """Applies a complex function to a :class:`OpenGLMobject`.
        The x and y coordinates correspond to the real and imaginary parts respectively.

        Example
        -------

        .. manim:: ApplyFuncExample

            class ApplyFuncExample(Scene):
                def construct(self):
                    circ = Circle().scale(1.5)
                    circ_ref = circ.copy()
                    circ.apply_complex_function(
                        lambda x: np.exp(x*1j)
                    )
                    t = ValueTracker(0)
                    circ.add_updater(
                        lambda x: x.become(circ_ref.copy().apply_complex_function(
                            lambda x: np.exp(x+t.get_value()*1j)
                        )).set_color(BLUE)
                    )
                    self.add(circ_ref)
                    self.play(TransformFromCopy(circ_ref, circ))
                    self.play(t.animate.set_value(TAU), run_time=3)
        """

        def R3_func(point):
            x, y, z = point
            xy_complex = function(complex(x, y))
            return [xy_complex.real, xy_complex.imag, z]

        return self.apply_function(R3_func)

    def hierarchical_model_matrix(self):
        if self.parent is None:
            return self.model_matrix

        model_matrices = [self.model_matrix]
        current_object = self
        while current_object.parent is not None:
            model_matrices.append(current_object.parent.model_matrix)
            current_object = current_object.parent
        return np.linalg.multi_dot(list(reversed(model_matrices)))

    def wag(self, direction=RIGHT, axis=DOWN, wag_factor=1.0):
        for mob in self.family_members_with_points():
            alphas = np.dot(mob.points, np.transpose(axis))
            alphas -= min(alphas)
            alphas /= max(alphas)
            alphas = alphas**wag_factor
            mob.set_points(
                mob.points
                + np.dot(
                    alphas.reshape((len(alphas), 1)),
                    np.array(direction).reshape((1, mob.dim)),
                ),
            )
        return self

    # Positioning methods

    def center(self):
        """Moves the mobject to the center of the Scene."""
        self.shift(-self.get_center())
        return self

    def align_on_border(self, direction, buff=DEFAULT_MOBJECT_TO_EDGE_BUFFER):
        """
        Direction just needs to be a vector pointing towards side or
        corner in the 2d plane.
        """
        target_point = np.sign(direction) * (
            config["frame_x_radius"],
            config["frame_y_radius"],
            0,
        )
        point_to_align = self.get_bounding_box_point(direction)
        shift_val = target_point - point_to_align - buff * np.array(direction)
        shift_val = shift_val * abs(np.sign(direction))
        self.shift(shift_val)
        return self

    def to_corner(self, corner=LEFT + DOWN, buff=DEFAULT_MOBJECT_TO_EDGE_BUFFER):
        return self.align_on_border(corner, buff)

    def to_edge(self, edge=LEFT, buff=DEFAULT_MOBJECT_TO_EDGE_BUFFER):
        return self.align_on_border(edge, buff)

    def next_to(
        self,
        mobject_or_point,
        direction=RIGHT,
        buff=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
        aligned_edge=ORIGIN,
        submobject_to_align=None,
        index_of_submobject_to_align=None,
        coor_mask=np.array([1, 1, 1]),
    ):
        """Move this :class:`~.OpenGLMobject` next to another's :class:`~.OpenGLMobject` or coordinate.

        Examples
        --------

        .. manim:: GeometricShapes
            :save_last_frame:

            class GeometricShapes(Scene):
                def construct(self):
                    d = Dot()
                    c = Circle()
                    s = Square()
                    t = Triangle()
                    d.next_to(c, RIGHT)
                    s.next_to(c, LEFT)
                    t.next_to(c, DOWN)
                    self.add(d, c, s, t)

        """
        if isinstance(mobject_or_point, OpenGLMobject):
            mob = mobject_or_point
            if index_of_submobject_to_align is not None:
                target_aligner = mob[index_of_submobject_to_align]
            else:
                target_aligner = mob
            target_point = target_aligner.get_bounding_box_point(
                aligned_edge + direction,
            )
        else:
            target_point = mobject_or_point
        if submobject_to_align is not None:
            aligner = submobject_to_align
        elif index_of_submobject_to_align is not None:
            aligner = self[index_of_submobject_to_align]
        else:
            aligner = self
        point_to_align = aligner.get_bounding_box_point(aligned_edge - direction)
        self.shift((target_point - point_to_align + buff * direction) * coor_mask)
        return self

    def shift_onto_screen(self, **kwargs):
        space_lengths = [config["frame_x_radius"], config["frame_y_radius"]]
        for vect in UP, DOWN, LEFT, RIGHT:
            dim = np.argmax(np.abs(vect))
            buff = kwargs.get("buff", DEFAULT_MOBJECT_TO_EDGE_BUFFER)
            max_val = space_lengths[dim] - buff
            edge_center = self.get_edge_center(vect)
            if np.dot(edge_center, vect) > max_val:
                self.to_edge(vect, **kwargs)
        return self

    def is_off_screen(self):
        if self.get_left()[0] > config.frame_x_radius:
            return True
        if self.get_right()[0] < config.frame_x_radius:
            return True
        if self.get_bottom()[1] > config.frame_y_radius:
            return True
        if self.get_top()[1] < -config.frame_y_radius:
            return True
        return False

    def stretch_about_point(self, factor, dim, point):
        return self.stretch(factor, dim, about_point=point)

    def rescale_to_fit(self, length, dim, stretch=False, **kwargs):
        old_length = self.length_over_dim(dim)
        if old_length == 0:
            return self
        if stretch:
            self.stretch(length / old_length, dim, **kwargs)
        else:
            self.scale(length / old_length, **kwargs)
        return self

    def stretch_to_fit_width(self, width, **kwargs):
        """Stretches the :class:`~.OpenGLMobject` to fit a width, not keeping height/depth proportional.

        Returns
        -------
        :class:`OpenGLMobject`
            ``self``

        Examples
        --------
        ::

            >>> from manim import *
            >>> sq = Square()
            >>> sq.height
            2.0
            >>> sq.stretch_to_fit_width(5)
            Square
            >>> sq.width
            5.0
            >>> sq.height
            2.0
        """
        return self.rescale_to_fit(width, 0, stretch=True, **kwargs)

    def stretch_to_fit_height(self, height, **kwargs):
        """Stretches the :class:`~.OpenGLMobject` to fit a height, not keeping width/height proportional."""
        return self.rescale_to_fit(height, 1, stretch=True, **kwargs)

    def stretch_to_fit_depth(self, depth, **kwargs):
        """Stretches the :class:`~.OpenGLMobject` to fit a depth, not keeping width/height proportional."""
        return self.rescale_to_fit(depth, 1, stretch=True, **kwargs)

    def set_width(self, width, stretch=False, **kwargs):
        """Scales the :class:`~.OpenGLMobject` to fit a width while keeping height/depth proportional.

        Returns
        -------
        :class:`OpenGLMobject`
            ``self``

        Examples
        --------
        ::

            >>> from manim import *
            >>> sq = Square()
            >>> sq.height
            2.0
            >>> sq.scale_to_fit_width(5)
            Square
            >>> sq.width
            5.0
            >>> sq.height
            5.0
        """
        return self.rescale_to_fit(width, 0, stretch=stretch, **kwargs)

    scale_to_fit_width = set_width

    def set_height(self, height, stretch=False, **kwargs):
        """Scales the :class:`~.OpenGLMobject` to fit a height while keeping width/depth proportional."""
        return self.rescale_to_fit(height, 1, stretch=stretch, **kwargs)

    scale_to_fit_height = set_height

    def set_depth(self, depth, stretch=False, **kwargs):
        """Scales the :class:`~.OpenGLMobject` to fit a depth while keeping width/height proportional."""
        return self.rescale_to_fit(depth, 2, stretch=stretch, **kwargs)

    scale_to_fit_depth = set_depth

    def set_coord(self, value, dim, direction=ORIGIN):
        curr = self.get_coord(dim, direction)
        shift_vect = np.zeros(self.dim)
        shift_vect[dim] = value - curr
        self.shift(shift_vect)
        return self

    def set_x(self, x, direction=ORIGIN):
        """Set x value of the center of the :class:`~.OpenGLMobject` (``int`` or ``float``)"""
        return self.set_coord(x, 0, direction)

    def set_y(self, y, direction=ORIGIN):
        """Set y value of the center of the :class:`~.OpenGLMobject` (``int`` or ``float``)"""
        return self.set_coord(y, 1, direction)

    def set_z(self, z, direction=ORIGIN):
        """Set z value of the center of the :class:`~.OpenGLMobject` (``int`` or ``float``)"""
        return self.set_coord(z, 2, direction)

    def space_out_submobjects(self, factor=1.5, **kwargs):
        self.scale(factor, **kwargs)
        for submob in self.submobjects:
            submob.scale(1.0 / factor)
        return self

    def move_to(
        self,
        point_or_mobject,
        aligned_edge=ORIGIN,
        coor_mask=np.array([1, 1, 1]),
    ):
        """Move center of the :class:`~.OpenGLMobject` to certain coordinate."""
        if isinstance(point_or_mobject, OpenGLMobject):
            target = point_or_mobject.get_bounding_box_point(aligned_edge)
        else:
            target = point_or_mobject
        point_to_align = self.get_bounding_box_point(aligned_edge)
        self.shift((target - point_to_align) * coor_mask)
        return self

    def replace(self, mobject, dim_to_match=0, stretch=False):
        if not mobject.get_num_points() and not mobject.submobjects:
            self.scale(0)
            return self
        if stretch:
            for i in range(self.dim):
                self.rescale_to_fit(mobject.length_over_dim(i), i, stretch=True)
        else:
            self.rescale_to_fit(
                mobject.length_over_dim(dim_to_match),
                dim_to_match,
                stretch=False,
            )
        self.shift(mobject.get_center() - self.get_center())
        return self

    def surround(
        self,
        mobject: OpenGLMobject,
        dim_to_match: int = 0,
        stretch: bool = False,
        buff: float = MED_SMALL_BUFF,
    ):
        self.replace(mobject, dim_to_match, stretch)
        length = mobject.length_over_dim(dim_to_match)
        self.scale((length + buff) / length)
        return self

    def put_start_and_end_on(self, start, end):
        curr_start, curr_end = self.get_start_and_end()
        curr_vect = curr_end - curr_start
        if np.all(curr_vect == 0):
            raise Exception("Cannot position endpoints of closed loop")
        target_vect = np.array(end) - np.array(start)
        axis = (
            normalize(np.cross(curr_vect, target_vect))
            if np.linalg.norm(np.cross(curr_vect, target_vect)) != 0
            else OUT
        )
        self.scale(
            np.linalg.norm(target_vect) / np.linalg.norm(curr_vect),
            about_point=curr_start,
        )
        self.rotate(
            angle_between_vectors(curr_vect, target_vect),
            about_point=curr_start,
            axis=axis,
        )
        self.shift(start - curr_start)
        return self

    # Color functions

    def set_rgba_array(self, color=None, opacity=None, name="rgbas", recurse=True):
        if color is not None:
            rgbs = np.array([color_to_rgb(c) for c in listify(color)])
        if opacity is not None:
            opacities = listify(opacity)

        # Color only
        if color is not None and opacity is None:
            for mob in self.get_family(recurse):
                mob.data[name] = resize_array(
                    mob.data[name] if name in mob.data else np.empty((1, 3)), len(rgbs)
                )
                mob.data[name][:, :3] = rgbs

        # Opacity only
        if color is None and opacity is not None:
            for mob in self.get_family(recurse):
                mob.data[name] = resize_array(
                    mob.data[name] if name in mob.data else np.empty((1, 3)),
                    len(opacities),
                )
                mob.data[name][:, 3] = opacities

        # Color and opacity
        if color is not None and opacity is not None:
            rgbas = np.array([[*rgb, o] for rgb, o in zip(*make_even(rgbs, opacities))])
            for mob in self.get_family(recurse):
                mob.data[name] = rgbas.copy()
        return self

    def set_rgba_array_direct(self, rgbas: np.ndarray, name="rgbas", recurse=True):
        """Directly set rgba data from `rgbas` and optionally do the same recursively
        with submobjects. This can be used if the `rgbas` have already been generated
        with the correct shape and simply need to be set.

        Parameters
        ----------
        rgbas
            the rgba to be set as data
        name
            the name of the data attribute to be set
        recurse
            set to true to recursively apply this method to submobjects
        """
        for mob in self.get_family(recurse):
            mob.data[name] = rgbas.copy()

    def set_color(self, color: ParsableManimColor | None, opacity=None, recurse=True):
        self.set_rgba_array(color, opacity, recurse=False)
        # Recurse to submobjects differently from how set_rgba_array
        # in case they implement set_color differently
        if color is not None:
            self.color: ManimColor = ManimColor.parse(color)
        if opacity is not None:
            self.opacity = opacity
        if recurse:
            for submob in self.submobjects:
                submob.set_color(color, recurse=True)
        return self

    def set_opacity(self, opacity, recurse=True):
        self.set_rgba_array(color=None, opacity=opacity, recurse=False)
        if recurse:
            for submob in self.submobjects:
                submob.set_opacity(opacity, recurse=True)
        return self

    def get_color(self):
        return rgb_to_hex(self.rgbas[0, :3])

    def get_opacity(self):
        return self.rgbas[0, 3]

    def set_color_by_gradient(self, *colors):
        self.set_submobject_colors_by_gradient(*colors)
        return self

    def set_submobject_colors_by_gradient(self, *colors):
        if len(colors) == 0:
            raise Exception("Need at least one color")
        elif len(colors) == 1:
            return self.set_color(*colors)

        # mobs = self.family_members_with_points()
        mobs = self.submobjects
        new_colors = color_gradient(colors, len(mobs))

        for mob, color in zip(mobs, new_colors):
            mob.set_color(color)
        return self

    def fade(self, darkness=0.5, recurse=True):
        self.set_opacity(1.0 - darkness, recurse=recurse)

    def get_gloss(self):
        return self.gloss

    def set_gloss(self, gloss, recurse=True):
        for mob in self.get_family(recurse):
            mob.gloss = gloss
        return self

    def get_shadow(self):
        return self.shadow

    def set_shadow(self, shadow, recurse=True):
        for mob in self.get_family(recurse):
            mob.shadow = shadow
        return self

    # Background rectangle

    def add_background_rectangle(
        self, color: ParsableManimColor | None = None, opacity: float = 0.75, **kwargs
    ):
        # TODO, this does not behave well when the mobject has points,
        # since it gets displayed on top
        """Add a BackgroundRectangle as submobject.

        The BackgroundRectangle is added behind other submobjects.

        This can be used to increase the mobjects visibility in front of a noisy background.

        Parameters
        ----------
        color
            The color of the BackgroundRectangle
        opacity
            The opacity of the BackgroundRectangle
        kwargs
            Additional keyword arguments passed to the BackgroundRectangle constructor


        Returns
        -------
        :class:`OpenGLMobject`
            ``self``

        See Also
        --------
        :meth:`add_to_back`
        :class:`~.BackgroundRectangle`

        """
        from manim.mobject.geometry.shape_matchers import BackgroundRectangle

        self.background_rectangle = BackgroundRectangle(
            self, color=color, fill_opacity=opacity, **kwargs
        )
        self.add_to_back(self.background_rectangle)
        return self

    def add_background_rectangle_to_submobjects(self, **kwargs):
        for submobject in self.submobjects:
            submobject.add_background_rectangle(**kwargs)
        return self

    def add_background_rectangle_to_family_members_with_points(self, **kwargs):
        for mob in self.family_members_with_points():
            mob.add_background_rectangle(**kwargs)
        return self

    # Getters

    def get_bounding_box_point(self, direction):
        bb = self.get_bounding_box()
        indices = (np.sign(direction) + 1).astype(int)
        return np.array([bb[indices[i]][i] for i in range(3)])

    def get_edge_center(self, direction) -> np.ndarray:
        """Get edge coordinates for certain direction."""
        return self.get_bounding_box_point(direction)

    def get_corner(self, direction) -> np.ndarray:
        """Get corner coordinates for certain direction."""
        return self.get_bounding_box_point(direction)

    def get_center(self) -> np.ndarray:
        """Get center coordinates."""
        return self.get_bounding_box()[1]

    def get_center_of_mass(self):
        return self.get_all_points().mean(0)

    def get_boundary_point(self, direction):
        all_points = self.get_all_points()
        boundary_directions = all_points - self.get_center()
        norms = np.linalg.norm(boundary_directions, axis=1)
        boundary_directions /= np.repeat(norms, 3).reshape((len(norms), 3))
        index = np.argmax(np.dot(boundary_directions, np.array(direction).T))
        return all_points[index]

    def get_continuous_bounding_box_point(self, direction):
        dl, center, ur = self.get_bounding_box()
        corner_vect = ur - center
        return center + direction / np.max(
            np.abs(
                np.true_divide(
                    direction,
                    corner_vect,
                    out=np.zeros(len(direction)),
                    where=((corner_vect) != 0),
                ),
            ),
        )

    def get_top(self) -> np.ndarray:
        """Get top coordinates of a box bounding the :class:`~.OpenGLMobject`"""
        return self.get_edge_center(UP)

    def get_bottom(self) -> np.ndarray:
        """Get bottom coordinates of a box bounding the :class:`~.OpenGLMobject`"""
        return self.get_edge_center(DOWN)

    def get_right(self) -> np.ndarray:
        """Get right coordinates of a box bounding the :class:`~.OpenGLMobject`"""
        return self.get_edge_center(RIGHT)

    def get_left(self) -> np.ndarray:
        """Get left coordinates of a box bounding the :class:`~.OpenGLMobject`"""
        return self.get_edge_center(LEFT)

    def get_zenith(self) -> np.ndarray:
        """Get zenith coordinates of a box bounding a 3D :class:`~.OpenGLMobject`."""
        return self.get_edge_center(OUT)

    def get_nadir(self) -> np.ndarray:
        """Get nadir (opposite the zenith) coordinates of a box bounding a 3D :class:`~.OpenGLMobject`."""
        return self.get_edge_center(IN)

    def length_over_dim(self, dim):
        bb = self.get_bounding_box()
        return abs((bb[2] - bb[0])[dim])

    def get_width(self):
        """Returns the width of the mobject."""
        return self.length_over_dim(0)

    def get_height(self):
        """Returns the height of the mobject."""
        return self.length_over_dim(1)

    def get_depth(self):
        """Returns the depth of the mobject."""
        return self.length_over_dim(2)

    def get_coord(self, dim: int, direction=ORIGIN):
        """Meant to generalize ``get_x``, ``get_y`` and ``get_z``"""
        return self.get_bounding_box_point(direction)[dim]

    def get_x(self, direction=ORIGIN) -> np.float64:
        """Returns x coordinate of the center of the :class:`~.OpenGLMobject` as ``float``"""
        return self.get_coord(0, direction)

    def get_y(self, direction=ORIGIN) -> np.float64:
        """Returns y coordinate of the center of the :class:`~.OpenGLMobject` as ``float``"""
        return self.get_coord(1, direction)

    def get_z(self, direction=ORIGIN) -> np.float64:
        """Returns z coordinate of the center of the :class:`~.OpenGLMobject` as ``float``"""
        return self.get_coord(2, direction)

    def get_start(self):
        """Returns the point, where the stroke that surrounds the :class:`~.OpenGLMobject` starts."""
        self.throw_error_if_no_points()
        return np.array(self.points[0])

    def get_end(self):
        """Returns the point, where the stroke that surrounds the :class:`~.OpenGLMobject` ends."""
        self.throw_error_if_no_points()
        return np.array(self.points[-1])

    def get_start_and_end(self):
        """Returns starting and ending point of a stroke as a ``tuple``."""
        return self.get_start(), self.get_end()

    def point_from_proportion(self, alpha):
        points = self.points
        i, subalpha = integer_interpolate(0, len(points) - 1, alpha)
        return interpolate(points[i], points[i + 1], subalpha)

    def pfp(self, alpha):
        """Abbreviation for point_from_proportion"""
        return self.point_from_proportion(alpha)

    def get_pieces(self, n_pieces):
        template = self.copy()
        template.submobjects = []
        alphas = np.linspace(0, 1, n_pieces + 1)
        return OpenGLGroup(
            *(
                template.copy().pointwise_become_partial(self, a1, a2)
                for a1, a2 in zip(alphas[:-1], alphas[1:])
            )
        )

    def get_z_index_reference_point(self):
        # TODO, better place to define default z_index_group?
        z_index_group = getattr(self, "z_index_group", self)
        return z_index_group.get_center()

    # Match other mobject properties

    def match_color(self, mobject: OpenGLMobject):
        """Match the color with the color of another :class:`~.OpenGLMobject`."""
        return self.set_color(mobject.get_color())

    def match_dim_size(self, mobject: OpenGLMobject, dim, **kwargs):
        """Match the specified dimension with the dimension of another :class:`~.OpenGLMobject`."""
        return self.rescale_to_fit(mobject.length_over_dim(dim), dim, **kwargs)

    def match_width(self, mobject: OpenGLMobject, **kwargs):
        """Match the width with the width of another :class:`~.OpenGLMobject`."""
        return self.match_dim_size(mobject, 0, **kwargs)

    def match_height(self, mobject: OpenGLMobject, **kwargs):
        """Match the height with the height of another :class:`~.OpenGLMobject`."""
        return self.match_dim_size(mobject, 1, **kwargs)

    def match_depth(self, mobject: OpenGLMobject, **kwargs):
        """Match the depth with the depth of another :class:`~.OpenGLMobject`."""
        return self.match_dim_size(mobject, 2, **kwargs)

    def match_coord(self, mobject: OpenGLMobject, dim, direction=ORIGIN):
        """Match the coordinates with the coordinates of another :class:`~.OpenGLMobject`."""
        return self.set_coord(
            mobject.get_coord(dim, direction),
            dim=dim,
            direction=direction,
        )

    def match_x(self, mobject, direction=ORIGIN):
        """Match x coord. to the x coord. of another :class:`~.OpenGLMobject`."""
        return self.match_coord(mobject, 0, direction)

    def match_y(self, mobject, direction=ORIGIN):
        """Match y coord. to the x coord. of another :class:`~.OpenGLMobject`."""
        return self.match_coord(mobject, 1, direction)

    def match_z(self, mobject, direction=ORIGIN):
        """Match z coord. to the x coord. of another :class:`~.OpenGLMobject`."""
        return self.match_coord(mobject, 2, direction)

    def align_to(
        self,
        mobject_or_point: OpenGLMobject | Sequence[float],
        direction=ORIGIN,
    ):
        """
        Examples:
        mob1.align_to(mob2, UP) moves mob1 vertically so that its
        top edge lines ups with mob2's top edge.

        mob1.align_to(mob2, alignment_vect = RIGHT) moves mob1
        horizontally so that it's center is directly above/below
        the center of mob2
        """
        if isinstance(mobject_or_point, OpenGLMobject):
            point = mobject_or_point.get_bounding_box_point(direction)
        else:
            point = mobject_or_point

        for dim in range(self.dim):
            if direction[dim] != 0:
                self.set_coord(point[dim], dim, direction)
        return self

    def get_group_class(self):
        return OpenGLGroup

    @staticmethod
    def get_mobject_type_class():
        """Return the base class of this mobject type."""
        return OpenGLMobject

    # Alignment

    def align_data_and_family(self, mobject):
        self.align_family(mobject)
        self.align_data(mobject)

    def align_data(self, mobject):
        # In case any data arrays get resized when aligned to shader data
        # self.refresh_shader_data()
        for mob1, mob2 in zip(self.get_family(), mobject.get_family()):
            # Separate out how points are treated so that subclasses
            # can handle that case differently if they choose
            mob1.align_points(mob2)
            for key in mob1.data.keys() & mob2.data.keys():
                if key == "points":
                    continue
                arr1 = mob1.data[key]
                arr2 = mob2.data[key]
                if len(arr2) > len(arr1):
                    mob1.data[key] = resize_preserving_order(arr1, len(arr2))
                elif len(arr1) > len(arr2):
                    mob2.data[key] = resize_preserving_order(arr2, len(arr1))

    def align_points(self, mobject):
        max_len = max(self.get_num_points(), mobject.get_num_points())
        for mob in (self, mobject):
            mob.resize_points(max_len, resize_func=resize_preserving_order)
        return self

    def align_family(self, mobject):
        mob1 = self
        mob2 = mobject
        n1 = len(mob1)
        n2 = len(mob2)
        if n1 != n2:
            mob1.add_n_more_submobjects(max(0, n2 - n1))
            mob2.add_n_more_submobjects(max(0, n1 - n2))
        # Recurse
        for sm1, sm2 in zip(mob1.submobjects, mob2.submobjects):
            sm1.align_family(sm2)
        return self

    def push_self_into_submobjects(self):
        copy = self.deepcopy()
        copy.submobjects = []
        self.resize_points(0)
        self.add(copy)
        return self

    def add_n_more_submobjects(self, n):
        if n == 0:
            return self

        curr = len(self.submobjects)
        if curr == 0:
            # If empty, simply add n point mobjects
            null_mob = self.copy()
            null_mob.set_points([self.get_center()])
            self.submobjects = [null_mob.copy() for k in range(n)]
            return self
        target = curr + n
        repeat_indices = (np.arange(target) * curr) // target
        split_factors = [(repeat_indices == i).sum() for i in range(curr)]
        new_submobs = []
        for submob, sf in zip(self.submobjects, split_factors):
            new_submobs.append(submob)
            for _ in range(1, sf):
                new_submob = submob.copy()
                # If the submobject is at all transparent, then
                # make the copy completely transparent
                if submob.get_opacity() < 1:
                    new_submob.set_opacity(0)
                new_submobs.append(new_submob)
        self.submobjects = new_submobs
        return self

    # Interpolate

    def interpolate(self, mobject1, mobject2, alpha, path_func=straight_path()):
        """Turns this :class:`~.OpenGLMobject` into an interpolation between ``mobject1``
        and ``mobject2``.

        Examples
        --------

        .. manim:: DotInterpolation
            :save_last_frame:

            class DotInterpolation(Scene):
                def construct(self):
                    dotR = Dot(color=DARK_GREY)
                    dotR.shift(2 * RIGHT)
                    dotL = Dot(color=WHITE)
                    dotL.shift(2 * LEFT)

                    dotMiddle = OpenGLVMobject().interpolate(dotL, dotR, alpha=0.3)

                    self.add(dotL, dotR, dotMiddle)
        """
        for key in self.data:
            if key in self.locked_data_keys:
                continue
            if len(self.data[key]) == 0:
                continue
            if key not in mobject1.data or key not in mobject2.data:
                continue

            if key in ("points", "bounding_box"):
                func = path_func
            else:
                func = interpolate

            self.data[key][:] = func(mobject1.data[key], mobject2.data[key], alpha)

        for key in self.uniforms:
            if key != "fixed_orientation_center":
                self.uniforms[key] = interpolate(
                    mobject1.uniforms[key],
                    mobject2.uniforms[key],
                    alpha,
                )
            else:
                self.uniforms["fixed_orientation_center"] = tuple(
                    interpolate(
                        np.array(mobject1.uniforms["fixed_orientation_center"]),
                        np.array(mobject2.uniforms["fixed_orientation_center"]),
                        alpha,
                    )
                )
        return self

    def pointwise_become_partial(self, mobject, a, b):
        """
        Set points in such a way as to become only
        part of mobject.
        Inputs 0 <= a < b <= 1 determine what portion
        of mobject to become.
        """
        pass  # To implement in subclass

    def become(
        self,
        mobject: OpenGLMobject,
        match_height: bool = False,
        match_width: bool = False,
        match_depth: bool = False,
        match_center: bool = False,
        stretch: bool = False,
    ):
        """Edit all data and submobjects to be identical
        to another :class:`~.OpenGLMobject`

        .. note::

            If both match_height and match_width are ``True`` then the transformed :class:`~.OpenGLMobject`
            will match the height first and then the width

        Parameters
        ----------
        match_height
            If ``True``, then the transformed :class:`~.OpenGLMobject` will match the height of the original
        match_width
            If ``True``, then the transformed :class:`~.OpenGLMobject` will match the width of the original
        match_depth
            If ``True``, then the transformed :class:`~.OpenGLMobject` will match the depth of the original
        match_center
            If ``True``, then the transformed :class:`~.OpenGLMobject` will match the center of the original
        stretch
            If ``True``, then the transformed :class:`~.OpenGLMobject` will stretch to fit the proportions of the original

        Examples
        --------
        .. manim:: BecomeScene

            class BecomeScene(Scene):
                def construct(self):
                    circ = Circle(fill_color=RED, fill_opacity=0.8)
                    square = Square(fill_color=BLUE, fill_opacity=0.2)
                    self.add(circ)
                    self.wait(0.5)
                    circ.become(square)
                    self.wait(0.5)
        """

        if stretch:
            mobject.stretch_to_fit_height(self.height)
            mobject.stretch_to_fit_width(self.width)
            mobject.stretch_to_fit_depth(self.depth)
        else:
            if match_height:
                mobject.match_height(self)
            if match_width:
                mobject.match_width(self)
            if match_depth:
                mobject.match_depth(self)

        if match_center:
            mobject.move_to(self.get_center())

        self.align_family(mobject)
        for sm1, sm2 in zip(self.get_family(), mobject.get_family()):
            sm1.set_data(sm2.data)
            sm1.set_uniforms(sm2.uniforms)
        self.refresh_bounding_box(recurse_down=True)
        return self

    # Locking data

    def lock_data(self, keys):
        """
        To speed up some animations, particularly transformations,
        it can be handy to acknowledge which pieces of data
        won't change during the animation so that calls to
        interpolate can skip this, and so that it's not
        read into the shader_wrapper objects needlessly
        """
        if self.has_updaters:
            return
        # Be sure shader data has most up to date information
        self.refresh_shader_data()
        self.locked_data_keys = set(keys)

    def lock_matching_data(self, mobject1, mobject2):
        for sm, sm1, sm2 in zip(
            self.get_family(),
            mobject1.get_family(),
            mobject2.get_family(),
        ):
            keys = sm.data.keys() & sm1.data.keys() & sm2.data.keys()
            sm.lock_data(
                list(
                    filter(
                        lambda key: np.all(sm1.data[key] == sm2.data[key]),
                        keys,
                    ),
                ),
            )
        return self

    def unlock_data(self):
        for mob in self.get_family():
            mob.locked_data_keys = set()

    # Operations touching shader uniforms

    @affects_shader_info_id
    def fix_in_frame(self):
        self.is_fixed_in_frame = 1.0
        return self

    @affects_shader_info_id
    def fix_orientation(self):
        self.is_fixed_orientation = 1.0
        self.fixed_orientation_center = tuple(self.get_center())
        self.depth_test = True
        return self

    @affects_shader_info_id
    def unfix_from_frame(self):
        self.is_fixed_in_frame = 0.0
        return self

    @affects_shader_info_id
    def unfix_orientation(self):
        self.is_fixed_orientation = 0.0
        self.fixed_orientation_center = (0, 0, 0)
        self.depth_test = False
        return self

    @affects_shader_info_id
    def apply_depth_test(self):
        self.depth_test = True
        return self

    @affects_shader_info_id
    def deactivate_depth_test(self):
        self.depth_test = False
        return self

    # Shader code manipulation

    def replace_shader_code(self, old, new):
        # TODO, will this work with VMobject structure, given
        # that it does not simpler return shader_wrappers of
        # family?
        for wrapper in self.get_shader_wrapper_list():
            wrapper.replace_code(old, new)
        return self

    def set_color_by_code(self, glsl_code):
        """
        Takes a snippet of code and inserts it into a
        context which has the following variables:
        vec4 color, vec3 point, vec3 unit_normal.
        The code should change the color variable
        """
        self.replace_shader_code("///// INSERT COLOR FUNCTION HERE /////", glsl_code)
        return self

    def set_color_by_xyz_func(
        self,
        glsl_snippet,
        min_value=-5.0,
        max_value=5.0,
        colormap="viridis",
    ):
        """
        Pass in a glsl expression in terms of x, y and z which returns
        a float.
        """
        # TODO, add a version of this which changes the point data instead
        # of the shader code
        for char in "xyz":
            glsl_snippet = glsl_snippet.replace(char, "point." + char)
        rgb_list = get_colormap_list(colormap)
        self.set_color_by_code(
            "color.rgb = float_to_color({}, {}, {}, {});".format(
                glsl_snippet,
                float(min_value),
                float(max_value),
                get_colormap_code(rgb_list),
            ),
        )
        return self

    # For shader data

    def refresh_shader_wrapper_id(self):
        self.get_shader_wrapper().refresh_id()
        return self

    def get_shader_wrapper(self):
        from manim.renderer.shader_wrapper import ShaderWrapper

        # if hasattr(self, "__shader_wrapper"):
        # return self.__shader_wrapper

        self.shader_wrapper = ShaderWrapper(
            vert_data=self.get_shader_data(),
            vert_indices=self.get_shader_vert_indices(),
            uniforms=self.get_shader_uniforms(),
            depth_test=self.depth_test,
            texture_paths=self.texture_paths,
            render_primitive=self.render_primitive,
            shader_folder=self.__class__.shader_folder,
        )
        return self.shader_wrapper

    def get_shader_wrapper_list(self):
        shader_wrappers = it.chain(
            [self.get_shader_wrapper()],
            *(sm.get_shader_wrapper_list() for sm in self.submobjects),
        )
        batches = batch_by_property(shader_wrappers, lambda sw: sw.get_id())

        result = []
        for wrapper_group, _ in batches:
            shader_wrapper = wrapper_group[0]
            if not shader_wrapper.is_valid():
                continue
            shader_wrapper.combine_with(*wrapper_group[1:])
            if len(shader_wrapper.vert_data) > 0:
                result.append(shader_wrapper)
        return result

    def check_data_alignment(self, array, data_key):
        # Makes sure that self.data[key] can be broadcast into
        # the given array, meaning its length has to be either 1
        # or the length of the array
        d_len = len(self.data[data_key])
        if d_len != 1 and d_len != len(array):
            self.data[data_key] = resize_with_interpolation(
                self.data[data_key],
                len(array),
            )
        return self

    def get_resized_shader_data_array(self, length):
        # If possible, try to populate an existing array, rather
        # than recreating it each frame
        points = self.points
        shader_data = np.zeros(len(points), dtype=self.shader_dtype)
        return shader_data

    def read_data_to_shader(self, shader_data, shader_data_key, data_key):
        if data_key in self.locked_data_keys:
            return
        self.check_data_alignment(shader_data, data_key)
        shader_data[shader_data_key] = self.data[data_key]

    def get_shader_data(self):
        shader_data = self.get_resized_shader_data_array(self.get_num_points())
        self.read_data_to_shader(shader_data, "point", "points")
        return shader_data

    def refresh_shader_data(self):
        self.get_shader_data()

    def get_shader_uniforms(self):
        return self.uniforms

    def get_shader_vert_indices(self):
        return self.shader_indices

    @property
    def submobjects(self):
        return self._submobjects if hasattr(self, "_submobjects") else []

    @submobjects.setter
    def submobjects(self, submobject_list):
        self.remove(*self.submobjects)
        self.add(*submobject_list)

    # Errors

    def throw_error_if_no_points(self):
        if not self.has_points():
            message = (
                "Cannot call OpenGLMobject.{} " + "for a OpenGLMobject with no points"
            )
            caller_name = sys._getframe(1).f_code.co_name
            raise Exception(message.format(caller_name))


class OpenGLGroup(OpenGLMobject):
    def __init__(self, *mobjects, **kwargs):
        super().__init__(**kwargs)
        self.add(*mobjects)


class OpenGLPoint(OpenGLMobject):
    def __init__(
        self, location=ORIGIN, artificial_width=1e-6, artificial_height=1e-6, **kwargs
    ):
        self.artificial_width = artificial_width
        self.artificial_height = artificial_height
        super().__init__(**kwargs)
        self.set_location(location)

    def get_width(self):
        return self.artificial_width

    def get_height(self):
        return self.artificial_height

    def get_location(self):
        return self.points[0].copy()

    def get_bounding_box_point(self, *args, **kwargs):
        return self.get_location()

    def set_location(self, new_loc):
        self.set_points(np.array(new_loc, ndmin=2, dtype=float))


class _AnimationBuilder:
    def __init__(self, mobject):
        self.mobject = mobject
        self.mobject.generate_target()

        self.overridden_animation = None
        self.is_chaining = False
        self.methods = []

        # Whether animation args can be passed
        self.cannot_pass_args = False
        self.anim_args = {}

    def __call__(self, **kwargs):
        if self.cannot_pass_args:
            raise ValueError(
                "Animation arguments must be passed before accessing methods and can only be passed once",
            )

        self.anim_args = kwargs
        self.cannot_pass_args = True

        return self

    def __getattr__(self, method_name):
        method = getattr(self.mobject.target, method_name)
        has_overridden_animation = hasattr(method, "_override_animate")

        if (self.is_chaining and has_overridden_animation) or self.overridden_animation:
            raise NotImplementedError(
                "Method chaining is currently not supported for "
                "overridden animations",
            )

        def update_target(*method_args, **method_kwargs):
            if has_overridden_animation:
                self.overridden_animation = method._override_animate(
                    self.mobject,
                    *method_args,
                    anim_args=self.anim_args,
                    **method_kwargs,
                )
            else:
                self.methods.append([method, method_args, method_kwargs])
                method(*method_args, **method_kwargs)
            return self

        self.is_chaining = True
        self.cannot_pass_args = True

        return update_target

    def build(self):
        from manim.animation.transform import _MethodAnimation

        if self.overridden_animation:
            anim = self.overridden_animation
        else:
            anim = _MethodAnimation(self.mobject, self.methods)

        for attr, value in self.anim_args.items():
            setattr(anim, attr, value)

        return anim


def override_animate(method):
    r"""Decorator for overriding method animations.

    This allows to specify a method (returning an :class:`~.Animation`)
    which is called when the decorated method is used with the ``.animate`` syntax
    for animating the application of a method.

    .. seealso::

        :attr:`OpenGLMobject.animate`

    .. note::

        Overridden methods cannot be combined with normal or other overridden
        methods using method chaining with the ``.animate`` syntax.


    Examples
    --------

    .. manim:: AnimationOverrideExample

        class CircleWithContent(VGroup):
            def __init__(self, content):
                super().__init__()
                self.circle = Circle()
                self.content = content
                self.add(self.circle, content)
                content.move_to(self.circle.get_center())

            def clear_content(self):
                self.remove(self.content)
                self.content = None

            @override_animate(clear_content)
            def _clear_content_animation(self, anim_args=None):
                if anim_args is None:
                    anim_args = {}
                anim = Uncreate(self.content, **anim_args)
                self.clear_content()
                return anim

        class AnimationOverrideExample(Scene):
            def construct(self):
                t = Text("hello!")
                my_mobject = CircleWithContent(t)
                self.play(Create(my_mobject))
                self.play(my_mobject.animate.clear_content())
                self.wait()

    """

    def decorator(animation_method):
        method._override_animate = animation_method
        return animation_method

    return decorator


# Extracted from /Users/hochmax/learn/manim/manim/_config/utils.py
"""Utilities to create and set the config.

The main class exported by this module is :class:`ManimConfig`.  This class
contains all configuration options, including frame geometry (e.g. frame
height/width, frame rate), output (e.g. directories, logging), styling
(e.g. background color, transparency), and general behavior (e.g. writing a
movie vs writing a single frame).

See :doc:`/guides/configuration` for an introduction to Manim's configuration system.

"""

from __future__ import annotations

import argparse
import configparser
import copy
import errno
import logging
import os
import re
import sys
from collections.abc import Iterable, Iterator, Mapping, MutableMapping
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, NoReturn

import numpy as np

from manim import constants
from manim.constants import RendererType
from manim.utils.color import ManimColor
from manim.utils.tex import TexTemplate

if TYPE_CHECKING:
    from enum import EnumMeta

    from typing_extensions import Self

    from manim.typing import StrPath, Vector3D

__all__ = ["config_file_paths", "make_config_parser", "ManimConfig", "ManimFrame"]


def config_file_paths() -> list[Path]:
    """The paths where ``.cfg`` files will be searched for.

    When manim is first imported, it processes any ``.cfg`` files it finds.  This
    function returns the locations in which these files are searched for.  In
    ascending order of precedence, these are: the library-wide config file, the
    user-wide config file, and the folder-wide config file.

    The library-wide config file determines manim's default behavior.  The
    user-wide config file is stored in the user's home folder, and determines
    the behavior of manim whenever the user invokes it from anywhere in the
    system.  The folder-wide config file only affects scenes that are in the
    same folder.  The latter two files are optional.

    These files, if they exist, are meant to loaded into a single
    :class:`configparser.ConfigParser` object, and then processed by
    :class:`ManimConfig`.

    Returns
    -------
    List[:class:`Path`]
        List of paths which may contain ``.cfg`` files, in ascending order of
        precedence.

    See Also
    --------
    :func:`make_config_parser`, :meth:`ManimConfig.digest_file`,
    :meth:`ManimConfig.digest_parser`

    Notes
    -----
    The location of the user-wide config file is OS-specific.

    """
    library_wide = Path.resolve(Path(__file__).parent / "default.cfg")
    if sys.platform.startswith("win32"):
        user_wide = Path.home() / "AppData" / "Roaming" / "Manim" / "manim.cfg"
    else:
        user_wide = Path.home() / ".config" / "manim" / "manim.cfg"
    folder_wide = Path("manim.cfg")
    return [library_wide, user_wide, folder_wide]


def make_config_parser(
    custom_file: StrPath | None = None,
) -> configparser.ConfigParser:
    """Make a :class:`ConfigParser` object and load any ``.cfg`` files.

    The user-wide file, if it exists, overrides the library-wide file.  The
    folder-wide file, if it exists, overrides the other two.

    The folder-wide file can be ignored by passing ``custom_file``.  However,
    the user-wide and library-wide config files cannot be ignored.

    Parameters
    ----------
    custom_file
        Path to a custom config file.  If used, the folder-wide file in the
        relevant directory will be ignored, if it exists.  If None, the
        folder-wide file will be used, if it exists.

    Returns
    -------
    :class:`ConfigParser`
        A parser containing the config options found in the .cfg files that
        were found.  It is guaranteed to contain at least the config options
        found in the library-wide file.

    See Also
    --------
    :func:`config_file_paths`

    """
    library_wide, user_wide, folder_wide = config_file_paths()
    # From the documentation: "An application which requires initial values to
    # be loaded from a file should load the required file or files using
    # read_file() before calling read() for any optional files."
    # https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.read
    parser = configparser.ConfigParser()
    with library_wide.open() as file:
        parser.read_file(file)  # necessary file

    other_files = [user_wide, Path(custom_file) if custom_file else folder_wide]
    parser.read(other_files)  # optional files

    return parser


def _determine_quality(qual: str) -> str:
    for quality, values in constants.QUALITIES.items():
        if values["flag"] is not None and values["flag"] == qual:
            return quality

    return qual


class ManimConfig(MutableMapping):
    """Dict-like class storing all config options.

    The global ``config`` object is an instance of this class, and acts as a
    single source of truth for all of the library's customizable behavior.

    The global ``config`` object is capable of digesting different types of
    sources and converting them into a uniform interface.  These sources are
    (in ascending order of precedence): configuration files, command line
    arguments, and programmatic changes.  Regardless of how the user chooses to
    set a config option, she can access its current value using
    :class:`ManimConfig`'s attributes and properties.

    Notes
    -----
    Each config option is implemented as a property of this class.

    Each config option can be set via a config file, using the full name of the
    property.  If a config option has an associated CLI flag, then the flag is
    equal to the full name of the property.  Those that admit an alternative
    flag or no flag at all are documented in the individual property's
    docstring.

    Examples
    --------
    We use a copy of the global configuration object in the following
    examples for the sake of demonstration; you can skip these lines
    and just import ``config`` directly if you actually want to modify
    the configuration:

    .. code-block:: pycon

        >>> from manim import config as global_config
        >>> config = global_config.copy()

    Each config option allows for dict syntax and attribute syntax.  For
    example, the following two lines are equivalent,

    .. code-block:: pycon

        >>> from manim import WHITE
        >>> config.background_color = WHITE
        >>> config["background_color"] = WHITE

    The former is preferred; the latter is provided mostly for backwards
    compatibility.

    The config options are designed to keep internal consistency.  For example,
    setting ``frame_y_radius`` will affect ``frame_height``:

    .. code-block:: pycon

        >>> config.frame_height
        8.0
        >>> config.frame_y_radius = 5.0
        >>> config.frame_height
        10.0

    There are many ways of interacting with config options.  Take for example
    the config option ``background_color``.  There are three ways to change it:
    via a config file, via CLI flags, or programmatically.

    To set the background color via a config file, save the following
    ``manim.cfg`` file with the following contents.

    .. code-block::

       [CLI]
       background_color = WHITE

    In order to have this ``.cfg`` file apply to a manim scene, it needs to be
    placed in the same directory as the script,

    .. code-block:: bash

          project/
          ├─scene.py
          └─manim.cfg

    Now, when the user executes

    .. code-block:: bash

        manim scene.py

    the background of the scene will be set to ``WHITE``.  This applies regardless
    of where the manim command is invoked from.

    Command line arguments override ``.cfg`` files.  In the previous example,
    executing

    .. code-block:: bash

        manim scene.py -c BLUE

    will set the background color to BLUE, regardless of the contents of
    ``manim.cfg``.

    Finally, any programmatic changes made within the scene script itself will
    override the command line arguments.  For example, if ``scene.py`` contains
    the following

    .. code-block:: python

        from manim import *

        config.background_color = RED


        class MyScene(Scene): ...

    the background color will be set to RED, regardless of the contents of
    ``manim.cfg`` or the CLI arguments used when invoking manim.

    """

    _OPTS = {
        "assets_dir",
        "background_color",
        "background_opacity",
        "custom_folders",
        "disable_caching",
        "disable_caching_warning",
        "dry_run",
        "enable_wireframe",
        "ffmpeg_loglevel",
        "format",
        "flush_cache",
        "frame_height",
        "frame_rate",
        "frame_width",
        "frame_x_radius",
        "frame_y_radius",
        "from_animation_number",
        "images_dir",
        "input_file",
        "media_embed",
        "media_width",
        "log_dir",
        "log_to_file",
        "max_files_cached",
        "media_dir",
        "movie_file_extension",
        "notify_outdated_version",
        "output_file",
        "partial_movie_dir",
        "pixel_height",
        "pixel_width",
        "plugins",
        "preview",
        "progress_bar",
        "quality",
        "save_as_gif",
        "save_sections",
        "save_last_frame",
        "save_pngs",
        "scene_names",
        "show_in_file_browser",
        "tex_dir",
        "tex_template",
        "tex_template_file",
        "text_dir",
        "upto_animation_number",
        "renderer",
        "enable_gui",
        "gui_location",
        "use_projection_fill_shaders",
        "use_projection_stroke_shaders",
        "verbosity",
        "video_dir",
        "sections_dir",
        "fullscreen",
        "window_position",
        "window_size",
        "window_monitor",
        "write_all",
        "write_to_movie",
        "zero_pad",
        "force_window",
        "no_latex_cleanup",
        "preview_command",
    }

    def __init__(self) -> None:
        self._d: dict[str, Any | None] = {k: None for k in self._OPTS}

    # behave like a dict
    def __iter__(self) -> Iterator[str]:
        return iter(self._d)

    def __len__(self) -> int:
        return len(self._d)

    def __contains__(self, key: object) -> bool:
        try:
            self.__getitem__(key)
            return True
        except AttributeError:
            return False

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, val: Any) -> None:
        getattr(ManimConfig, key).fset(self, val)  # fset is the property's setter

    def update(self, obj: ManimConfig | dict[str, Any]) -> None:  # type: ignore[override]
        """Digest the options found in another :class:`ManimConfig` or in a dict.

        Similar to :meth:`dict.update`, replaces the values of this object with
        those of ``obj``.

        Parameters
        ----------
        obj
            The object to copy values from.

        Returns
        -------
        None

        Raises
        -----
        :class:`AttributeError`
            If ``obj`` is a dict but contains keys that do not belong to any
            config options.

        See Also
        --------
        :meth:`~ManimConfig.digest_file`, :meth:`~ManimConfig.digest_args`,
        :meth:`~ManimConfig.digest_parser`

        """

        if isinstance(obj, ManimConfig):
            self._d.update(obj._d)
            if obj.tex_template:
                self.tex_template = obj.tex_template

        elif isinstance(obj, dict):
            # First update the underlying _d, then update other properties
            _dict = {k: v for k, v in obj.items() if k in self._d}
            for k, v in _dict.items():
                self[k] = v

            _dict = {k: v for k, v in obj.items() if k not in self._d}
            for k, v in _dict.items():
                self[k] = v

    # don't allow to delete anything
    def __delitem__(self, key: str) -> NoReturn:
        raise AttributeError("'ManimConfig' object does not support item deletion")

    def __delattr__(self, key: str) -> NoReturn:
        raise AttributeError("'ManimConfig' object does not support item deletion")

    # copy functions
    def copy(self) -> Self:
        """Deepcopy the contents of this ManimConfig.

        Returns
        -------
        :class:`ManimConfig`
            A copy of this object containing no shared references.

        See Also
        --------
        :func:`tempconfig`

        Notes
        -----
        This is the main mechanism behind :func:`tempconfig`.

        """
        return copy.deepcopy(self)

    def __copy__(self) -> Self:
        """See ManimConfig.copy()."""
        return copy.deepcopy(self)

    def __deepcopy__(self, memo: dict[str, Any]) -> Self:
        """See ManimConfig.copy()."""
        c = type(self)()
        # Deepcopying the underlying dict is enough because all properties
        # either read directly from it or compute their value on the fly from
        # values read directly from it.
        c._d = copy.deepcopy(self._d, memo)
        return c

    # helper type-checking methods
    def _set_from_list(self, key: str, val: Any, values: list[Any]) -> None:
        """Set ``key`` to ``val`` if ``val`` is contained in ``values``."""
        if val in values:
            self._d[key] = val
        else:
            raise ValueError(f"attempted to set {key} to {val}; must be in {values}")

    def _set_from_enum(self, key: str, enum_value: Any, enum_class: EnumMeta) -> None:
        """Set ``key`` to the enum object with value ``enum_value`` in the given
        ``enum_class``.

        Tests::

            >>> from enum import Enum
            >>> class Fruit(Enum):
            ...     APPLE = 1
            ...     BANANA = 2
            ...     CANTALOUPE = 3
            >>> test_config = ManimConfig()
            >>> test_config._set_from_enum("fruit", 1, Fruit)
            >>> test_config._d['fruit']
            <Fruit.APPLE: 1>
            >>> test_config._set_from_enum("fruit", Fruit.BANANA, Fruit)
            >>> test_config._d['fruit']
            <Fruit.BANANA: 2>
            >>> test_config._set_from_enum("fruit", 42, Fruit)
            Traceback (most recent call last):
            ...
            ValueError: 42 is not a valid Fruit
        """
        self._d[key] = enum_class(enum_value)

    def _set_boolean(self, key: str, val: Any) -> None:
        """Set ``key`` to ``val`` if ``val`` is Boolean."""
        if val in [True, False]:
            self._d[key] = val
        else:
            raise ValueError(f"{key} must be boolean")

    def _set_tuple(self, key: str, val: tuple[Any]) -> None:
        if isinstance(val, tuple):
            self._d[key] = val
        else:
            raise ValueError(f"{key} must be tuple")

    def _set_str(self, key: str, val: Any) -> None:
        """Set ``key`` to ``val`` if ``val`` is a string."""
        if isinstance(val, str):
            self._d[key] = val
        elif not val:
            self._d[key] = ""
        else:
            raise ValueError(f"{key} must be str or falsy value")

    def _set_between(self, key: str, val: float, lo: float, hi: float) -> None:
        """Set ``key`` to ``val`` if lo <= val <= hi."""
        if lo <= val <= hi:
            self._d[key] = val
        else:
            raise ValueError(f"{key} must be {lo} <= {key} <= {hi}")

    def _set_int_between(self, key: str, val: int, lo: int, hi: int) -> None:
        """Set ``key`` to ``val`` if lo <= val <= hi."""
        if lo <= val <= hi:
            self._d[key] = val
        else:
            raise ValueError(
                f"{key} must be an integer such that {lo} <= {key} <= {hi}",
            )

    def _set_pos_number(self, key: str, val: int, allow_inf: bool) -> None:
        """Set ``key`` to ``val`` if ``val`` is a positive integer."""
        if isinstance(val, int) and val > -1:
            self._d[key] = val
        elif allow_inf and val in [-1, float("inf")]:
            self._d[key] = float("inf")
        else:
            raise ValueError(
                f"{key} must be a non-negative integer (use -1 for infinity)",
            )

    def __repr__(self) -> str:
        rep = ""
        for k, v in sorted(self._d.items(), key=lambda x: x[0]):
            rep += f"{k}: {v}, "
        return rep

    # builders
    def digest_parser(self, parser: configparser.ConfigParser) -> Self:
        """Process the config options present in a :class:`ConfigParser` object.

        This method processes arbitrary parsers, not only those read from a
        single file, whereas :meth:`~ManimConfig.digest_file` can only process one
        file at a time.

        Parameters
        ----------
        parser
            An object reflecting the contents of one or many ``.cfg`` files.  In
            particular, it may reflect the contents of multiple files that have
            been parsed in a cascading fashion.

        Returns
        -------
        self : :class:`ManimConfig`
            This object, after processing the contents of ``parser``.

        See Also
        --------
        :func:`make_config_parser`, :meth:`~.ManimConfig.digest_file`,
        :meth:`~.ManimConfig.digest_args`,

        Notes
        -----
        If there are multiple ``.cfg`` files to process, it is always more
        efficient to parse them into a single :class:`ConfigParser` object
        first, and then call this function once (instead of calling
        :meth:`~.ManimConfig.digest_file` multiple times).

        Examples
        --------
        To digest the config options set in two files, first create a
        ConfigParser and parse both files and then digest the parser:

        .. code-block:: python

            parser = configparser.ConfigParser()
            parser.read([file1, file2])
            config = ManimConfig().digest_parser(parser)

        In fact, the global ``config`` object is initialized like so:

        .. code-block:: python

            parser = make_config_parser()
            config = ManimConfig().digest_parser(parser)

        """
        self._parser = parser

        # boolean keys
        for key in [
            "notify_outdated_version",
            "write_to_movie",
            "save_last_frame",
            "write_all",
            "save_pngs",
            "save_as_gif",
            "save_sections",
            "preview",
            "show_in_file_browser",
            "log_to_file",
            "disable_caching",
            "disable_caching_warning",
            "flush_cache",
            "custom_folders",
            "enable_gui",
            "fullscreen",
            "use_projection_fill_shaders",
            "use_projection_stroke_shaders",
            "enable_wireframe",
            "force_window",
            "no_latex_cleanup",
        ]:
            setattr(self, key, parser["CLI"].getboolean(key, fallback=False))

        # int keys
        for key in [
            "from_animation_number",
            "upto_animation_number",
            "max_files_cached",
            # the next two must be set BEFORE digesting frame_width and frame_height
            "pixel_height",
            "pixel_width",
            "window_monitor",
            "zero_pad",
        ]:
            setattr(self, key, parser["CLI"].getint(key))

        # str keys
        for key in [
            "assets_dir",
            "verbosity",
            "media_dir",
            "log_dir",
            "video_dir",
            "sections_dir",
            "images_dir",
            "text_dir",
            "tex_dir",
            "partial_movie_dir",
            "input_file",
            "output_file",
            "movie_file_extension",
            "background_color",
            "renderer",
            "window_position",
        ]:
            setattr(self, key, parser["CLI"].get(key, fallback="", raw=True))

        # float keys
        for key in [
            "background_opacity",
            "frame_rate",
            # the next two are floats but have their own logic, applied later
            # "frame_width",
            # "frame_height",
        ]:
            setattr(self, key, parser["CLI"].getfloat(key))

        # tuple keys
        gui_location = tuple(
            map(int, re.split(r"[;,\-]", parser["CLI"]["gui_location"])),
        )
        setattr(self, "gui_location", gui_location)

        window_size = parser["CLI"][
            "window_size"
        ]  # if not "default", get a tuple of the position
        if window_size != "default":
            window_size = tuple(map(int, re.split(r"[;,\-]", window_size)))
        setattr(self, "window_size", window_size)

        # plugins
        plugins = parser["CLI"].get("plugins", fallback="", raw=True)
        if plugins == "":
            plugins = []
        else:
            plugins = plugins.split(",")
        self.plugins = plugins
        # the next two must be set AFTER digesting pixel_width and pixel_height
        self["frame_height"] = parser["CLI"].getfloat("frame_height", 8.0)
        width = parser["CLI"].getfloat("frame_width", None)
        if width is None:
            self["frame_width"] = self["frame_height"] * self["aspect_ratio"]
        else:
            self["frame_width"] = width

        # other logic
        val = parser["CLI"].get("tex_template_file")
        if val:
            self.tex_template_file = val

        val = parser["CLI"].get("progress_bar")
        if val:
            setattr(self, "progress_bar", val)

        val = parser["ffmpeg"].get("loglevel")
        if val:
            self.ffmpeg_loglevel = val

        try:
            val = parser["jupyter"].getboolean("media_embed")
        except ValueError:
            val = None
        setattr(self, "media_embed", val)

        val = parser["jupyter"].get("media_width")
        if val:
            setattr(self, "media_width", val)

        val = parser["CLI"].get("quality", fallback="", raw=True)
        if val:
            self.quality = _determine_quality(val)

        return self

    def digest_args(self, args: argparse.Namespace) -> Self:
        """Process the config options present in CLI arguments.

        Parameters
        ----------
        args
            An object returned by :func:`.main_utils.parse_args()`.

        Returns
        -------
        self : :class:`ManimConfig`
            This object, after processing the contents of ``parser``.

        See Also
        --------
        :func:`.main_utils.parse_args()`, :meth:`~.ManimConfig.digest_parser`,
        :meth:`~.ManimConfig.digest_file`

        Notes
        -----
        If ``args.config_file`` is a non-empty string, ``ManimConfig`` tries to digest the
        contents of said file with :meth:`~ManimConfig.digest_file` before
        digesting any other CLI arguments.

        """
        # if the input file is a config file, parse it properly
        if args.file.suffix == ".cfg":
            args.config_file = args.file

        # if args.file is `-`, the animation code has to be taken from STDIN, so the
        # input file path shouldn't be absolute, since that file won't be read.
        if str(args.file) == "-":
            self.input_file = args.file

        # if a config file has been passed, digest it first so that other CLI
        # flags supersede it
        if args.config_file:
            self.digest_file(args.config_file)

        # read input_file from the args if it wasn't set by the config file
        if not self.input_file:
            self.input_file = Path(args.file).absolute()

        self.scene_names = args.scene_names if args.scene_names is not None else []
        self.output_file = args.output_file

        for key in [
            "notify_outdated_version",
            "preview",
            "show_in_file_browser",
            "write_to_movie",
            "save_last_frame",
            "save_pngs",
            "save_as_gif",
            "save_sections",
            "write_all",
            "disable_caching",
            "format",
            "flush_cache",
            "progress_bar",
            "transparent",
            "scene_names",
            "verbosity",
            "renderer",
            "background_color",
            "enable_gui",
            "fullscreen",
            "use_projection_fill_shaders",
            "use_projection_stroke_shaders",
            "zero_pad",
            "enable_wireframe",
            "force_window",
            "dry_run",
            "no_latex_cleanup",
            "preview_command",
        ]:
            if hasattr(args, key):
                attr = getattr(args, key)
                # if attr is None, then no argument was passed and we should
                # not change the current config
                if attr is not None:
                    self[key] = attr

        for key in [
            "media_dir",  # always set this one first
            "log_dir",
            "log_to_file",  # always set this one last
        ]:
            if hasattr(args, key):
                attr = getattr(args, key)
                # if attr is None, then no argument was passed and we should
                # not change the current config
                if attr is not None:
                    self[key] = attr

        if self["save_last_frame"]:
            self["write_to_movie"] = False

        # Handle the -n flag.
        nflag = args.from_animation_number
        if nflag:
            self.from_animation_number = nflag[0]
            try:
                self.upto_animation_number = nflag[1]
            except Exception:
                logging.getLogger("manim").info(
                    f"No end scene number specified in -n option. Rendering from {nflag[0]} onwards...",
                )

        # Handle the quality flags
        self.quality = _determine_quality(getattr(args, "quality", None))

        # Handle the -r flag.
        rflag = args.resolution
        if rflag:
            self.pixel_width = int(rflag[0])
            self.pixel_height = int(rflag[1])

        fps = args.frame_rate
        if fps:
            self.frame_rate = float(fps)

        # Handle --custom_folders
        if args.custom_folders:
            for opt in [
                "media_dir",
                "video_dir",
                "sections_dir",
                "images_dir",
                "text_dir",
                "tex_dir",
                "log_dir",
                "partial_movie_dir",
            ]:
                self[opt] = self._parser["custom_folders"].get(opt, raw=True)
            # --media_dir overrides the default.cfg file
            if hasattr(args, "media_dir") and args.media_dir:
                self.media_dir = args.media_dir

        # Handle --tex_template
        if args.tex_template:
            self.tex_template = TexTemplate.from_file(args.tex_template)

        if (
            self.renderer == RendererType.OPENGL
            and getattr(args, "write_to_movie") is None
        ):
            # --write_to_movie was not passed on the command line, so don't generate video.
            self["write_to_movie"] = False

        # Handle --gui_location flag.
        if getattr(args, "gui_location") is not None:
            self.gui_location = args.gui_location

        return self

    def digest_file(self, filename: StrPath) -> Self:
        """Process the config options present in a ``.cfg`` file.

        This method processes a single ``.cfg`` file, whereas
        :meth:`~ManimConfig.digest_parser` can process arbitrary parsers, built
        perhaps from multiple ``.cfg`` files.

        Parameters
        ----------
        filename
            Path to the ``.cfg`` file.

        Returns
        -------
        self : :class:`ManimConfig`
            This object, after processing the contents of ``filename``.

        See Also
        --------
        :meth:`~ManimConfig.digest_file`, :meth:`~ManimConfig.digest_args`,
        :func:`make_config_parser`

        Notes
        -----
        If there are multiple ``.cfg`` files to process, it is always more
        efficient to parse them into a single :class:`ConfigParser` object
        first and digesting them with one call to
        :meth:`~ManimConfig.digest_parser`, instead of calling this method
        multiple times.

        """
        if not Path(filename).is_file():
            raise FileNotFoundError(
                errno.ENOENT,
                "Error: --config_file could not find a valid config file.",
                str(filename),
            )

        return self.digest_parser(make_config_parser(filename))

    # config options are properties

    @property
    def preview(self) -> bool:
        """Whether to play the rendered movie (-p)."""
        return self._d["preview"] or self._d["enable_gui"]

    @preview.setter
    def preview(self, value: bool) -> None:
        self._set_boolean("preview", value)

    @property
    def show_in_file_browser(self) -> bool:
        """Whether to show the output file in the file browser (-f)."""
        return self._d["show_in_file_browser"]

    @show_in_file_browser.setter
    def show_in_file_browser(self, value: bool) -> None:
        self._set_boolean("show_in_file_browser", value)

    @property
    def progress_bar(self) -> str:
        """Whether to show progress bars while rendering animations."""
        return self._d["progress_bar"]

    @progress_bar.setter
    def progress_bar(self, value: str) -> None:
        self._set_from_list("progress_bar", value, ["none", "display", "leave"])

    @property
    def log_to_file(self) -> bool:
        """Whether to save logs to a file."""
        return self._d["log_to_file"]

    @log_to_file.setter
    def log_to_file(self, value: bool) -> None:
        self._set_boolean("log_to_file", value)

    @property
    def notify_outdated_version(self) -> bool:
        """Whether to notify if there is a version update available."""
        return self._d["notify_outdated_version"]

    @notify_outdated_version.setter
    def notify_outdated_version(self, value: bool) -> None:
        self._set_boolean("notify_outdated_version", value)

    @property
    def write_to_movie(self) -> bool:
        """Whether to render the scene to a movie file (-w)."""
        return self._d["write_to_movie"]

    @write_to_movie.setter
    def write_to_movie(self, value: bool) -> None:
        self._set_boolean("write_to_movie", value)

    @property
    def save_last_frame(self) -> bool:
        """Whether to save the last frame of the scene as an image file (-s)."""
        return self._d["save_last_frame"]

    @save_last_frame.setter
    def save_last_frame(self, value: bool) -> None:
        self._set_boolean("save_last_frame", value)

    @property
    def write_all(self) -> bool:
        """Whether to render all scenes in the input file (-a)."""
        return self._d["write_all"]

    @write_all.setter
    def write_all(self, value: bool) -> None:
        self._set_boolean("write_all", value)

    @property
    def save_pngs(self) -> bool:
        """Whether to save all frames in the scene as images files (-g)."""
        return self._d["save_pngs"]

    @save_pngs.setter
    def save_pngs(self, value: bool) -> None:
        self._set_boolean("save_pngs", value)

    @property
    def save_as_gif(self) -> bool:
        """Whether to save the rendered scene in .gif format (-i)."""
        return self._d["save_as_gif"]

    @save_as_gif.setter
    def save_as_gif(self, value: bool) -> None:
        self._set_boolean("save_as_gif", value)

    @property
    def save_sections(self) -> bool:
        """Whether to save single videos for each section in addition to the movie file."""
        return self._d["save_sections"]

    @save_sections.setter
    def save_sections(self, value: bool) -> None:
        self._set_boolean("save_sections", value)

    @property
    def enable_wireframe(self) -> bool:
        """Whether to enable wireframe debugging mode in opengl."""
        return self._d["enable_wireframe"]

    @enable_wireframe.setter
    def enable_wireframe(self, value: bool) -> None:
        self._set_boolean("enable_wireframe", value)

    @property
    def force_window(self) -> bool:
        """Whether to force window when using the opengl renderer."""
        return self._d["force_window"]

    @force_window.setter
    def force_window(self, value: bool) -> None:
        self._set_boolean("force_window", value)

    @property
    def no_latex_cleanup(self) -> bool:
        """Prevents deletion of .aux, .dvi, and .log files produced by Tex and MathTex."""
        return self._d["no_latex_cleanup"]

    @no_latex_cleanup.setter
    def no_latex_cleanup(self, value: bool) -> None:
        self._set_boolean("no_latex_cleanup", value)

    @property
    def preview_command(self) -> str:
        return self._d["preview_command"]

    @preview_command.setter
    def preview_command(self, value: str) -> None:
        self._set_str("preview_command", value)

    @property
    def verbosity(self) -> str:
        """Logger verbosity; "DEBUG", "INFO", "WARNING", "ERROR", or "CRITICAL" (-v)."""
        return self._d["verbosity"]

    @verbosity.setter
    def verbosity(self, val: str) -> None:
        self._set_from_list(
            "verbosity",
            val,
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )
        logging.getLogger("manim").setLevel(val)

    @property
    def format(self) -> str:
        """File format; "png", "gif", "mp4", "webm" or "mov"."""
        return self._d["format"]

    @format.setter
    def format(self, val: str) -> None:
        self._set_from_list(
            "format",
            val,
            [None, "png", "gif", "mp4", "mov", "webm"],
        )
        if self.format == "webm":
            logging.getLogger("manim").warning(
                "Output format set as webm, this can be slower than other formats",
            )

    @property
    def ffmpeg_loglevel(self) -> str:
        """Verbosity level of ffmpeg (no flag)."""
        return self._d["ffmpeg_loglevel"]

    @ffmpeg_loglevel.setter
    def ffmpeg_loglevel(self, val: str) -> None:
        self._set_from_list(
            "ffmpeg_loglevel",
            val,
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )
        logging.getLogger("libav").setLevel(self.ffmpeg_loglevel)

    @property
    def media_embed(self) -> bool:
        """Whether to embed videos in Jupyter notebook."""
        return self._d["media_embed"]

    @media_embed.setter
    def media_embed(self, value: bool) -> None:
        self._set_boolean("media_embed", value)

    @property
    def media_width(self) -> str:
        """Media width in Jupyter notebook."""
        return self._d["media_width"]

    @media_width.setter
    def media_width(self, value: str) -> None:
        self._set_str("media_width", value)

    @property
    def pixel_width(self) -> int:
        """Frame width in pixels (--resolution, -r)."""
        return self._d["pixel_width"]

    @pixel_width.setter
    def pixel_width(self, value: int) -> None:
        self._set_pos_number("pixel_width", value, False)

    @property
    def pixel_height(self) -> int:
        """Frame height in pixels (--resolution, -r)."""
        return self._d["pixel_height"]

    @pixel_height.setter
    def pixel_height(self, value: int) -> None:
        self._set_pos_number("pixel_height", value, False)

    @property
    def aspect_ratio(self) -> int:
        """Aspect ratio (width / height) in pixels (--resolution, -r)."""
        return self._d["pixel_width"] / self._d["pixel_height"]

    @property
    def frame_height(self) -> float:
        """Frame height in logical units (no flag)."""
        return self._d["frame_height"]

    @frame_height.setter
    def frame_height(self, value: float) -> None:
        self._d.__setitem__("frame_height", value)

    @property
    def frame_width(self) -> float:
        """Frame width in logical units (no flag)."""
        return self._d["frame_width"]

    @frame_width.setter
    def frame_width(self, value: float) -> None:
        self._d.__setitem__("frame_width", value)

    @property
    def frame_y_radius(self) -> float:
        """Half the frame height (no flag)."""
        return self._d["frame_height"] / 2

    @frame_y_radius.setter
    def frame_y_radius(self, value: float) -> None:
        self._d.__setitem__("frame_y_radius", value) or self._d.__setitem__(
            "frame_height", 2 * value
        )

    @property
    def frame_x_radius(self) -> float:
        """Half the frame width (no flag)."""
        return self._d["frame_width"] / 2

    @frame_x_radius.setter
    def frame_x_radius(self, value: float) -> None:
        self._d.__setitem__("frame_x_radius", value) or self._d.__setitem__(
            "frame_width", 2 * value
        )

    @property
    def top(self) -> Vector3D:
        """Coordinate at the center top of the frame."""
        return self.frame_y_radius * constants.UP

    @property
    def bottom(self) -> Vector3D:
        """Coordinate at the center bottom of the frame."""
        return self.frame_y_radius * constants.DOWN

    @property
    def left_side(self) -> Vector3D:
        """Coordinate at the middle left of the frame."""
        return self.frame_x_radius * constants.LEFT

    @property
    def right_side(self) -> Vector3D:
        """Coordinate at the middle right of the frame."""
        return self.frame_x_radius * constants.RIGHT

    @property
    def frame_rate(self) -> float:
        """Frame rate in frames per second."""
        return self._d["frame_rate"]

    @frame_rate.setter
    def frame_rate(self, value: float) -> None:
        self._d.__setitem__("frame_rate", value)

    # TODO: This was parsed before maybe add ManimColor(val), but results in circular import
    @property
    def background_color(self) -> ManimColor:
        """Background color of the scene (-c)."""
        return self._d["background_color"]

    @background_color.setter
    def background_color(self, value: Any) -> None:
        self._d.__setitem__("background_color", ManimColor(value))

    @property
    def from_animation_number(self) -> int:
        """Start rendering animations at this number (-n)."""
        return self._d["from_animation_number"]

    @from_animation_number.setter
    def from_animation_number(self, value: int) -> None:
        self._d.__setitem__("from_animation_number", value)

    @property
    def upto_animation_number(self) -> int:
        """Stop rendering animations at this number. Use -1 to avoid skipping (-n)."""
        return self._d["upto_animation_number"]

    @upto_animation_number.setter
    def upto_animation_number(self, value: int) -> None:
        self._set_pos_number("upto_animation_number", value, True)

    @property
    def max_files_cached(self) -> int:
        """Maximum number of files cached.  Use -1 for infinity (no flag)."""
        return self._d["max_files_cached"]

    @max_files_cached.setter
    def max_files_cached(self, value: int) -> None:
        self._set_pos_number("max_files_cached", value, True)

    @property
    def window_monitor(self) -> int:
        """The monitor on which the scene will be rendered."""
        return self._d["window_monitor"]

    @window_monitor.setter
    def window_monitor(self, value: int) -> None:
        self._set_pos_number("window_monitor", value, True)

    @property
    def flush_cache(self) -> bool:
        """Whether to delete all the cached partial movie files."""
        return self._d["flush_cache"]

    @flush_cache.setter
    def flush_cache(self, value: bool) -> None:
        self._set_boolean("flush_cache", value)

    @property
    def disable_caching(self) -> bool:
        """Whether to use scene caching."""
        return self._d["disable_caching"]

    @disable_caching.setter
    def disable_caching(self, value: bool) -> None:
        self._set_boolean("disable_caching", value)

    @property
    def disable_caching_warning(self) -> bool:
        """Whether a warning is raised if there are too much submobjects to hash."""
        return self._d["disable_caching_warning"]

    @disable_caching_warning.setter
    def disable_caching_warning(self, value: bool) -> None:
        self._set_boolean("disable_caching_warning", value)

    @property
    def movie_file_extension(self) -> str:
        """Either .mp4, .webm or .mov."""
        return self._d["movie_file_extension"]

    @movie_file_extension.setter
    def movie_file_extension(self, value: str) -> None:
        self._set_from_list("movie_file_extension", value, [".mp4", ".mov", ".webm"])

    @property
    def background_opacity(self) -> float:
        """A number between 0.0 (fully transparent) and 1.0 (fully opaque)."""
        return self._d["background_opacity"]

    @background_opacity.setter
    def background_opacity(self, value: float) -> None:
        self._set_between("background_opacity", value, 0, 1)

    @property
    def frame_size(self) -> tuple[int, int]:
        """Tuple with (pixel width, pixel height) (no flag)."""
        return (self._d["pixel_width"], self._d["pixel_height"])

    @frame_size.setter
    def frame_size(self, value: tuple[int, int]) -> None:
        self._d.__setitem__("pixel_width", value[0]) or self._d.__setitem__(
            "pixel_height", value[1]
        )

    @property
    def quality(self) -> str | None:
        """Video quality (-q)."""
        keys = ["pixel_width", "pixel_height", "frame_rate"]
        q = {k: self[k] for k in keys}
        for qual in constants.QUALITIES:
            if all(q[k] == constants.QUALITIES[qual][k] for k in keys):
                return qual
        return None

    @quality.setter
    def quality(self, value: str | None) -> None:
        if value is None:
            return
        if value not in constants.QUALITIES:
            raise KeyError(f"quality must be one of {list(constants.QUALITIES.keys())}")
        q = constants.QUALITIES[value]
        self.frame_size = q["pixel_width"], q["pixel_height"]
        self.frame_rate = q["frame_rate"]

    @property
    def transparent(self) -> bool:
        """Whether the background opacity is 0.0 (-t)."""
        return self._d["background_opacity"] == 0.0

    @transparent.setter
    def transparent(self, value: bool) -> None:
        self._d["background_opacity"] = float(not value)
        self.resolve_movie_file_extension(value)

    @property
    def dry_run(self) -> bool:
        """Whether dry run is enabled."""
        return self._d["dry_run"]

    @dry_run.setter
    def dry_run(self, val: bool) -> None:
        self._d["dry_run"] = val
        if val:
            self.write_to_movie = False
            self.write_all = False
            self.save_last_frame = False
            self.format = None

    @property
    def renderer(self) -> RendererType:
        """The currently active renderer.

        Populated with one of the available renderers in :class:`.RendererType`.

        Tests::

            >>> test_config = ManimConfig()
            >>> test_config.renderer is None  # a new ManimConfig is unpopulated
            True
            >>> test_config.renderer = 'opengl'
            >>> test_config.renderer
            <RendererType.OPENGL: 'opengl'>
            >>> test_config.renderer = 42
            Traceback (most recent call last):
            ...
            ValueError: 42 is not a valid RendererType

        Check that capitalization of renderer types is irrelevant::

            >>> test_config.renderer = 'OpenGL'
            >>> test_config.renderer = 'cAirO'
        """
        return self._d["renderer"]

    @renderer.setter
    def renderer(self, value: str | RendererType) -> None:
        """The setter of the renderer property.

        Takes care of switching inheritance bases using the
        :class:`.ConvertToOpenGL` metaclass.
        """
        if isinstance(value, str):
            value = value.lower()
        renderer = RendererType(value)
        try:
            from manim.mobject.opengl.opengl_compatibility import ConvertToOpenGL
            from manim.mobject.opengl.opengl_mobject import OpenGLMobject
            from manim.mobject.opengl.opengl_vectorized_mobject import OpenGLVMobject

            from ..mobject.mobject import Mobject
            from ..mobject.types.vectorized_mobject import VMobject

            for cls in ConvertToOpenGL._converted_classes:
                if renderer == RendererType.OPENGL:
                    conversion_dict = {
                        Mobject: OpenGLMobject,
                        VMobject: OpenGLVMobject,
                    }
                else:
                    conversion_dict = {
                        OpenGLMobject: Mobject,
                        OpenGLVMobject: VMobject,
                    }

                cls.__bases__ = tuple(
                    conversion_dict.get(base, base) for base in cls.__bases__
                )
        except ImportError:
            # The renderer is set during the initial import of the
            # library for the first time. The imports above cause an
            # ImportError due to circular imports. However, the
            # metaclass sets stuff up correctly in this case, so we
            # can just do nothing.
            pass

        self._set_from_enum("renderer", renderer, RendererType)

    @property
    def media_dir(self) -> str:
        """Main output directory.  See :meth:`ManimConfig.get_dir`."""
        return self._d["media_dir"]

    @media_dir.setter
    def media_dir(self, value: str | Path) -> None:
        self._set_dir("media_dir", value)

    @property
    def window_position(self) -> str:
        """Set the position of preview window. You can use directions, e.g. UL/DR/ORIGIN/LEFT...or the position(pixel) of the upper left corner of the window, e.g. '960,540'."""
        return self._d["window_position"]

    @window_position.setter
    def window_position(self, value: str) -> None:
        self._d.__setitem__("window_position", value)

    @property
    def window_size(self) -> str:
        """The size of the opengl window. 'default' to automatically scale the window based on the display monitor."""
        return self._d["window_size"]

    @window_size.setter
    def window_size(self, value: str) -> None:
        self._d.__setitem__("window_size", value)

    def resolve_movie_file_extension(self, is_transparent: bool) -> None:
        if is_transparent:
            self.movie_file_extension = ".webm" if self.format == "webm" else ".mov"
        elif self.format == "webm":
            self.movie_file_extension = ".webm"
        elif self.format == "mov":
            self.movie_file_extension = ".mov"
        else:
            self.movie_file_extension = ".mp4"

    @property
    def enable_gui(self) -> bool:
        """Enable GUI interaction."""
        return self._d["enable_gui"]

    @enable_gui.setter
    def enable_gui(self, value: bool) -> None:
        self._set_boolean("enable_gui", value)

    @property
    def gui_location(self) -> tuple[Any]:
        """Enable GUI interaction."""
        return self._d["gui_location"]

    @gui_location.setter
    def gui_location(self, value: tuple[Any]) -> None:
        self._set_tuple("gui_location", value)

    @property
    def fullscreen(self) -> bool:
        """Expand the window to its maximum possible size."""
        return self._d["fullscreen"]

    @fullscreen.setter
    def fullscreen(self, value: bool) -> None:
        self._set_boolean("fullscreen", value)

    @property
    def use_projection_fill_shaders(self) -> bool:
        """Use shaders for OpenGLVMobject fill which are compatible with transformation matrices."""
        return self._d["use_projection_fill_shaders"]

    @use_projection_fill_shaders.setter
    def use_projection_fill_shaders(self, value: bool) -> None:
        self._set_boolean("use_projection_fill_shaders", value)

    @property
    def use_projection_stroke_shaders(self) -> bool:
        """Use shaders for OpenGLVMobject stroke which are compatible with transformation matrices."""
        return self._d["use_projection_stroke_shaders"]

    @use_projection_stroke_shaders.setter
    def use_projection_stroke_shaders(self, value: bool) -> None:
        self._set_boolean("use_projection_stroke_shaders", value)

    @property
    def zero_pad(self) -> int:
        """PNG zero padding. A number between 0 (no zero padding) and 9 (9 columns minimum)."""
        return self._d["zero_pad"]

    @zero_pad.setter
    def zero_pad(self, value: int) -> None:
        self._set_int_between("zero_pad", value, 0, 9)

    def get_dir(self, key: str, **kwargs: Any) -> Path:
        """Resolve a config option that stores a directory.

        Config options that store directories may depend on one another.  This
        method is used to provide the actual directory to the end user.

        Parameters
        ----------
        key
            The config option to be resolved.  Must be an option ending in
            ``'_dir'``, for example ``'media_dir'`` or ``'video_dir'``.

        kwargs
            Any strings to be used when resolving the directory.

        Returns
        -------
        :class:`pathlib.Path`
            Path to the requested directory.  If the path resolves to the empty
            string, return ``None`` instead.

        Raises
        ------
        :class:`KeyError`
            When ``key`` is not a config option that stores a directory and
            thus :meth:`~ManimConfig.get_dir` is not appropriate; or when
            ``key`` is appropriate but there is not enough information to
            resolve the directory.

        Notes
        -----
        Standard :meth:`str.format` syntax is used to resolve the paths so the
        paths may contain arbitrary placeholders using f-string notation.
        However, these will require ``kwargs`` to contain the required values.

        Examples
        --------

        The value of ``config.tex_dir`` is ``'{media_dir}/Tex'`` by default,
        i.e. it is a subfolder of wherever ``config.media_dir`` is located.  In
        order to get the *actual* directory, use :meth:`~ManimConfig.get_dir`.

        .. code-block:: pycon

            >>> from manim import config as globalconfig
            >>> config = globalconfig.copy()
            >>> config.tex_dir
            '{media_dir}/Tex'
            >>> config.media_dir
            './media'
            >>> config.get_dir("tex_dir").as_posix()
            'media/Tex'

        Resolving directories is done in a lazy way, at the last possible
        moment, to reflect any changes in other config options:

        .. code-block:: pycon

            >>> config.media_dir = "my_media_dir"
            >>> config.get_dir("tex_dir").as_posix()
            'my_media_dir/Tex'

        Some directories depend on information that is not available to
        :class:`ManimConfig`. For example, the default value of `video_dir`
        includes the name of the input file and the video quality
        (e.g. 480p15). This informamtion has to be supplied via ``kwargs``:

        .. code-block:: pycon

            >>> config.video_dir
            '{media_dir}/videos/{module_name}/{quality}'
            >>> config.get_dir("video_dir")
            Traceback (most recent call last):
            KeyError: 'video_dir {media_dir}/videos/{module_name}/{quality} requires the following keyword arguments: module_name'
            >>> config.get_dir("video_dir", module_name="myfile").as_posix()
            'my_media_dir/videos/myfile/1080p60'

        Note the quality does not need to be passed as keyword argument since
        :class:`ManimConfig` does store information about quality.

        Directories may be recursively defined.  For example, the config option
        ``partial_movie_dir`` depends on ``video_dir``, which in turn depends
        on ``media_dir``:

        .. code-block:: pycon

            >>> config.partial_movie_dir
            '{video_dir}/partial_movie_files/{scene_name}'
            >>> config.get_dir("partial_movie_dir")
            Traceback (most recent call last):
            KeyError: 'partial_movie_dir {video_dir}/partial_movie_files/{scene_name} requires the following keyword arguments: scene_name'
            >>> config.get_dir(
            ...     "partial_movie_dir", module_name="myfile", scene_name="myscene"
            ... ).as_posix()
            'my_media_dir/videos/myfile/1080p60/partial_movie_files/myscene'

        Standard f-string syntax is used.  Arbitrary names can be used when
        defining directories, as long as the corresponding values are passed to
        :meth:`ManimConfig.get_dir` via ``kwargs``.

        .. code-block:: pycon

            >>> config.media_dir = "{dir1}/{dir2}"
            >>> config.get_dir("media_dir")
            Traceback (most recent call last):
            KeyError: 'media_dir {dir1}/{dir2} requires the following keyword arguments: dir1'
            >>> config.get_dir("media_dir", dir1="foo", dir2="bar").as_posix()
            'foo/bar'
            >>> config.media_dir = "./media"
            >>> config.get_dir("media_dir").as_posix()
            'media'

        """
        dirs = [
            "assets_dir",
            "media_dir",
            "video_dir",
            "sections_dir",
            "images_dir",
            "text_dir",
            "tex_dir",
            "log_dir",
            "input_file",
            "output_file",
            "partial_movie_dir",
        ]
        if key not in dirs:
            raise KeyError(
                "must pass one of "
                "{media,video,images,text,tex,log}_dir "
                "or {input,output}_file",
            )

        dirs.remove(key)  # a path cannot contain itself

        all_args = {k: self._d[k] for k in dirs}
        all_args.update(kwargs)
        all_args["quality"] = f"{self.pixel_height}p{self.frame_rate:g}"

        path = self._d[key]
        while "{" in path:
            try:
                path = path.format(**all_args)
            except KeyError as exc:
                raise KeyError(
                    f"{key} {self._d[key]} requires the following "
                    + "keyword arguments: "
                    + " ".join(exc.args),
                ) from exc
        return Path(path) if path else None

    def _set_dir(self, key: str, val: str | Path) -> None:
        if isinstance(val, Path):
            self._d.__setitem__(key, str(val))
        else:
            self._d.__setitem__(key, val)

    @property
    def assets_dir(self) -> str:
        """Directory to locate video assets (no flag)."""
        return self._d["assets_dir"]

    @assets_dir.setter
    def assets_dir(self, value: str | Path) -> None:
        self._set_dir("assets_dir", value)

    @property
    def log_dir(self) -> str:
        """Directory to place logs. See :meth:`ManimConfig.get_dir`."""
        return self._d["log_dir"]

    @log_dir.setter
    def log_dir(self, value: str | Path) -> None:
        self._set_dir("log_dir", value)

    @property
    def video_dir(self) -> str:
        """Directory to place videos (no flag). See :meth:`ManimConfig.get_dir`."""
        return self._d["video_dir"]

    @video_dir.setter
    def video_dir(self, value: str | Path) -> None:
        self._set_dir("video_dir", value)

    @property
    def sections_dir(self) -> str:
        """Directory to place section videos (no flag). See :meth:`ManimConfig.get_dir`."""
        return self._d["sections_dir"]

    @sections_dir.setter
    def sections_dir(self, value: str | Path) -> None:
        self._set_dir("sections_dir", value)

    @property
    def images_dir(self) -> str:
        """Directory to place images (no flag).  See :meth:`ManimConfig.get_dir`."""
        return self._d["images_dir"]

    @images_dir.setter
    def images_dir(self, value: str | Path) -> None:
        self._set_dir("images_dir", value)

    @property
    def text_dir(self) -> str:
        """Directory to place text (no flag).  See :meth:`ManimConfig.get_dir`."""
        return self._d["text_dir"]

    @text_dir.setter
    def text_dir(self, value: str | Path) -> None:
        self._set_dir("text_dir", value)

    @property
    def tex_dir(self) -> str:
        """Directory to place tex (no flag).  See :meth:`ManimConfig.get_dir`."""
        return self._d["tex_dir"]

    @tex_dir.setter
    def tex_dir(self, value: str | Path) -> None:
        self._set_dir("tex_dir", value)

    @property
    def partial_movie_dir(self) -> str:
        """Directory to place partial movie files (no flag).  See :meth:`ManimConfig.get_dir`."""
        return self._d["partial_movie_dir"]

    @partial_movie_dir.setter
    def partial_movie_dir(self, value: str | Path) -> None:
        self._set_dir("partial_movie_dir", value)

    @property
    def custom_folders(self) -> str:
        """Whether to use custom folder output."""
        return self._d["custom_folders"]

    @custom_folders.setter
    def custom_folders(self, value: str | Path) -> None:
        self._set_dir("custom_folders", value)

    @property
    def input_file(self) -> str:
        """Input file name."""
        return self._d["input_file"]

    @input_file.setter
    def input_file(self, value: str | Path) -> None:
        self._set_dir("input_file", value)

    @property
    def output_file(self) -> str:
        """Output file name (-o)."""
        return self._d["output_file"]

    @output_file.setter
    def output_file(self, value: str | Path) -> None:
        self._set_dir("output_file", value)

    @property
    def scene_names(self) -> list[str]:
        """Scenes to play from file."""
        return self._d["scene_names"]

    @scene_names.setter
    def scene_names(self, value: list[str]) -> None:
        self._d.__setitem__("scene_names", value)

    @property
    def tex_template(self) -> TexTemplate:
        """Template used when rendering Tex.  See :class:`.TexTemplate`."""
        if not hasattr(self, "_tex_template") or not self._tex_template:
            fn = self._d["tex_template_file"]
            if fn:
                self._tex_template = TexTemplate.from_file(fn)
            else:
                self._tex_template = TexTemplate()
        return self._tex_template

    @tex_template.setter
    def tex_template(self, val: TexTemplate) -> None:
        if isinstance(val, TexTemplate):
            self._tex_template = val

    @property
    def tex_template_file(self) -> Path:
        """File to read Tex template from (no flag).  See :class:`.TexTemplate`."""
        return self._d["tex_template_file"]

    @tex_template_file.setter
    def tex_template_file(self, val: str) -> None:
        if val:
            if not os.access(val, os.R_OK):
                logging.getLogger("manim").warning(
                    f"Custom TeX template {val} not found or not readable.",
                )
            else:
                self._d["tex_template_file"] = Path(val)
        else:
            self._d["tex_template_file"] = val  # actually set the falsy value

    @property
    def plugins(self) -> list[str]:
        """List of plugins to enable."""
        return self._d["plugins"]

    @plugins.setter
    def plugins(self, value: list[str]):
        self._d["plugins"] = value


# TODO: to be used in the future - see PR #620
# https://github.com/ManimCommunity/manim/pull/620
class ManimFrame(Mapping):
    _OPTS: ClassVar[set[str]] = {
        "pixel_width",
        "pixel_height",
        "aspect_ratio",
        "frame_height",
        "frame_width",
        "frame_y_radius",
        "frame_x_radius",
        "top",
        "bottom",
        "left_side",
        "right_side",
    }
    _CONSTANTS: ClassVar[dict[str, Vector3D]] = {
        "UP": np.array((0.0, 1.0, 0.0)),
        "DOWN": np.array((0.0, -1.0, 0.0)),
        "RIGHT": np.array((1.0, 0.0, 0.0)),
        "LEFT": np.array((-1.0, 0.0, 0.0)),
        "IN": np.array((0.0, 0.0, -1.0)),
        "OUT": np.array((0.0, 0.0, 1.0)),
        "ORIGIN": np.array((0.0, 0.0, 0.0)),
        "X_AXIS": np.array((1.0, 0.0, 0.0)),
        "Y_AXIS": np.array((0.0, 1.0, 0.0)),
        "Z_AXIS": np.array((0.0, 0.0, 1.0)),
        "UL": np.array((-1.0, 1.0, 0.0)),
        "UR": np.array((1.0, 1.0, 0.0)),
        "DL": np.array((-1.0, -1.0, 0.0)),
        "DR": np.array((1.0, -1.0, 0.0)),
    }

    _c: ManimConfig

    def __init__(self, c: ManimConfig) -> None:
        if not isinstance(c, ManimConfig):
            raise TypeError("argument must be instance of 'ManimConfig'")
        # need to use __dict__ directly because setting attributes is not
        # allowed (see __setattr__)
        self.__dict__["_c"] = c

    # there are required by parent class Mapping to behave like a dict
    def __getitem__(self, key: str | int) -> Any:
        if key in self._OPTS:
            return self._c[key]
        elif key in self._CONSTANTS:
            return self._CONSTANTS[key]
        else:
            raise KeyError(key)

    def __iter__(self) -> Iterable[str]:
        return iter(list(self._OPTS) + list(self._CONSTANTS))

    def __len__(self) -> int:
        return len(self._OPTS)

    # make this truly immutable
    def __setattr__(self, attr: Any, val: Any) -> NoReturn:
        raise TypeError("'ManimFrame' object does not support item assignment")

    def __setitem__(self, key: Any, val: Any) -> NoReturn:
        raise TypeError("'ManimFrame' object does not support item assignment")

    def __delitem__(self, key: Any) -> NoReturn:
        raise TypeError("'ManimFrame' object does not support item deletion")


for opt in list(ManimFrame._OPTS) + list(ManimFrame._CONSTANTS):
    setattr(ManimFrame, opt, property(lambda self, o=opt: self[o]))


# Extracted from /Users/hochmax/learn/manim/docs/source/changelog/0.1.0-changelog.rst
******
v0.1.0
******

:Date: October 21, 2020

This is the first release of manimce after forking from 3b1b/manim.  As such,
developers have focused on cleaning up and refactoring the codebase while still
maintaining backwards compatibility wherever possible.


New Features
============

Command line
------------

#. Output of 'manim --help' has been improved
#. Implement logging with the :code:`rich` library and a :code:`logger` object instead of plain ol' prints
#. Added a flag :code:`--dry_run`, which doesn't write any media
#. Allow for running manim with :code:`python3 -m manim`
#. Refactored Tex Template management. You can now use custom templates with command line args using :code:`--tex_template`!
#. Re-add :code:`--save_frames` flag, which will save each frame as a png
#. Re-introduce manim feature that allows you to type manim code in :code:`stdin` if you pass a minus sign :code:`(-)` as filename
#. Added the :code:`--custom_folders` flag which yields a simpler output folder structure
#. Re-implement GIF export with the :code:`-i` flag (using this flag outputs ONLY a .gif file, and no .mp4 file)
#. Added a :code:`--verbose` flag
#. You can save the logs to a file by using :code:`--log_to_file`
#. Read :code:`tex_template` from config file if not specified by :code:`--tex_template`.
#. Add experimental javascript rendering with :code:`--use_js_renderer`
#. Add :code:`-q/--quality [k|p|h|m|l]` flag and removed :code:`-m/-l` flags.
#. Removed :code:`--sound` flag


Config system
-------------

#. Implement a :code:`manim.cfg` config file system, that consolidates the global configuration, the command line argument parsing, and some of the constants defined in :code:`constants.py`
#. Added utilities for manipulating Manim’s :code:`.cfg` files.
#. Added a subcommand structure for easier use of utilities managing :code:`.cfg` files
#. Also some variables have been moved from ``constants.py`` to the new config system:

    #. ``FRAME_HEIGHT`` to ``config["frame_width"]``
    #. ``TOP`` to ``config["frame_height"] / 2 * UP``
    #. ``BOTTOM`` to ``config["frame_height"] / 2 * DOWN``
    #. ``LEFT_SIDE`` to ``config["frame_width"] / 2 * LEFT``
    #. ``RIGHT_SIDE`` to ``config["frame_width"] / 2 * RIGHT``
    #. ``self.camera.frame_rate`` to ``config["frame_rate"]``




Mobjects, Scenes, and Animations
--------------------------------

#. Add customizable left and right bracket for :code:`Matrix` mobject and :code:`set_row_colors` method for matrix mobject
#. Add :code:`AddTeXLetterByLetter` animation
#. Enhanced GraphScene

    #. You can now add arrow tips to axes
    #. extend axes a bit at the start and/or end
    #. have invisible axes
    #. highlight the area between two curves
#. ThreeDScene now supports 3dillusion_camera_rotation
#. Add :code:`z_index` for manipulating depth of Objects on scene.
#. Add a :code:`VDict` class: a :code:`VDict` is to a :code:`VGroup` what a :code:`dict` is to a :code:`list`
#. Added Scene-caching feature. Now, if a partial movie file is unchanged in your code, it isn’t rendered again! [HIGHLY UNSTABLE We're working on it ;)]
#. Most :code:`get_` and :code:`set_` methods have been removed in favor of instance attributes and properties
#. The :code:`Container` class has been made into an AbstractBaseClass, i.e. in cannot be instantiated.  Instead, use one of its children classes
#. The ``TextMobject`` and ``TexMobject`` objects have been deprecated, due to their confusing names, in favour of ``Tex`` and ``MathTex``. You can still, however, continue to use ``TextMobject`` and ``TexMobject``, albeit with Deprecation Warnings constantly reminding you to switch.
#. Add a :code:`Variable` class for displaying text that continuously updates to reflect the value of a python variable.
#. The ``Tex`` and ``MathTex`` objects allow you to specify a custom TexTemplate using the ``template`` keyword argument.
#. :code:`VGroup` now supports printing the class names of contained mobjects and :code:`VDict` supports printing the internal dict of mobjects
#. Add all the standard easing functions
#. :code:`Scene` now renders when :code:`Scene.render()` is called rather than upon instantiation.
#. :code:`ValueTracker` now supports increment using the `+=` operator (in addition to the already existing `increment_value` method)
#. Add :class:`PangoText` for rendering texts using Pango.


Documentation
=============

#. Added clearer installation instructions, tutorials, examples, and API reference [WIP]


Fixes
=====

#. Initialization of directories has been moved to :code:`config.py`, and a bunch of bugs associated to file structure generation have been fixed
#. Nonfunctional file :code:`media_dir.txt` has been removed
#. Nonfunctional :code:`if` statements in :code:`scene_file_writer.py` have been removed
#. Fix a bug where trying to render the example scenes without specifying the scene would show all scene objects in the library
#. Many :code:`Exceptions` have been replaced for more specific exception subclasses
#. Fixed a couple of subtle bugs in :code:`ArcBetweenPoints`


Of interest to developers
=========================

#. Python code formatting is now enforced by using the :code:`black` tool
#. PRs now require two approving code reviews from community devs before they can be merged
#. Added tests to ensure stuff doesn't break between commits (For developers) [Uses Github CI, and Pytest]
#. Add contribution guidelines (for developers)
#. Added autogenerated documentation with sphinx and autodoc/autosummary [WIP]
#. Made manim internally use relative imports
#. Since the introduction of the :code:`TexTemplate` class, the files :code:`tex_template.tex` and :code:`ctex_template.tex` have been removed
#. Added logging tests tools.
#. Added ability to save logs in json
#. Move to Poetry.
#. Colors have moved to an Enum

Other Changes
=============

#. Cleanup 3b1b Specific Files
#. Rename package from manimlib to manim
#. Move all imports to :code:`__init__`, so :code:`from manim import *` replaces :code:`from manimlib.imports import *`
#. Global dir variable handling has been removed. Instead :code:`initialize_directories`, if needed, overrides the values from the cfg files at runtime.


# Extracted from /Users/hochmax/learn/manim/docs/source/contributing/testing.rst
============
Adding Tests
============
If you are adding new features to manim, you should add appropriate tests for them. Tests prevent
manim from breaking at each change by checking that no other
feature has been broken and/or been unintentionally modified.

.. warning::

   The full tests suite requires Cairo 1.18 in order to run all tests.
   However, Cairo 1.18 may not be available from your package manager,
   like ``apt``, and it is very likely that you have an older version installed,
   e.g., 1.16. If you run tests with a version prior to 1.18,
   many tests will be skipped. Those tests are not skipped in the online CI.

   If you want to run all tests locally, you need to install Cairo 1.18 or above.
   You can do so by compiling Cairo from source:

   1. download ``cairo-1.18.0.tar.xz`` from
      `here <https://www.cairographics.org/releases/>`_.
      and uncompress it;
   2. open the INSTALL file and follow the instructions (you might need to install
      ``meson`` and ``ninja``);
   3. run the tests suite and verify that the Cairo version is correct.

How Manim tests
---------------

Manim uses pytest as its testing framework.
To start the testing process, go to the root directory of the project and run pytest in your terminal.
Any errors that occur during testing will be displayed in the terminal.

Some useful pytest flags:

- ``-x`` will make pytest stop at the first failure it encounters

- ``-s`` will make pytest display all the print messages (including those during scene generation, like DEBUG messages)

- ``--skip_slow`` will skip the (arbitrarily) slow tests

- ``--show_diff`` will show a visual comparison in case a unit test is failing.


How it Works
~~~~~~~~~~~~

At the moment there are three types of tests:

#. Unit Tests:

   Tests for most of the basic functionalities of manim. For example, there a test for
   ``Mobject``, that checks if it can be added to a Scene, etc.

#. Graphical unit tests:
   Because ``manim`` is a graphics library, we test frames. To do so, we create test scenes that render a specific feature.
   When pytest runs, it compares the result of the test to the control data, either at 6 fps or just the last frame. If it matches, the tests
   pass. If the test and control data differ, the tests fail. You can use ``--show_diff`` flag with ``pytest`` to visually
   see the differences. The ``extract_frames.py`` script lets you see all the frames of a test.

#. Videos format tests:

   As Manim is a video library, we have to test videos as well. Unfortunately,
   we cannot directly test video content as rendered videos can
   differ slightly depending on the system (for reasons related to
   ffmpeg). Therefore, we only compare video configuration values, exported in
   .json.

Architecture
------------

The ``manim/tests`` directory looks like this:

::

    .
    ├── conftest.py
    ├── control_data
    │   ├── graphical_units_data
    │   │   ├── creation
    │   │   │   ├── DrawBorderThenFillTest.npy
    │   │   │   ├── FadeInFromDownTest.npy
    │   │   │   ├── FadeInFromLargeTest.npy
    │   │   │   ├── FadeInFromTest.npy
    │   │   │   ├── FadeInTest.npy
    │   │   │   ├── ...
    │   │   ├── geometry
    │   │   │   ├── AnnularSectorTest.npy
    │   │   │   ├── AnnulusTest.npy
    │   │   │   ├── ArcBetweenPointsTest.npy
    │   │   │   ├── ArcTest.npy
    │   │   │   ├── CircleTest.npy
    │   │   │   ├── CoordinatesTest.npy
    │   │   │   ├── ...
    │   │   ├── graph
    │   │   │   ├── ...
    |   |   |   | ...
    │   └── videos_data
    │       ├── SquareToCircleWithDefaultValues.json
    │       └── SquareToCircleWithlFlag.json
    ├── helpers
    │   ├── graphical_units.py
    │   ├── __init__.py
    │   └── video_utils.py
    ├── __init__.py
    ├── test_camera.py
    ├── test_config.py
    ├── test_copy.py
    ├── test_vectorized_mobject.py
    ├── test_graphical_units
    │   ├── conftest.py
    │   ├── __init__.py
    │   ├── test_creation.py
    │   ├── test_geometry.py
    │   ├── test_graph.py
    │   ├── test_indication.py
    │   ├── test_movements.py
    │   ├── test_threed.py
    │   ├── test_transform.py
    │   └── test_updaters.py
    ├── test_logging
    │   ├── basic_scenes.py
    │   ├── expected.txt
    │   ├── testloggingconfig.cfg
    │   └── test_logging.py
    ├── test_scene_rendering
    │   ├── conftest.py
    │   ├── __init__.py
    │   ├── simple_scenes.py
    │   ├── standard_config.cfg
    │   └── test_cli_flags.py
    └── utils
        ├── commands.py
        ├── __init__.py
        ├── testing_utils.py
        └── video_tester.py
       ...

The Main Directories
--------------------

- ``control_data/``:

  The directory containing control data. ``control_data/graphical_units_data/`` contains the expected and correct frame data for graphical tests, and
  ``control_data/videos_data/`` contains the .json files used to check videos.

- ``test_graphical_units/``:

  Contains graphical tests.

- ``test_scene_rendering/``:

  For tests that need to render a scene in some way, such as tests for CLI
  flags (end-to-end tests).

- ``utils/``:

  Useful internal functions used by pytest.

  .. note:: fixtures are not contained here, they are in ``conftest.py``.

- ``helpers/``:

  Helper functions for developers to setup graphical/video tests.

Adding a New Test
-----------------

Unit Tests
~~~~~~~~~~

Pytest determines which functions are tests by searching for files whose
names begin with "test\_", and then within those files for functions
beginning with "test" and classes beginning with "Test". These kinds of
tests must be in ``tests/`` (e.g. ``tests/test_container.py``).

Graphical Unit Test
~~~~~~~~~~~~~~~~~~~

The test must be written in the correct file (i.e. the file that corresponds to the appropriate category the feature belongs to) and follow the structure
of unit tests.

For example, to test the ``Circle`` VMobject which resides in
``manim/mobject/geometry.py``, add the CircleTest to
``test/test_geometry.py``.

The name of the module is indicated by the variable __module_test__, that **must** be declared in any graphical test file. The module name is used to store the graphical control data.

.. important::
    You will need to use the ``frames_comparison`` decorator to create a test. The test function **must** accept a
    parameter named ``scene`` that will be used like ``self`` in a standard ``construct`` method.

Here's an example in ``test_geometry.py``:

.. code:: python

  from manim import *
  from manim.utils.testing.frames_comparison import frames_comparison

  __module_test__ = "geometry"


  @frames_comparison
  def test_circle(scene):
      circle = Circle()
      scene.play(Animation(circle))

The decorator can be used with or without parentheses. **By default, the test only tests the last frame. To enable multi-frame testing, you have to set ``last_frame=False`` in the parameters.**

.. code:: python

  @frames_comparison(last_frame=False)
  def test_circle(scene):
      circle = Circle()
      scene.play(Animation(circle))

You can also specify, when needed, which base scene you need (ThreeDScene, for example) :

.. code:: python

  @frames_comparison(last_frame=False, base_scene=ThreeDScene)
  def test_circle(scene):
      circle = Circle()
      scene.play(Animation(circle))

Feel free to check the documentation of ``@frames_comparison`` for more.

Note that tests name must follow the syntax ``test_<thing_to_test>``, otherwise pytest will not recognize it as a test.

.. warning::
  If you run pytest now, you will get a ``FileNotFound`` error. This is because
  you have not created control data for your test.

To create the control data for your test, you have to use the flag ``--set_test`` along with pytest.
For the example above, it would be

.. code-block:: bash

    pytest test_geometry.py::test_circle --set_test -s

(``-s`` is here to see manim logs, so you can see what's going on).

If you want to see all the control data frames (e.g. to make sure your test is doing what you want), use the
``extract_frames.py`` script. The first parameter is the path to a ``.npz`` file and the second parameter is the
directory you want the frames created. The frames will be named ``frame0.png``, ``frame1.png``, etc.

.. code-block:: bash

    python scripts/extract_frames.py tests/test_graphical_units/control_data/plot/axes.npz output


Please make sure to add the control data to git as soon as it is produced with ``git add <your-control-data.npz>``.


Videos tests
~~~~~~~~~~~~

To test videos generated, we use the decorator
``tests.utils.videos_tester.video_comparison``:

.. code:: python

    @video_comparison(
        "SquareToCircleWithlFlag.json", "videos/simple_scenes/480p15/SquareToCircle.mp4"
    )
    def test_basic_scene_l_flag(tmp_path, manim_cfg_file, simple_scenes_path):
        scene_name = "SquareToCircle"
        command = [
            "python",
            "-m",
            "manim",
            simple_scenes_path,
            scene_name,
            "-l",
            "--media_dir",
            str(tmp_path),
        ]
        out, err, exit_code = capture(command)
        assert exit_code == 0, err

.. note:: ``assert exit*\ code == 0, err`` is used in case of the command fails
  to run. The decorator takes two arguments: json name and the path
  to where the video should be generated, starting from the ``media/`` dir.

Note the fixtures here:

- tmp_path is a pytest fixture to get a tmp_path. Manim will output here, according to the flag ``--media_dir``.

- ``manim_cfg_file`` fixture that return a path pointing to ``test_scene_rendering/standard_config.cfg``. It's just to shorten the code, in the case multiple tests need to use this cfg file.

- ``simple_scenes_path`` same as above, except for ``test_scene_rendering/simple_scene.py``

You have to generate a ``.json`` file first to be able to test your video. To
do that, use ``helpers.save_control_data_from_video``.

For instance, a test that will check if the l flag works properly will first
require rendering a video using the -l flag from a scene. Then we will test
(in this case, SquareToCircle), that lives in
``test_scene_rendering/simple_scene.py``. Change directories to ``tests/``,
create a file (e.g. ``create\_data.py``) that you will remove as soon as
you're done. Then run:

.. code:: python

    save_control_data_from_video("<path-to-video>", "SquareToCircleWithlFlag.json")

Running this will save
``control_data/videos_data/SquareToCircleWithlFlag.json``, which will
look like this:

.. code:: json

    {
        "name": "SquareToCircleWithlFlag",
        "config": {
            "codec_name": "h264",
            "width": 854,
            "height": 480,
            "avg_frame_rate": "15/1",
            "duration": "1.000000",
            "nb_frames": "15"
        }
    }

If you have any questions, please don't hesitate to ask on `Discord
<https://www.manim.community/discord/>`_, in your pull request, or in an issue.


# Extracted from /Users/hochmax/learn/manim/docs/source/contributing/performance.rst
=====================
Improving performance
=====================

One of Manim's main flaws as an animation library is its slow performance.
As of time of writing (January 2022), the library is still very unoptimized.
As such, we highly encourage contributors to help out in optimizing the code.

Profiling
=========

Before the library can be optimized, we first need to identify the bottlenecks
in performance via profiling. There are numerous Python profilers available for
this purpose; some examples include cProfile and Scalene.

Running an animation as a script
--------------------------------

Most instructions for profilers assume you can run the python file directly as a
script from the command line. While Manim animations are usually run from the
command-line, we can run them as scripts by adding something like the following
to the bottom of the file:

.. code-block:: python

    with tempconfig({"quality": "medium_quality", "disable_caching": True}):
        scene = SceneName()
        scene.render()

Where ``SceneName`` is the name of the scene you want to run. You can then run the
file directly, and can thus follow the instructions for most profilers.

An example: profiling with cProfile and SnakeViz
-------------------------------------------------

Install SnakeViz:

.. code-block:: bash

    pip install snakeviz

cProfile is included with in Python's standard library and does not need to be installed.

Suppose we want to profile ``SquareToCircle``. Then we add and save the following code
to ``square_to_circle.py``:

.. code-block:: python

    from manim import *


    class SquareToCircle(Scene):
        def construct(self):
            s = Square()
            c = Circle()
            self.add(s)
            self.play(Transform(s, c))


    with tempconfig({"quality": "medium_quality", "disable_caching": True}):
        scene = SquareToCircle()
        scene.render()

Now run the following in the terminal:

.. code-block:: bash

   python -m cProfile -o square_to_circle.txt square_to_circle.py

This will create a file called ``square_to_circle.txt``.

Now, we can run SnakeViz on the profile file:

.. code-block:: bash

   snakeviz square_to_circle.txt

A browser window or tab will open with a visualization of the profile, which should
look something like this:

.. image:: /_static/snakeviz.png


# Extracted from /Users/hochmax/learn/manim/docs/source/contributing/docs/examples.rst
===============
Adding Examples
===============

This is a page for adding examples to the documentation.
Here are some guidelines you should follow before you publish your examples.

Guidelines for examples
-----------------------

Everybody is welcome to contribute examples to the documentation. Since straightforward
examples are a great resource for quickly learning manim, here are some guidelines.

What makes a great example
--------------------------

.. note::

   As soon as a new version of manim is released, the documentation will be a snapshot of that
   version. Examples contributed after the release will only be shown in the latest documentation.

* Examples should be ready to copy and paste for use.

* Examples should be brief yet still easy to understand.

* Examples don't require the ``from manim import *`` statement, this will be added automatically when the docs are built.

* There should be a balance of animated and non-animated examples.

- As manim makes animations, we can include lots of animated examples; however, our RTD has a maximum 20 minutes to build. Animated examples should only be used when necessary, as last frame examples render faster.

- Lots of examples (e.g. size of a plot-axis, setting opacities, making texts, etc.) will also work as images. It is a lot more convenient to see the end product immediately instead of waiting for an animation to reveal it.

* Please ensure the examples run on the current main branch when you contribute an example.

* If the functions used are confusing for people, make sure to add comments in the example to explain what they do.

How examples are structured
---------------------------

* Examples can be organized into chapters and subchapters.

- When you create examples, the beginning example chapter should focus on only one functionality. When the functionality is simple, multiple ideas can be illustrated under a single example.

- As soon as simple functionalities are explained, the chapter may include more complex examples which build on the simpler ideas.

Writing examples
~~~~~~~~~~~~~~~~

When you want to add/edit examples, they can be found in the ``docs/source/`` directory, or directly in the manim source code (e.g. ``manim/mobject/mobject.py``). The examples are written in
``rst`` format and use the manim directive (see :mod:`manim.utils.docbuild.manim_directive` ), ``.. manim::``. Every example is in its own block, and looks like this:

.. code:: rst

    Formulas
    ========

    .. manim:: Formula1
        :save_last_frame:

        class Formula1(Scene):
            def construct(self):
                t = MathTex(r"\int_a^b f'(x) dx = f(b) - f(a)")
                self.add(t)
                self.wait(1)

In the building process of the docs, all ``rst`` files are scanned, and the
manim directive (``.. manim::``) blocks are identified as scenes that will be run
by the current version of manim.
Here is the syntax:

* ``.. manim:: [SCENE_NAME]`` has no indentation and ``SCENE_NAME`` refers to the name of the class below.

* The flags are followed in the next line (no blank line here!), with the indentation level of one tab.

All possible flags can be found at :mod:`manim.utils.docbuild.manim_directive`.

In the example above, the ``Formula1`` following ``.. manim::`` is the scene
that the directive expects to render; thus, in the python code, the class
has the same name: ``class Formula1(Scene)``.

.. note::

   Sometimes, when you reload an example in your browser, it has still the old
   website somewhere in its cache. If this is the case, delete the website cache,
   or open a new incognito tab in your browser, then the latest docs
   should be shown.
   **Only for locally built documentation:** If this still doesn't work, you may need
   to delete the contents of ``docs/source/references`` before rebuilding
   the documentation.


# Extracted from /Users/hochmax/learn/manim/docs/source/installation/jupyter.rst
Jupyter Notebooks
=================


Binder
------

`Binder <https://mybinder.readthedocs.io/en/latest/>`__ is an online
platform that hosts shareable and customizable computing environments
in the form of Jupyter notebooks. Manim ships with a built-in ``%%manim``
Jupyter magic command which makes it easy to use in these notebooks.

To see an example for such an environment, visit our interactive
tutorial over at https://try.manim.community/.

It is relatively straightforward to prepare your own notebooks in
a way that allows them to be shared interactively via Binder as well:

#. First, prepare a directory containing one or multiple notebooks
   which you would like to share in an interactive environment. You
   can create these notebooks by using Jupyter notebooks with a
   local installation of Manim, or also by working in our pre-existing
   `interactive tutorial environment <https://try.manim.community/>`__.
#. In the same directory containing your notebooks, add a
   file named ``Dockerfile`` with the following content:

   .. code-block:: dockerfile

      FROM docker.io/manimcommunity/manim:v0.9.0

      COPY --chown=manimuser:manimuser . /manim

   Don't forget to change the version tag ``v0.9.0`` to the version you
   were working with locally when creating your notebooks.
#. Make the directory with your worksheets and the ``Dockerfile``
   available to the public (and in particular: to Binder!). There are
   `several different options to do so
   <https://mybinder.readthedocs.io/en/latest/introduction.html#how-can-i-prepare-a-repository-for-binder>`__,
   within the community we usually work with GitHub
   repositories or gists.
#. Once your material is publicly available, visit
   https://mybinder.org and follow the instructions there to
   generate an interactive environment for your worksheets.

.. hint::

   The repository containing our `interactive tutorial
   <https://try.manim.community>`__ can be found at
   https://github.com/ManimCommunity/jupyter_examples.


Google Colaboratory
-------------------

It is also possible to install Manim in a
`Google Colaboratory <https://colab.research.google.com/>`__ environment.
In contrast to Binder, where you can customize and prepare the environment
beforehand (such that Manim is already installed and ready to be used), you
will have to take care of that every time you start
a new notebook in Google Colab. Fortunately, this
is not particularly difficult.

After creating a new notebook, paste the following code block in a cell,
then execute it.

.. code-block::

   !sudo apt update
   !sudo apt install libcairo2-dev \
       texlive texlive-latex-extra texlive-fonts-extra \
       texlive-latex-recommended texlive-science \
       tipa libpango1.0-dev
   !pip install manim
   !pip install IPython==8.21.0

You should start to see Colab installing all the dependencies specified
in these commands. After the execution has completed, you will be prompted
to restart the runtime. Click the "restart runtime" button at the bottom of
the cell output. You are now ready to use Manim in Colab!

To check that everything works as expected, first import Manim by running

.. code-block::

   from manim import *

in a new code cell. Then create another cell containing the
following code::

   %%manim -qm -v WARNING SquareToCircle

   class SquareToCircle(Scene):
      def construct(self):
         square = Square()
         circle = Circle()
         circle.set_fill(PINK, opacity=0.5)
         self.play(Create(square))
         self.play(Transform(square, circle))
         self.wait()

Upon running this cell, a short animation transforming a square
into a circle should be rendered and displayed.


# Extracted from /Users/hochmax/learn/manim/docs/source/guides/add_voiceovers.rst
###########################
Adding Voiceovers to Videos
###########################

Creating a full-fledged video with voiceovers is a bit more involved than
creating purely visual Manim scenes. One has to use `a video editing
program <https://en.wikipedia.org/wiki/List_of_video_editing_software>`__
to add the voiceovers after the video has been rendered. This process
can be difficult and time-consuming, since it requires a lot of planning
and preparation.

To ease the process of adding voiceovers to videos, we have created
`Manim Voiceover <https://voiceover.manim.community>`__, a plugin
that lets you add voiceovers to scenes directly in Python. To install it, run

.. code-block:: bash

    pip install "manim-voiceover[azure,gtts]"

Visit `the installation page <https://voiceover.manim.community/en/latest/installation.html>`__
for more details on how to install Manim Voiceover.

Basic Usage
###########

Manim Voiceover lets you ...

- Add voiceovers to Manim videos directly in Python, without having to use a video editor.
- Record voiceovers with your microphone during rendering through a simple command line interface.
- Develop animations with auto-generated AI voices from various free and proprietary services.

It provides a very simple API that lets you specify your voiceover script
and then record it during rendering:

.. code-block:: python

    from manim import *
    from manim_voiceover import VoiceoverScene
    from manim_voiceover.services.recorder import RecorderService


    # Simply inherit from VoiceoverScene instead of Scene to get all the
    # voiceover functionality.
    class RecorderExample(VoiceoverScene):
        def construct(self):
            # You can choose from a multitude of TTS services,
            # or in this example, record your own voice:
            self.set_speech_service(RecorderService())

            circle = Circle()

            # Surround animation sections with with-statements:
            with self.voiceover(text="This circle is drawn as I speak.") as tracker:
                self.play(Create(circle), run_time=tracker.duration)
                # The duration of the animation is received from the audio file
                # and passed to the tracker automatically.

            # This part will not start playing until the previous voiceover is finished.
            with self.voiceover(text="Let's shift it to the left 2 units.") as tracker:
                self.play(circle.animate.shift(2 * LEFT), run_time=tracker.duration)

To get started with Manim Voiceover,
visit the `Quick Start Guide <https://voiceover.manim.community/en/latest/quickstart.html>`__.

Visit the `Example Gallery <https://voiceover.manim.community/en/latest/examples.html>`__
to see some examples of Manim Voiceover in action.


# Extracted from /Users/hochmax/learn/manim/docs/source/guides/configuration.rst
Configuration
#############

Manim provides an extensive configuration system that allows it to adapt to
many different use cases.  There are many configuration options that can be
configured at different times during the scene rendering process.  Each option
can be configured programmatically via `the ManimConfig class`_, at the time
of command invocation via `command-line arguments`_, or at the time the library
is first imported via `the config files`_.

The most common, simplest, and recommended way to configure Manim is
via the command-line interface (CLI), which is described directly below.

Command-line arguments
**********************

By far the most commonly used command in the CLI is the ``render`` command,
which is used to render scene(s) to an output file.
It is used with the following arguments:

.. program-output:: manim render --help
   :ellipsis: 9

However, since Manim defaults to the :code:`render` command whenever no command
is specified, the following form is far more common and can be used instead:

.. code-block:: bash

   manim [OPTIONS] FILE [SCENES]

An example of using the above form is:

.. code-block:: bash

   manim -qm file.py SceneOne

This asks Manim to search for a Scene class called :code:`SceneOne` inside the
file ``file.py`` and render it with medium quality (specified by the ``-qm`` flag).

Another frequently used flag is ``-p`` ("preview"), which makes manim
open the rendered video after it's done rendering.

.. note:: The ``-p`` flag does not change any properties of the global
          ``config`` dict.  The ``-p`` flag is only a command-line convenience.

Advanced examples
=================

To render a scene in high quality, but only output the last frame of the scene
instead of the whole video, you can execute

.. code-block:: bash

   manim -sqh <file.py> SceneName

The following example specifies the output file name (with the :code:`-o`
flag), renders only the first ten animations (:code:`-n` flag) with a white
background (:code:`-c` flag), and saves the animation as a ``.gif`` instead of as a
``.mp4`` file (``--format=gif`` flag).  It uses the default quality and does not try to
open the file after it is rendered.

.. code-block:: bash

   manim -o myscene --format=gif -n 0,10 -c WHITE <file.py> SceneName

A list of all CLI flags
========================

.. command-output:: manim --help
.. command-output:: manim render --help
.. command-output:: manim cfg --help
.. command-output:: manim plugins --help

The ManimConfig class
*********************

The most direct way of configuring Manim is through the global ``config`` object,
which is an instance of :class:`.ManimConfig`.  Each property of this class is
a config option that can be accessed either with standard attribute syntax or
with dict-like syntax:

.. code-block:: pycon

   >>> from manim import *
   >>> config.background_color = WHITE
   >>> config["background_color"] = WHITE

.. note:: The former is preferred; the latter is provided for backwards
          compatibility.

Most classes, including :class:`.Camera`, :class:`.Mobject`, and
:class:`.Animation`, read some of their default configuration from the global
``config``.

.. code-block:: pycon

   >>> Camera({}).background_color
   <Color white>
   >>> config.background_color = RED  # 0xfc6255
   >>> Camera({}).background_color
   <Color #fc6255>

:class:`.ManimConfig` is designed to keep internal consistency.  For example,
setting ``frame_y_radius`` will affect ``frame_height``:

.. code-block:: pycon

    >>> config.frame_height
    8.0
    >>> config.frame_y_radius = 5.0
    >>> config.frame_height
    10.0

The global ``config`` object is meant to be the single source of truth for all
config options.  All of the other ways of setting config options ultimately
change the values of the global ``config`` object.

The following example illustrates the video resolution chosen for examples
rendered in our documentation with a reference frame.

.. manim:: ShowScreenResolution
    :save_last_frame:

    class ShowScreenResolution(Scene):
        def construct(self):
            pixel_height = config["pixel_height"]  #  1080 is default
            pixel_width = config["pixel_width"]  # 1920 is default
            frame_width = config["frame_width"]
            frame_height = config["frame_height"]
            self.add(Dot())
            d1 = Line(frame_width * LEFT / 2, frame_width * RIGHT / 2).to_edge(DOWN)
            self.add(d1)
            self.add(Text(str(pixel_width)).next_to(d1, UP))
            d2 = Line(frame_height * UP / 2, frame_height * DOWN / 2).to_edge(LEFT)
            self.add(d2)
            self.add(Text(str(pixel_height)).next_to(d2, RIGHT))


The config files
****************

As the last example shows, executing Manim from the command line may involve
using many flags simultaneously.  This may become a nuisance if you must
execute the same script many times in a short time period, for example, when
making small incremental tweaks to your scene script.  For this reason, Manim
can also be configured using a configuration file.  A configuration file is a
file ending with the suffix ``.cfg``.

To use a local configuration file when rendering your scene, you must create a
file with the name ``manim.cfg`` in the same directory as your scene code.

.. warning:: The config file **must** be named ``manim.cfg``. Currently, Manim
             does not support config files with any other name.

The config file must start with the section header ``[CLI]``.  The
configuration options under this header have the same name as the CLI flags
and serve the same purpose.  Take, for example, the following config file.

.. code-block:: ini

   [CLI]
   # my config file
   output_file = myscene
   save_as_gif = True
   background_color = WHITE

Config files are parsed with the standard python library ``configparser``. In
particular, they will ignore any line that starts with a pound symbol ``#``.

Now, executing the following command

.. code-block:: bash

   manim -o myscene -i -c WHITE <file.py> SceneName

is equivalent to executing the following command, provided that ``manim.cfg``
is in the same directory as <file.py>,

.. code-block:: bash

   manim <file.py> SceneName

.. tip:: The names of the configuration options admissible in config files are
         exactly the same as the **long names** of the corresponding command-
         line flags.  For example, the ``-c`` and ``--background_color`` flags
         are interchangeable, but the config file only accepts
         :code:`background_color` as an admissible option.

Since config files are meant to replace CLI flags, all CLI flags can be set via
a config file.  Moreover, any config option can be set via a config file,
whether or not it has an associated CLI flag.  See the bottom of this document
for a list of all CLI flags and config options.

Manim will look for a ``manim.cfg`` config file in the same directory as the
file being rendered, and **not** in the directory of execution.  For example,

.. code-block:: bash

   manim -o myscene -i -c WHITE <path/to/file.py> SceneName

will use the config file found in ``path/to/file.py``, if any.  It will **not**
use the config file found in the current working directory, even if it exists.
In this way, the user may keep different config files for different scenes or
projects, and execute them with the right configuration from anywhere in the
system.

The file described here is called the **folder-wide** config file because it
affects all scene scripts found in the same folder.


The user config file
====================

As explained in the previous section, a :code:`manim.cfg` config file only
affects the scene scripts in its same folder.  However, the user may also
create a special config file that will apply to all scenes rendered by that
user. This is referred to as the **user-wide** config file, and it will apply
regardless of where Manim is executed from, and regardless of where the scene
script is stored.

The user-wide config file lives in a special folder, depending on the operating
system.

* Windows: :code:`UserDirectory`/AppData/Roaming/Manim/manim.cfg
* MacOS: :code:`UserDirectory`/.config/manim/manim.cfg
* Linux: :code:`UserDirectory`/.config/manim/manim.cfg

Here, :code:`UserDirectory` is the user's home folder.


.. note:: A user may have many **folder-wide** config files, one per folder,
          but only one **user-wide** config file.  Different users in the same
          computer may each have their own user-wide config file.

.. warning:: Do not store scene scripts in the same folder as the user-wide
             config file.  In this case, the behavior is undefined.

Whenever you use Manim from anywhere in the system, Manim will look for a
user-wide config file and read its configuration.


Cascading config files
======================

What happens if you execute Manim and it finds both a folder-wide config file
and a user-wide config file?  Manim will read both files, but if they are
incompatible, **the folder-wide file takes precedence**.

For example, take the following user-wide config file

.. code-block:: ini

   # user-wide
   [CLI]
   output_file = myscene
   save_as_gif = True
   background_color = WHITE

and the following folder-wide file

.. code-block:: ini

   # folder-wide
   [CLI]
   save_as_gif = False

Then, executing :code:`manim <file.py> SceneName` will be equivalent to not
using any config files and executing

.. code-block:: bash

   manim -o myscene -c WHITE <file.py> SceneName

Any command-line flags have precedence over any config file.  For example,
using the previous two config files and executing :code:`manim -c RED
<file.py> SceneName` is equivalent to not using any config files and
executing

.. code-block:: bash

   manim -o myscene -c RED <file.py> SceneName

There is also a **library-wide** config file that determines Manim's default
behavior and applies to every user of the library.  It has the least
precedence, so any config options in the user-wide and any folder-wide files
will override the library-wide file.  This is referred to as the *cascading*
config file system.

.. warning:: **The user should not try to modify the library-wide file**.
	     Contributors should receive explicit confirmation from the core
	     developer team before modifying it.


Order of operations
*******************

.. raw:: html

    <div class="mxgraph" style="max-width:100%;border:1px solid transparent;" data-mxgraph="{&quot;highlight&quot;:&quot;#0000ff&quot;,&quot;nav&quot;:true,&quot;resize&quot;:true,&quot;toolbar&quot;:&quot;zoom layers lightbox&quot;,&quot;edit&quot;:&quot;_blank&quot;,&quot;url&quot;:&quot;https://drive.google.com/uc?id=1WYVKKoRbXrumHEcyQKQ9s1yCnBvfU2Ui&amp;export=download&quot;}"></div>
    <script type="text/javascript" src="https://viewer.diagrams.net/embed2.js?&fetch=https%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1WYVKKoRbXrumHEcyQKQ9s1yCnBvfU2Ui%26export%3Ddownload"></script>



With so many different ways of configuring Manim, it can be difficult to know
when each config option is being set.  In fact, this will depend on how Manim
is being used.

If Manim is imported from a module, then the configuration system will follow
these steps:

1. The library-wide config file is loaded.
2. The user-wide and folder-wide files are loaded if they exist.
3. All files found in the previous two steps are parsed in a single
   :class:`ConfigParser` object, called ``parser``.  This is where *cascading*
   happens.
4. :class:`logging.Logger` is instantiated to create Manim's global ``logger``
   object. It is configured using the "logger" section of the parser,
   i.e. ``parser['logger']``.
5. :class:`ManimConfig` is instantiated to create the global ``config`` object.
6. The ``parser`` from step 3 is fed into the ``config`` from step 5 via
   :meth:`ManimConfig.digest_parser`.
7. Both ``logger`` and ``config`` are exposed to the user.

If Manim is being invoked from the command line, all of the previous steps
happen, and are complemented by:

8. The CLI flags are parsed and fed into ``config`` via
   :meth:`~ManimConfig.digest_args`.
9. If the ``--config_file`` flag was used, a new :class:`ConfigParser` object
   is created with the contents of the library-wide file, the user-wide file if
   it exists, and the file passed via ``--config_file``.  In this case, the
   folder-wide file, if it exists, is ignored.
10. The new parser is fed into ``config``.
11. The rest of the CLI flags are processed.

To summarize, the order of precedence for configuration options, from lowest to
highest precedence is:

1. Library-wide config file,
2. user-wide config file, if it exists,
3. folder-wide config file, if it exists OR custom config file, if passed via
   ``--config_file``,
4. other CLI flags, and
5. any programmatic changes made after the config system is set.


A list of all config options
****************************

.. code::

   ['aspect_ratio', 'assets_dir', 'background_color', 'background_opacity',
   'bottom', 'custom_folders', 'disable_caching', 'dry_run',
   'ffmpeg_loglevel', 'flush_cache', 'frame_height', 'frame_rate',
   'frame_size', 'frame_width', 'frame_x_radius', 'frame_y_radius',
   'from_animation_number', `fullscreen`, 'images_dir', 'input_file', 'left_side',
   'log_dir', 'log_to_file', 'max_files_cached', 'media_dir', 'media_width',
   'movie_file_extension', 'notify_outdated_version', 'output_file', 'partial_movie_dir',
   'pixel_height', 'pixel_width', 'plugins', 'preview',
   'progress_bar', 'quality', 'right_side', 'save_as_gif', 'save_last_frame',
   'save_pngs', 'scene_names', 'show_in_file_browser', 'sound', 'tex_dir',
   'tex_template', 'tex_template_file', 'text_dir', 'top', 'transparent',
   'upto_animation_number', 'use_opengl_renderer', 'verbosity', 'video_dir',
   'window_position', 'window_monitor', 'window_size', 'write_all', 'write_to_movie',
   'enable_wireframe', 'force_window']


Accessing CLI command options
*****************************

Entering ``manim``, or ``manim --help``, will open the main help page.

.. code::

   Usage: manim [OPTIONS] COMMAND [ARGS]...

     Animation engine for explanatory math videos.

   Options:
     --version  Show version and exit.
     --help     Show this message and exit.

   Commands:
     cfg      Manages Manim configuration files.
     init     Sets up a new project in current working directory with default
              settings.

              It copies files from templates directory and pastes them in the
              current working dir.
     new      Create a new project or insert a new scene.
     plugins  Manages Manim plugins.
     render   Render SCENE(S) from the input FILE.

   See 'manim <command>' to read about a specific subcommand.

   Made with <3 by Manim Community developers.

Each of the subcommands has its own help page which can be accessed similarly:

.. code::

   manim render
   manim render --help


# Extracted from /Users/hochmax/learn/manim/docs/source/guides/deep_dive.rst
A deep dive into Manim's internals
==================================

**Author:** `Benjamin Hackl <https://benjamin-hackl.at>`__

.. admonition:: Disclaimer

    This guide reflects the state of the library as of version ``v0.16.0``
    and primarily treats the Cairo renderer. The situation in the latest
    version of Manim might be different; in case of substantial deviations
    we will add a note below.

Introduction
------------

Manim can be a wonderful library, if it behaves the way you would like it to,
and/or the way you expect it to. Unfortunately, this is not always the case
(as you probably know if you have played with some manimations yourself already).
To understand where things *go wrong*, digging through the library's source code
is sometimes the only option -- but in order to do that, you need to know where
to start digging.

This article is intended as some sort of life line through the render process.
We aim to give an appropriate amount of detail describing what happens when
Manim reads your scene code and produces the corresponding animation. Throughout
this article, we will focus on the following toy example::

    from manim import *

    class ToyExample(Scene):
        def construct(self):
            orange_square = Square(color=ORANGE, fill_opacity=0.5)
            blue_circle = Circle(color=BLUE, fill_opacity=0.5)
            self.add(orange_square)
            self.play(ReplacementTransform(orange_square, blue_circle, run_time=3))
            small_dot = Dot()
            small_dot.add_updater(lambda mob: mob.next_to(blue_circle, DOWN))
            self.play(Create(small_dot))
            self.play(blue_circle.animate.shift(RIGHT))
            self.wait()
            self.play(FadeOut(blue_circle, small_dot))

Before we go into details or even look at the rendered output of this scene,
let us first describe verbally what happens in this *manimation*. In the first
three lines of the ``construct`` method, a :class:`.Square` and a :class:`.Circle`
are initialized, then the square is added to the scene. The first frame of the
rendered output should thus show an orange square.

Then the actual animations happen: the square first transforms into a circle,
then a :class:`.Dot` is created (Where do you guess the dot is located when
it is first added to the scene? Answering this already requires detailed
knowledge about the render process.). The dot has an updater attached to it, and
as the circle moves right, the dot moves with it. In the end, all mobjects are
faded out.

Actually rendering the code yields the following video:

.. manim:: ToyExample
    :hide_source:

    class ToyExample(Scene):
        def construct(self):
            orange_square = Square(color=ORANGE, fill_opacity=0.5)
            blue_circle = Circle(color=BLUE, fill_opacity=0.5)
            self.add(orange_square)
            self.play(ReplacementTransform(orange_square, blue_circle, run_time=3))
            small_dot = Dot()
            small_dot.add_updater(lambda mob: mob.next_to(blue_circle, DOWN))
            self.play(Create(small_dot))
            self.play(blue_circle.animate.shift(RIGHT))
            self.wait()
            self.play(FadeOut(blue_circle, small_dot))


For this example, the output (fortunately) coincides with our expectations.

Overview
--------

Because there is a lot of information in this article, here is a brief overview
discussing the contents of the following chapters on a very high level.

- `Preliminaries`_: In this chapter we unravel all the steps that take place
  to prepare a scene for rendering; right until the point where the user-overridden
  ``construct`` method is ran. This includes a brief discussion on using Manim's CLI
  versus other means of rendering (e.g., via Jupyter notebooks, or in your Python
  script by calling the :meth:`.Scene.render` method yourself).
- `Mobject Initialization`_: For the second chapter we dive into creating and handling
  Mobjects, the basic elements that should be displayed in our scene.
  We discuss the :class:`.Mobject` base class, how there are essentially
  three different types of Mobjects, and then discuss the most important of them,
  vectorized Mobjects. In particular, we describe the internal point data structure
  that governs how the mechanism responsible for drawing the vectorized Mobject
  to the screen sets the corresponding Bézier curves. We conclude the chapter
  with a tour into :meth:`.Scene.add`, the bookkeeping mechanism controlling which
  mobjects should be rendered.
- `Animations and the Render Loop`_: And finally, in the last chapter we walk
  through the instantiation of :class:`.Animation` objects (the blueprints that
  hold information on how Mobjects should be modified when the render loop runs),
  followed by a investigation of the infamous :meth:`.Scene.play` call. We will
  see that there are three relevant parts in a :meth:`.Scene.play` call;
  a part in which the passed animations and keyword arguments are processed
  and prepared, followed by the actual "render loop" in which the library
  steps through a time line and renders frame by frame. The final part
  does some post-processing to save a short video segment ("partial movie file")
  and cleanup for the next call to :meth:`.Scene.play`. In the end, after all of
  :meth:`.Scene.construct` has been run, the library combines the partial movie
  files to one video.

And with that, let us get *in medias res*.

Preliminaries
-------------

Importing the library
^^^^^^^^^^^^^^^^^^^^^

Independent of how exactly you are telling your system
to render the scene, i.e., whether you run ``manim -qm -p file_name.py ToyExample``, or
whether you are rendering the scene directly from the Python script via a snippet
like

::

    with tempconfig({"quality": "medium_quality", "preview": True}):
        scene = ToyExample()
        scene.render()

or whether you are rendering the code in a Jupyter notebook, you are still telling your
python interpreter to import the library. The usual pattern used to do this is

::

    from manim import *

which (while being a debatable strategy in general) imports a lot of classes and
functions shipped with the library and makes them available in your global name space.
I explicitly avoided stating that it imports **all** classes and functions of the
library, because it does not do that: Manim makes use of the practice described
in `Section 6.4.1 of the Python tutorial <https://docs.python.org/3/tutorial/modules.html#importing-from-a-package>`__,
and all module members that should be exposed to the user upon running the ``*``-import
are explicitly declared in the ``__all__`` variable of the module.

Manim also uses this strategy internally: taking a peek at the file that is run when
the import is called, ``__init__.py`` (see
`here <https://github.com/ManimCommunity/manim/blob/main/manim/__init__.py>`__),
you will notice that most of the code in that module is concerned with importing
members from various different submodules, again using ``*``-imports.

.. hint::

    If you would ever contribute a new submodule to Manim, the main
    ``__init__.py`` is where it would have to be listed in order to make its
    members accessible to users after importing the library.

In that file, there is one particular import at the beginning of the file however,
namely::

    from ._config import *

This initializes Manim's global configuration system, which is used in various places
throughout the library. After the library runs this line, the current configuration
options are set. The code in there takes care of reading the options in your ``.cfg``
files (all users have at least the global one that is shipped with the library)
as well as correctly handling command line arguments (if you used the CLI to render).

You can read more about the config system in the
:doc:`corresponding thematic guide </guides/configuration>`, and if you are interested in learning
more about the internals of the configuration system and how it is initialized,
follow the code flow starting in `the config module's init file
<https://github.com/ManimCommunity/manim/blob/main/manim/_config/__init__.py>`__.

Now that the library is imported, we can turn our attention to the next step:
reading your scene code (which is not particularly exciting, Python just creates
a new class ``ToyExample`` based on our code; Manim is virtually not involved
in that step, with the exception that ``ToyExample`` inherits from ``Scene``).

However, with the ``ToyExample`` class created and ready to go, there is a new
excellent question to answer: how is the code in our ``construct`` method
actually executed?

Scene instantiation and rendering
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The answer to this question depends on how exactly you are running the code.
To make things a bit clearer, let us first consider the case that you
have created a file ``toy_example.py`` which looks like this::

    from manim import *

    class ToyExample(Scene):
        def construct(self):
            orange_square = Square(color=ORANGE, fill_opacity=0.5)
            blue_circle = Circle(color=BLUE, fill_opacity=0.5)
            self.add(orange_square)
            self.play(ReplacementTransform(orange_square, blue_circle, run_time=3))
            small_dot = Dot()
            small_dot.add_updater(lambda mob: mob.next_to(blue_circle, DOWN))
            self.play(Create(small_dot))
            self.play(blue_circle.animate.shift(RIGHT))
            self.wait()
            self.play(FadeOut(blue_circle, small_dot))

    with tempconfig({"quality": "medium_quality", "preview": True}):
        scene = ToyExample()
        scene.render()

With such a file, the desired scene is rendered by simply running this Python
script via ``python toy_example.py``. Then, as described above, the library
is imported and Python has read and defined the ``ToyExample`` class (but,
read carefully: *no instance of this class has been created yet*).

At this point, the interpreter is about to enter the ``tempconfig`` context
manager. Even if you have not seen Manim's ``tempconfig`` before, its name
already suggests what it does: it creates a copy of the current state of the
configuration, applies the changes to the key-value pairs in the passed
dictionary, and upon leaving the context the original version of the
configuration is restored. TL;DR: it provides a fancy way of temporarily setting
configuration options.

Inside the context manager, two things happen: an actual ``ToyExample``-scene
object is instantiated, and the ``render`` method is called. Every way of using
Manim ultimately does something along of these lines, the library always instantiates
the scene object and then calls its ``render`` method. To illustrate that this
really is the case, let us briefly look at the two most common ways of rendering
scenes:

**Command Line Interface.** When using the CLI and running the command
``manim -qm -p toy_example.py ToyExample`` in your terminal, the actual
entry point is Manim's ``__main__.py`` file (located
`here <https://github.com/ManimCommunity/manim/blob/main/manim/__main__.py>`__.
Manim uses `Click <https://click.palletsprojects.com/en/8.0.x/>`__ to implement
the command line interface, and the corresponding code is located in Manim's
``cli`` module (https://github.com/ManimCommunity/manim/tree/main/manim/cli).
The corresponding code creating the scene class and calling its render method
is located `here <https://github.com/ManimCommunity/manim/blob/ac1ee9a683ce8b92233407351c681f7d71a4f2db/manim/cli/render/commands.py#L139-L141>`__.

**Jupyter notebooks.** In Jupyter notebooks, the communication with the library
is handled by the ``%%manim`` magic command, which is implemented in the
``manim.utils.ipython_magic`` module. There is
:meth:`some documentation <.ManimMagic.manim>` available for the magic command,
and the code creating the scene class and calling its render method is located
`here <https://github.com/ManimCommunity/manim/blob/ac1ee9a683ce8b92233407351c681f7d71a4f2db/manim/utils/ipython_magic.py#L137-L138>`__.


Now that we know that either way, a :class:`.Scene` object is created, let us investigate
what Manim does when that happens. When instantiating our scene object

::

    scene = ToyExample()

the ``Scene.__init__`` method is called, given that we did not implement our own initialization
method. Inspecting the corresponding code (see
`here <https://github.com/ManimCommunity/manim/blob/main/manim/scene/scene.py>`__)
reveals that ``Scene.__init__`` first sets several attributes of the scene objects that do not
depend on any configuration options set in ``config``. Then the scene inspects the value of
``config.renderer``, and based on its value, either instantiates a ``CairoRenderer`` or an
``OpenGLRenderer`` object and assigns it to its ``renderer`` attribute.

The scene then asks its renderer to initialize the scene by calling

::

    self.renderer.init_scene(self)

Inspecting both the default Cairo renderer and the OpenGL renderer shows that the ``init_scene``
method effectively makes the renderer instantiate a :class:`.SceneFileWriter` object, which
basically is Manim's interface to ``libav`` (FFMPEG) and actually writes the movie file. The Cairo
renderer (see the implementation `here <https://github.com/ManimCommunity/manim/blob/main/manim/renderer/cairo_renderer.py>`__) does not require any further initialization. The OpenGL renderer
does some additional setup to enable the realtime rendering preview window, which we do not go
into detail further here.

.. warning::

    Currently, there is a lot of interplay between a scene and its renderer. This is a flaw
    in Manim's current architecture, and we are working on reducing this interdependency to
    achieve a less convoluted code flow.

After the renderer has been instantiated and initialized its file writer, the scene populates
further initial attributes (notable mention: the ``mobjects`` attribute which keeps track
of the mobjects that have been added to the scene). It is then done with its instantiation
and ready to be rendered.

The rest of this article is concerned with the last line in our toy example script::

    scene.render()

This is where the actual magic happens.

Inspecting the `implementation of the render method <https://github.com/ManimCommunity/manim/blob/df1a60421ea1119cbbbd143ef288d294851baaac/manim/scene/scene.py#L211>`__
reveals that there are several hooks that can be used for pre- or postprocessing
a scene. Unsurprisingly, :meth:`.Scene.render` describes the full *render cycle*
of a scene. During this life cycle, there are three custom methods whose base
implementation is empty and that can be overwritten to suit your purposes. In
the order they are called, these customizable methods are:

- :meth:`.Scene.setup`, which is intended for preparing and, well, *setting up*
  the scene for your animation (e.g., adding initial mobjects, assigning custom
  attributes to your scene class, etc.),
- :meth:`.Scene.construct`, which is the *script* for your screen play and
  contains programmatic descriptions of your animations, and
- :meth:`.Scene.tear_down`, which is intended for any operations you might
  want to run on the scene after the last frame has already been rendered
  (for example, this could run some code that generates a custom thumbnail
  for the video based on the state of the objects in the scene -- this
  hook is more relevant for situations where Manim is used within other
  Python scripts).

After these three methods are run, the animations have been fully rendered,
and Manim calls :meth:`.CairoRenderer.scene_finished` to gracefully
complete the rendering process. This checks whether any animations have been
played -- and if so, it tells the :class:`.SceneFileWriter` to close the output
file. If not, Manim assumes that a static image should be output
which it then renders using the same strategy by calling the render loop
(see below) once.

**Back in our toy example,** the call to :meth:`.Scene.render` first
triggers :meth:`.Scene.setup` (which only consists of ``pass``), followed by
a call of :meth:`.Scene.construct`. At this point, our *animation script*
is run, starting with the initialization of ``orange_square``.


Mobject Initialization
----------------------

Mobjects are, in a nutshell, the Python objects that represent all the
*things* we want to display in our scene. Before we follow our debugger
into the depths of mobject initialization code, it makes sense to
discuss Manim's different types of Mobjects and their basic data
structure.

What even is a Mobject?
^^^^^^^^^^^^^^^^^^^^^^^

:class:`.Mobject` stands for *mathematical object* or *Manim object*
(depends on who you ask 😄). The Python class :class:`.Mobject` is
the base class for all objects that should be displayed on screen.
Looking at the `initialization method
<https://github.com/ManimCommunity/manim/blob/5d72d9cfa2e3dd21c844b1da807576f5a7194fda/manim/mobject/mobject.py#L94>`__
of :class:`.Mobject`, you will find that not too much happens in there:

- some initial attribute values are assigned, like ``name`` (which makes the
  render logs mention the name of the mobject instead of its type),
  ``submobjects`` (initially an empty list), ``color``, and some others.
- Then, two methods related to *points* are called: ``reset_points``
  followed by ``generate_points``,
- and finally, ``init_colors`` is called.

Digging deeper, you will find that :meth:`.Mobject.reset_points` simply
sets the ``points`` attribute of the mobject to an empty NumPy vector,
while the other two methods, :meth:`.Mobject.generate_points` and
:meth:`.Mobject.init_colors` are just implemented as ``pass``.

This makes sense: :class:`.Mobject` is not supposed to be used as
an *actual* object that is displayed on screen; in fact the camera
(which we will discuss later in more detail; it is the class that is,
for the Cairo renderer, responsible for "taking a picture" of the
current scene) does not process "pure" :class:`Mobjects <.Mobject>`
in any way, they *cannot* even appear in the rendered output.

This is where different types of mobjects come into play. Roughly
speaking, the Cairo renderer setup knows three different types of
mobjects that can be rendered:

- :class:`.ImageMobject`, which represent images that you can display
  in your scene,
- :class:`.PMobject`, which are very special mobjects used to represent
  point clouds; we will not discuss them further in this guide,
- :class:`.VMobject`, which are *vectorized mobjects*, that is, mobjects
  that consist of points that are connected via curves. These are pretty
  much everywhere, and we will discuss them in detail in the next section.

... and what are VMobjects?
^^^^^^^^^^^^^^^^^^^^^^^^^^^

As just mentioned, :class:`VMobjects <.VMobject>` represent vectorized
mobjects. To render a :class:`.VMobject`, the camera looks at the
``points`` attribute of a :class:`.VMobject` and divides it into sets
of four points each. Each of these sets is then used to construct a
cubic Bézier curve with the first and last entry describing the
end points of the curve ("anchors"), and the second and third entry
describing the control points in between ("handles").

.. hint::
  To learn more about Bézier curves, take a look at the excellent
  online textbook `A Primer on Bézier curves <https://pomax.github.io/bezierinfo/>`__
  by `Pomax <https://twitter.com/TheRealPomax>`__ -- there is a playground representing
  cubic Bézier curves `in §1 <https://pomax.github.io/bezierinfo/#introduction>`__,
  the red and yellow points are "anchors", and the green and blue
  points are "handles".

In contrast to :class:`.Mobject`, :class:`.VMobject` can be displayed
on screen (even though, technically, it is still considered a base class).
To illustrate how points are processed, consider the following short example
of a :class:`.VMobject` with 8 points (and thus made out of 8/4 = 2 cubic
Bézier curves). The resulting :class:`.VMobject` is drawn in green.
The handles are drawn as red dots with a line to their closest anchor.

.. manim:: VMobjectDemo
    :save_last_frame:

    class VMobjectDemo(Scene):
        def construct(self):
            plane = NumberPlane()
            my_vmobject = VMobject(color=GREEN)
            my_vmobject.points = [
                np.array([-2, -1, 0]),  # start of first curve
                np.array([-3, 1, 0]),
                np.array([0, 3, 0]),
                np.array([1, 3, 0]),  # end of first curve
                np.array([1, 3, 0]),  # start of second curve
                np.array([0, 1, 0]),
                np.array([4, 3, 0]),
                np.array([4, -2, 0]),  # end of second curve
            ]
            handles = [
                Dot(point, color=RED) for point in
                [[-3, 1, 0], [0, 3, 0], [0, 1, 0], [4, 3, 0]]
            ]
            handle_lines = [
                Line(
                    my_vmobject.points[ind],
                    my_vmobject.points[ind+1],
                    color=RED,
                    stroke_width=2
                ) for ind in range(0, len(my_vmobject.points), 2)
            ]
            self.add(plane, *handles, *handle_lines, my_vmobject)


.. warning::
  Manually setting the points of your :class:`.VMobject` is usually
  discouraged; there are specialized methods that can take care of
  that for you -- but it might be relevant when implementing your own,
  custom :class:`.VMobject`.



Squares and Circles: back to our Toy Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With a basic understanding of different types of mobjects,
and an idea of how vectorized mobjects are built we can now
come back to our toy example and the execution of the
:meth:`.Scene.construct` method. In the first two lines
of our animation script, the ``orange_square`` and the
``blue_circle`` are initialized.

When creating the orange square by running

::

  Square(color=ORANGE, fill_opacity=0.5)

the initialization method of :class:`.Square`,
``Square.__init__``, is called. `Looking at the
implementation <https://github.com/ManimCommunity/manim/blob/5d72d9cfa2e3dd21c844b1da807576f5a7194fda/manim/mobject/geometry/polygram.py#L607>`__,
we can see that the ``side_length`` attribute of the square is set,
and then

::

  super().__init__(height=side_length, width=side_length, **kwargs)

is called. This ``super`` call is the Python way of calling the
initialization function of the parent class. As :class:`.Square`
inherits from :class:`.Rectangle`, the next method called
is ``Rectangle.__init__``. There, only the first three lines
are really relevant for us::

  super().__init__(UR, UL, DL, DR, color=color, **kwargs)
  self.stretch_to_fit_width(width)
  self.stretch_to_fit_height(height)

First, the initialization function of the parent class of
:class:`.Rectangle` -- :class:`.Polygon` -- is called. The
four positional arguments passed are the four corners of
the polygon: ``UR`` is up right (and equal to ``UP + RIGHT``),
``UL`` is up left (and equal to ``UP + LEFT``), and so forth.
Before we follow our debugger deeper, let us observe what
happens with the constructed polygon: the remaining two lines
stretch the polygon to fit the specified width and height
such that a rectangle with the desired measurements is created.

The initialization function of :class:`.Polygon` is particularly
simple, it only calls the initialization function of its parent
class, :class:`.Polygram`. There, we have almost reached the end
of the chain: :class:`.Polygram` inherits from :class:`.VMobject`,
whose initialization function mainly sets the values of some
attributes (quite similar to ``Mobject.__init__``, but more specific
to the Bézier curves that make up the mobject).

After calling the initialization function of :class:`.VMobject`,
the constructor of :class:`.Polygram` also does something somewhat
odd: it sets the points (which, you might remember above, should
actually be set in a corresponding ``generate_points`` method
of :class:`.Polygram`).

.. warning::
  In several instances, the implementation of mobjects does
  not really stick to all aspects of Manim's interface. This
  is unfortunate, and increasing consistency is something
  that we actively work on. Help is welcome!

Without going too much into detail, :class:`.Polygram` sets its
``points`` attribute via :meth:`.VMobject.start_new_path`,
:meth:`.VMobject.add_points_as_corners`, which take care of
setting the quadruples of anchors and handles appropriately.
After the points are set, Python continues to process the
call stack until it reaches the method that was first called;
the initialization method of :class:`.Square`. After this,
the square is initialized and assigned to the ``orange_square``
variable.

The initialization of ``blue_circle`` is similar to the one of
``orange_square``, with the main difference being that the inheritance
chain of :class:`.Circle` is different. Let us briefly follow the trace
of the debugger:

The implementation of :meth:`.Circle.__init__` immediately calls
the initialization method of :class:`.Arc`, as a circle in Manim
is simply an arc with an angle of :math:`\tau = 2\pi`. When
initializing the arc, some basic attributes are set (like
``Arc.radius``, ``Arc.arc_center``, ``Arc.start_angle``, and
``Arc.angle``), and then the initialization method of its
parent class, :class:`.TipableVMobject`, is called (which is
a rather abstract base class for mobjects which a arrow tip can
be attached to). Note that in contrast to :class:`.Polygram`,
this class does **not** preemptively generate the points of the circle.

After that, things are less exciting: :class:`.TipableVMobject` again
sets some attributes relevant for adding arrow tips, and afterwards
passes to the initialization method of :class:`.VMobject`. From there,
:class:`.Mobject` is initialized and :meth:`.Mobject.generate_points`
is called, which actually runs the method implemented in
:meth:`.Arc.generate_points`.

After both our ``orange_square`` and the ``blue_circle`` are initialized,
the square is actually added to the scene. The :meth:`.Scene.add` method
is actually doing a few interesting things, so it is worth to dig a bit
deeper in the next section.


Adding Mobjects to the Scene
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The code in our ``construct`` method that is run next is

::

  self.add(orange_square)

From a high-level point of view, :meth:`.Scene.add` adds the
``orange_square`` to the list of mobjects that should be rendered,
which is stored in the ``mobjects`` attribute of the scene. However,
it does so in a very careful way to avoid the situation that a mobject
is being added to the scene more than once. At a first glance, this
sounds like a simple task -- the problem is that ``Scene.mobjects``
is not a "flat" list of mobjects, but a list of mobjects which
might contain mobjects themselves, and so on.

Stepping through the code in :meth:`.Scene.add`, we see that first
it is checked whether we are currently using the OpenGL renderer
(which we are not) -- adding mobjects to the scene works slightly
different (and actually easier!) for the OpenGL renderer. Then, the
code branch for the Cairo renderer is entered and the list of so-called
foreground mobjects (which are rendered on top of all other mobjects)
is added to the list of passed mobjects. This is to ensure that the
foreground mobjects will stay above of the other mobjects, even after
adding the new ones. In our case, the list of foreground mobjects
is actually empty, and nothing changes.

Next, :meth:`.Scene.restructure_mobjects` is called with the list
of mobjects to be added as the ``to_remove`` argument, which might
sound odd at first. Practically, this ensures that mobjects are not
added twice, as mentioned above: if they were present in the scene
``Scene.mobjects`` list before (even if they were contained as a
child of some other mobject), they are first removed from the list.
The way :meth:`.Scene.restrucutre_mobjects` works is rather aggressive:
It always operates on a given list of mobjects; in the ``add`` method
two different lists occur: the default one, ``Scene.mobjects`` (no extra
keyword argument is passed), and ``Scene.moving_mobjects`` (which we will
discuss later in more detail). It iterates through all of the members of
the list, and checks whether any of the mobjects passed in ``to_remove``
are contained as children (in any nesting level). If so, **their parent
mobject is deconstructed** and their siblings are inserted directly
one level higher. Consider the following example::

  >>> from manim import Scene, Square, Circle, Group
  >>> test_scene = Scene()
  >>> mob1 = Square()
  >>> mob2 = Circle()
  >>> mob_group = Group(mob1, mob2)
  >>> test_scene.add(mob_group)
  <manim.scene.scene.Scene object at ...>
  >>> test_scene.mobjects
  [Group]
  >>> test_scene.restructure_mobjects(to_remove=[mob1])
  <manim.scene.scene.Scene object at ...>
  >>> test_scene.mobjects
  [Circle]

Note that the group is disbanded and the circle moves into the
root layer of mobjects in ``test_scene.mobjects``.

After the mobject list is "restructured", the mobject to be added
are simply appended to ``Scene.mobjects``. In our toy example,
the ``Scene.mobjects`` list is actually empty, so the
``restructure_mobjects`` method does not actually do anything. The
``orange_square`` is simply added to ``Scene.mobjects``, and as
the aforementioned ``Scene.moving_mobjects`` list is, at this point,
also still empty, nothing happens and :meth:`.Scene.add` returns.

We will hear more about the ``moving_mobject`` list when we discuss
the render loop. Before we do that, let us look at the next line
of code in our toy example, which includes the initialization of
an animation class,
::

  ReplacementTransform(orange_square, blue_circle, run_time=3)

Hence it is time to talk about :class:`.Animation`.


Animations and the Render Loop
------------------------------

Initializing animations
^^^^^^^^^^^^^^^^^^^^^^^

Before we follow the trace of the debugger, let us briefly discuss
the general structure of the (abstract) base class :class:`.Animation`.
An animation object holds all the information necessary for the renderer
to generate the corresponding frames. Animations (in the sense of
animation objects) in Manim are *always* tied to a specific mobject;
even in the case of :class:`.AnimationGroup` (which you should actually
think of as an animation on a group of mobjects rather than a group
of animations). Moreover, except for in a particular special case,
the run time of animations is also fixed and known beforehand.

The initialization of animations actually is not very exciting,
:meth:`.Animation.__init__` merely sets some attributes derived
from the passed keyword arguments and additionally ensures that
the ``Animation.starting_mobject`` and ``Animation.mobject``
attributes are populated. Once the animation is played, the
``starting_mobject`` attribute holds an unmodified copy of the
mobject the animation is attached to; during the initialization
it is set to a placeholder mobject. The ``mobject`` attribute
is set to the mobject the animation is attached to.

Animations have a few special methods which are called during the
render loop:

- :meth:`.Animation.begin`, which is called (as hinted by its name)
  at the beginning of every animation, so before the first frame
  is rendered. In it, all the required setup for the animation happens.
- :meth:`.Animation.finish` is the counterpart to the ``begin`` method
  which is called at the end of the life cycle of the animation (after
  the last frame has been rendered).
- :meth:`.Animation.interpolate` is the method that updates the mobject
  attached to the animation to the corresponding animation completion
  percentage. For example, if in the render loop,
  ``some_animation.interpolate(0.5)`` is called, the attached mobject
  will be updated to the state where 50% of the animation are completed.

We will discuss details about these and some further animation methods
once we walk through the actual render loop. For now, we continue with
our toy example and the code that is run when initializing the
:class:`.ReplacementTransform` animation.

The initialization method of :class:`.ReplacementTransform` only
consists of a call to the constructor of its parent class,
:class:`.Transform`, with the additional keyword argument
``replace_mobject_with_target_in_scene`` set to ``True``.
:class:`.Transform` then sets attributes that control how the
points of the starting mobject are deformed into the points of
the target mobject, and then passes on to the initialization
method of :class:`.Animation`. Other basic properties of the
animation (like its ``run_time``, the ``rate_func``, etc.) are
processed there -- and then the animation object is fully
initialized and ready to be played.

The ``play`` call: preparing to enter Manim's render loop
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We are finally there, the render loop is in our reach. Let us
walk through the code that is run when :meth:`.Scene.play` is called.

.. hint::

  Recall that this article is specifically about the Cairo renderer.
  Up to here, things were more or less the same for the OpenGL renderer
  as well; while some base mobjects might be different, the control flow
  and lifecycle of mobjects is still more or less the same. There are more
  substantial differences when it comes to the rendering loop.

As you will see when inspecting the method, :meth:`.Scene.play` almost
immediately passes over to the ``play`` method of the renderer,
in our case :class:`.CairoRenderer.play`. The one thing :meth:`.Scene.play`
takes care of is the management of subcaptions that you might have
passed to it (see the the documentation of :meth:`.Scene.play` and
:meth:`.Scene.add_subcaption` for more information).

.. warning::

  As has been said before, the communication between scene and renderer
  is not in a very clean state at this point, so the following paragraphs
  might be confusing if you don't run a debugger and step through the
  code yourself a bit.

Inside :meth:`.CairoRenderer.play`, the renderer first checks whether
it may skip rendering of the current play call. This might happen, for example,
when ``-s`` is passed to the CLI (i.e., only the last frame should be rendered),
or when the ``-n`` flag is passed and the current play call is outside of the
specified render bounds. The "skipping status" is updated in form of the
call to :meth:`.CairoRenderer.update_skipping_status`.

Next, the renderer asks the scene to process the animations in the play
call so that renderer obtains all of the information it needs. To
be more concrete, :meth:`.Scene.compile_animation_data` is called,
which then takes care of several things:

- The method processes all animations and the keyword arguments passed
  to the initial :meth:`.Scene.play` call. In particular, this means
  that it makes sure all arguments passed to the play call are actually
  animations (or ``.animate`` syntax calls, which are also assembled to
  be actual :class:`.Animation`-objects at that point). It also propagates
  any animation-related keyword arguments (like ``run_time``,
  or ``rate_func``) passed to :class:`.Scene.play` to each individual
  animation. The processed animations are then stored in the ``animations``
  attribute of the scene (which the renderer later reads...).
- It adds all mobjects to which the animations that are played are
  bound to to the scene (provided the animation is not an mobject-introducing
  animation -- for these, the addition to the scene happens later).
- In case the played animation is a :class:`.Wait` animation (this is the
  case in a :meth:`.Scene.wait` call), the method checks whether a static
  image should be rendered, or whether the render loop should be processed
  as usual (see :meth:`.Scene.should_update_mobjects` for the exact conditions,
  basically it checks whether there are any time-dependent updater functions
  and so on).
- Finally, the method determines the total run time of the play call (which
  at this point is computed as the maximum of the run times of the passed
  animations). This is stored in the ``duration`` attribute of the scene.


After the animation data has been compiled by the scene, the renderer
continues to prepare for entering the render loop. It now checks the
skipping status which has been determined before. If the renderer can
skip this play call, it does so: it sets the current play call hash (which
we will get back to in a moment) to ``None`` and increases the time of the
renderer by the determined animation run time.

Otherwise, the renderer checks whether or not Manim's caching system should
be used. The idea of the caching system is simple: for every play call, a
hash value is computed, which is then stored and upon re-rendering the scene,
the hash is generated again and checked against the stored value. If it is the
same, the cached output is reused, otherwise it is fully rerendered again.
We will not go into details of the caching system here; if you would like
to learn more, the :func:`.get_hash_from_play_call` function in the
:mod:`.utils.hashing` module is essentially the entry point to the caching
mechanism.

In the event that the animation has to be rendered, the renderer asks
its :class:`.SceneFileWriter` to open an output container. The process
is started by a call to ``libav`` and opens a container to which rendered
raw frames can be written. As long as the output is open, the container
can be accessed via the ``output_container`` attribute of the file writer.
With the writing process in place, the renderer then asks the scene
to "begin" the animations.

First, it literally *begins* all of the animations by calling their
setup methods (:meth:`.Animation._setup_scene`, :meth:`.Animation.begin`).
In doing so, the mobjects that are newly introduced by an animation
(like via :class:`.Create` etc.) are added to the scene. Furthermore, the
animation suspends updater functions being called on its mobject, and
it sets its mobject to the state that corresponds to the first frame
of the animation.

After this has happened for all animations in the current ``play`` call,
the Cairo renderer determines which of the scene's mobjects can be
painted statically to the background, and which ones have to be
redrawn every frame. It does so by calling
:meth:`.Scene.get_moving_and_static_mobjects`, and the resulting
partition of mobjects is stored in the corresponding ``moving_mobjects``
and ``static_mobjects`` attributes.

.. NOTE::

  The mechanism that determines static and moving mobjects is
  specific for the Cairo renderer, the OpenGL renderer works differently.
  Basically, moving mobjects are determined by checking whether they,
  any of their children, or any of the mobjects "below" them (in the
  sense of the order in which mobjects are processed in the scene)
  either have an update function attached, or whether they appear
  in one of the current animations. See the implementation of
  :meth:`.Scene.get_moving_mobjects` for more details.

Up to this very point, we did not actually render any (partial)
image or movie files from the scene yet. This is, however, about to change.
Before we enter the render loop, let us briefly revisit our toy
example and discuss how the generic :meth:`.Scene.play` call
setup looks like there.

For the call that plays the :class:`.ReplacementTransform`, there
is no subcaption to be taken care of. The renderer then asks
the scene to compile the animation data: the passed argument
already is an animation (no additional preparations needed),
there is no need for processing any keyword arguments (as
we did not specify any additional ones to ``play``). The
mobject bound to the animation, ``orange_square``, is already
part of the scene (so again, no action taken). Finally, the run
time is extracted (3 seconds long) and stored in
``Scene.duration``. The renderer then checks whether it should
skip (it should not), then whether the animation is already
cached (it is not). The corresponding animation hash value is
determined and passed to the file writer, which then also calls
``libav`` to start the writing process which waits for rendered
frames from the library.

The scene then ``begin``\ s the animation: for the
:class:`.ReplacementTransform` this means that the animation populates
all of its relevant animation attributes (i.e., compatible copies
of the starting and the target mobject so that it can safely interpolate
between the two).

The mechanism determining static and moving mobjects considers
all of the scenes mobjects (at this point only the
``orange_square``), and determines that the ``orange_square`` is
bound to an animation that is currently played. As a result,
the square is classified as a "moving mobject".

Time to render some frames.


The render loop (for real this time)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As mentioned above, due to the mechanism that determines static and moving
mobjects in the scene, the renderer knows which mobjects it can paint
statically to the background of the scene. Practically, this means that
it partially renders a scene (to produce a background image), and then
when iterating through the time progression of the animation only the
"moving mobjects" are re-painted on top of the static background.

The renderer calls :meth:`.CairoRenderer.save_static_frame_data`, which
first checks whether there are currently any static mobjects, and if there
are, it updates the frame (only with the static mobjects; more about how
exactly this works in a moment) and then saves a NumPy array representing
the rendered frame in the ``static_image`` attribute. In our toy example,
there are no static mobjects, and so the ``static_image`` attribute is
simply set to ``None``.

Next, the renderer asks the scene whether the current animation is
a "frozen frame" animation, which would mean that the renderer actually
does not have to repaint the moving mobjects in every frame of the time
progression. It can then just take the latest static frame, and display it
throughout the animation.

.. NOTE::

  An animation is considered a "frozen frame" animation if only a
  static :class:`.Wait` animation is played. See the description
  of :meth:`.Scene.compile_animation_data` above, or the
  implementation of :meth:`.Scene.should_update_mobjects` for
  more details.

If this is not the case (just as in our toy example), the renderer
then calls the :meth:`.Scene.play_internal` method, which is the
integral part of the render loop (in which the library steps through
the time progression of the animation and renders the corresponding
frames).

Within :meth:`.Scene.play_internal`, the following steps are performed:

- The scene determines the run time of the animations by calling
  :meth:`.Scene.get_run_time`. This method basically takes the maximum
  ``run_time`` attribute of all of the animations passed to the
  :meth:`.Scene.play` call.
- Then the *time progression* is constructed via the (internal)
  :meth:`.Scene._get_animation_time_progression` method, which wraps
  the actual :meth:`.Scene.get_time_progression` method. The time
  progression is a ``tqdm`` `progress bar object <https://tqdm.github.io>`__
  for an iterator over ``np.arange(0, run_time, 1 / config.frame_rate)``. In
  other words, the time progression holds the time stamps (relative to the
  current animations, so starting at 0 and ending at the total animation run time,
  with the step size determined by the render frame rate) of the timeline where
  a new animation frame should be rendered.
- Then the scene iterates over the time progression: for each time stamp ``t``,
  :meth:`.Scene.update_to_time` is called, which ...

  - ... first computes the time passed since the last update (which might be 0,
    especially for the initial call) and references it as ``dt``,
  - then (in the order in which the animations are passed to :meth:`.Scene.play`)
    calls :meth:`.Animation.update_mobjects` to trigger all updater functions that
    are attached to the respective animation except for the "main mobject" of
    the animation (that is, for example, for :class:`.Transform` the unmodified
    copies of start and target mobject -- see :meth:`.Animation.get_all_mobjects_to_update`
    for more details),
  - then the relative time progression with respect to the current animation
    is computed (``alpha = t / animation.run_time``), which is then used to
    update the state of the animation with a call to :meth:`.Animation.interpolate`.
  - After all of the passed animations have been processed, the updater functions
    of all mobjects in the scene, all meshes, and finally those attached to
    the scene itself are run.

At this point, the internal (Python) state of all mobjects has been updated
to match the currently processed timestamp. If rendering should not be skipped,
then it is now time to *take a picture*!

.. NOTE::

  The update of the internal state (iteration over the time progression) happens
  *always* once :meth:`.Scene.play_internal` is entered. This ensures that even
  if frames do not need to be rendered (because, e.g., the ``-n`` CLI flag has
  been passed, something has been cached, or because we might be in a *Section*
  with skipped rendering), updater functions still run correctly, and the state
  of the first frame that *is* rendered is kept consistent.

To render an image, the scene calls the corresponding method of its renderer,
:meth:`.CairoRenderer.render` and passes just the list of *moving mobjects* (remember,
the *static mobjects* are assumed to have already been painted statically to
the background of the scene). All of the hard work then happens when the renderer
updates its current frame via a call to :meth:`.CairoRenderer.update_frame`:

First, the renderer prepares its :class:`.Camera` by checking whether the renderer
has a ``static_image`` different from ``None`` stored already. If so, it sets the
image as the *background image* of the camera via :meth:`.Camera.set_frame_to_background`,
and otherwise it just resets the camera via :meth:`.Camera.reset`. The camera is then
asked to capture the scene with a call to :meth:`.Camera.capture_mobjects`.

Things get a bit technical here, and at some point it is more efficient to
delve into the implementation -- but here is a summary of what happens once the
camera is asked to capture the scene:

- First, a flat list of mobjects is created (so submobjects get extracted from
  their parents). This list is then processed in groups of the same type of
  mobjects (e.g., a batch of vectorized mobjects, followed by a batch of image mobjects,
  followed by more vectorized mobjects, etc. -- in many cases there will just be
  one batch of vectorized mobjects).
- Depending on the type of the currently processed batch, the camera uses dedicated
  *display functions* to convert the :class:`.Mobject` Python object to
  a NumPy array stored in the camera's ``pixel_array`` attribute.
  The most important example in that context is the display function for
  vectorized mobjects, :meth:`.Camera.display_multiple_vectorized_mobjects`,
  or the more particular (in case you did not add a background image to your
  :class:`.VMobject`), :meth:`.Camera.display_multiple_non_background_colored_vmobjects`.
  This method first gets the current Cairo context, and then, for every (vectorized)
  mobject in the batch, calls :meth:`.Camera.display_vectorized`. There,
  the actual background stroke, fill, and then stroke of the mobject is
  drawn onto the context. See :meth:`.Camera.apply_stroke` and
  :meth:`.Camera.set_cairo_context_color` for more details -- but it does not get
  much deeper than that, in the latter method the actual Bézier curves
  determined by the points of the mobject are drawn; this is where the low-level
  interaction with Cairo happens.

After all batches have been processed, the camera has an image representation
of the Scene at the current time stamp in form of a NumPy array stored in its
``pixel_array`` attribute. The renderer then takes this array and passes it to
its :class:`.SceneFileWriter`. This concludes one iteration of the render loop,
and once the time progression has been processed completely, a final bit
of cleanup is performed before the :meth:`.Scene.play_internal` call is completed.

A TL;DR for the render loop, in the context of our toy example, reads as follows:

- The scene finds that a 3 second long animation (the :class:`.ReplacementTransform`
  changing the orange square to the blue circle) should be played. Given the requested
  medium render quality, the frame rate is 30 frames per second, and so the time
  progression with steps ``[0, 1/30, 2/30, ..., 89/30]`` is created.
- In the internal render loop, each of these time stamps is processed:
  there are no updater functions, so effectively the scene updates the
  state of the transformation animation to the desired time stamp (for example,
  at time stamp ``t = 45/30``, the animation is completed to a rate of
  ``alpha = 0.5``).
- Then the scene asks the renderer to do its job. The renderer asks its camera
  to capture the scene, the only mobject that needs to be processed at this point
  is the main mobject attached to the transformation; the camera converts the
  current state of the mobject to entries in a NumPy array. The renderer passes
  this array to the file writer.
- At the end of the loop, 90 frames have been passed to the file writer.

Completing the render loop
^^^^^^^^^^^^^^^^^^^^^^^^^^

The last few steps in the :meth:`.Scene.play_internal` call are not too
exciting: for every animation, the corresponding :meth:`.Animation.finish`
and :meth:`.Animation.clean_up_from_scene` methods are called.

.. NOTE::

  Note that as part of :meth:`.Animation.finish`, the :meth:`.Animation.interpolate`
  method is called with an argument of 1.0 -- you might have noticed already that
  the last frame of an animation can sometimes be a bit off or incomplete.
  This is by current design! The last frame rendered in the render loop (and displayed
  for a duration of ``1 / frame_rate`` seconds in the rendered video) corresponds to
  the state of the animation ``1 / frame_rate`` seconds before it ends. To display
  the final frame as well in the video, we would need to append another ``1 / frame_rate``
  seconds to the video -- which would then mean that a 1 second rendered Manim video
  would be slightly longer than 1 second. We decided against this at some point.

In the end, the time progression is closed (which completes the displayed progress bar)
in the terminal. With the closing of the time progression, the
:meth:`.Scene.play_internal` call is completed, and we return to the renderer,
which now orders the :class:`.SceneFileWriter` to close the output container that has
been opened for this animation: a partial movie file is written.

This pretty much concludes the walkthrough of a :class:`.Scene.play` call,
and actually there is not too much more to say for our toy example either: at
this point, a partial movie file that represents playing the
:class:`.ReplacementTransform` has been written. The initialization of
the :class:`.Dot` happens analogous to the initialization of ``blue_circle``,
which has been discussed above. The :meth:`.Mobject.add_updater` call literally
just attaches a function to the ``updaters`` attribute of the ``small_dot``. And
the remaining :meth:`.Scene.play` and :meth:`.Scene.wait` calls follow the
exact same procedure as discussed in the render loop section above; each such call
produces a corresponding partial movie file.

Once the :meth:`.Scene.construct` method has been fully processed (and thus all
of the corresponding partial movie files have been written), the
scene calls its cleanup method :meth:`.Scene.tear_down`, and then
asks its renderer to finish the scene. The renderer, in turn, asks
its scene file writer to wrap things up by calling :meth:`.SceneFileWriter.finish`,
which triggers the combination of the partial movie files into the final product.

And there you go! This is a more or less detailed description of how Manim works
under the hood. While we did not discuss every single line of code in detail
in this walkthrough, it should still give you a fairly good idea of how the general
structural design of the library and at least the Cairo rendering flow in particular
looks like.


# Extracted from /Users/hochmax/learn/manim/docs/source/tutorials/quickstart.rst
==========
Quickstart
==========

.. note::
 Before proceeding, install Manim and make sure it's running properly by
 following the steps in :doc:`../installation`. For
 information on using Manim with Jupyterlab or Jupyter notebook, go to the
 documentation for the
 :meth:`IPython magic command <manim.utils.ipython_magic.ManimMagic.manim>`,
 ``%%manim``.

Overview
********

This quickstart guide will lead you through creating a sample project using Manim: an animation
engine for precise programmatic animations.

First, you will use a command line
interface to create a ``Scene``, the class through which Manim generates videos.
In the ``Scene`` you will animate a circle. Then you will add another ``Scene`` showing
a square transforming into a circle. This will be your introduction to Manim's animation ability.
Afterwards, you will position multiple mathematical objects (``Mobject``\s). Finally, you
will learn the ``.animate`` syntax, a powerful feature that animates the methods you
use to modify ``Mobject``\s.


Starting a new project
**********************

Start by creating a new folder. For the purposes of this guide, name the folder ``project``:

.. code-block:: bash

   project/

This folder is the root folder for your project. It contains all the files that Manim needs to function,
as well as any output that your project produces.


Animating a circle
******************

1. Open a text editor, such as Notepad. Copy the following code snippet into the window:

.. code-block:: python

   from manim import *


   class CreateCircle(Scene):
       def construct(self):
           circle = Circle()  # create a circle
           circle.set_fill(PINK, opacity=0.5)  # set the color and transparency
           self.play(Create(circle))  # show the circle on screen

2. Save the code snippet into your project folder with the name ``scene.py``.

.. code-block:: bash

   project/
   └─scene.py

3. Open the command line, navigate to your project folder, and execute
the following command:

.. code-block:: bash

   manim -pql scene.py CreateCircle

Manim will output rendering information, then create an MP4 file.
Your default movie player will play the MP4 file, displaying the following animation.

.. manim:: CreateCircle
   :hide_source:

   class CreateCircle(Scene):
       def construct(self):
           circle = Circle()                   # create a circle
           circle.set_fill(PINK, opacity=0.5)  # set the color and transparency
           self.play(Create(circle))     # show the circle on screen

If you see an animation of a pink circle being drawn, congratulations!
You just wrote your first Manim scene from scratch.

If you get an error
message instead, you do not see a video, or if the video output does not
look like the preceding animation, it is likely that Manim has not been
installed correctly. Please refer to our :doc:`FAQ section </faq/index>`
for help with the most common issues.


***********
Explanation
***********

Let's go over the script you just executed line by line to see how Manim was
able to draw the circle.

The first line imports all of the contents of the library:

.. code-block:: python

   from manim import *

This is the recommended way of using Manim, as a single script often uses
multiple names from the Manim namespace. In your script, you imported and used
``Scene``, ``Circle``, ``PINK`` and ``Create``.

Now let's look at the next two lines:

.. code-block:: python

   class CreateCircle(Scene):
       def construct(self):
           [...]

Most of the time, the code for scripting an animation is entirely contained within
the :meth:`~.Scene.construct` method of a :class:`.Scene` class.
Inside :meth:`~.Scene.construct`, you can create objects, display them on screen, and animate them.

The next two lines create a circle and set its color and opacity:

.. code-block:: python

           circle = Circle()  # create a circle
           circle.set_fill(PINK, opacity=0.5)  # set the color and transparency

Finally, the last line uses the animation :class:`.Create` to display the
circle on your screen:

.. code-block:: python

           self.play(Create(circle))  # show the circle on screen

.. tip:: All animations must reside within the :meth:`~.Scene.construct` method of a
         class derived from :class:`.Scene`.  Other code, such as auxiliary
         or mathematical functions, may reside outside the class.


Transforming a square into a circle
***********************************

With our circle animation complete, let's move on to something a little more complicated.

1. Open ``scene.py``, and add the following code snippet below the ``CreateCircle`` class:

.. code-block:: python

   class SquareToCircle(Scene):
       def construct(self):
           circle = Circle()  # create a circle
           circle.set_fill(PINK, opacity=0.5)  # set color and transparency

           square = Square()  # create a square
           square.rotate(PI / 4)  # rotate a certain amount

           self.play(Create(square))  # animate the creation of the square
           self.play(Transform(square, circle))  # interpolate the square into the circle
           self.play(FadeOut(square))  # fade out animation

2. Render ``SquareToCircle`` by running the following command in the command line:

.. code-block:: bash

   manim -pql scene.py SquareToCircle

The following animation will render:

.. manim:: SquareToCircle2
   :hide_source:

   class SquareToCircle2(Scene):
       def construct(self):
           circle = Circle()  # create a circle
           circle.set_fill(PINK, opacity=0.5)  # set color and transparency

           square = Square()  # create a square
           square.rotate(PI / 4)  # rotate a certain amount

           self.play(Create(square))  # animate the creation of the square
           self.play(Transform(square, circle))  # interpolate the square into the circle
           self.play(FadeOut(square))  # fade out animation

This example shows one of the primary features of Manim: the ability to
implement complicated and mathematically intensive animations (such as cleanly
interpolating between two geometric shapes) with just a few lines of code.


Positioning ``Mobject``\s
*************************

Next, let's go over some basic techniques for positioning ``Mobject``\s.

1. Open ``scene.py``, and add the following code snippet below the ``SquareToCircle`` method:

.. code-block:: python

   class SquareAndCircle(Scene):
       def construct(self):
           circle = Circle()  # create a circle
           circle.set_fill(PINK, opacity=0.5)  # set the color and transparency

           square = Square()  # create a square
           square.set_fill(BLUE, opacity=0.5)  # set the color and transparency

           square.next_to(circle, RIGHT, buff=0.5)  # set the position
           self.play(Create(circle), Create(square))  # show the shapes on screen

2. Render ``SquareAndCircle`` by running the following command in the command line:

.. code-block:: bash

   manim -pql scene.py SquareAndCircle

The following animation will render:

.. manim:: SquareAndCircle2
   :hide_source:

   class SquareAndCircle2(Scene):
       def construct(self):
           circle = Circle()  # create a circle
           circle.set_fill(PINK, opacity=0.5)  # set the color and transparency

           square = Square() # create a square
           square.set_fill(BLUE, opacity=0.5) # set the color and transparency

           square.next_to(circle, RIGHT, buff=0.5) # set the position
           self.play(Create(circle), Create(square))  # show the shapes on screen

``next_to`` is a ``Mobject`` method for positioning ``Mobject``\s.

We first specified
the pink circle as the square's reference point by passing ``circle`` as the method's first argument.
The second argument is used to specify the direction the ``Mobject`` is placed relative to the reference point.
In this case, we set the direction to ``RIGHT``, telling Manim to position the square to the right of the circle.
Finally, ``buff=0.5`` applied a small distance buffer between the two objects.

Try changing ``RIGHT`` to ``LEFT``, ``UP``, or ``DOWN`` instead, and see how that changes the position of the square.

Using positioning methods, you can render a scene with multiple ``Mobject``\s,
setting their locations in the scene using coordinates or positioning them
relative to each other.

For more information on ``next_to`` and other positioning methods, check out the
list of :class:`.Mobject` methods in our reference manual.


Using ``.animate`` syntax to animate methods
********************************************

The final lesson in this tutorial is using ``.animate``, a ``Mobject`` method which
animates changes you make to a ``Mobject``. When you prepend ``.animate`` to any
method call that modifies a ``Mobject``, the method becomes an animation which
can be played using ``self.play``. Let's return to ``SquareToCircle`` to see the
differences between using methods when creating a ``Mobject``,
and animating those method calls with ``.animate``.

1. Open ``scene.py``, and add the following code snippet below the ``SquareAndCircle`` class:

.. code-block:: python

   class AnimatedSquareToCircle(Scene):
       def construct(self):
           circle = Circle()  # create a circle
           square = Square()  # create a square

           self.play(Create(square))  # show the square on screen
           self.play(square.animate.rotate(PI / 4))  # rotate the square
           self.play(Transform(square, circle))  # transform the square into a circle
           self.play(
               square.animate.set_fill(PINK, opacity=0.5)
           )  # color the circle on screen

2. Render ``AnimatedSquareToCircle`` by running the following command in the command line:

.. code-block:: bash

   manim -pql scene.py AnimatedSquareToCircle

The following animation will render:

.. manim:: AnimatedSquareToCircle2
   :hide_source:

   class AnimatedSquareToCircle2(Scene):
       def construct(self):
           circle = Circle()  # create a circle
           square = Square()  # create a square

           self.play(Create(square))  # show the square on screen
           self.play(square.animate.rotate(PI / 4))  # rotate the square
           self.play(Transform(square, circle))  # transform the square into a circle
           self.play(square.animate.set_fill(PINK, opacity=0.5))  # color the circle on screen

The first ``self.play`` creates the square. The second animates rotating it 45 degrees.
The third transforms the square into a circle, and the last colors the circle pink.
Although the end result is the same as that of ``SquareToCircle``, ``.animate`` shows
``rotate`` and ``set_fill`` being applied to the ``Mobject`` dynamically, instead of creating them
with the changes already applied.

Try other methods, like ``flip`` or ``shift``, and see what happens.

3. Open ``scene.py``, and add the following code snippet below the ``AnimatedSquareToCircle`` class:

.. code-block:: python

   class DifferentRotations(Scene):
       def construct(self):
           left_square = Square(color=BLUE, fill_opacity=0.7).shift(2 * LEFT)
           right_square = Square(color=GREEN, fill_opacity=0.7).shift(2 * RIGHT)
           self.play(
               left_square.animate.rotate(PI), Rotate(right_square, angle=PI), run_time=2
           )
           self.wait()

4. Render ``DifferentRotations`` by running the following command in the command line:

.. code-block:: bash

   manim -pql scene.py DifferentRotations

The following animation will render:

.. manim:: DifferentRotations2
   :hide_source:

   class DifferentRotations2(Scene):
       def construct(self):
           left_square = Square(color=BLUE, fill_opacity=0.7).shift(2*LEFT)
           right_square = Square(color=GREEN, fill_opacity=0.7).shift(2*RIGHT)
           self.play(left_square.animate.rotate(PI), Rotate(right_square, angle=PI), run_time=2)
           self.wait()

This ``Scene`` illustrates the quirks of ``.animate``. When using ``.animate``, Manim
actually takes a ``Mobject``'s starting state and its ending state and interpolates the two.
In the ``AnimatedSquareToCircle`` class, you can observe this when the square rotates:
the corners of the square appear to contract slightly as they move into the positions required
for the first square to transform into the second one.

In ``DifferentRotations``, the difference between ``.animate``'s interpretation of rotation and the
``Rotate`` method is far more apparent. The starting and ending states of a ``Mobject`` rotated 180 degrees
are the same, so ``.animate`` tries to interpolate two identical objects and the result is the left square.
If you find that your own usage of ``.animate`` is causing similar unwanted behavior, consider
using conventional animation methods like the right square, which uses ``Rotate``.


``Transform`` vs ``ReplacementTransform``
*****************************************
The difference between ``Transform`` and ``ReplacementTransform`` is that ``Transform(mob1, mob2)`` transforms the points
(as well as other attributes like color) of ``mob1`` into the points/attributes of ``mob2``.

``ReplacementTransform(mob1, mob2)`` on the other hand literally replaces ``mob1`` on the scene with ``mob2``.

The use of ``ReplacementTransform`` or ``Transform`` is mostly up to personal preference. They can be used to accomplish the same effect, as shown below.

.. code-block:: python

    class TwoTransforms(Scene):
        def transform(self):
            a = Circle()
            b = Square()
            c = Triangle()
            self.play(Transform(a, b))
            self.play(Transform(a, c))
            self.play(FadeOut(a))

        def replacement_transform(self):
            a = Circle()
            b = Square()
            c = Triangle()
            self.play(ReplacementTransform(a, b))
            self.play(ReplacementTransform(b, c))
            self.play(FadeOut(c))

        def construct(self):
            self.transform()
            self.wait(0.5)  # wait for 0.5 seconds
            self.replacement_transform()


However, in some cases it is more beneficial to use ``Transform``, like when you are transforming several mobjects one after the other.
The code below avoids having to keep a reference to the last mobject that was transformed.

.. manim:: TransformCycle

    class TransformCycle(Scene):
        def construct(self):
            a = Circle()
            t1 = Square()
            t2 = Triangle()
            self.add(a)
            self.wait()
            for t in [t1,t2]:
                self.play(Transform(a,t))

************
You're done!
************

With a working installation of Manim and this sample project under your belt,
you're ready to start creating animations of your own.  To learn
more about what Manim is doing under the hood, move on to the next tutorial:
:doc:`output_and_config`.  For an overview of
Manim's features, as well as its configuration and other settings, check out the
other :doc:`Tutorials <../tutorials/index>`.  For a list of all available features, refer to the
:doc:`../reference` page.


# Extracted from /Users/hochmax/learn/manim/example_scenes/customtex.py
from manim import *


class TexTemplateFromCLI(Scene):
    """This scene uses a custom TexTemplate file.
    The path of the TexTemplate _must_ be passed with the command line
    argument `--tex_template <path to template>`.
    For this scene, you can use the custom_template.tex file next to it.
    This scene will fail to render if a tex_template.tex that doesn't
    import esvect is passed, and will throw a LaTeX error in that case.
    """

    def construct(self):
        text = MathTex(r"\vv{vb}")
        self.play(Write(text))
        self.wait(1)


class InCodeTexTemplate(Scene):
    """This example scene demonstrates how to modify the tex template
    for a particular scene from the code for the scene itself.
    """

    def construct(self):
        # Create a new template
        myTemplate = TexTemplate()

        # Add packages to the template
        myTemplate.add_to_preamble(r"\usepackage{esvect}")

        # Set the compiler and output format (default: latex and .dvi)
        # possible tex compilers: "latex", "pdflatex", "xelatex", "lualatex", "luatex"
        # possible output formats: ".dvi",  ".pdf", and ".xdv"
        myTemplate.tex_compiler = "latex"
        myTemplate.output_format = ".dvi"

        # To use this template in a Tex() or MathTex() object
        # use the keyword argument tex_template
        text = MathTex(r"\vv{vb}", tex_template=myTemplate)
        self.play(Write(text))
        self.wait(1)


# Extracted from /Users/hochmax/learn/manim/example_scenes/opengl.py
from pathlib import Path

import manim.utils.opengl as opengl
from manim import *
from manim.opengl import *  # type: ignore

# Copied from https://3b1b.github.io/manim/getting_started/example_scenes.html#surfaceexample.
# Lines that do not yet work with the Community Version are commented.


def get_plane_mesh(context):
    shader = Shader(context, name="vertex_colors")
    attributes = np.zeros(
        18,
        dtype=[
            ("in_vert", np.float32, (4,)),
            ("in_color", np.float32, (4,)),
        ],
    )
    attributes["in_vert"] = np.array(
        [
            # xy plane
            [-1, -1, 0, 1],
            [-1, 1, 0, 1],
            [1, 1, 0, 1],
            [-1, -1, 0, 1],
            [1, -1, 0, 1],
            [1, 1, 0, 1],
            # yz plane
            [0, -1, -1, 1],
            [0, -1, 1, 1],
            [0, 1, 1, 1],
            [0, -1, -1, 1],
            [0, 1, -1, 1],
            [0, 1, 1, 1],
            # xz plane
            [-1, 0, -1, 1],
            [-1, 0, 1, 1],
            [1, 0, 1, 1],
            [-1, 0, -1, 1],
            [1, 0, -1, 1],
            [1, 0, 1, 1],
        ],
    )
    attributes["in_color"] = np.array(
        [
            # xy plane
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            # yz plane
            [0, 1, 0, 1],
            [0, 1, 0, 1],
            [0, 1, 0, 1],
            [0, 1, 0, 1],
            [0, 1, 0, 1],
            [0, 1, 0, 1],
            # xz plane
            [0, 0, 1, 1],
            [0, 0, 1, 1],
            [0, 0, 1, 1],
            [0, 0, 1, 1],
            [0, 0, 1, 1],
            [0, 0, 1, 1],
        ],
    )
    return Mesh(shader, attributes)


class TextTest(Scene):
    def construct(self):
        import string

        text = Text(string.ascii_lowercase, stroke_width=4, stroke_color=BLUE).scale(2)
        text2 = (
            Text(string.ascii_uppercase, stroke_width=4, stroke_color=BLUE)
            .scale(2)
            .next_to(text, DOWN)
        )
        # self.add(text, text2)
        self.play(Write(text))
        self.play(Write(text2))
        self.interactive_embed()


class GuiTest(Scene):
    def construct(self):
        mesh = get_plane_mesh(self.renderer.context)
        # mesh.attributes["in_vert"][:, 0]
        self.add(mesh)

        def update_mesh(mesh, dt):
            mesh.model_matrix = np.matmul(
                opengl.rotation_matrix(z=dt),
                mesh.model_matrix,
            )

        mesh.add_updater(update_mesh)

        self.interactive_embed()


class GuiTest2(Scene):
    def construct(self):
        mesh = get_plane_mesh(self.renderer.context)
        mesh.attributes["in_vert"][:, 0] -= 2
        self.add(mesh)

        mesh2 = get_plane_mesh(self.renderer.context)
        mesh2.attributes["in_vert"][:, 0] += 2
        self.add(mesh2)

        def callback(sender, data):
            mesh2.attributes["in_color"][:, 3] = dpg.get_value(sender)

        self.widgets.append(
            {
                "name": "mesh2 opacity",
                "widget": "slider_float",
                "callback": callback,
                "min_value": 0,
                "max_value": 1,
                "default_value": 1,
            },
        )

        self.interactive_embed()


class ThreeDMobjectTest(Scene):
    def construct(self):
        # config["background_color"] = "#333333"

        s = Square(fill_opacity=0.5).shift(2 * RIGHT)
        self.add(s)

        sp = Sphere().shift(2 * LEFT)
        self.add(sp)

        mesh = get_plane_mesh(self.renderer.context)
        self.add(mesh)

        def update_mesh(mesh, dt):
            mesh.model_matrix = np.matmul(
                opengl.rotation_matrix(z=dt),
                mesh.model_matrix,
            )

        mesh.add_updater(update_mesh)

        self.interactive_embed()


class NamedFullScreenQuad(Scene):
    def construct(self):
        surface = FullScreenQuad(self.renderer.context, fragment_shader_name="design_3")
        surface.shader.set_uniform(
            "u_resolution",
            (config["pixel_width"], config["pixel_height"], 0.0),
        )
        surface.shader.set_uniform("u_time", 0)
        self.add(surface)

        t = 0

        def update_surface(surface, dt):
            nonlocal t
            t += dt
            surface.shader.set_uniform("u_time", t / 4)

        surface.add_updater(update_surface)

        # self.wait()
        self.interactive_embed()


class InlineFullScreenQuad(Scene):
    def construct(self):
        surface = FullScreenQuad(
            self.renderer.context,
            """
            #version 330


            #define TWO_PI 6.28318530718

            uniform vec2 u_resolution;
            uniform float u_time;
            out vec4 frag_color;

            //  Function from Iñigo Quiles
            //  https://www.shadertoy.com/view/MsS3Wc
            vec3 hsb2rgb( in vec3 c ){
                vec3 rgb = clamp(abs(mod(c.x*6.0+vec3(0.0,4.0,2.0),
                                         6.0)-3.0)-1.0,
                                 0.0,
                                 1.0 );
                rgb = rgb*rgb*(3.0-2.0*rgb);
                return c.z * mix( vec3(1.0), rgb, c.y);
            }

            void main(){
                vec2 st = gl_FragCoord.xy/u_resolution;
                vec3 color = vec3(0.0);

                // Use polar coordinates instead of cartesian
                vec2 toCenter = vec2(0.5)-st;
                float angle = atan(toCenter.y,toCenter.x);
                angle += u_time;
                float radius = length(toCenter)*2.0;

                // Map the angle (-PI to PI) to the Hue (from 0 to 1)
                // and the Saturation to the radius
                color = hsb2rgb(vec3((angle/TWO_PI)+0.5,radius,1.0));

                frag_color = vec4(color,1.0);
            }
            """,
        )
        surface.shader.set_uniform(
            "u_resolution",
            (config["pixel_width"], config["pixel_height"]),
        )
        shader_time = 0

        def update_surface(surface):
            nonlocal shader_time
            surface.shader.set_uniform("u_time", shader_time)
            shader_time += 1 / 60.0

        surface.add_updater(update_surface)
        self.add(surface)
        # self.wait(5)
        self.interactive_embed()


class SimpleInlineFullScreenQuad(Scene):
    def construct(self):
        surface = FullScreenQuad(
            self.renderer.context,
            """
            #version 330

            uniform float v_red;
            uniform float v_green;
            uniform float v_blue;
            out vec4 frag_color;

            void main() {
              frag_color = vec4(v_red, v_green, v_blue, 1);
            }
            """,
        )
        surface.shader.set_uniform("v_red", 0)
        surface.shader.set_uniform("v_green", 0)
        surface.shader.set_uniform("v_blue", 0)

        increase = True
        val = 0.5
        surface.shader.set_uniform("v_red", val)
        surface.shader.set_uniform("v_green", val)
        surface.shader.set_uniform("v_blue", val)

        def update_surface(mesh, dt):
            nonlocal increase
            nonlocal val
            if increase:
                val += dt
            else:
                val -= dt
            if val >= 1:
                increase = False
            elif val <= 0:
                increase = True
            surface.shader.set_uniform("v_red", val)
            surface.shader.set_uniform("v_green", val)
            surface.shader.set_uniform("v_blue", val)

        surface.add_updater(update_surface)

        self.add(surface)
        self.wait(5)


class InlineShaderExample(Scene):
    def construct(self):
        config["background_color"] = "#333333"

        c = Circle(fill_opacity=0.7).shift(UL)
        self.add(c)

        shader = Shader(
            self.renderer.context,
            source={
                "vertex_shader": """
                #version 330

                in vec4 in_vert;
                in vec4 in_color;
                out vec4 v_color;
                uniform mat4 u_model_view_matrix;
                uniform mat4 u_projection_matrix;

                void main() {
                    v_color = in_color;
                    vec4 camera_space_vertex = u_model_view_matrix * in_vert;
                    vec4 clip_space_vertex = u_projection_matrix * camera_space_vertex;
                    gl_Position = clip_space_vertex;
                }
            """,
                "fragment_shader": """
            #version 330

            in vec4 v_color;
            out vec4 frag_color;

            void main() {
              frag_color = v_color;
            }
            """,
            },
        )
        shader.set_uniform("u_model_view_matrix", opengl.view_matrix())
        shader.set_uniform(
            "u_projection_matrix",
            opengl.orthographic_projection_matrix(),
        )

        attributes = np.zeros(
            6,
            dtype=[
                ("in_vert", np.float32, (4,)),
                ("in_color", np.float32, (4,)),
            ],
        )
        attributes["in_vert"] = np.array(
            [
                [-1, -1, 0, 1],
                [-1, 1, 0, 1],
                [1, 1, 0, 1],
                [-1, -1, 0, 1],
                [1, -1, 0, 1],
                [1, 1, 0, 1],
            ],
        )
        attributes["in_color"] = np.array(
            [
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
            ],
        )
        mesh = Mesh(shader, attributes)
        self.add(mesh)

        self.wait(5)
        # self.embed_2()


class NamedShaderExample(Scene):
    def construct(self):
        shader = Shader(self.renderer.context, "manim_coords")
        shader.set_uniform("u_color", (0.0, 1.0, 0.0, 1.0))

        view_matrix = self.camera.formatted_view_matrix
        shader.set_uniform("u_model_view_matrix", view_matrix)
        shader.set_uniform(
            "u_projection_matrix",
            opengl.perspective_projection_matrix(),
        )
        attributes = np.zeros(
            6,
            dtype=[
                ("in_vert", np.float32, (4,)),
            ],
        )
        attributes["in_vert"] = np.array(
            [
                [-1, -1, 0, 1],
                [-1, 1, 0, 1],
                [1, 1, 0, 1],
                [-1, -1, 0, 1],
                [1, -1, 0, 1],
                [1, 1, 0, 1],
            ],
        )
        mesh = Mesh(shader, attributes)
        self.add(mesh)

        self.wait(5)


class InteractiveDevelopment(Scene):
    def construct(self):
        circle = Circle()
        circle.set_fill(BLUE, opacity=0.5)
        circle.set_stroke(BLUE_E, width=4)
        square = Square()

        self.play(Create(square))
        self.wait()

        # This opens an iPython terminal where you can keep writing
        # lines as if they were part of this construct method.
        # In particular, 'square', 'circle' and 'self' will all be
        # part of the local namespace in that terminal.
        # self.embed()

        # Try copying and pasting some of the lines below into
        # the interactive shell
        self.play(ReplacementTransform(square, circle))
        self.wait()
        self.play(circle.animate.stretch(4, 0))
        self.play(Rotate(circle, 90 * DEGREES))
        self.play(circle.animate.shift(2 * RIGHT).scale(0.25))

        # text = Text(
        #     """
        #     In general, using the interactive shell
        #     is very helpful when developing new scenes
        # """
        # )
        # self.play(Write(text))

        # # In the interactive shell, you can just type
        # # play, add, remove, clear, wait, save_state and restore,
        # # instead of self.play, self.add, self.remove, etc.

        # # To interact with the window, type touch().  You can then
        # # scroll in the window, or zoom by holding down 'z' while scrolling,
        # # and change camera perspective by holding down 'd' while moving
        # # the mouse.  Press 'r' to reset to the standard camera position.
        # # Press 'q' to stop interacting with the window and go back to
        # # typing new commands into the shell.

        # # In principle you can customize a scene to be responsive to
        # # mouse and keyboard interactions
        # always(circle.move_to, self.mouse_point)


class SurfaceExample(Scene):
    def construct(self):
        # surface_text = Text("For 3d scenes, try using surfaces")
        # surface_text.fix_in_frame()
        # surface_text.to_edge(UP)
        # self.add(surface_text)
        # self.wait(0.1)

        torus1 = Torus(major_radius=1, minor_radius=1)
        torus2 = Torus(major_radius=3, minor_radius=1)
        sphere = Sphere(radius=3, resolution=torus1.resolution)
        # You can texture a surface with up to two images, which will
        # be interpreted as the side towards the light, and away from
        # the light.  These can be either urls, or paths to a local file
        # in whatever you've set as the image directory in
        # the custom_config.yml file

        script_location = Path(__file__).resolve().parent
        day_texture = (
            script_location / "assets" / "1280px-Whole_world_-_land_and_oceans.jpg"
        )
        night_texture = script_location / "assets" / "1280px-The_earth_at_night.jpg"

        surfaces = [
            OpenGLTexturedSurface(surface, day_texture, night_texture)
            for surface in [sphere, torus1, torus2]
        ]

        for mob in surfaces:
            mob.shift(IN)
            mob.mesh = OpenGLSurfaceMesh(mob)
            mob.mesh.set_stroke(BLUE, 1, opacity=0.5)

        # Set perspective
        frame = self.renderer.camera
        frame.set_euler_angles(
            theta=-30 * DEGREES,
            phi=70 * DEGREES,
        )

        surface = surfaces[0]

        self.play(
            FadeIn(surface),
            Create(surface.mesh, lag_ratio=0.01, run_time=3),
        )
        for mob in surfaces:
            mob.add(mob.mesh)
        surface.save_state()
        self.play(Rotate(surface, PI / 2), run_time=2)
        for mob in surfaces[1:]:
            mob.rotate(PI / 2)

        self.play(Transform(surface, surfaces[1]), run_time=3)

        self.play(
            Transform(surface, surfaces[2]),
            # Move camera frame during the transition
            frame.animate.increment_phi(-10 * DEGREES),
            frame.animate.increment_theta(-20 * DEGREES),
            run_time=3,
        )
        # Add ambient rotation
        frame.add_updater(lambda m, dt: m.increment_theta(-0.1 * dt))

        # Play around with where the light is
        # light_text = Text("You can move around the light source")
        # light_text.move_to(surface_text)
        # light_text.fix_in_frame()

        # self.play(FadeTransform(surface_text, light_text))
        light = self.camera.light_source
        self.add(light)
        light.save_state()
        self.play(light.animate.move_to(3 * IN), run_time=5)
        self.play(light.animate.shift(10 * OUT), run_time=5)

        # drag_text = Text("Try moving the mouse while pressing d or s")
        # drag_text.move_to(light_text)
        # drag_text.fix_in_frame()


# Extracted from /Users/hochmax/learn/manim/example_scenes/basic.py
#!/usr/bin/env python


from manim import *

# To watch one of these scenes, run the following:
# python --quality m manim -p example_scenes.py SquareToCircle
#
# Use the flag --quality l for a faster rendering at a lower quality.
# Use -s to skip to the end and just save the final frame
# Use the -p to have preview of the animation (or image, if -s was
# used) pop up once done.
# Use -n <number> to skip ahead to the nth animation of a scene.
# Use -r <number> to specify a resolution (for example, -r 1920,1080
# for a 1920x1080 video)


class OpeningManim(Scene):
    def construct(self):
        title = Tex(r"This is some \LaTeX")
        basel = MathTex(r"\sum_{n=1}^\infty \frac{1}{n^2} = \frac{\pi^2}{6}")
        VGroup(title, basel).arrange(DOWN)
        self.play(
            Write(title),
            FadeIn(basel, shift=DOWN),
        )
        self.wait()

        transform_title = Tex("That was a transform")
        transform_title.to_corner(UP + LEFT)
        self.play(
            Transform(title, transform_title),
            LaggedStart(*(FadeOut(obj, shift=DOWN) for obj in basel)),
        )
        self.wait()

        grid = NumberPlane()
        grid_title = Tex("This is a grid", font_size=72)
        grid_title.move_to(transform_title)

        self.add(grid, grid_title)  # Make sure title is on top of grid
        self.play(
            FadeOut(title),
            FadeIn(grid_title, shift=UP),
            Create(grid, run_time=3, lag_ratio=0.1),
        )
        self.wait()

        grid_transform_title = Tex(
            r"That was a non-linear function \\ applied to the grid",
        )
        grid_transform_title.move_to(grid_title, UL)
        grid.prepare_for_nonlinear_transform()
        self.play(
            grid.animate.apply_function(
                lambda p: p
                + np.array(
                    [
                        np.sin(p[1]),
                        np.sin(p[0]),
                        0,
                    ],
                ),
            ),
            run_time=3,
        )
        self.wait()
        self.play(Transform(grid_title, grid_transform_title))
        self.wait()


class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()
        square = Square()
        square.flip(RIGHT)
        square.rotate(-3 * TAU / 8)
        circle.set_fill(PINK, opacity=0.5)

        self.play(Create(square))
        self.play(Transform(square, circle))
        self.play(FadeOut(square))


class WarpSquare(Scene):
    def construct(self):
        square = Square()
        self.play(
            ApplyPointwiseFunction(
                lambda point: complex_to_R3(np.exp(R3_to_complex(point))),
                square,
            ),
        )
        self.wait()


class WriteStuff(Scene):
    def construct(self):
        example_text = Tex("This is a some text", tex_to_color_map={"text": YELLOW})
        example_tex = MathTex(
            "\\sum_{k=1}^\\infty {1 \\over k^2} = {\\pi^2 \\over 6}",
        )
        group = VGroup(example_text, example_tex)
        group.arrange(DOWN)
        group.width = config["frame_width"] - 2 * LARGE_BUFF

        self.play(Write(example_text))
        self.play(Write(example_tex))
        self.wait()


class UpdatersExample(Scene):
    def construct(self):
        decimal = DecimalNumber(
            0,
            show_ellipsis=True,
            num_decimal_places=3,
            include_sign=True,
        )
        square = Square().to_edge(UP)

        decimal.add_updater(lambda d: d.next_to(square, RIGHT))
        decimal.add_updater(lambda d: d.set_value(square.get_center()[1]))
        self.add(square, decimal)
        self.play(
            square.animate.to_edge(DOWN),
            rate_func=there_and_back,
            run_time=5,
        )
        self.wait()


class SpiralInExample(Scene):
    def construct(self):
        logo_green = "#81b29a"
        logo_blue = "#454866"
        logo_red = "#e07a5f"

        font_color = "#ece6e2"

        pi = MathTex(r"\pi").scale(7).set_color(font_color)
        pi.shift(2.25 * LEFT + 1.5 * UP)

        circle = Circle(color=logo_green, fill_opacity=0.7, stroke_width=0).shift(LEFT)
        square = Square(color=logo_blue, fill_opacity=0.8, stroke_width=0).shift(UP)
        triangle = Triangle(color=logo_red, fill_opacity=0.9, stroke_width=0).shift(
            RIGHT
        )
        pentagon = Polygon(
            *[
                [np.cos(2 * np.pi / 5 * i), np.sin(2 * np.pi / 5 * i), 0]
                for i in range(5)
            ],
            color=PURPLE_B,
            fill_opacity=1,
            stroke_width=0,
        ).shift(UP + 2 * RIGHT)
        shapes = VGroup(triangle, square, circle, pentagon, pi)
        self.play(SpiralIn(shapes, fade_in_fraction=0.9))
        self.wait()
        self.play(FadeOut(shapes))


Triangle.set_default(stroke_width=20)


class LineJoints(Scene):
    def construct(self):
        t1 = Triangle()
        t2 = Triangle(joint_type=LineJointType.ROUND)
        t3 = Triangle(joint_type=LineJointType.BEVEL)

        grp = VGroup(t1, t2, t3).arrange(RIGHT)
        grp.set(width=config.frame_width - 1)

        self.add(grp)


# See many more examples at https://docs.manim.community/en/stable/examples.html


# Extracted from /Users/hochmax/learn/manim/example_scenes/advanced_tex_fonts.py
from manim import *

# French Cursive LaTeX font example from http://jf.burnol.free.fr/showcase.html

# Example 1 Manually creating a Template

TemplateForFrenchCursive = TexTemplate(
    preamble=r"""
\usepackage[english]{babel}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage[T1]{fontenc}
\usepackage[default]{frcursive}
\usepackage[eulergreek,noplusnominus,noequal,nohbar,%
nolessnomore,noasterisk]{mathastext}
""",
)


def FrenchCursive(*tex_strings, **kwargs):
    return Tex(*tex_strings, tex_template=TemplateForFrenchCursive, **kwargs)


class TexFontTemplateManual(Scene):
    """An example scene that uses a manually defined TexTemplate() object to create
    LaTeX output in French Cursive font"""

    def construct(self):
        self.add(Tex("Tex Font Example").to_edge(UL))
        self.play(Create(FrenchCursive("$f: A \\longrightarrow B$").shift(UP)))
        self.play(Create(FrenchCursive("Behold! We can write math in French Cursive")))
        self.wait(1)
        self.play(
            Create(
                Tex(
                    "See more font templates at \\\\ http://jf.burnol.free.fr/showcase.html",
                ).shift(2 * DOWN),
            ),
        )
        self.wait(2)


# Example 2, using a Template from the collection


class TexFontTemplateLibrary(Scene):
    """An example scene that uses TexTemplate objects from the TexFontTemplates collection
    to create sample LaTeX output in every font that will compile on the local system.

    Please Note:
    Many of the in the TexFontTemplates collection require that specific fonts
    are installed on your local machine.
    For example, choosing the template TexFontTemplates.comic_sans will
    not compile if the Comic Sans Micrososft font is not installed.

    This scene will only render those Templates that do not cause a TeX
    compilation error on your system. Furthermore, some of the ones that do render,
    may still render incorrectly. This is beyond the scope of manim.
    Feel free to experiment.
    """

    def construct(self):
        def write_one_line(template):
            x = Tex(template.description, tex_template=template).shift(UP)
            self.play(Create(x))
            self.wait(1)
            self.play(FadeOut(x))

        examples = [
            TexFontTemplates.american_typewriter,  # "American Typewriter"
            TexFontTemplates.antykwa,  # "Antykwa Półtawskiego (TX Fonts for Greek and math symbols)"
            TexFontTemplates.apple_chancery,  # "Apple Chancery"
            TexFontTemplates.auriocus_kalligraphicus,  # "Auriocus Kalligraphicus (Symbol Greek)"
            TexFontTemplates.baskervald_adf_fourier,  # "Baskervald ADF with Fourier"
            TexFontTemplates.baskerville_it,  # "Baskerville (Italic)"
            TexFontTemplates.biolinum,  # "Biolinum"
            TexFontTemplates.brushscriptx,  # "BrushScriptX-Italic (PX math and Greek)"
            TexFontTemplates.chalkboard_se,  # "Chalkboard SE"
            TexFontTemplates.chalkduster,  # "Chalkduster"
            TexFontTemplates.comfortaa,  # "Comfortaa"
            TexFontTemplates.comic_sans,  # "Comic Sans MS"
            TexFontTemplates.droid_sans,  # "Droid Sans"
            TexFontTemplates.droid_sans_it,  # "Droid Sans (Italic)"
            TexFontTemplates.droid_serif,  # "Droid Serif"
            TexFontTemplates.droid_serif_px_it,  # "Droid Serif (PX math symbols) (Italic)"
            TexFontTemplates.ecf_augie,  # "ECF Augie (Euler Greek)"
            TexFontTemplates.ecf_jd,  # "ECF JD (with TX fonts)"
            TexFontTemplates.ecf_skeetch,  # "ECF Skeetch (CM Greek)"
            TexFontTemplates.ecf_tall_paul,  # "ECF Tall Paul (with Symbol font)"
            TexFontTemplates.ecf_webster,  # "ECF Webster (with TX fonts)"
            TexFontTemplates.electrum_adf,  # "Electrum ADF (CM Greek)"
            TexFontTemplates.epigrafica,  # Epigrafica
            TexFontTemplates.fourier_utopia,  # "Fourier Utopia (Fourier upright Greek)"
            TexFontTemplates.french_cursive,  # "French Cursive (Euler Greek)"
            TexFontTemplates.gfs_bodoni,  # "GFS Bodoni"
            TexFontTemplates.gfs_didot,  # "GFS Didot (Italic)"
            TexFontTemplates.gfs_neoHellenic,  # "GFS NeoHellenic"
            TexFontTemplates.gnu_freesans_tx,  # "GNU FreeSerif (and TX fonts symbols)"
            TexFontTemplates.gnu_freeserif_freesans,  # "GNU FreeSerif and FreeSans"
            TexFontTemplates.helvetica_fourier_it,  # "Helvetica with Fourier (Italic)"
            TexFontTemplates.latin_modern_tw_it,  # "Latin Modern Typewriter Proportional (CM Greek) (Italic)"
            TexFontTemplates.latin_modern_tw,  # "Latin Modern Typewriter Proportional"
            TexFontTemplates.libertine,  # "Libertine"
            TexFontTemplates.libris_adf_fourier,  # "Libris ADF with Fourier"
            TexFontTemplates.minion_pro_myriad_pro,  # "Minion Pro and Myriad Pro (and TX fonts symbols)"
            TexFontTemplates.minion_pro_tx,  # "Minion Pro (and TX fonts symbols)"
            TexFontTemplates.new_century_schoolbook,  # "New Century Schoolbook (Symbol Greek)"
            TexFontTemplates.new_century_schoolbook_px,  # "New Century Schoolbook (Symbol Greek, PX math symbols)"
            TexFontTemplates.noteworthy_light,  # "Noteworthy Light"
            TexFontTemplates.palatino,  # "Palatino (Symbol Greek)"
            TexFontTemplates.papyrus,  # "Papyrus"
            TexFontTemplates.romande_adf_fourier_it,  # "Romande ADF with Fourier (Italic)"
            TexFontTemplates.slitex,  # "SliTeX (Euler Greek)"
            TexFontTemplates.times_fourier_it,  # "Times with Fourier (Italic)"
            TexFontTemplates.urw_avant_garde,  # "URW Avant Garde (Symbol Greek)"
            TexFontTemplates.urw_zapf_chancery,  # "URW Zapf Chancery (CM Greek)"
            TexFontTemplates.venturis_adf_fourier_it,  # "Venturis ADF with Fourier (Italic)"
            TexFontTemplates.verdana_it,  # "Verdana (Italic)"
            TexFontTemplates.vollkorn_fourier_it,  # "Vollkorn with Fourier (Italic)"
            TexFontTemplates.vollkorn,  # "Vollkorn (TX fonts for Greek and math symbols)"
            TexFontTemplates.zapf_chancery,  # "Zapf Chancery"
        ]

        self.add(Tex("Tex Font Template Example").to_edge(UL))

        for font in examples:
            try:
                write_one_line(font)
            except Exception:
                print("FAILURE on ", font.description, " - skipping.")

        self.play(
            Create(
                Tex(
                    "See more font templates at \\\\ http://jf.burnol.free.fr/showcase.html",
                ).shift(2 * DOWN),
            ),
        )
        self.wait(2)


