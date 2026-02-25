# Circular Cover Analyzer

An interactive Streamlit-based application for geometric analysis of image primitives.
The system processes an input image, computes circular covers and similarity relationships among detected components, and visualizes the results as downloadable SVG files.

---

## 🚀 Overview

This project implements a complete pipeline for:

* Image preprocessing using OpenCV
* Connected component analysis
* Primitive center extraction
* Circular cover generation
* Convex hull–based grouping
* Pairwise similarity using Levenshtein distance
* Interactive visualization via Streamlit

The application allows users to upload an image, configure parameters, run the analysis pipeline, and preview/download the generated SVG outputs.

---

## 🧩 System Architecture

### 🔹 Frontend (Streamlit UI)

Responsible for:

* Image upload
* Parameter input
* Triggering computation
* SVG preview
* File download

### 🔹 Backend (Python Pipeline)

Responsible for:

* Image preprocessing
* Connected component labeling
* Circular cover computation
* Convex hull grouping
* Similarity computation
* SVG generation

---

## 📁 Project Structure

```
project-root/
│
├── app.py                      # Streamlit UI
├── pipeline.py                 # Main processing pipeline
├── helper_functions/           # Supporting modules
│   ├── get_center.py
│   ├── make_circular_cover.py
│   ├── make_svg_file.py
│   ├── find_similarity.py
│   └── ...
│
├── outputs/                    # Generated SVG outputs (auto-created)
├── temp/                       # Temporary files (auto-created)
├── requirements.txt            # Python dependencies
└── README.md
```

---

## ⚙️ Installation

### 1️⃣ Clone the repository

```bash
git clone <your-repo-url>
cd <repo-folder>
```

---

### 2️⃣ Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

---

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

Launch the Streamlit interface:

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal (usually):

```
http://localhost:8501
```

---

## 🧪 How to Use

1. Upload an input image
2. Enter:

   * **Radius step**
   * **Angle step**
3. Click **Run Processing**
4. Wait for computation to finish
5. Preview generated SVG outputs
6. Download any SVG as needed

---

## 📤 Output Files

The pipeline generates three SVG visualizations:

* **Grouped Primitives** → convex hull grouping
* **Separate Primitives** → individual circular covers
* **Final Output** → similarity-based grouping

All outputs are stored in the `outputs/` directory and available for download via the UI.

---

## 💻 Requirements

* Python ≥ 3.9 (tested on Python 3.10)
* Works on:

  * Linux ✅
  * macOS ✅
  * Windows ✅

---

## ⚠️ Notes on Performance

* The pipeline uses multiprocessing for speed.
* Runtime depends on image size and number of detected components.
* Very large images may require higher memory.

---

## 🌐 Deployment

This app can be deployed for free using:

* Streamlit Community Cloud (recommended)
* Render
* HuggingFace Spaces

---

## 🔮 Future Improvements

Planned enhancements include:

* Progress bar for long computations
* Batch image processing
* Zoom & pan SVG viewer
* Background job queue
* Full SVG asset embedding for portability

---

## 👨‍💻 Author

**Sonu Kumar**
Roll No: 24CS60R22

---

## 📜 License

This project is intended for academic and research purposes.
