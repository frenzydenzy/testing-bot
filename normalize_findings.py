#!/usr/bin/env python3
"""Normalize SonarQube issue exports and Checkmarx/SARIF reports to a common JSON format."""
import argparse, json, sys
from pathlib import Path

def read_json(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)

def sev(v):
    s=str(v or "UNKNOWN").upper()
    return {"BLOCKER":"CRITICAL","CRITICAL":"CRITICAL","HIGH":"HIGH","MAJOR":"HIGH",
            "MEDIUM":"MEDIUM","MODERATE":"MEDIUM","MINOR":"LOW","LOW":"LOW",
            "INFO":"INFO","INFORMATIONAL":"INFO"}.get(s,s)

def sonar_items(data):
    issues=data.get("issues",[]) if isinstance(data,dict) else []
    out=[]
    for x in issues:
        out.append({
            "source_tool":"SonarQube","scanner":"SonarQube",
            "rule_id":x.get("rule"),"title":x.get("message") or x.get("rule"),
            "description":x.get("message"),"severity_original":x.get("severity") or x.get("impacts"),
            "severity_normalized":sev(x.get("severity")),
            "type":x.get("type"),"category":"sonarqube_issue",
            "path":x.get("component","").split(":",1)[-1],
            "line":x.get("line"),"end_line":x.get("textRange",{}).get("endLine"),
            "url":x.get("url"),"status":x.get("status"),
            "scope":"unknown","evidence":x.get("message")
        })
    return out

def sarif_items(data):
    out=[]
    for run in data.get("runs",[]):
        tool=run.get("tool",{}).get("driver",{})
        toolname=tool.get("name","SARIF tool")
        rules=tool.get("rules",[])
        rulemap={r.get("id"):r for r in rules}
        for res in run.get("results",[]):
            rid=res.get("ruleId")
            rule=rulemap.get(rid,{})
            loc=(res.get("locations") or [{}])[0].get("physicalLocation",{})
            art=loc.get("artifactLocation",{})
            region=loc.get("region",{})
            level=res.get("level","")
            props=res.get("properties",{}) or {}
            out.append({
                "source_tool":toolname,"scanner":toolname,"rule_id":rid,
                "title":res.get("message",{}).get("text") or rule.get("shortDescription",{}).get("text") or rid,
                "description":rule.get("fullDescription",{}).get("text"),
                "severity_original":props.get("severity") or level,
                "severity_normalized":sev(props.get("severity") or level),
                "category":",".join(rule.get("properties",{}).get("tags",[]) or []),
                "path":art.get("uri"),"line":region.get("startLine"),
                "end_line":region.get("endLine"),"scope":"unknown",
                "evidence":res.get("message",{}).get("text"),
                "fingerprints":res.get("fingerprints") or res.get("partialFingerprints"),
                "help_uri":rule.get("helpUri")
            })
    return out

