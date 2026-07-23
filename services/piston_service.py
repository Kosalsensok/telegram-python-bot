import asyncio
import os
import sys
import tempfile
import logging
from typing import Dict, Any, Optional

async def execute_code(language: str, code: str) -> Optional[Dict[str, Any]]:
    """
    Executes code locally as a fallback since public APIs (Piston, Wandbox) 
    are offline, timing out, or require whitelisting.
    """
    language = language.lower().strip()
    
    # Map common aliases
    if language in ["py", "python3"]:
        language = "python"
    elif language in ["js", "javascript", "ts", "typescript", "nodejs"]:
        language = "javascript"
    elif language in ["c++", "cpp"]:
        language = "cpp"
        
    supported_langs = {
        "python": {"ext": ".py", "cmd": [sys.executable]},
        "javascript": {"ext": ".js", "cmd": ["node"]},
        "java": {"ext": ".java", "cmd": ["java"]}
    }
    
    if language not in supported_langs:
        return {
            "compile": {"output": ""},
            "run": {"output": f"⚠️ Language '{language}' is not supported for local execution. Supported: Python, JavaScript, Java."}
        }
        
    config = supported_langs[language]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # For Java, name it Main.java to avoid public class naming issues
        filename = "Main.java" if language == "java" else f"script{config['ext']}"
        file_path = os.path.join(temp_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
            
        cmd = config["cmd"] + [file_path]
        
        try:
            # Run the code as a subprocess with a timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=temp_dir
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10.0)
            except asyncio.TimeoutError:
                process.kill()
                stdout, stderr = await process.communicate()
                return {
                    "compile": {"output": ""},
                    "run": {"output": "⏳ Execution timed out (10s limit)."}
                }
                
            out_str = stdout.decode('utf-8', errors='replace').strip()
            err_str = stderr.decode('utf-8', errors='replace').strip()
            
            final_output = out_str
            if err_str:
                if final_output:
                    final_output += "\n\n=== ERROR ===\n" + err_str
                else:
                    final_output = err_str
                
            return {
                "compile": {"output": ""},
                "run": {"output": final_output}
            }
            
        except Exception as e:
            logging.error(f"Local execution error for {language}: {e}")
            return {
                "compile": {"output": ""},
                "run": {"output": f"❌ Server execution error: {str(e)}\nMake sure {config['cmd'][0]} is installed on the host machine."}
            }
