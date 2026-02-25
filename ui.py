import streamlit as st
import tempfile
import os

from pipeline import run_pipeline

st.set_page_config(layout="wide")
st.title("Mandala - MTP")

# ================= SESSION STATE INIT =================
if "results_ready" not in st.session_state:
    st.session_state.results_ready = False

if "svg_cache" not in st.session_state:
    st.session_state.svg_cache = {}

# ================= HELPERS =================
def make_svg_responsive(svg_text: str) -> str:
    """
    Inject responsive attributes into SVG so it scales properly.
    """
    if "<svg" in svg_text and "viewBox" not in svg_text:
        svg_text = svg_text.replace(
            "<svg",
            '<svg width="100%" height="100%" preserveAspectRatio="xMidYMid meet"',
            1,
        )
    return svg_text


def display_svg_responsive(svg_content: str, height: int = 500):
    """
    Display SVG inside a responsive scrollable container.
    """
    html = f"""
    <div style="width:100%; height:{height}px; overflow:auto; border:1px solid #ddd; border-radius:8px;">
        <div style="width:100%; height:100%; display:flex; justify-content:center; align-items:center;">
            {svg_content}
        </div>
    </div>
    """
    st.components.v1.html(html, height=height + 20)



import glob
import base64


def display_svg_thumbnail(svg_content: str, height: int = 140):
    """
    Display a small SVG thumbnail inside a box.
    Uses base64 for reliable rendering.
    """
    b64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")

    html = f"""
    <div style="
        width:100%;
        height:{height}px;
        border:1px solid white;              /* thin white border */
        border-radius:8px;
        display:flex;
        justify-content:center;
        align-items:center;
        background:black;                    /* black background */
        overflow:hidden;
    ">
        <img src="data:image/svg+xml;base64,{b64}"
            style="max-width:95%; max-height:95%; object-fit:contain;" />
    </div>
    """
    st.components.v1.html(html, height=height + 10)


# ================= UI INPUTS =================
uploaded_file = st.file_uploader(
    "Upload image",
    type=["png", "jpg", "jpeg"]
)

radius_step = st.number_input("Radius step", min_value=1, value=1)
angle_step = st.number_input("Angle step", min_value=1, value=1)

# ================= RUN BUTTON =================
if st.button("Run Processing"):

    if uploaded_file is None:
        st.warning("Please upload an image.")
        st.stop()

    # reset previous results
    st.session_state.results_ready = False
    st.session_state.svg_cache = {}

    # save uploaded image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(uploaded_file.read())
        temp_image_path = tmp.name

    # run heavy pipeline
    with st.spinner("Processing... this may take some time"):
        run_pipeline(
            temp_image_path,
            radius_step,
            angle_step
        )

    # ================= LOAD SVG FILES =================
    svg_files = {
        "Mandala rectilinear cover": "outputs/rect_cover.svg",
        "Mandala circular cover": "outputs/seperate_primitive.svg",
        "Grouped primitives": "outputs/similar_primitive.svg",
    }

    cache = {}
    for title, path in svg_files.items():
        if os.path.exists(path):
            with open(path, "r") as f:
                svg_data = f.read()
                svg_data = make_svg_responsive(svg_data)
                cache[title] = svg_data
        else:
            st.warning(f"{path} not found.")

    st.session_state.svg_cache = cache
    st.session_state.results_ready = True
    st.success("Processing complete!")

# ================= SHOW RESULTS (PERSISTENT) =================
if st.session_state.results_ready:

    for title, svg_data in st.session_state.svg_cache.items():

        st.subheader(title)

        # ✅ responsive preview (FIXES SCALING)
        display_svg_responsive(svg_data, height=500)

        # ✅ persistent download button (FIXES DISAPPEARING)
        st.download_button(
            label=f"Download {title}",
            data=svg_data,
            file_name=title.replace(" ", "_") + ".svg",
            mime="image/svg+xml",
            key=f"download_{title}"
        )
    # ================= PRIMITIVES FOUND =================
    primitive_dir = "outputs/primitive_found"

    if os.path.exists(primitive_dir):

        primitive_files = sorted(
            glob.glob(os.path.join(primitive_dir, "primitive_*.svg"))
        )

        if primitive_files:
            st.markdown("---")
            st.subheader("Primitives Found")

            # number of thumbnails per row
            cols_per_row = 6

            for i in range(0, len(primitive_files), cols_per_row):
                row_files = primitive_files[i:i + cols_per_row]
                cols = st.columns(cols_per_row)

                for col, svg_path in zip(cols, row_files):
                    with open(svg_path, "r") as f:
                        svg_data = f.read()
                        svg_data = make_svg_responsive(svg_data)

                    with col:
                        display_svg_thumbnail(svg_data, height=140)
