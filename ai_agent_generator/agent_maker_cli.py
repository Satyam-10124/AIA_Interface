#!/usr/bin/env python3
import os
import json
import re
import argparse
import logging
import traceback
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv

from .agent_generator_crew import agent_generator_crew
from .agent_schemas import AgentFilesBundle, VerificationReport, AgentSpecOutput, AgentFileOutput

# Load env
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AgentMakerCLI")


def slugify(name: str) -> str:
    return "-".join(
        "".join(ch.lower() if ch.isalnum() else " " for ch in name).split()
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="AI Agent Generator CLI - Turn an idea into runnable CrewAI agent code with verification"
    )
    parser.add_argument("--idea", "-i", required=True, type=str, help="Plain-language idea for the agent to build")
    parser.add_argument("--name", "-n", type=str, default="", help="Optional display name for the agent")
    parser.add_argument("--output-dir", "-o", type=str, default="./generated_agents", help="Directory to write the agent code to")
    parser.add_argument("--verify", "-v", action="store_true", help="Run verification after generating code")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logs")
    return parser.parse_args()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_bundle(bundle: AgentFilesBundle, root: Path) -> None:
    ensure_dir(root)
    # Write code files
    for f in bundle.files:
        file_path = root / f.filename
        ensure_dir(file_path.parent)
        file_path.write_text(f.code, encoding="utf-8")
    # Optional tests
    if bundle.tests:
        for rel, content in bundle.tests.items():
            test_path = root / rel
            ensure_dir(test_path.parent)
            test_path.write_text(content, encoding="utf-8")


def _extract_json_candidates(raw_text: str) -> list[dict]:
    """Extract potential JSON objects from a raw LLM string.

    - Prefer fenced code blocks marked as ```json ... ```
    - Fallback: first {...} span in the text
    """
    candidates: list[dict] = []
    if not isinstance(raw_text, str):
        return candidates

    # 1) Parse fenced code blocks: ```json\n...\n```
    for lang, code_block in re.findall(r"```(\w+)?\n([\s\S]*?)```", raw_text, re.DOTALL):
        lang = (lang or "").lower()
        if lang == "json":
            try:
                obj = json.loads(code_block)
                if isinstance(obj, dict):
                    candidates.append(obj)
            except Exception:
                pass

    # 2) Naive fallback: first JSON-looking blob
    if not candidates:
        m = re.search(r"\{[\s\S]*\}", raw_text)
        if m:
            try:
                obj = json.loads(m.group(0))
                if isinstance(obj, dict):
                    candidates.append(obj)
            except Exception:
                pass

    return candidates


def _maybe_bundle_from_any(obj: Any) -> AgentFilesBundle | None:
    """Try to coerce any object into AgentFilesBundle if possible."""
    try:
        if isinstance(obj, AgentFilesBundle):
            return obj
        if hasattr(obj, "model_dump"):
            data = obj.model_dump()
            if isinstance(data, dict) and "files" in data:
                return AgentFilesBundle(**data)
        if isinstance(obj, dict) and "files" in obj:
            return AgentFilesBundle(**obj)
        if isinstance(obj, str):
            # Try direct JSON
            try:
                parsed = json.loads(obj)
                if isinstance(parsed, dict) and "files" in parsed:
                    return AgentFilesBundle(**parsed)
            except Exception:
                pass
            # Try fenced JSON blocks
            for cand in _extract_json_candidates(obj):
                if isinstance(cand, dict) and "files" in cand:
                    try:
                        return AgentFilesBundle(**cand)
                    except Exception:
                        continue
    except Exception:
        return None
    return None


