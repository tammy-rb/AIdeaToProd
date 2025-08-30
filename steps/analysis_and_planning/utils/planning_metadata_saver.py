import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

class PlanningMetadataSaver:
    """
    Saves relevant planning metadata to a JSON file.
    Robust to CrewAI shapes and noisy tool traces.
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def save(self, result: Dict[str, Any]):
        print("Saving planning metadata...")
        
        # 1) Basics
        status = result.get("status")
        config = result.get("config") or {}
        app_name = config.get("app_name")
        
        # 2) Normalize crew output
        crew_output = result.get("result")
        tasks_output = self._extract_tasks_output(crew_output)
        
        # 3) Extract per-agent payloads (more permissive matching)
        hld = self._extract_by_agent(tasks_output, ["high-level design", "hld"])
        dd = self._extract_by_agent(tasks_output, ["detailed design", "dd"])
        cs = self._extract_by_agent(tasks_output, ["code structure", "architect", "structure"])
        jira = self._extract_by_agent(tasks_output, ["jira", "delivery planner", "project organizer", "epic", "story"])
        
        # 4) Build compact metadata with timestamp
        metadata: Dict[str, Any] = {
            "status": status,
            "app_name": app_name,
            "last_updated": datetime.now().isoformat(),  # Add timestamp here
        }
        
        if hld:
            metadata["hld"] = {
                "folder_id": hld.get("folder_id"),
                "folder_name": hld.get("folder_name"),
                "hl_doc_id": hld.get("hl_doc_id"),
                "hl_doc_name": hld.get("hl_doc_name"),
                "error": hld.get("error"),
            }
        
        if dd and any(k in dd for k in ("detailed_doc_id", "error")):
            metadata["dd"] = {
                "detailed_doc_id": dd.get("detailed_doc_id"),
                "detailed_doc_name": dd.get("detailed_doc_name"),
                "folder_id": dd.get("folder_id"),
                "error": dd.get("error"),
            }
        
        # ---- Code Structure: save when we see meaningful fields OR fallback to raw ----
        if cs and any(k in cs for k in ("root", "tree", "files", "assumptions", "error")):
            # Clean up the data and remove nulls
            code_structure = {}
            if cs.get("app_name"):
                code_structure["app_name"] = cs["app_name"]
            if cs.get("root"):
                code_structure["root"] = cs["root"]
            if cs.get("tree"):
                # Clean up tree formatting
                tree = cs["tree"].replace("\\n", "\n") if isinstance(cs["tree"], str) else cs["tree"]
                code_structure["tree"] = tree
            if cs.get("files"):
                code_structure["files"] = cs["files"]
            if cs.get("assumptions"):
                code_structure["assumptions"] = cs["assumptions"]
            if cs.get("error"):
                code_structure["error"] = cs["error"]
            
            if code_structure:  # Only add if we have actual content
                metadata["code_structure"] = code_structure
        else:
            # FALLBACK: Try to extract code structure from any task's raw content
            cs_raw = self._extract_code_structure_from_raw(tasks_output)
            if cs_raw:
                metadata["code_structure"] = cs_raw
        
        # ---- Jira: robust parse + fallback to string plan if needed ----
        if jira:
            # If jira parsed as dict but is sparse, try to enrich from raw
            jira_enriched = self._ensure_jira_fields(jira, tasks_output)
            if any(k in jira_enriched for k in ("jira_project_key","implementation_plan","implementation_plan_str", "epics_created_count","stories_created_count","error")):
                metadata["jira"] = {
                    "jira_project_key": jira_enriched.get("jira_project_key"),
                    "implementation_plan": jira_enriched.get("implementation_plan", []),
                    "implementation_plan_str": jira_enriched.get("implementation_plan_str"),
                    "epics_created_count": jira_enriched.get("epics_created_count"),
                    "stories_created_count": jira_enriched.get("stories_created_count"),
                    "error": jira_enriched.get("error"),
                }
        
        # 5) Ensure dir & save
        dir_path = os.path.dirname(self.file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Metadata saved to {self.file_path}")
        print(f"📅 Last updated: {metadata['last_updated']}")
    
    # -----------------------
    # Helpers
    # -----------------------
    
    def _extract_tasks_output(self, crew_output: Any) -> List[Any]:
        """
        Returns a list of TaskOutput-like objects.
        """
        if crew_output is None:
            return []
        
        tasks = getattr(crew_output, "tasks_output", None)
        if tasks:
            return list(tasks)
        
        if any(hasattr(crew_output, attr) for attr in ("agent", "raw", "json_dict")):
            return [crew_output]
        
        return []
    
    def _extract_by_agent(self, tasks_output: List[Any], agent_name_keywords: List[str]) -> Dict[str, Any]:
        """
        Finds the first matching task (case-insensitive) and parses its JSON payload.
        """
        for task in tasks_output:
            agent = getattr(task, "agent", "") or ""
            agent_l = str(agent).lower()
            
            if not agent_l:
                continue
            
            if any(kw in agent_l for kw in agent_name_keywords):
                # Prefer json_dict
                jd = getattr(task, "json_dict", None)
                if isinstance(jd, dict) and jd:
                    return jd
                
                # Fallback: parse raw
                raw = getattr(task, "raw", "") or ""
                parsed = self._parse_json_from_raw(raw)
                
                # If list -> pick last dict
                if isinstance(parsed, list):
                    dicts = [x for x in parsed if isinstance(x, dict)]
                    if dicts:
                        return dicts[-1]
                    return {"error": "Parsed list without dicts"}  # keep a clear error
                
                if isinstance(parsed, dict):
                    return parsed
                
                # As last resort, return error with excerpt
                return {"error": "Could not parse task JSON", "raw_excerpt": raw[:400]}
        
        return {}
    
    def _extract_code_structure_from_raw(self, tasks_output: List[Any]) -> Optional[Dict[str, Any]]:
        """
        Fallback method to extract code structure from any task's raw content.
        This handles cases where the agent matching fails.
        """
        for task in tasks_output:
            raw = getattr(task, "raw", "") or ""
            
            # Look for code structure indicators in the raw content
            if any(indicator in raw.lower() for indicator in ["app_name", "root", "tree", "files", "assumptions"]):
                parsed = self._parse_json_from_raw(raw)
                
                if isinstance(parsed, dict):
                    # Check if this looks like a code structure payload
                    if any(k in parsed for k in ("app_name", "root", "tree", "files", "assumptions")):
                        result = {
                            "app_name": parsed.get("app_name"),
                            "root": parsed.get("root"),
                            "tree": parsed.get("tree"),
                            "files": parsed.get("files", []),
                            "assumptions": parsed.get("assumptions", []),
                        }
                        
                        # Clean up the tree format - remove escaped newlines
                        if result.get("tree"):
                            result["tree"] = result["tree"].replace("\\n", "\n")
                        
                        return result
                
                # If parsing failed but we found indicators, try one more time with better cleaning
                if "app_name" in raw and "tree" in raw:
                    # Try to extract just the JSON part more aggressively
                    cleaned_json = self._extract_clean_json_from_raw(raw)
                    if cleaned_json:
                        return cleaned_json
                    
                    # Last resort: save as raw but structured better
                    return {
                        "error": "Could not parse JSON, saved raw content",
                        "raw_content": raw[:1000],  # Truncate if too long
                        "raw_source": "fallback_raw"
                    }
        
        return None
    
    def _extract_clean_json_from_raw(self, raw: str) -> Optional[Dict[str, Any]]:
        """
        More aggressive JSON extraction for problematic content.
        """
        # Look for content between curly braces that might be JSON
        brace_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(brace_pattern, raw, re.DOTALL)
        
        for match in reversed(matches):  # Try from last to first
            # Clean up common issues
            cleaned = match.strip()
            
            # Try to parse
            try:
                parsed = json.loads(cleaned)
                if isinstance(parsed, dict) and any(k in parsed for k in ("app_name", "root", "tree", "files", "assumptions")):
                    result = {
                        "app_name": parsed.get("app_name"),
                        "root": parsed.get("root"),
                        "tree": parsed.get("tree"),
                        "files": parsed.get("files", []),
                        "assumptions": parsed.get("assumptions", []),
                    }
                    
                    # Clean up the tree format
                    if result.get("tree"):
                        result["tree"] = result["tree"].replace("\\n", "\n")
                    
                    return result
            except json.JSONDecodeError:
                continue
        
        return None
    
    def _parse_json_from_raw(self, raw: str) -> Any:
        """
        Extract the last JSON object/array from a noisy string with multiple fenced blocks.
        """
        if not raw:
            return {"error": "empty task output"}
        
        # First, try to extract from fenced code blocks
        fenced_json = self._extract_fenced_json(raw)
        if fenced_json:
            return fenced_json
        
        # Normalize: strip ```json fences for fallback processing
        text = raw.strip().replace("```json", "```").replace("```", "\n")
        
        candidates: List[str] = []
        
        def scan_pairs(open_ch: str, close_ch: str):
            depth = 0
            start_idx = None
            in_string = False
            escape = False
            
            for i, ch in enumerate(text):
                if in_string:
                    if escape:
                        escape = False
                    elif ch == "\\":
                        escape = True
                    elif ch == '"':
                        in_string = False
                    continue
                else:
                    if ch == '"':
                        in_string = True
                        continue
                
                if ch == open_ch:
                    if depth == 0:
                        start_idx = i
                    depth += 1
                elif ch == close_ch:
                    if depth > 0:
                        depth -= 1
                        if depth == 0 and start_idx is not None:
                            candidates.append(text[start_idx:i+1])
                            start_idx = None
        
        scan_pairs("{", "}")
        scan_pairs("[", "]")
        
        for chunk in reversed(candidates):
            try:
                return json.loads(chunk)
            except Exception:
                continue
        
        try:
            return json.loads(text)
        except Exception as e:
            return {"error": f"failed to parse JSON: {e}", "raw_excerpt": text[-400:]}
    
    def _extract_fenced_json(self, raw: str) -> Optional[Any]:
        """
        Extract and parse JSON from fenced code blocks (```...```).
        """
        # Find all fenced code blocks
        fences = list(re.finditer(r'```(?:json)?\s*(.*?)\s*```', raw, re.DOTALL | re.IGNORECASE))
        
        # Try each fenced block from last to first
        for fence_match in reversed(fences):
            content = fence_match.group(1).strip()
            if content:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    continue
        
        return None
    
    # ---------- Jira fallback enrichment ----------
    
    def _ensure_jira_fields(self, jira_dict: Dict[str, Any], tasks_output: List[Any]) -> Dict[str, Any]:
        """
        If Jira dict is missing fields or implementation_plan is empty, 
        try to enrich by pulling from the Jira task raw via regex.
        """
        if any(k in jira_dict for k in ("implementation_plan", "jira_project_key", "epics_created_count", "stories_created_count")) \
                and jira_dict.get("implementation_plan"):
            return jira_dict  # already good
        
        # Find the Jira task raw
        raw = ""
        for task in tasks_output:
            agent = getattr(task, "agent", "") or ""
            if any(kw in str(agent).lower() for kw in ["jira", "delivery planner", "project organizer"]):
                raw = getattr(task, "raw", "") or ""
                if raw:
                    break
        
        if not raw:
            return jira_dict
        
        # Try to extract the final fenced JSON block verbatim
        block = self._extract_last_json_block_text(raw)
        if block:
            try:
                obj = json.loads(block)
                # Merge non-destructively
                jira_dict = {**obj, **jira_dict, **{k: v for k, v in obj.items() if v}}
            except Exception:
                pass
        
        # If implementation_plan still missing/empty -> regex fallback
        if not jira_dict.get("implementation_plan"):
            plan_list, plan_str = self._regex_extract_implementation_plan(raw)
            if plan_list:
                jira_dict["implementation_plan"] = plan_list
            elif plan_str:
                jira_dict["implementation_plan_str"] = plan_str
        
        # Ensure jira_project_key if present in raw
        if not jira_dict.get("jira_project_key"):
            m = re.search(r'"jira_project_key"\s*:\s*"([^"]+)"', raw)
            if m:
                jira_dict["jira_project_key"] = m.group(1)
        
        # counts
        if jira_dict.get("epics_created_count") is None:
            m = re.search(r'"epics_created_count"\s*:\s*(\d+)', raw)
            if m:
                jira_dict["epics_created_count"] = int(m.group(1))
        
        if jira_dict.get("stories_created_count") is None:
            m = re.search(r'"stories_created_count"\s*:\s*(\d+)', raw)
            if m:
                jira_dict["stories_created_count"] = int(m.group(1))
        
        # If everything failed, keep an explicit error but don't drop partials
        if not any(jira_dict.get(k) for k in ("implementation_plan", "implementation_plan_str", "jira_project_key", "epics_created_count", "stories_created_count")):
            jira_dict.setdefault("error", "Could not extract Jira payload")
        
        return jira_dict
    
    def _extract_last_json_block_text(self, raw: str) -> Optional[str]:
        """
        Returns the text of the last fenced JSON-ish block or last {...} object found.
        """
        text = raw.strip()
        
        # Try last fenced block ```...```
        fences = list(re.finditer(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE))
        if fences:
            return fences[-1].group(1).strip()
        
        # Fallback: last balanced { ... }
        brace_spans: List[tuple] = []
        depth = 0
        start = None
        in_string = False
        escape = False
        
        for i, ch in enumerate(text):
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
            else:
                if ch == '"':
                    in_string = True
                elif ch == "{":
                    if depth == 0:
                        start = i
                    depth += 1
                elif ch == "}":
                    if depth > 0:
                        depth -= 1
                        if depth == 0 and start is not None:
                            brace_spans.append((start, i+1))
                            start = None
        
        if brace_spans:
            s, e = brace_spans[-1]
            return text[s:e].strip()
        
        return None
    
    def _regex_extract_implementation_plan(self, raw: str) -> (List[str], Optional[str]):
        """
        Extracts implementation_plan entries via regex; returns (list, string_fallback).
        """
        m = re.search(r'"implementation_plan"\s*:\s*\[(.*?)\]', raw, re.DOTALL | re.IGNORECASE)
        if not m:
            return [], None
        
        inner = m.group(1)
        
        # Find quoted strings within the array
        items = re.findall(r'"([^"]+)"', inner)
        items = [s.strip() for s in items if s.strip()]
        
        if items:
            return items, None
        
        # Fallback: store the raw inner segment as a string
        return [], inner.strip() if inner else None