# app.py
import os
import io
import base64
from flask import Flask, send_file
import dash
from dash import dcc, html, Input, Output, State
from backend import process_pdf
from PIL import Image
import fitz

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

server = Flask(__name__)
app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True)
app.title = "PXL → PAPER"

# ---------------- Layout ----------------
app.layout = html.Div([
    html.H2("🖋️ PXL → PAPER — Upload & Preview"),

    html.Div([
        html.Div([
            html.H4("📄 Upload Digital File"),
            dcc.Upload(id="upload-pdf", children=html.Button("Upload File"), multiple=False),
            html.Div(id="pdf-preview", style={"marginTop": "10px"})
        ], style={"width": "48%", "display": "inline-block"}),

        html.Div([
            html.H4("✍️ Upload Handwriting Font (.ttf)"),
            dcc.Upload(id="upload-font", children=html.Button("Upload Font"), multiple=False),
            html.Div(id="font-preview", style={"marginTop": "10px"})
        ], style={"width": "48%", "display": "inline-block", "marginLeft": "4%"})
    ], style={"marginBottom": "30px"}),

    html.Button("✏️ Convert to Handwritten", id="convert-btn", disabled=True),
    html.Div(id="upload-status", style={"marginTop": "10px", "fontWeight": "bold", "color": "#007700"}),

    dcc.Store(id="stored-files"),
    dcc.Store(id="conversion-trigger"),
    dcc.Store(id="scroll-trigger"),

    html.Hr(),

    html.Div(id="preview-block", style={"display": "none"}, children=[
        html.H2("📄 Handwritten Output Preview"),
        dcc.Loading(
            type="default",
            children=html.Div([
                html.Label("Preview Page"),
                dcc.Slider(id="page-slider", min=0, max=0, step=1, value=0),
                html.Img(id="page-preview", style={"width": "100%", "maxWidth": "600px", "marginTop": "20px"})
            ])
        ),
        html.Div([
            html.A("📥 Download PDF", id="download-pdf", href="", target="_blank"),
            html.A("🖼️ Download PNG", id="download-png", href="", target="_blank", style={"marginLeft": "20px"}),
            html.A("🖼️ Download JPG", id="download-jpg", href="", target="_blank", style={"marginLeft": "20px"})
        ], style={"fontWeight": "bold", "fontSize": "18px", "marginTop": "20px"})
    ])
])

# ---------------- Upload Validation ----------------
@app.callback(
    Output("convert-btn", "disabled"),
    Output("upload-status", "children"),
    Output("stored-files", "data"),
    Input("upload-pdf", "contents"),
    Input("upload-pdf", "filename"),
    Input("upload-font", "contents"),
    Input("upload-font", "filename")
)
def validate_uploads(pdf_content, pdf_name, font_content, font_name):
    if not pdf_content or not font_content:
        return True, "⚠️ Upload both digital file and font.", None

    def save_file(content, filename, folder):
        data = content.split(",")[1]
        decoded = base64.b64decode(data)
        path = os.path.join(folder, filename)
        with open(path, "wb") as f:
            f.write(decoded)
        return path

    pdf_path = save_file(pdf_content, pdf_name, UPLOAD_FOLDER)
    font_path = save_file(font_content, font_name, UPLOAD_FOLDER)

    return False, "✅ Files uploaded. Ready to convert.", {
        "pdf_path": pdf_path,
        "font_path": font_path,
        "sketch": True,
        "ink": 30,
        "diagrams": True
    }

# ---------------- File Preview ----------------
@app.callback(
    Output("pdf-preview", "children"),
    Output("font-preview", "children"),
    Input("upload-pdf", "contents"),
    Input("upload-pdf", "filename"),
    Input("upload-font", "contents"),
    Input("upload-font", "filename")
)
def show_file_preview(pdf_content, pdf_name, font_content, font_name):
    def preview_file(content, name):
        if not content:
            return None
        ext = name.split(".")[-1].lower()
        data = content.split(",")[1]
        decoded = base64.b64decode(data)

        if ext in ["png", "jpg", "jpeg"]:
            return html.Img(src=content, style={"maxWidth": "300px"})
        elif ext == "txt":
            text = decoded.decode("utf-8", errors="ignore")[:500]
            return html.Pre(text)
        elif ext == "ttf":
            return html.Div(f"✅ Font '{name}' uploaded.")
        elif ext == "pdf":
            try:
                doc = fitz.open(stream=decoded, filetype="pdf")
                page = doc.load_page(0)
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                encoded = base64.b64encode(img_bytes).decode()
                return html.Img(src=f"data:image/png;base64,{encoded}", style={"maxWidth": "300px"})
            except Exception:
                return html.Div(f"📄 PDF '{name}' uploaded. Preview unavailable.")
        else:
            return html.Div(f"📁 File '{name}' uploaded ({len(decoded)} bytes)")

    return preview_file(pdf_content, pdf_name), preview_file(font_content, font_name)

# ---------------- Trigger Conversion ----------------
@app.callback(Output("conversion-trigger", "data"), Input("convert-btn", "n_clicks"), State("stored-files", "data"))
def trigger_conversion(n_clicks, data):
    return data if n_clicks else None

# ---------------- Conversion & Preview ----------------
output_pages_cache = {}

@app.callback(
    Output("page-preview", "src"),
    Output("page-slider", "max"),
    Output("download-pdf", "href"),
    Output("download-png", "href"),
    Output("download-jpg", "href"),
    Output("preview-block", "style"),
    Output("scroll-trigger", "data"),
    Input("conversion-trigger", "data"),
    Input("page-slider", "value"),
    prevent_initial_call=True
)
def render_preview(data, page_num):
    if not data:
        return "", 0, "", "", "", {"display": "none"}, None

    output_pdf, output_pages = process_pdf(
        digital_path=data["pdf_path"],
        font_path=data["font_path"],
        output_dir=OUTPUT_FOLDER,
        enable_sketch=data["sketch"],
        ink_intensity=data["ink"],
        include_diagrams=data["diagrams"]
    )

    output_pages_cache["pages"] = output_pages
    output_pages_cache["pdf"] = output_pdf

    page_num = page_num or 0
    page_num = min(page_num, len(output_pages) - 1)

    buffer = io.BytesIO()
    output_pages[page_num].save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode()

    base = os.path.basename(output_pdf).replace(".pdf", "")
    return (
        f"data:image/png;base64,{encoded}",
        len(output_pages) - 1,
        f"/download/pdf/{base}.pdf",
        f"/download/png/{base}_{page_num}.png",
        f"/download/jpg/{base}_{page_num}.jpg",
        {"display": "block"},
        True
    )

# ---------------- Client-Side Scroll ----------------
app.clientside_callback(
    """
    function(trigger) {
        if (trigger) {
            const block = document.getElementById("preview-block");
            if (block) {
                block.scrollIntoView({ behavior: "smooth" });
            }
        }
        return null;
    }
    """,
    Output("scroll-anchor", "children"),
    Input("scroll-trigger", "data")
)

# ---------------- Download Routes ----------------
@server.route("/download/<format>/<filename>")
def download_file(format, filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    return send_file(path, as_attachment=True)

# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(debug=True)