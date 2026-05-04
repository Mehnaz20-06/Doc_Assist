from pathlib import Path

from flask import Flask, redirect, render_template_string, request, url_for
from werkzeug.utils import secure_filename

from main import DATA_PATH, generate_data_store
from query_data import answer_query

app = Flask(__name__)
ALLOWED_EXTENSIONS = {".md"}

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Docs Q&A</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --ink: #18202b;
      --muted: #5f6b7a;
      --line: #dfe4ea;
      --accent: #176a63;
      --accent-strong: #0f4f49;
      --warn: #9a4f13;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", Arial, sans-serif;
      background: var(--bg);
      color: var(--ink);
    }
    header {
      border-bottom: 1px solid var(--line);
      background: #fff;
    }
    .wrap {
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
    }
    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      min-height: 68px;
    }
    h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 650;
      letter-spacing: 0;
    }
    .model {
      color: var(--muted);
      font-size: 14px;
    }
    main {
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 18px;
      padding: 22px 0;
    }
    section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }
    h2 {
      margin: 0 0 14px;
      font-size: 16px;
      font-weight: 650;
    }
    .doc-list {
      display: grid;
      gap: 8px;
      margin: 0 0 18px;
      padding: 0;
      list-style: none;
    }
    .doc-list li {
      padding: 9px 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      color: var(--muted);
      font-size: 14px;
      overflow-wrap: anywhere;
    }
    form {
      display: grid;
      gap: 12px;
    }
    input[type="file"],
    textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      font: inherit;
    }
    input[type="file"] {
      padding: 9px;
    }
    textarea {
      min-height: 118px;
      resize: vertical;
      padding: 12px;
      line-height: 1.45;
    }
    button {
      border: 0;
      border-radius: 6px;
      background: var(--accent);
      color: white;
      cursor: pointer;
      font: inherit;
      font-weight: 650;
      min-height: 40px;
      padding: 0 14px;
    }
    button:hover { background: var(--accent-strong); }
    .secondary {
      background: #e8efee;
      color: var(--accent-strong);
    }
    .secondary:hover { background: #d8e5e3; }
    .status {
      margin: 0 0 16px;
      padding: 10px 12px;
      border-radius: 6px;
      border: 1px solid #e5d1bd;
      color: var(--warn);
      background: #fff7ef;
      font-size: 14px;
      white-space: pre-wrap;
    }
    .answer {
      margin-top: 16px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcfd;
      line-height: 1.55;
      white-space: pre-wrap;
    }
    .hint {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
      margin: 10px 0 0;
    }
    @media (max-width: 780px) {
      main { grid-template-columns: 1fr; }
      .topbar { align-items: flex-start; flex-direction: column; padding: 14px 0; }
    }
  </style>
</head>
<body>
  <header>
    <div class="wrap topbar">
      <h1>Docs Q&A</h1>
      <div class="model">Vector DB: Chroma | LLM: Ollama phi3:mini</div>
    </div>
  </header>

  <div class="wrap">
    <main>
      <section>
        <h2>Documents</h2>
        <ul class="doc-list">
          {% for doc in docs %}
            <li>{{ doc }}</li>
          {% else %}
            <li>No markdown files yet.</li>
          {% endfor %}
        </ul>

        <form action="/upload" method="post" enctype="multipart/form-data">
          <input type="file" name="document" accept=".md" required>
          <button type="submit">Upload Markdown</button>
        </form>

        <form action="/rebuild" method="post" style="margin-top: 14px;">
          <button class="secondary" type="submit">Rebuild Vector DB</button>
        </form>
        <p class="hint">After adding or editing files, rebuild before asking new questions.</p>
      </section>

      <section>
        <h2>Ask A Question</h2>
        {% if status %}
          <p class="status">{{ status }}</p>
        {% endif %}
        <form action="/ask" method="post">
          <textarea name="question" placeholder="Ask from your documents..." required>{{ question or "" }}</textarea>
          <button type="submit">Ask</button>
        </form>

        {% if answer %}
          <div class="answer">{{ answer }}</div>
        {% endif %}
      </section>
    </main>
  </div>
</body>
</html>
"""


def list_documents():
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    return sorted(path.name for path in DATA_PATH.glob("*.md"))


def render_page(status=None, question=None, answer=None):
    return render_template_string(
        PAGE,
        docs=list_documents(),
        status=status,
        question=question,
        answer=answer,
    )


@app.get("/")
def index():
    return render_page()


@app.post("/upload")
def upload():
    uploaded_file = request.files.get("document")
    if not uploaded_file or not uploaded_file.filename:
        return render_page(status="Choose a markdown file first.")

    filename = secure_filename(uploaded_file.filename)
    if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        return render_page(status="Only .md files are supported.")

    uploaded_file.save(DATA_PATH / filename)
    return render_page(status=f"Uploaded {filename}. Rebuild the vector DB before querying it.")


@app.post("/rebuild")
def rebuild():
    try:
        generate_data_store()
    except Exception as error:
        return render_page(status=f"Rebuild failed: {error}")

    return render_page(status="Vector DB rebuilt successfully.")


@app.post("/ask")
def ask():
    question = request.form.get("question", "").strip()
    if not question:
        return render_page(status="Enter a question first.")

    answer = answer_query(question)
    return render_page(question=question, answer=answer)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
