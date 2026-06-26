# ✍️ Pixel → Paper

### Transform Digital Documents into Personalized Handwritten Documents

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Deep Learning](https://img.shields.io/badge/Deep%20Learning-CNN-orange)
![Dash](https://img.shields.io/badge/Dash-Framework-blue)
![Flask](https://img.shields.io/badge/Flask-Backend-black)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📖 Overview

**Pixel → Paper** is an AI-powered document conversion system that transforms digital documents into realistic handwritten-style outputs while preserving the original document layout, diagrams, tables, and embedded images.

The project combines Deep Learning-inspired image processing techniques with handwriting simulation to generate documents that closely resemble natural handwritten notes.

---

## ✨ Features

* 📝 Convert digital PDFs into handwritten-style PDFs
* ✍️ Support for custom handwriting (.ttf) fonts
* 🖼️ Convert embedded images into pencil-sketch illustrations
* 📐 Preserve document layout and formatting
* 📊 Maintain diagrams, tables, lines, and geometric shapes
* 👀 Real-time document preview
* 📄 Export converted documents as PDF
* 🖼️ Export each page as PNG and JPG
* ⚡ Fast and modular processing pipeline

---

## 🧠 Deep Learning Foundation

Pixel → Paper is inspired by **Convolutional Neural Networks (CNNs)** to emulate handwriting characteristics.

The system applies CNN-inspired processing techniques to:

* Extract spatial features
* Preserve document structure
* Simulate handwriting strokes
* Generate sketch-like visuals
* Mimic natural ink variation

---

## 🏗 Project Architecture

```
User Upload
     │
     ▼
PDF + Handwriting Font (.ttf)
     │
     ▼
Document Parsing
(PyMuPDF)
     │
     ▼
Text Processing
     │
     ▼
Handwriting Rendering
     │
     ▼
Image Sketch Conversion
     │
     ▼
Layout Reconstruction
     │
     ▼
Output Generation
(PDF • PNG • JPG)
```

---

## 🔄 Conversion Pipeline

1. Upload PDF document
2. Upload handwriting font (.ttf)
3. Parse document pages
4. Extract text, images, and shapes
5. Convert images into sketch format
6. Render text using handwriting simulation
7. Preserve layout and formatting
8. Generate handwritten document
9. Download converted files

---

## 🛠 Technologies Used

### Programming Language

* Python

### Frontend

* Dash

### Backend

* Flask

### Libraries

* PyMuPDF
* Pillow (PIL)
* OpenCV
* NumPy
* FontTools

### Deep Learning Concepts

* CNN-inspired rendering
* Spatial mapping
* Edge detection
* Gaussian blur
* Stroke variation
* Sketch generation

---

## 📂 Project Structure

```
Pixel-To-Paper/
│
├── app.py
├── backend.py
├── requirements.txt
├── README.md
```

---

## 🚀 Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Pixel-To-Paper.git
```

Move into the project folder

```bash
cd Pixel-To-Paper
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

or

```bash
flask run
```

or

```bash
python backend.py
```

(depending on your project structure)

---

## 📸 Output

The application generates:

* 📄 Handwritten PDF
* 🖼️ PNG images (one per page)
* 🖼️ JPG images (one per page)

---

## 💡 Advantages

* Preserves document layout
* Converts images into sketches
* Supports handwritten font rendering
* Multi-format export
* Modular architecture
* Fast processing
* User-friendly workflow

---

## ⚠️ Current Limitations

* Supports only `.ttf` handwriting fonts
* No handwriting extraction from scanned samples
* No pen-pressure simulation
* No mobile-responsive interface
* Limited bold/italic style preservation
* No font preview before conversion

---

## 🚀 Future Enhancements

* 🤖 True CNN-based handwriting synthesis
* 📱 Mobile-responsive interface
* ✍️ Pen-pressure simulation
* 🖋️ Automatic handwriting extraction from PDF, PNG, JPG, and DOCX
* 🔤 Font preview before conversion
* 📄 Universal document format support
* 🎨 Adjustable ink intensity and stroke thickness
* 🧠 AI-powered handwriting generation
* 💾 Layout serialization for reusable templates
* 🎯 Per-section styling customization

---

## 🎯 Applications

* Student handwritten assignments
* Research documentation
* Personalized notes
* Educational content
* Product documentation
* Creative document styling
* Digital archiving

---

## 👨‍💻 Author

**Kumaran S**

B.E. Computer Science and Engineering

Jeppiaar Engineering College

---
