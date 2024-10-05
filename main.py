from fastapi import FastAPI, File, UploadFile, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from transformers import pipeline
import PyPDF2
from io import BytesIO

app = FastAPI()

class ChatRequest(BaseModel):
    question: str

response = requests.post("https://your-fastapi-service.onrender.com/summarize", files=files)

# Initialize the summarization and QA pipelines
summarizer = pipeline("summarization")
qa_pipeline = pipeline("question-answering")

# Store the uploaded PDF content temporarily
pdf_text = ""

@app.post("/summarize")
async def summarize(file: UploadFile = File(...)):
    global pdf_text
    contents = await file.read()
    pdf_stream = BytesIO(contents)
    pdf_reader = PyPDF2.PdfReader(pdf_stream)
    text = ""

    # Extract text from each page
    for page in pdf_reader.pages:
        text += page.extract_text() + " "

    pdf_text = text  # Store the extracted text for chat

    if not pdf_text.strip():
        return JSONResponse(content={"error": "No text found in the PDF."}, status_code=400)

    # Summarize the text
    summaries = []
    chunk_size = 1000  # Adjust based on text length
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        summary = summarizer(chunk, min_length=50, max_length=150, do_sample=False)
        summaries.append(summary[0]['summary_text'])

    final_summary = "\n".join(summaries)
    return JSONResponse(content={"summary": final_summary})

@app.post("/chat")
async def chat(chat_request: ChatRequest = Body(...)):
    global pdf_text
    question = chat_request.question

    if pdf_text:
        # Split text into manageable chunks
        chunks = pdf_text.split('. ')  # Adjust to better segment text
        answers = []

        for chunk in chunks:
            result = qa_pipeline(question=question, context=chunk)
            if result['score'] > 0.1:  # Adjust threshold based on testing
                answers.append(result['answer'])

        # Remove duplicates
        unique_answers = list(set(answers))
        
        return JSONResponse(content={"answers": unique_answers})
    else:
        return JSONResponse(content={"answers": ["No PDF content available for answering."]})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