def generic_items(data):
    # Preserve generic Checkmarx JSON result records where possible.
    if isinstance(data,list): items=data
    elif isinstance(data,dict):
        items=None
        for k in ("results","vulnerabilities","findings","items","scanResults"):
            if isinstance(data.get(k),list):
                items=data[k]; break
        if items is None:
            # A Checkmarx report may wrap scanner-specific results in nested objects.
            for k in ("sast","sca","iacSecurity","iac","secretDetection","containers"):
                v=data.get(k)
                if isinstance(v,list): items=(items or [])+v
                elif isinstance(v,dict):
                    for kk in ("results","findings","vulnerabilities"):
                        if isinstance(v.get(kk),list): items=(items or [])+v[kk]
            if items is None: raise ValueError("Unrecognized JSON report shape; expected results/findings/vulnerabilities or SARIF.")
    else: raise ValueError("Unsupported JSON root.")
    out=[]
    for x in items:
        if not isinstance(x,dict): continue
        loc=x.get("location") or x.get("locations") or {}
        if isinstance(loc,list): loc=loc[0] if loc else {}
        if not isinstance(loc,dict): loc={}
        file=x.get("fileName") or x.get("file") or x.get("path") or loc.get("fileName") or loc.get("path")
        line=x.get("line") or x.get("lineNumber") or loc.get("line") or loc.get("lineNumber")
        scanner=x.get("scanner") or x.get("engine") or x.get("type") or "Checkmarx"
        severity=x.get("severity") or x.get("severityLevel") or x.get("priority")
        out.append({
            "source_tool":"Checkmarx","scanner":scanner,
            "rule_id":x.get("queryId") or x.get("ruleId") or x.get("id") or x.get("cve"),
            "title":x.get("name") or x.get("title") or x.get("description") or "Checkmarx finding",
            "description":x.get("description") or x.get("data",{}).get("description") if isinstance(x.get("data"),dict) else x.get("description"),
            "severity_original":severity,"severity_normalized":sev(severity),
            "category":x.get("category") or x.get("vulnerabilityType") or scanner,
            "path":file,"line":line,"end_line":x.get("endLine"),
            "scope":"unknown","evidence":x.get("dataFlow") or x.get("resultDescription") or x.get("description"),
            "cwe":x.get("cwe") or x.get("cweId"),"cve":x.get("cve"),
            "package":x.get("packageName") or x.get("package"),
            "version":x.get("version"),"recommendation":x.get("recommendation") or x.get("remediation")
        })
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input",required=True)
    ap.add_argument("--format",choices=["auto","sarif","sonar","checkmarx"],default="auto")
    ap.add_argument("--output",default="normalized-findings.json")
    ap.add_argument("--markdown")
    ap.add_argument("--changed-files",help="Text file containing one changed repository path per line")
    args=ap.parse_args()
    data=read_json(args.input)
    fmt=args.format
    if fmt=="auto":
        fmt="sarif" if isinstance(data,dict) and "runs" in data else ("sonar" if isinstance(data,dict) and "issues" in data and "total" in data else "checkmarx")
    if fmt=="sarif": findings=sarif_items(data)
    elif fmt=="sonar": findings=sonar_items(data)
    else: findings=generic_items(data)
    changed=None
    if args.changed_files:
        changed={x.strip().replace("\\","/") for x in Path(args.changed_files).read_text(encoding="utf-8").splitlines() if x.strip()}
        for f in findings:
            p=(f.get("path") or "").replace("\\","/")
            f["scope"]="changed" if p in changed or any(p.endswith("/"+c) for c in changed) else "out_of_scope"
    else:
        for f in findings: f["scope"]="unknown"
    result={"schema_version":"1.0","input_file":args.input,"input_format":fmt,
            "finding_count":len(findings),"findings":findings,
            "scope_note":"Path matching is a coarse filter, not proof that a finding was introduced by the diff. Verify changed line ranges against the confirmed-base diff."}
    Path(args.output).write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    if args.markdown:
        lines=["# Normalized Security Findings","",f"- Input: `{args.input}`",f"- Format: `{fmt}`",f"- Findings: **{len(findings)}**","",
               "> Scope labels are path-based only. Confirm each finding against the committed diff before calling it newly introduced.","",
               "| Severity | Tool | Rule | Path:Line | Scope | Finding |","|---|---|---|---|---|---|"]
        for f in findings:
            path=(f.get("path") or "—")+(":"+str(f.get("line")) if f.get("line") else "")
            vals=[f.get("severity_normalized"),f.get("source_tool"),f.get("rule_id"),path,f.get("scope"),f.get("title")]
            lines.append("| "+" | ".join(str(v or "—").replace("|","\\|").replace("\n"," ") for v in vals)+" |")
        Path(args.markdown).write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"Normalized {len(findings)} findings -> {args.output}")
if __name__=="__main__":
    try: main()
    except Exception as e:
        print(f"ERROR: {e}",file=sys.stderr); sys.exit(2)
