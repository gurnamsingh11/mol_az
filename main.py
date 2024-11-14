import io
import re
from contextlib import redirect_stdout
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from functions import initial_checks
from tool_func import langgraph_agent_executor
from prompts import sys
from tool_func import messages


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/sop_navigation_az_mol/")
async def sop_navigation(
    query, file_path="Coordination of Benefits (COB) - All States Medicaid - SOP.json"
):
    try:
        messages.clear()
        messages.append(("system", sys))
        processed_claim = initial_checks(query)
        inp = f"file_path: json-files/{file_path}, Claim: {processed_claim}"

        output_stream = io.StringIO()
        with redirect_stdout(output_stream):
            res = langgraph_agent_executor.invoke({"messages": [("user", inp)]})
        verbose_output = output_stream.getvalue()
        verbose_output = (
            verbose_output.replace("Action: json_spec_list_keys", "")
            .replace("Action: json_spec_get_value", "")
            .replace("ValueError", "")
        )
        cleaned_text = re.sub(
            r"\u001b\[\d+;\d+m|\u001b\[0m|\u001b\[1m>", "", verbose_output
        )
        return cleaned_text

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))