def _maybe_report_from_any(obj: Any) -> VerificationReport | None:
    """Try to coerce any object into VerificationReport if possible."""
    required = {"passed", "syntax_ok", "import_ok", "tests_ok"}
    try:
        if isinstance(obj, VerificationReport):
            return obj
        if hasattr(obj, "model_dump"):
            data = obj.model_dump()
            if isinstance(data, dict) and required.issubset(data.keys()):
                return VerificationReport(**data)
        if isinstance(obj, dict) and required.issubset(obj.keys()):
            return VerificationReport(**obj)
        if isinstance(obj, str):
            # Try direct JSON
            try:
                parsed = json.loads(obj)
                if isinstance(parsed, dict) and required.issubset(parsed.keys()):
                    return VerificationReport(**parsed)
            except Exception:
                pass
            # Try fenced JSON blocks
            for cand in _extract_json_candidates(obj):
                if isinstance(cand, dict) and required.issubset(cand.keys()):
                    try:
                        return VerificationReport(**cand)
                    except Exception:
                        continue
    except Exception:
        return None
    return None

    # 1) Parse fenced code blocks: ```json\n...\n```
    for lang, code_block in re.findall(r"```(\w+)?\n([\s\S]*?)```", raw_text, re.DOTALL):
        lang = (lang or "").lower()
        if lang == "json":
            try:
                obj = json.loads(code_block)
                if isinstance(obj, dict):
                    candidates.append(obj)
            except Exception:
                pass

    # 2) Naive fallback: first JSON-looking blob
    if not candidates:
        m = re.search(r"\{[\s\S]*\}", raw_text)
        if m:
            try:
                obj = json.loads(m.group(0))
                if isinstance(obj, dict):
                    candidates.append(obj)
            except Exception:
                pass

    return candidates


