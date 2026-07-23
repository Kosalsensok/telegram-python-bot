import asyncio
import os
import sys
import tempfile
import logging
import aiohttp
from typing import Dict, Any, Optional

async def _execute_wandbox(code: str, compiler: str = "gcc-head") -> Optional[str]:
    """
    Executes code using Wandbox API for compiled languages like C/C++.
    """
    url = "https://wandbox.org/api/compile.json"
    payload = {
        "compiler": compiler,
        "code": code
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=10.0)) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    prog_out = data.get("program_output", "")
                    comp_err = data.get("compiler_error", "")
                    prog_err = data.get("program_error", "")
                    
                    output_parts = []
                    if comp_err:
                        output_parts.append(f"=== COMPILER OUTPUT / ERRORS ===\n{comp_err.strip()}")
                    if prog_out:
                        output_parts.append(prog_out.strip())
                    if prog_err:
                        output_parts.append(f"=== RUNTIME ERROR ===\n{prog_err.strip()}")
                        
                    return "\n\n".join(output_parts).strip()
    except Exception as e:
        logging.warning(f"Wandbox API execution failed: {e}")
    return None

async def execute_code(language: str, code: str) -> Optional[Dict[str, Any]]:
    """
    Executes code locally (Python, JS, TS, Java) or via cloud compiler API for C/C++.
    """
    language = language.lower().strip()
    
    # Map common aliases
    if language in ["py", "python3"]:
        language = "python"
    elif language in ["js", "javascript", "node", "nodejs"]:
        language = "javascript"
    elif language in ["ts", "typescript"]:
        language = "typescript"
    elif language in ["c++", "cpp", "c"]:
        language = "cpp"
        
    # C/C++ execution via Wandbox cloud compiler
    if language == "cpp":
        wandbox_out = await _execute_wandbox(code, "gcc-head")
        if wandbox_out is not None:
            if not wandbox_out:
                wandbox_out = "(C/C++ code executed successfully with no output)"
            return {
                "compile": {"output": ""},
                "run": {"output": wandbox_out}
            }
        
    supported_langs = {
        "python": {"ext": ".py", "cmd": [sys.executable]},
        "javascript": {"ext": ".js", "cmd": ["node"]},
        "typescript": {"ext": ".ts", "cmd": ["node", "--experimental-strip-types"]},
        "java": {"ext": ".java", "cmd": ["java"]}
    }
    
    if language not in supported_langs:
        return {
            "compile": {"output": ""},
            "run": {"output": f"⚠️ Language '{language}' is not supported. Supported languages: Python, JavaScript, TypeScript, Java, C/C++."}
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
                try:
                    process.kill()
                except Exception:
                    pass
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
                
            if not final_output:
                final_output = "(Code executed successfully with no output)"

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
