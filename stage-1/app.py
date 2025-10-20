from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import db
import models
import nlp_parser

app = FastAPI(title="String Analyzer Service - Stage 1", redirect_slashes=False)

# Add CORS middleware to allow autograder access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    value: Any = None  # Allow None so we can check manually


@app.get("/")
def root():
    return {"ok": True}

@app.post("/strings", status_code=201)
def create_string(req: CreateRequest):
    if req.value is None:
        raise HTTPException(status_code=400, detail='Missing "value" field')
    if not isinstance(req.value, str):
        raise HTTPException(status_code=422, detail='"value" must be a string')

    value = req.value
    if db.exists(value):
        raise HTTPException(status_code=409, detail="String already exists")

    props = models.analyze_string(value)
    entry = db.create_entry(value, props)
    return JSONResponse(status_code=201, content=entry)


@app.get("/strings")
def list_strings(
    is_palindrome: Optional[bool] = Query(None),
    min_length: Optional[int] = Query(None, ge=0),
    max_length: Optional[int] = Query(None, ge=0),
    word_count: Optional[int] = Query(None, ge=0),
    contains_character: Optional[str] = Query(None, min_length=1, max_length=1),
):
    try:
        results = db.filter_entries(
            is_palindrome=is_palindrome,
            min_length=min_length,
            max_length=max_length,
            word_count=word_count,
            contains_character=contains_character,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"data": results, "count": len(results), "filters_applied": {
        k: v for k, v in {
            "is_palindrome": is_palindrome,
            "min_length": min_length,
            "max_length": max_length,
            "word_count": word_count,
            "contains_character": contains_character,
        }.items() if v is not None
    }}


@app.get("/strings/filter-by-natural-language")
def filter_by_nl(query: str = Query(..., min_length=1)):
    parsed = nlp_parser.parse(query)
    if parsed is None:
        raise HTTPException(status_code=400, detail="Unable to parse natural language query")
    # Check for conflicting filters
    if parsed.get("min_length") and parsed.get("max_length") and parsed["min_length"] > parsed["max_length"]:
        raise HTTPException(status_code=422, detail="Parsed filters are conflicting")

    results = db.filter_entries(**parsed)
    return {"data": results, "count": len(results), "interpreted_query": {"original": query, "parsed_filters": parsed}}


@app.get("/strings/{string_value}")
def get_string(string_value: str):
    entry = db.get_by_value(string_value)
    if not entry:
        raise HTTPException(status_code=404, detail="String not found")
    return entry


@app.delete("/strings/{string_value}", status_code=204)
def delete_string(string_value: str):
    deleted = db.delete_by_value(string_value)
    if not deleted:
        raise HTTPException(status_code=404, detail="String not found")
    return JSONResponse(status_code=204, content=None)