def main() -> int:
    args = parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    idea = args.idea.strip()
    agent_name = args.name.strip() or idea[:40]
    name_slug = slugify(agent_name)
    serper_available = bool(os.getenv("SERPER_API_KEY"))

    output_dir = Path(args.output_dir).resolve()
    agent_root = output_dir / name_slug

    print("\n==============================")
    print("🤖 AI Agent Generator CLI")
    print("==============================\n")
    print("📋 Idea:", idea[:120] + ("..." if len(idea) > 120 else ""))
    print("📛 Agent Name:", agent_name)
    print("📁 Output Root:", str(agent_root))

    inputs: Dict[str, Any] = {
        "idea": idea,
        "agent_name": agent_name,
        "agent_name_slug": name_slug,
        "output_dir": str(output_dir),
        "output_root": str(agent_root),
        "serper_available": str(serper_available).lower(),
    }

    try:
        print("\n🚀 Generating agent code via Crew...")
        agent_generator_crew.kickoff(inputs=inputs)
    except Exception as e:
        print("\n❌ Crew execution failed:")
        print(str(e))
        print(traceback.format_exc())
        return 1

    # Collect structured outputs
    spec: AgentSpecOutput | None = None
    bundle: AgentFilesBundle | None = None
    report: VerificationReport | None = None

    for t in agent_generator_crew.tasks:
        out = getattr(t, "output", None)
        if out is None:
            continue
        # Candidate attributes to examine from the task output
        cand_attrs = [
            "exported_output",
            "raw_output",
            "raw",
            "pydantic",
            "json_dict",
            "value",
        ]
        candidates: list[Any] = []
        for attr in cand_attrs:
            try:
                val = getattr(out, attr, None)
                if val is not None:
                    candidates.append(val)
            except Exception:
                continue
        # Always include the object itself and its string form as last resorts
        candidates.append(out)
        try:
            candidates.append(str(out))
        except Exception:
            pass

        for c in candidates:
            if spec is None and isinstance(c, AgentSpecOutput):
                spec = c
            if bundle is None:
                maybe_b = _maybe_bundle_from_any(c)
                if maybe_b is not None:
                    bundle = maybe_b
            if report is None:
                maybe_r = _maybe_report_from_any(c)
                if maybe_r is not None:
                    report = maybe_r

    if bundle is None:
        print("\n⚠️ No code bundle returned by the crew. Nothing to write.")
        return 1

    # Write files as a fallback in case the FileWriterTool was not used in-task
    print("\n💾 Writing files to:", str(agent_root))
    write_bundle(bundle, agent_root)

    # Ensure requirements.txt exists (fallback)
    req_path = agent_root / "requirements.txt"
    has_req_in_bundle = any(getattr(f, "filename", "").lower() == "requirements.txt" for f in bundle.files)
    if not req_path.exists():
        deps = bundle.dependencies or []
        if not deps:
            # Sensible defaults
            deps = [
                "crewai==0.193.2",
                "crewai-tools==0.75.0",
                "python-dotenv==1.0.0",
                "pytest==8.2.2",
            ]
        ensure_dir(req_path.parent)
        req_path.write_text("\n".join(deps) + "\n", encoding="utf-8")
        # Reflect in bundle for printing
        try:
            bundle.files.append(AgentFileOutput(filename="requirements.txt", code=req_path.read_text(encoding="utf-8")))
        except Exception:
            pass

    # Ensure README.md exists (fallback)
    readme_path = agent_root / "README.md"
    has_readme_in_bundle = any(getattr(f, "filename", "").lower() == "readme.md" for f in bundle.files)
    if not readme_path.exists():
        title = agent_name or name_slug.replace("-", " ").title()
        entrypoint = bundle.entrypoint or "main.py"
        # Compute a robust run command
        run_cmd = None
        if isinstance(entrypoint, str) and entrypoint.startswith("src/") and entrypoint.endswith(".py"):
            module = entrypoint[len("src/") : -len(".py")].replace("/", ".")
            run_cmd = f"PYTHONPATH=src python -m {module}"
        else:
            run_cmd = f"python {entrypoint}"
        readme = f"""# {title}\n\n"""
        readme += """A generated CrewAI project that triages insurance claims: validates inputs, flags potential fraud, prioritizes severity, and routes cases.\n\n"""
        readme += """## Quickstart\n\n"""
        readme += """1. Create and activate a virtual environment\n\n"""
        readme += """   - macOS/Linux:\n\n```
python3 -m venv .venv
source .venv/bin/activate
```
\n"""
        readme += """2. Install dependencies\n\n```
pip install -r requirements.txt
```
\n"""
        readme += f"""3. Run the agent CLI\n\n```
{run_cmd} data/sample_claim.json
```
\nIf you don't have a sample file, pass a path to your claim JSON.\n\n"""
        readme += """4. Run tests\n\n```
pytest -q
```
\n"""
        readme += """## Environment Variables\n\n- SERPER_API_KEY (optional): Enables web search via SerperDevTool if present.\n- Create a `.env` from `.env.example` and fill in values as needed.\n\n"""
        ensure_dir(readme_path.parent)
        readme_path.write_text(readme, encoding="utf-8")
        try:
            bundle.files.append(AgentFileOutput(filename="README.md", code=readme))
        except Exception:
            pass

    print("\n📦 Generated files:")
    for f in bundle.files:
        print("  •", str(agent_root / f.filename))
    if bundle.tests:
        for rel in bundle.tests.keys():
            print("  •", str(agent_root / rel))

    if args.verify:
        print("\n🧪 Running verification task...")
        try:
            # Re-run only the verifier task by kicking off crew again may be costly; rely on prior run result if present
            if report is None:
                # If not present from first run, run a minimal kickoff that leverages the same inputs
                agent_generator_crew.kickoff(inputs=inputs)
                for t in agent_generator_crew.tasks:
                    out = getattr(t, "output", None)
                    if out is None:
                        continue
                    obj = getattr(out, "exported_output", None) or getattr(out, "raw_output", None)
                    if isinstance(obj, VerificationReport):
                        report = obj
                        break
        except Exception as e:
            print("\n⚠️ Verification kickoff failed:", str(e))

        if report is not None:
            print("\n✅ Verification Report:")
            print("  • passed:", report.passed)
            print("  • syntax_ok:", report.syntax_ok)
            print("  • import_ok:", report.import_ok)
            print("  • tests_ok:", report.tests_ok)
            if report.errors:
                print("  • errors:")
                for err in report.errors:
                    print("    -", err)
            if report.warnings:
                print("  • warnings:")
                for w in report.warnings:
                    print("    -", w)
            if report.suggestions:
                print("  • suggestions:")
                for s in report.suggestions:
                    print("    -", s)
        else:
            print("\n⚠️ No verification report produced.")

    print("\n🎉 Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
