import os
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import re

# Ensure the OpenAI API key is set
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

# Initialize the vector database using Chroma
persist_directory = "my_db"
embedding = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"], model="text-embedding-3-large")
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)

# Set up the retriever
retriever = vectordb.as_retriever(search_kwargs={"k": 30})

# Initialize the language model
llm = ChatOpenAI(model_name="gpt-4o", openai_api_key=os.environ["OPENAI_API_KEY"])

# Create the QA chain with return_source_documents set to True
qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)

# Function to process user queries
def process_query(query):
    response = qa_chain.invoke({"query": query})
    answer = response["result"]
    source_docs = response["source_documents"]
    return answer, source_docs

# Function to refine the query using GPT-4
def refine_query_with_gpt4o(user_query):
    messages = [
        {"role": "system", "content": "You are giving instructions to an AI model that must write python scripts which create manim animations. Your input is an abstract topic, which you must map to a reasonable teaching lesson in a ca 5 second long manim video. the video may include text and animation. The AI you are instructing needs very detailed information about what kind of code to produce. \
         Below you have a list of possible components that the other AI might use. Select 10 of them that sound like they can achieve your lesson goal. \
         Tell him to pay attention to the visual layout and the coordinates on the screen. \
         You do not write python code. You do not define the layout. Talk directly to the other model. Be detailed:\
./CODE_OF_CONDUCT.md \
./conftest.py \
./docker/readme.md \
./tests/test_linear_transformation_scene.py \
./tests/test_ipython_magic.py \
./tests/interface/test_commands.py \
./tests/test_camera.py \
./tests/conftest.py \
./tests/test_scene_rendering/infallible_scenes.py \
./tests/test_scene_rendering/simple_scenes.py \
./tests/test_scene_rendering/conftest.py \
./tests/test_scene_rendering/test_file_writer.py \
./tests/test_scene_rendering/test_play_logic.py \
./tests/test_scene_rendering/test_caching_related.py \
./tests/test_scene_rendering/test_sections.py \
./tests/test_scene_rendering/__init__.py \
./tests/test_scene_rendering/test_cli_flags.py \
./tests/test_scene_rendering/test_cairo_renderer.py \
./tests/test_scene_rendering/opengl/test_cli_flags_opengl.py \
./tests/test_scene_rendering/opengl/test_play_logic_opengl.py \
./tests/test_scene_rendering/opengl/test_opengl_renderer.py \
./tests/test_scene_rendering/opengl/__init__.py \
./tests/test_scene_rendering/opengl/test_caching_related_opengl.py \
./tests/module/animation/test_animate.py \
./tests/module/animation/test_animation.py \
./tests/module/animation/test_creation.py \
./tests/module/animation/test_composition.py \
./tests/module/animation/test_override_animation.py \
./tests/module/utils/test_deprecation.py \
./tests/module/utils/test_manim_color.py \
./tests/module/utils/test_file_ops.py \
./tests/module/utils/test_tex.py \
./tests/module/utils/_subdivision_matrices.py \
./tests/module/utils/_split_matrices.py \
./tests/module/utils/test_units.py \
./tests/module/utils/test_color.py \
./tests/module/utils/test_hashing.py \
./tests/module/utils/test_space_ops.py \
./tests/module/utils/test_bezier.py \
./tests/module/scene/test_auto_zoom.py \
./tests/module/scene/test_threed_scene.py \
./tests/module/scene/test_sound.py \
./tests/module/scene/test_scene.py \
./tests/module/mobject/svg/test_svg_mobject.py \
./tests/module/mobject/types/vectorized_mobject/test_vectorized_mobject.py \
./tests/module/mobject/types/vectorized_mobject/test_stroke.py \
./tests/module/mobject/test_boolean_ops.py \
./tests/module/mobject/test_image.py \
./tests/module/mobject/graphing/test_coordinate_system.py \
./tests/module/mobject/graphing/test_ticks.py \
./tests/module/mobject/graphing/test_axes_shift.py \
./tests/module/mobject/graphing/test_number_line.py \
./tests/module/mobject/test_value_tracker.py \
./tests/module/mobject/geometry/test_unit_geometry.py \
./tests/module/mobject/text/test_numbers.py \
./tests/module/mobject/text/test_texmobject.py \
./tests/module/mobject/text/test_text_mobject.py \
./tests/module/mobject/text/test_markup.py \
./tests/module/mobject/mobject/test_family.py \
./tests/module/mobject/mobject/test_copy.py \
./tests/module/mobject/mobject/test_set_attr.py \
./tests/module/mobject/mobject/test_get_set.py \
./tests/module/mobject/mobject/test_opengl_metaclass.py \
./tests/module/mobject/mobject/test_mobject.py \
./tests/module/mobject/test_graph.py \
./tests/assert_utils.py \
./tests/__init__.py \
./tests/utils/logging_tester.py \
./tests/utils/testing_utils.py \
./tests/utils/__init__.py \
./tests/utils/video_tester.py \
./tests/test_code_mobject.py \
./tests/test_graphical_units/test_boolops.py \
./tests/test_graphical_units/test_utils.py \
./tests/test_graphical_units/test_opengl.py \
./tests/test_graphical_units/conftest.py \
./tests/test_graphical_units/test_indication.py \
./tests/test_graphical_units/test_coordinate_systems.py \
./tests/test_graphical_units/test_transform.py \
./tests/test_graphical_units/test_mobjects.py \
./tests/test_graphical_units/test_modifier_methods.py \
./tests/test_graphical_units/test_tables.py \
./tests/test_graphical_units/test_numbers.py \
./tests/test_graphical_units/test_img_and_svg.py \
./tests/test_graphical_units/__init__.py \
./tests/test_graphical_units/test_banner.py \
./tests/test_graphical_units/test_polyhedra.py \
./tests/test_graphical_units/test_creation.py \
./tests/test_graphical_units/test_composition.py \
./tests/test_graphical_units/test_vector_scene.py \
./tests/test_graphical_units/test_threed.py \
./tests/test_graphical_units/test_text.py \
./tests/test_graphical_units/test_brace.py \
./tests/test_graphical_units/test_functions.py \
./tests/test_graphical_units/test_movements.py \
./tests/test_graphical_units/test_transform_matching_parts.py \
./tests/test_graphical_units/test_speed.py \
./tests/test_graphical_units/test_tex_mobject.py \
./tests/test_graphical_units/test_updaters.py \
./tests/test_graphical_units/test_axes.py \
./tests/test_graphical_units/test_specialized.py \
./tests/test_graphical_units/test_geometry.py \
./tests/test_graphical_units/test_probability.py \
./tests/test_plugins/simple_scenes.py \
./tests/test_plugins/test_plugins.py \
./tests/test_plugins/__init__.py \
./tests/miscellaneous/test_version.py \
./tests/test_config.py \
./tests/template_generate_graphical_units_data.py \
./tests/test_logging/bad_tex_scene.py \
./tests/test_logging/test_logging.py \
./tests/test_logging/basic_scenes_write_stuff.py \
./tests/test_logging/basic_scenes_square_to_circle.py \
./tests/test_logging/__init__.py \
./tests/test_logging/basic_scenes_error.py \
./tests/helpers/video_utils.py \
./tests/helpers/__init__.py \
./tests/helpers/graphical_units.py \
./tests/helpers/path_utils.py \
./tests/opengl/test_number_line_opengl.py \
./tests/opengl/test_sound_opengl.py \
./tests/opengl/test_opengl_vectorized_mobject.py \
./tests/opengl/test_config_opengl.py \
./tests/opengl/test_animate_opengl.py \
./tests/opengl/test_axes_shift_opengl.py \
./tests/opengl/test_coordinate_system_opengl.py \
./tests/opengl/test_copy_opengl.py \
./tests/opengl/test_scene_opengl.py \
./tests/opengl/test_composition_opengl.py \
./tests/opengl/test_ipython_magic_opengl.py \
./tests/opengl/__init__.py \
./tests/opengl/test_unit_geometry_opengl.py \
./tests/opengl/test_texmobject_opengl.py \
./tests/opengl/test_svg_mobject_opengl.py \
./tests/opengl/test_text_mobject_opengl.py \
./tests/opengl/test_graph_opengl.py \
./tests/opengl/test_value_tracker_opengl.py \
./tests/opengl/test_family_opengl.py \
./tests/opengl/test_override_animation_opengl.py \
./tests/opengl/test_ticks_opengl.py \
./tests/opengl/test_markup_opengl.py \
./tests/opengl/test_color_opengl.py \
./tests/opengl/test_stroke_opengl.py \
./tests/opengl/test_opengl_surface.py \
./tests/opengl/test_numbers_opengl.py \
./tests/opengl/test_opengl_mobject.py \
./manim/renderer/cairo_renderer.py \
./manim/renderer/shader.py \
./manim/renderer/opengl_renderer_window.py \
./manim/renderer/__init__.py \
./manim/renderer/vectorized_mobject_rendering.py \
./manim/renderer/shader_wrapper.py \
./manim/renderer/shaders/include/NOTE.md \
./manim/renderer/opengl_renderer.py \
./manim/plugins/__init__.py \
./manim/plugins/plugins_flags.py \
./manim/camera/moving_camera.py \
./manim/camera/three_d_camera.py \
./manim/camera/__init__.py \
./manim/camera/multi_camera.py \
./manim/camera/camera.py \
./manim/camera/mapping_camera.py \
./manim/constants.py \
./manim/animation/speedmodifier.py \
./manim/animation/creation.py \
./manim/animation/transform_matching_parts.py \
./manim/animation/__init__.py \
./manim/animation/numbers.py \
./manim/animation/movement.py \
./manim/animation/animation.py \
./manim/animation/specialized.py \
./manim/animation/transform.py \
./manim/animation/updaters/update.py \
./manim/animation/updaters/__init__.py \
./manim/animation/updaters/mobject_update_utils.py \
./manim/animation/indication.py \
./manim/animation/composition.py \
./manim/animation/changing.py \
./manim/animation/rotation.py \
./manim/animation/growing.py \
./manim/animation/fading.py \
./manim/__init__.py \
./manim/utils/sounds.py \
./manim/utils/rate_functions.py \
./manim/utils/tex.py \
./manim/utils/paths.py \
./manim/utils/ipython_magic.py \
./manim/utils/deprecation.py \
./manim/utils/color/__init__.py \
./manim/utils/color/core.py \
./manim/utils/color/AS2700.py \
./manim/utils/color/manim_colors.py \
./manim/utils/color/BS381.py \
./manim/utils/color/XKCD.py \
./manim/utils/color/X11.py \
./manim/utils/bezier.py \
./manim/utils/simple_functions.py \
./manim/utils/file_ops.py \
./manim/utils/__init__.py \
./manim/utils/space_ops.py \
./manim/utils/config_ops.py \
./manim/utils/testing/_test_class_makers.py \
./manim/utils/testing/frames_comparison.py \
./manim/utils/testing/__init__.py \
./manim/utils/testing/_show_diff.py \
./manim/utils/testing/_frames_testers.py \
./manim/utils/opengl.py \
./manim/utils/module_ops.py \
./manim/utils/docbuild/autoaliasattr_directive.py \
./manim/utils/docbuild/autocolor_directive.py \
./manim/utils/docbuild/__init__.py \
./manim/utils/docbuild/manim_directive.py \
./manim/utils/docbuild/module_parsing.py \
./manim/utils/caching.py \
./manim/utils/debug.py \
./manim/utils/unit.py \
./manim/utils/images.py \
./manim/utils/family.py \
./manim/utils/exceptions.py \
./manim/utils/tex_templates.py \
./manim/utils/family_ops.py \
./manim/utils/commands.py \
./manim/utils/hashing.py \
./manim/utils/parameter_parsing.py \
./manim/utils/iterables.py \
./manim/utils/tex_file_writing.py \
./manim/cli/init/__init__.py \
./manim/cli/init/commands.py \
./manim/cli/plugins/__init__.py \
./manim/cli/plugins/commands.py \
./manim/cli/default_group.py \
./manim/cli/render/render_options.py \
./manim/cli/render/global_options.py \
./manim/cli/render/__init__.py \
./manim/cli/render/ease_of_access_options.py \
./manim/cli/render/output_options.py \
./manim/cli/render/commands.py \
./manim/cli/__init__.py \
./manim/cli/cfg/__init__.py \
./manim/cli/cfg/group.py \
./manim/cli/checkhealth/checks.py \
./manim/cli/checkhealth/__init__.py \
./manim/cli/checkhealth/commands.py \
./manim/gui/__init__.py \
./manim/gui/gui.py \
./manim/typing.py \
./manim/scene/zoomed_scene.py \
./manim/scene/three_d_scene.py \
./manim/scene/scene_file_writer.py \
./manim/scene/__init__.py \
./manim/scene/scene.py \
./manim/scene/section.py \
./manim/scene/vector_space_scene.py \
./manim/scene/moving_camera_scene.py \
./manim/mobject/svg/svg_mobject.py \
./manim/mobject/svg/brace.py \
./manim/mobject/svg/__init__.py \
./manim/mobject/matrix.py \
./manim/mobject/types/vectorized_mobject.py \
./manim/mobject/types/__init__.py \
./manim/mobject/types/image_mobject.py \
./manim/mobject/types/point_cloud_mobject.py \
./manim/mobject/three_d/three_dimensions.py \
./manim/mobject/three_d/__init__.py \
./manim/mobject/three_d/three_d_utils.py \
./manim/mobject/three_d/polyhedra.py \
./manim/mobject/vector_field.py \
./manim/mobject/graph.py \
./manim/mobject/__init__.py \
./manim/mobject/logo.py \
./manim/mobject/utils.py \
./manim/mobject/graphing/functions.py \
./manim/mobject/graphing/__init__.py \
./manim/mobject/graphing/number_line.py \
./manim/mobject/graphing/probability.py \
./manim/mobject/graphing/coordinate_systems.py \
./manim/mobject/graphing/scale.py \
./manim/mobject/frame.py \
./manim/mobject/table.py \
./manim/mobject/mobject.py \
./manim/mobject/geometry/line.py \
./manim/mobject/geometry/__init__.py \
./manim/mobject/geometry/shape_matchers.py \
./manim/mobject/geometry/boolean_ops.py \
./manim/mobject/geometry/tips.py \
./manim/mobject/geometry/polygram.py \
./manim/mobject/geometry/arc.py \
./manim/mobject/geometry/labeled.py \
./manim/mobject/text/text_mobject.py \
./manim/mobject/text/__init__.py \
./manim/mobject/text/numbers.py \
./manim/mobject/text/tex_mobject.py \
./manim/mobject/text/code_mobject.py \
./manim/mobject/value_tracker.py \
./manim/mobject/opengl/opengl_geometry.py \
./manim/mobject/opengl/opengl_surface.py \
./manim/mobject/opengl/opengl_mobject.py \
./manim/mobject/opengl/opengl_point_cloud_mobject.py \
./manim/mobject/opengl/__init__.py \
./manim/mobject/opengl/dot_cloud.py \
./manim/mobject/opengl/opengl_compatibility.py \
./manim/mobject/opengl/opengl_vectorized_mobject.py \
./manim/mobject/opengl/opengl_image_mobject.py \
./manim/mobject/opengl/opengl_three_dimensions.py \
./manim/__main__.py \
./manim/_config/__init__.py \
./manim/_config/utils.py \
./manim/_config/logger_utils.py \
./manim/_config/cli_colors.py \
./manim/opengl/__init__.py \
./docs/source/index.rst \
./docs/source/tutorials_guides.rst \
./docs/source/contributing.rst \
./docs/source/changelog/0.11.0-changelog.rst \
./docs/source/changelog/0.1.0-changelog.rst \
./docs/source/changelog/0.13.1-changelog.rst \
./docs/source/changelog/0.9.0-changelog.rst \
./docs/source/changelog/0.6.0-changelog.rst \
./docs/source/changelog/0.16.0-changelog.rst \
./docs/source/changelog/0.18.0-changelog.rst \
./docs/source/changelog/0.8.0-changelog.rst \
./docs/source/changelog/0.15.2-changelog.rst \
./docs/source/changelog/0.7.0-changelog.rst \
./docs/source/changelog/0.17.0-changelog.rst \
./docs/source/changelog/0.10.0-changelog.rst \
./docs/source/changelog/0.17.3-changelog.rst \
./docs/source/changelog/0.15.1-changelog.rst \
./docs/source/changelog/0.17.2-changelog.rst \
./docs/source/changelog/0.15.0-changelog.rst \
./docs/source/changelog/0.5.0-changelog.rst \
./docs/source/changelog/0.2.0-changelog.rst \
./docs/source/changelog/0.12.0-changelog.rst \
./docs/source/changelog/0.17.1-changelog.rst \
./docs/source/changelog/0.3.0-changelog.rst \
./docs/source/changelog/0.13.0-changelog.rst \
./docs/source/changelog/0.1.1-changelog.rst \
./docs/source/changelog/0.14.0-changelog.rst \
./docs/source/changelog/0.4.0-changelog.rst \
./docs/source/reference.rst \
./docs/source/_templates/autosummary/class.rst \
./docs/source/_templates/autosummary/module.rst \
./docs/source/faq/index.rst \
./docs/source/faq/opengl.md \
./docs/source/faq/general.md \
./docs/source/faq/help.md \
./docs/source/faq/internals.md \
./docs/source/faq/installation.md \
./docs/source/contributing/testing.rst \
./docs/source/contributing/docs/admonitions.rst \
./docs/source/contributing/docs/docstrings.rst \
./docs/source/contributing/docs/examples.rst \
./docs/source/contributing/docs/references.rst \
./docs/source/contributing/docs/typings.rst \
./docs/source/contributing/docs.rst \
./docs/source/contributing/development.rst \
./docs/source/contributing/internationalization.rst \
./docs/source/contributing/performance.rst \
./docs/source/plugins.rst \
./docs/source/conf.py \
./docs/source/examples.rst \
./docs/source/installation/docker.rst \
./docs/source/installation/linux.rst \
./docs/source/installation/jupyter.rst \
./docs/source/installation/macos.rst \
./docs/source/installation/conda.rst \
./docs/source/installation/windows.rst \
./docs/source/guides/index.rst \
./docs/source/guides/using_text.rst \
./docs/source/guides/add_voiceovers.rst \
./docs/source/guides/configuration.rst \
./docs/source/guides/deep_dive.rst \
./docs/source/reference_index/cameras.rst \
./docs/source/reference_index/scenes.rst \
./docs/source/reference_index/animations.rst \
./docs/source/reference_index/configuration.rst \
./docs/source/reference_index/mobjects.rst \
./docs/source/reference_index/utilities_misc.rst \
./docs/source/installation.rst \
./docs/source/tutorials/index.rst \
./docs/source/tutorials/output_and_config.rst \
./docs/source/tutorials/building_blocks.rst \
./docs/source/tutorials/quickstart.rst \
./docs/source/changelog.rst \
./README.md \
./CONTRIBUTING.md \
./scripts/template_docsting_with_example.py \
./scripts/extract_frames.py \
./scripts/make_and_open_docs.py \
./scripts/dev_changelog.py \
./.github/PULL_REQUEST_TEMPLATE.md \
./.github/PULL_REQUEST_TEMPLATE/hackathon.md \
./.github/PULL_REQUEST_TEMPLATE/documentation.md \
./.github/PULL_REQUEST_TEMPLATE/bugfix.md \
./.github/scripts/ci_build_cairo.py \
./.github/ISSUE_TEMPLATE/feature_request.md \
./.github/ISSUE_TEMPLATE/installation_issue.md \
./.github/ISSUE_TEMPLATE/bug_report.md \
./example_scenes/customtex.py \
./example_scenes/opengl.py \
./example_scenes/basic.py \
./example_scenes/advanced_tex_fonts.py"},

        {"role": "user", "content": f"Please refine the following query to be more suitable for creating a Manim animation: {user_query}"}
    ]
    response = llm.invoke(messages)
    refined_query = response.content.strip()
    return refined_query

def extract_longest_python_code(text):
    code_blocks = re.findall(r"```python(.*?)```", text, re.DOTALL)
    if not code_blocks:
        return None
    longest_code_block = max(code_blocks, key=len)
    return longest_code_block.strip()

# Example usage
if __name__ == "__main__":
    user_query = "I want to learn the physics of ackermann steering"
    refined_query = refine_query_with_gpt4o(user_query)
    print(refined_query)
    answer, source_docs = process_query(refined_query + "\ndo not split your python code into multiple segments. \
                                        Give the entire python file instead. \
                                        Do not include a main function. \
                                        Position the text in a meaningful relation to the animation. \
                                        Pay attention so that objects dont overlap each other, when new stuff is added. \
                                        Delete old elements when new stuff is plotted \
                                        Make sure to not render objects outside of the screen.")
    print("Response:", answer)
    
    longest_python_code = extract_longest_python_code(answer)
    if longest_python_code:
        with open("manim.py", "w") as file:
            file.write(longest_python_code)
        print("Longest Python code written to manim.py")
    else:
        print("No Python code found in the response.")
    
    print("Source Documents:")
    for doc in source_docs:
        print(doc.metadata["source"])