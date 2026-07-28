#!/usr/bin/env python3
"""Render the complete, evidence-authenticated current regex comparison."""
from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
import copy
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import threading
import time
import zlib

ROOT = Path('/home/dev-user/src/rebar')
SCHEMA = 'rebar-candidate-current-overview-v17'
SELF = 'tools/render_candidate_current_overview_v17.py'
OUT = 'docs/evidence/candidate-current-overview-v17'
PYTHON = '/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14'
GO_BRIDGE = '52101f0afe29a568e3c2e22a06d47c89c051e08a0e2024ad4891c5ae2d60fb6a'
OLD = {
 'source': ('tools/render_candidate_current_overview_v16.py', '4228b6b74708ecd3ba143b1556ae9e6c0592b118ce22285751f7b53d976a95c4'),
 'inputs': ('docs/evidence/candidate-current-overview-v16.inputs.json', 'd96cc1b22b7ef87c1717cfcddefb98b5ec73b9d7a746cdf09e7556f05969c754'),
 'summary': ('docs/evidence/candidate-current-overview-v16.json', '8d11c93210e53a8b4b40eb51f14894a97d7351f5030acd1819aca75c9b39a3fc'),
 'svg': ('docs/evidence/candidate-current-overview-v16.svg', '0d72d79ae4efdd79cc0e98495fd8f946d26ead704d594f96b43145fc5f29fd65'),
 'campaign_source': ('tools/run_owned_six_family_original_p0_campaign_v1.py', '50ac9f549739bb6b540f1762177f25b46c1fa345dce717ea7163e15d98ae7e88'),
 'campaign_contract': ('oracle/phase2/six-family-p0-campaign-v1.json', 'c619e63dd18b8242bfc1af9e01030eff60e8d17128a83de216992b5cdc619801'),
}
ARCHIVE = ('oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-cpp-phase2-v1-failures.json.gz', '0462adbd6ee7bafb274578462117513669de9b849473a2e1ada441407bc814a2', 3244833)
RECEIPT = ('oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-cpp-phase2-v1-failures-publication-receipt.json', '7b1156c07441acd579149ca9b3aedcb9308eb75a130ce7f7df98aa6a89d776f6', 3936)
EXPANDED = ('58d918b4febe8fcbc5b9f7945c376ae639455fb69da46336b674a8dca1dd0fae', 97639407)
SUITES = (('original_bounded_v5',151),('public_v3',864),('scanner_v3',1024),('buffer_v3',768),('managed_v1',1024),('scanner_verbose_v1',2854),('public_types_v1',6912),('substitution_v2',5120),('shape_v2',10240),('public_surface_v19',1376),('subinterpreter_v2',128),('pep688_v4',264),('threaded_pattern_v1',512))
SEMANTIC = {'original_bounded_v5':43,'public_v3':40,'scanner_v3':992,'buffer_v3':181,'managed_v1':600,'public_surface_v19':336,'pep688_v4':116}
INFRA = ('scanner_verbose_v1','public_types_v1','substitution_v2','shape_v2','threaded_pattern_v1')
FAMILIES = ('python','rust','c','zig','cpp','go','fortran')
MAX_REPORT = 256 * 1024 * 1024
WITHDRAWN_OUTPUTS = {
 OUT+'.inputs.json':'15d054747dad1c40dfb8c90eabc13663f0574acd6b090069a369129d98b5c8c1',
 OUT+'.json':'9cd6d7cdf34d0b7f430661c21f9882c1031973d130818a9a63be8d87e89d2b71',
 OUT+'.svg':'91b8cdd106f996a73ea73c7662972daabf6f7b2fc5b1bac7c1805df2a6b63a55',
}


class GraphError(Exception):
    pass


def need(value, message):
    if value is not True:
        raise GraphError(message)


def digest(raw):
    need(type(raw) is bytes, 'hash complete bytes only')
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    try:
        return (json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(',', ':'))+'\n').encode('ascii')
    except (TypeError, ValueError, UnicodeError) as e:
        raise GraphError('non-canonical evidence') from e


def unique(pairs):
    out = {}
    for k, v in pairs:
        need(type(k) is str and k not in out, 'duplicate JSON field')
        out[k] = v
    return out


def document(raw, *, canonical_required=True):
    try:
        value = json.loads(raw, object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(GraphError('nonfinite JSON')))
    except (ValueError, TypeError, UnicodeError) as e:
        raise GraphError('invalid exact JSON') from e
    need(type(value) is dict, 'JSON must be an object')
    if canonical_required:
        need(canonical(value) == raw, 'JSON bytes are not canonical')
    return value


def checked_path(value):
    need(type(value) is str and value and '\\' not in value and '\x00' not in value, 'invalid relative owner')
    parts = value.split('/')
    need(all(p not in ('','.','..') for p in parts), 'owner escaped repository')
    return parts


def read_owner(path, expected, maximum=MAX_REPORT, *, private=False, size=None):
    parts=checked_path(path)
    need(type(expected) is str and len(expected)==64 and all(c in '0123456789abcdef' for c in expected), 'invalid exact owner digest')
    flags=os.O_RDONLY|getattr(os,'O_CLOEXEC',0)|getattr(os,'O_NOFOLLOW',0)
    df=flags|getattr(os,'O_DIRECTORY',0)
    fds=[]
    try:
        current=os.open(str(ROOT),df); fds.append(current)
        for part in parts[:-1]:
            current=os.open(part,df,dir_fd=current); fds.append(current)
        fd=os.open(parts[-1],flags,dir_fd=current); fds.append(fd)
        before=os.fstat(fd); named=os.stat(parts[-1],dir_fd=current,follow_symlinks=False)
        need(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode) and (before.st_dev,before.st_ino)==(named.st_dev,named.st_ino) and 0<before.st_size<=maximum, 'invalid, linked, truncated or oversized owner '+path)
        if private: need(stat.S_IMODE(before.st_mode)==0o600,'campaign evidence must be owner-only')
        if size is not None: need(before.st_size==size,'exact owner length changed')
        chunks=[]; remaining=before.st_size
        while remaining:
            chunk=os.read(fd,min(remaining,1048576)); need(bool(chunk),'truncated owner'); chunks.append(chunk); remaining-=len(chunk)
        need(os.read(fd,1)==b'','concealed owner bytes')
        after=os.fstat(fd); raw=b''.join(chunks)
        need((before.st_dev,before.st_ino,before.st_size)==(after.st_dev,after.st_ino,after.st_size) and digest(raw)==expected,'owner identity or contents changed '+path)
        return raw,(before.st_dev,before.st_ino)
    finally:
        for fd in reversed(fds): os.close(fd)


def pin(path, sha):
    checked_path(path)
    return {'path':path,'sha256':sha}


def verify_legacy():
    legacy={k:read_owner(*v)[0] for k,v in OLD.items()}
    oldin=document(legacy['inputs']); oldsum=document(legacy['summary']); contract=document(legacy['campaign_contract'])
    need(oldin.get('schema')=='rebar-candidate-current-overview-v16-inputs' and oldsum.get('schema')=='rebar-candidate-current-overview-v16-summary','V16 context replaced')
    snap=oldsum.get('snapshot'); need(type(snap)is dict,'missing prior snapshot')
    need(oldin.get('full_case_denominator')==31237 and oldin.get('suite_count')==13 and snap.get('full_case_denominator')==31237 and snap.get('baseline_passed')==31237 and snap.get('suite_count')==13,'original baseline denominator changed')
    need(oldin.get('candidate_families')==list(FAMILIES) and snap.get('frozen_independent_engine_family_count')==6 and snap.get('current_source_owner_count')==25 and snap.get('all_actual_candidate_and_native_evidence_owner_count')==65 and snap.get('qualified_candidate_count')==0,'historical engine or evidence denominator changed')
    need(snap.get('final_comparison_planned_case_count')==4194304 and snap.get('final_comparison_cases_generated') is False and snap.get('final_holdout_opened') is False and snap.get('performance')=='NOT MEASURED','final holdout or performance was opened')
    for family,key in (('rust','rust_actual_semantic_mismatch_count'),('c','c_actual_semantic_mismatch_count'),('zig','zig_actual_semantic_mismatch_count')):
        need(snap.get(key)=={'rust':2042,'c':2094,'zig':1764}[family],'prior semantic failures changed')
    pins=oldin.get('frozen_inputs'); need(type(pins)is dict and len(pins)==103,'prior frozen evidence was removed')
    for key,value in pins.items():
        need(type(value)is dict and set(value)=={'path','sha256'},'invalid old context pin')
        read_owner(value['path'],value['sha256'])
    owners=[]
    for row in oldin['families']:
        sources=row.get('owned_sources')
        need(type(sources)is list,'family source closure missing')
        for item in sources:
            need(type(item)is dict and set(item)=={'path','sha256'},'wrong source closure')
            read_owner(item['path'],item['sha256']); owners.append(item['path'])
    need(len(owners)==25 and len(set(owners))==25,'source families overlap')
    need(contract.get('schema')=='rebar-owned-six-family-original-p0-campaign-v1-source-freeze' and contract.get('suite_count')==13 and contract.get('case_execution_denominator')==31237 and contract.get('source_owner_count')==25 and contract.get('historical_evidence',{}).get('total_distinct_evidence_owner_count')==65,'actual campaign freeze changed')
    return oldin,oldsum,contract


def validate_campaign(receipt,report,archive_identity,receipt_identity):
    need(receipt.get('schema')=='rebar-owned-six-family-original-p0-campaign-v1-durable-publication-receipt' and receipt.get('status')=='PASS' and receipt.get('candidate_status')=='FAIL' and receipt.get('candidate_family')=='cpp','publication success is not C++ compatibility success')
    need(report.get('schema')=='rebar-owned-six-family-original-p0-campaign-v1-complete-candidate-evaluation' and report.get('status')=='FAIL' and report.get('candidate_family')=='cpp' and report.get('candidate_qualified') is False,'actual C++ outcome was concealed')
    for obj in (receipt,report):
        need(obj.get('suite_count')==13 and obj.get('case_execution_denominator')==31237 and obj.get('completed_suite_count')==13,'the complete original campaign was shortened')
        need(obj.get('campaign_source_sha256')==OLD['campaign_source'][1] and obj.get('campaign_document_sha256')==OLD['campaign_contract'][1],'campaign owner was replaced')
        need(obj.get('hidden_cases_read')==0 and obj.get('benchmark_files_read')==0 and obj.get('clock_samples')==0 and obj.get('timing_trials_run')==0 and obj.get('performance')=='NOT MEASURED' and obj.get('holdout')=='NOT OPENED' and obj.get('winner_selected') is False,'campaign opened or measured protected evidence')
        need(obj.get('all_mismatches_crashes_and_timeouts_preserved') is True,'actual failure detail was hidden')
    arc=receipt.get('archive'); need(type(arc)is dict and arc.get('sha256')==ARCHIVE[1] and arc.get('size_bytes')==ARCHIVE[2] and arc.get('mode')==0o600 and arc.get('exclusive_creation') is True and arc.get('file_fsync_completed') is True and arc.get('same_inode_readback_verified') is True and receipt.get('archive_directory_fsync_completed') is True,'archive durability not proven')
    need((arc.get('device'),arc.get('inode'))==archive_identity and archive_identity!=receipt_identity,'campaign repository owners are not genuinely distinct')
    need(receipt.get('uncompressed_sha256')==EXPANDED[0] and receipt.get('uncompressed_bytes')==EXPANDED[1] and receipt.get('failure_preserved') is True,'expanded actual failure was changed')
    need(receipt.get('activation')==report.get('activation') and receipt.get('restoration')==report.get('restoration'),'signed activation or recovery was substituted')
    activation=report['activation']; restore=report['restoration']
    need(type(activation)is dict and activation.get('status')=='PASS' and activation.get('family')=='cpp' and activation.get('group_atomic') is False,'genuine V4 C++ activation missing')
    need(type(restore)is dict and restore.get('status')=='PASS' and restore.get('route')=='reportful-restore','original state was not restored before publication')
    original=restore.get('actual_restoration'); need(type(original)is dict and original.get('status')=='PASS' and original.get('family')=='cpp' and original.get('reportless_recovery') is False and original.get('group_atomic') is False,'genuine reportful recovery missing')
    targets=original.get('restored_targets'); need(type(targets)is dict and set(targets)=={'bridge'} and targets['bridge'].get('status')=='restored-originally-absent' and targets['bridge'].get('removed_only_authenticated_promoted_inode') is True,'combined bridge was not restored to its absent original')
    rows=report.get('suite_results'); need(type(rows)is list and len(rows)==13,'not every original worker was preserved')
    semantic={}; infra=[]; passes=[]; crashes=0; timeouts=0
    for row,(name,count) in zip(rows,SUITES,strict=True):
        need(type(row)is dict and row.get('suite')==name and row.get('case_execution_denominator')==count and row.get('actual_worker_started') is True,'original worker route omitted or reordered')
        proc=row.get('process'); need(type(proc)is dict,'actual original worker stream omitted')
        need(proc.get('returncode') in (0,1),'actual worker crashed')
        need(proc.get('timed_out') is False and proc.get('stdout_overflow') is False and proc.get('stderr_overflow') is False and proc.get('stdout_reader_error') is None and proc.get('stderr_reader_error') is None,'actual timeout, overflow, or stream failure was hidden')
        for channel in ('stdout','stderr'):
            encoded=proc.get(channel+'_base64'); length=proc.get(channel+'_bytes'); expected=proc.get(channel+'_sha256')
            need(type(encoded)is str and type(length)is int and length>=0 and type(expected)is str,'complete original worker stream omitted')
            try: raw=base64.b64decode(encoded,validate=True)
            except (ValueError,TypeError) as error: raise GraphError('invalid original worker stream') from error
            need(len(raw)==length and digest(raw)==expected and base64.b64encode(raw).decode('ascii')==encoded,'original worker stream was clipped or forged')
        timeouts += int(proc.get('timed_out') is True)
        if row.get('status')=='PASS':
            need(row.get('genuine_original_suite') is True and row.get('mismatch_count')==0,'unproven passing suite')
            if name=='subinterpreter_v2':
                observed=row.get('complete_original_observation')
                need(type(observed)is dict and observed.get('actual_case_interpreter_exec_calls')==394 and observed.get('actual_initialization_interpreter_exec_calls')==11 and observed.get('actual_guard_cleanup_interpreter_exec_calls')==11 and observed.get('actual_interpreters_created')==11 and observed.get('actual_interpreters_destroyed')==11 and observed.get('all_real_pipes_read_to_eof') is True and observed.get('all_real_pipe_descriptors_closed') is True,'the 128 real nested interpreter cases were not genuinely completed')
            passes.append((name,count))
        elif row.get('status')=='FAIL' and row.get('genuine_original_suite') is True:
            mismatches=row.get('mismatch_count'); need(type(mismatches)is int and mismatches>0,'invented semantic mismatch')
            need(type(row.get('all_mismatches'))is list and len(row['all_mismatches'])==mismatches and row.get('semantic_failure_preserved') is True,'actual mismatch records were concealed')
            semantic[name]=mismatches
        else:
            need(row.get('status')=='FAIL' and row.get('genuine_original_suite') is False and row.get('mismatch_count') is None,'infrastructure failure misrepresented as semantic mismatch')
            infra.append(name)
    need(passes==[('subinterpreter_v2',128)] and semantic==SEMANTIC and tuple(infra)==INFRA and sum(semantic.values())==2308 and timeouts==0 and report.get('verified_passing_case_count')==128,'real C++ suite totals or failure classes changed')
    return {'status':'FAIL','completed_suite_count':13,'passing_suite_count':1,'verified_passing_case_count':128,'semantic_mismatch_count':2308,'semantic_failure_suite_counts':semantic,'infrastructure_failure_suites':infra,'crash_count':crashes,'timeout_count':timeouts,'restoration_status':'PASS','restoration_route':'reportful-restore','restored_original_state':'originally absent','candidate_qualified':False}


def xml(value):
    return str(value).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;').replace("'",'&apos;')


def make_svg(snapshot,source_hash,manifest_hash):
    names={'python':'Python re','rust':'Rust','c':'C','zig':'Zig','cpp':'C++','go':'Go','fortran':'Fortran'}
    details={'python':('31,237 / 31,237','All original Python checks passed','pass'),'rust':('FAILED; NOT QUALIFIED','7,461 verified passes; 2,042 actual matching differences','fail'),'c':('FAILED; NOT QUALIFIED','7,197 verified passes; 2,094 actual matching differences','fail'),'zig':('FAILED; NOT QUALIFIED','3,583 verified passes; 1,764 actual matching differences','fail'),'cpp':('FAILED; NOT QUALIFIED','128 verified passes; 2,308 matching differences; 5 separate infrastructure failures','fail'),'go':('BUILT; MATCHING NOT MEASURED','Built twice from independent Go source; not yet compatibility-tested','pending'),'fortran':('BUILD NOT REPRODUCIBLE','Compiled twice; engine outputs differ; matching NOT MEASURED','pending')}
    t=lambda x,y,s,c='body',a=None:'<text x="'+str(x)+'" y="'+str(y)+'" class="'+c+'"'+(' text-anchor="'+a+'"' if a else '')+'>'+xml(s)+'</text>'
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1580" viewBox="0 0 1600 1580" role="img" aria-labelledby="v17-title v17-description">','<title id="v17-title">Which from-scratch engines match Python re?</title>','<desc id="v17-description">Python passes all 31,237 original checks. Zero of six replacements is fully compatible. C++ genuinely passes 128 checks, has 2,308 recorded matching differences across seven groups, and five separate infrastructure failures. Rust, C, and Zig also have preserved actual failures. Go matching has not been tested. Fortran engines do not reproduce. All 67 repository evidence records are preserved. Speed, memory, and confidence are not measured; the proposed 4,194,304-case holdout has not been generated or opened.</desc>','<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.title{font-size:36px;font-weight:760;fill:#16324f}.heading{font-size:25px;font-weight:740;fill:#16324f}.body{font-size:16px;fill:#42556c}.name{font-size:18px;font-weight:720;fill:#16324f}.pass{font-size:15px;font-weight:740;fill:#00794c}.fail{font-size:15px;font-weight:740;fill:#a15e00}.pending{font-size:15px;font-weight:720;fill:#58697d}.big{font-size:31px;font-weight:760;fill:#16324f}.foot{font-size:12px;fill:#53667b}</style>','<rect width="1600" height="1580" rx="22" fill="#f4f7fb"/>',t(56,70,'Can these engines replace Python re?','title'),t(58,101,'Python 3.14.6 · independent, from-scratch engines · every real failure preserved')]
    cards=[('31,237','original compatibility checks'),('0 of 6','fully compatible replacements'),('67','verified repository evidence files'),('NOT MEASURED','speed and memory')]
    for idx,(n,label) in enumerate(cards):
        x=56+idx*386; parts += ['<rect x="'+str(x)+'" y="124" width="368" height="100" rx="13" fill="#ffffff" stroke="#dae4ee"/>',t(x+15,168,n,'big'),t(x+15,200,label)]
    parts += ['<rect x="56" y="247" width="1488" height="742" rx="16" fill="#ffffff" stroke="#dae4ee"/>',t(78,288,'1. Does it match Python?','heading'),t(80,316,'Every result uses the same original 31,237 checks. Unrun checks are never counted as passes.')]
    for idx,key in enumerate(FAMILIES):
        y=345+idx*79; result,detail,style=details[key]; parts += ['<rect x="78" y="'+str(y)+'" width="1443" height="67" rx="9" fill="#f8fafd" stroke="#e5ecf2"/>',t(96,y+27,names[key],'name'),t(1498,y+27,result,style,'end'),t(270,y+50,detail)]
    parts += [t(82,932,'C++: seven genuine matching-failure groups; five separate infrastructure failures; 0 crashes or timeouts.'),t(82,955,'All 13 original groups ran. The original C++ bridge state was safely restored.'),'<rect x="56" y="1010" width="1488" height="435" rx="16" fill="#ffffff" stroke="#dae4ee"/>',t(78,1052,'2. Is any candidate faster?','heading'),t(80,1080,'NOT MEASURED. There are no speed bars, confidence intervals, memory claims, or rankings.')]
    for idx,key in enumerate(FAMILIES):
        y=1100+idx*34; parts += [t(95,y+18,names[key],'name'),t(1500,y+18,'REFERENCE ONLY; NOT TIMED' if key=='python' else 'NOT MEASURED','pending','end')]
    parts += [t(82,1380,'The 1.5× speed target is a goal, not an observed result.'),t(82,1411,'Proposed 4,194,304-case holdout: NOT GENERATED; NOT OPENED.'),t(60,1480,'V16 history and all independent family sources are authenticated; the C++ failure and restoration are preserved.','foot'),t(60,1506,'Inputs SHA-256: '+manifest_hash,'foot'),t(60,1530,'Renderer SHA-256: '+source_hash,'foot'),'</svg>\n']
    return '\n'.join(parts).encode('utf-8')


def build(source_hash):
    need(len(source_hash)==64 and digest(read_owner(SELF,source_hash)[0])==source_hash,'V17 source changed')
    oldin,oldsum,contract=verify_legacy()
    archive,aid=read_owner(ARCHIVE[0],ARCHIVE[1],MAX_REPORT,private=True,size=ARCHIVE[2]); rr,rid=read_owner(RECEIPT[0],RECEIPT[1],MAX_REPORT,private=True,size=RECEIPT[2]); need(aid!=rid,'campaign archive and receipt share an inode')
    receipt=document(rr); inflater=zlib.decompressobj(16+zlib.MAX_WBITS); expanded=inflater.decompress(archive,MAX_REPORT+1)
    need(inflater.eof and not inflater.unused_data and not inflater.unconsumed_tail and len(expanded)==EXPANDED[1] and digest(expanded)==EXPANDED[0],'complete original report changed or exceeded its 256-MiB bound')
    report=document(expanded,canonical_required=False); cpp=validate_campaign(receipt,report,aid,rid)
    prior=oldsum['snapshot']; snapshot=copy.deepcopy(prior); snapshot.update({'qualified_candidate_count':0,'all_actual_candidate_and_native_evidence_owner_count':67,'preserved_prior_candidate_evidence_owner_count':65,'preserved_v16_all_actual_candidate_and_cpp_evidence_owner_count':prior['all_actual_candidate_and_cpp_evidence_owner_count'],'all_actual_candidate_and_cpp_evidence_owner_count':55,'preserved_v16_verified_activation_v4_actual_activation_count':prior['verified_activation_v4_actual_activation_count'],'verified_activation_v4_actual_activation_count':1,'verified_activation_v4_current_active_target_count':0,'verified_activation_v4_source_status':'V4 SOURCE VERIFIED; ONE C++ ACTIVATION PERFORMED AND ORIGINAL STATE RESTORED','current_tested_candidate_family_count':4,'cpp_full_original_campaign':cpp,'cpp_matching_test_status':'FAIL','cpp_candidate_qualified':False,'cpp_activation_status':'ACTIVATED; ORIGINAL STATE RESTORED; NO ACTIVE TARGETS','performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','hidden_cases_read':0,'clock_samples':0,'timing_trials_run':0,'final_comparison_cases_generated':False,'final_comparison_planned_case_count':4194304,'final_holdout_opened':False,'winner_selected':False})
    validate_snapshot(snapshot)
    manifest={'schema':SCHEMA+'-inputs','version':17,'python':'3.14.6','renderer':pin(SELF,source_hash),'previous_overview':{k:pin(*v) for k,v in OLD.items() if k in ('source','inputs','summary','svg')},'campaign_source':pin(*OLD['campaign_source']),'campaign_contract':pin(*OLD['campaign_contract']),'cpp_campaign_archive':pin(ARCHIVE[0],ARCHIVE[1]),'cpp_campaign_receipt':pin(RECEIPT[0],RECEIPT[1]),'full_case_denominator':31237,'suite_count':13,'candidate_families':list(FAMILIES),'current_source_owner_count':25,'historical_repository_evidence_owner_count':65,'new_repository_evidence_owner_count':2,'repository_evidence_owner_count':67,'performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','final_comparison_planned_case_count':4194304,'final_comparison_cases_generated':False,'final_holdout_opened':False,'winner_selected':False}
    mraw=canonical(manifest); msha=digest(mraw); svg=make_svg(snapshot,source_hash,msha)
    summary={'schema':SCHEMA+'-summary','status':'PASS','python':'3.14.6','source':pin(SELF,source_hash),'inputs':pin(OUT+'.inputs.json',msha),'svg':pin(OUT+'.svg',digest(svg)),'snapshot':snapshot,'families':copy.deepcopy(oldin['families']),'full_case_denominator':31237,'suite_count':13,'repository_evidence_owner_count':67,'performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','hidden_cases_read':0,'clock_samples':0,'timing_trials_run':0,'final_comparison_planned_case_count':4194304,'final_comparison_cases_generated':False,'final_holdout_opened':False,'winner_selected':False}
    for row in summary['families']:
        if row.get('family')=='cpp': row.update({'correctness':'FAILED; NOT QUALIFIED','matching_test_status':'FAIL','activation_status':'ACTIVATED; ORIGINAL STATE RESTORED','qualified':False,'complete_campaign':cpp})
    return manifest,snapshot,((OUT+'.inputs.json',mraw),(OUT+'.svg',svg),(OUT+'.json',canonical(summary)))


def validate_snapshot(snapshot):
    need(type(snapshot)is dict and snapshot.get('full_case_denominator')==31237 and snapshot.get('suite_count')==13 and snapshot.get('baseline_passed')==31237,'snapshot baseline denominator changed')
    need(snapshot.get('qualified_candidate_count')==0 and snapshot.get('current_source_owner_count')==25 and snapshot.get('frozen_independent_engine_family_count')==6 and snapshot.get('current_tested_candidate_family_count')==4,'current source, tested, or qualification counts were invented')
    need(snapshot.get('all_actual_candidate_and_native_evidence_owner_count')==67 and snapshot.get('all_actual_candidate_and_cpp_evidence_owner_count')==55 and snapshot.get('preserved_prior_candidate_evidence_owner_count')==65 and snapshot.get('preserved_v16_all_actual_candidate_and_cpp_evidence_owner_count')==53,'historical and current evidence owner ledgers were mixed')
    need(snapshot.get('preserved_v16_verified_activation_v4_actual_activation_count')==0 and snapshot.get('verified_activation_v4_actual_activation_count')==1 and snapshot.get('verified_activation_v4_current_active_target_count')==0 and snapshot.get('verified_activation_v4_source_status')=='V4 SOURCE VERIFIED; ONE C++ ACTIVATION PERFORMED AND ORIGINAL STATE RESTORED' and snapshot.get('cpp_activation_status')=='ACTIVATED; ORIGINAL STATE RESTORED; NO ACTIVE TARGETS','actual V4 activation and restored state were concealed')
    cpp=snapshot.get('cpp_full_original_campaign')
    need(type(cpp)is dict and cpp.get('status')=='FAIL' and cpp.get('completed_suite_count')==13 and cpp.get('passing_suite_count')==1 and cpp.get('verified_passing_case_count')==128 and cpp.get('semantic_mismatch_count')==2308 and cpp.get('semantic_failure_suite_counts')==SEMANTIC and cpp.get('infrastructure_failure_suites')==list(INFRA) and cpp.get('crash_count')==0 and cpp.get('timeout_count')==0 and cpp.get('restoration_status')=='PASS' and cpp.get('candidate_qualified') is False,'actual 13-suite C++ failures were changed')
    need(snapshot.get('performance')=='NOT MEASURED' and snapshot.get('memory')=='NOT MEASURED' and snapshot.get('confidence_intervals')=='NOT MEASURED' and snapshot.get('hidden_cases_read')==0 and snapshot.get('clock_samples')==0 and snapshot.get('timing_trials_run')==0 and snapshot.get('final_comparison_planned_case_count')==4194304 and snapshot.get('final_comparison_cases_generated') is False and snapshot.get('final_holdout_opened') is False and snapshot.get('winner_selected') is False,'unmeasured timing or unopened holdout was falsified')


def output(path,raw,verify,refresh=False):
    target=ROOT/path; parts=checked_path(path); need(parts[:2]==['docs','evidence'],'output outside approved graph directory')
    flags=os.O_RDONLY|getattr(os,'O_CLOEXEC',0)|getattr(os,'O_NOFOLLOW',0)
    try:
        fd=os.open(str(target),flags)
    except FileNotFoundError:
        need(not verify,'required V17 graph output is missing')
        wf=os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_CLOEXEC',0)|getattr(os,'O_NOFOLLOW',0); fd=os.open(str(target),wf,0o644)
        try:
            cursor=0
            while cursor<len(raw):
                count=os.write(fd,raw[cursor:]); need(type(count)is int and count>0,'partial graph write'); cursor+=count
            os.fsync(fd)
        finally: os.close(fd)
        read_owner(path,digest(raw),max(len(raw),1))
        return
    try:
        before=os.fstat(fd); need(stat.S_ISREG(before.st_mode),'existing V17 output is not regular'); chunks=[]; left=before.st_size
        while left:
            block=os.read(fd,min(left,1048576)); need(bool(block),'truncated V17 output'); chunks.append(block); left-=len(block)
        existing=b''.join(chunks); need(os.read(fd,1)==b'','existing graph has concealed bytes')
        if existing==raw: return
        need(refresh and not verify and path in WITHDRAWN_OUTPUTS and digest(existing)==WITHDRAWN_OUTPUTS[path],'refuse to replace an unauthenticated V17 graph output')
        directory=os.open(str(ROOT/'docs'/'evidence'),os.O_RDONLY|getattr(os,'O_DIRECTORY',0)|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_CLOEXEC',0))
        temp='.rebar-v17-authenticated-refresh-'+digest(raw)[:24]
        pending=None
        try:
            pending=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_CLOEXEC',0),0o644,dir_fd=directory)
            cursor=0
            while cursor<len(raw):
                written=os.write(pending,raw[cursor:]); need(type(written)is int and written>0,'partial authenticated V17 refresh'); cursor+=written
            os.fsync(pending)
            old=os.stat(parts[-1],dir_fd=directory,follow_symlinks=False)
            need((old.st_dev,old.st_ino)==(before.st_dev,before.st_ino),'withdrawn output was replaced during refresh')
            os.replace(temp,parts[-1],src_dir_fd=directory,dst_dir_fd=directory); os.fsync(directory)
        finally:
            if pending is not None: os.close(pending)
            os.close(directory)
    finally: os.close(fd)


def self_test():
    need(sum(n for _,n in SUITES)==31237 and len(SUITES)==13,'original denominator changed')
    need(sum(SEMANTIC.values())==2308 and len(SEMANTIC)==7 and len(INFRA)==5,'authentic CPP failure facts changed')
    need(set(SEMANTIC).isdisjoint(INFRA) and set(SEMANTIC)|set(INFRA)|{'subinterpreter_v2'}=={x for x,_ in SUITES},'suite classifications overlap')
    h=digest(b'v17-synthetic-only'); mh=digest(b'v17-synthetic-input'); pic=make_svg({'qualified_candidate_count':0},h,mh)
    need(b'0 of 6' in pic and b'2,308' in pic and b'128 verified passes' in pic and b'5 separate infrastructure failures' in pic and b'4,194,304' in pic and b'NOT MEASURED' in pic and b'NOT OPENED' in pic and b'role="img"' in pic,'truthful accessible overview missing')
    controls=0
    for bad in (b'{"a":1,"a":2}\n',b'{"a":NaN}\n',b'[]\n'):
        try: document(bad)
        except (GraphError,ValueError,UnicodeError): controls+=1
    need(controls==3,'hostile JSON controls failed')
    snapshot={'full_case_denominator':31237,'suite_count':13,'baseline_passed':31237,'qualified_candidate_count':0,'current_source_owner_count':25,'frozen_independent_engine_family_count':6,'current_tested_candidate_family_count':4,'all_actual_candidate_and_native_evidence_owner_count':67,'all_actual_candidate_and_cpp_evidence_owner_count':55,'preserved_prior_candidate_evidence_owner_count':65,'preserved_v16_all_actual_candidate_and_cpp_evidence_owner_count':53,'preserved_v16_verified_activation_v4_actual_activation_count':0,'verified_activation_v4_actual_activation_count':1,'verified_activation_v4_current_active_target_count':0,'verified_activation_v4_source_status':'V4 SOURCE VERIFIED; ONE C++ ACTIVATION PERFORMED AND ORIGINAL STATE RESTORED','cpp_activation_status':'ACTIVATED; ORIGINAL STATE RESTORED; NO ACTIVE TARGETS','cpp_full_original_campaign':{'status':'FAIL','completed_suite_count':13,'passing_suite_count':1,'verified_passing_case_count':128,'semantic_mismatch_count':2308,'semantic_failure_suite_counts':dict(SEMANTIC),'infrastructure_failure_suites':list(INFRA),'crash_count':0,'timeout_count':0,'restoration_status':'PASS','candidate_qualified':False},'performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','hidden_cases_read':0,'clock_samples':0,'timing_trials_run':0,'final_comparison_planned_case_count':4194304,'final_comparison_cases_generated':False,'final_holdout_opened':False,'winner_selected':False}
    validate_snapshot(snapshot)
    mutations=[('full_case_denominator',31236),('suite_count',12),('baseline_passed',31236),('qualified_candidate_count',1),('current_source_owner_count',24),('frozen_independent_engine_family_count',5),('current_tested_candidate_family_count',3),('all_actual_candidate_and_native_evidence_owner_count',66),('all_actual_candidate_and_cpp_evidence_owner_count',53),('preserved_prior_candidate_evidence_owner_count',64),('preserved_v16_all_actual_candidate_and_cpp_evidence_owner_count',55),('preserved_v16_verified_activation_v4_actual_activation_count',1),('verified_activation_v4_actual_activation_count',0),('verified_activation_v4_current_active_target_count',1),('verified_activation_v4_source_status','NOT RUN'),('cpp_activation_status','NOT RUN'),('performance','PASS'),('memory','PASS'),('confidence_intervals','PASS'),('hidden_cases_read',1),('clock_samples',1),('timing_trials_run',1),('final_comparison_planned_case_count',4194303),('final_comparison_cases_generated',True),('final_holdout_opened',True),('winner_selected',True)]
    for field,value in mutations:
        bad=copy.deepcopy(snapshot); bad[field]=value
        try: validate_snapshot(bad)
        except GraphError: controls+=1
        else: raise GraphError('failed to reject forged '+field)
    nested=[('status','PASS'),('completed_suite_count',12),('passing_suite_count',2),('verified_passing_case_count',129),('semantic_mismatch_count',2307),('infrastructure_failure_suites',list(INFRA[:-1])),('crash_count',1),('timeout_count',1),('restoration_status','FAIL'),('candidate_qualified',True)]
    for field,value in nested:
        bad=copy.deepcopy(snapshot); bad['cpp_full_original_campaign'][field]=value
        try: validate_snapshot(bad)
        except GraphError: controls+=1
        else: raise GraphError('failed to reject forged CPP '+field)
    for name in SEMANTIC:
        bad=copy.deepcopy(snapshot); bad['cpp_full_original_campaign']['semantic_failure_suite_counts'][name]+=1
        try: validate_snapshot(bad)
        except GraphError: controls+=1
        else: raise GraphError('failed to reject forged semantic suite '+name)
    need(controls>=46,'substantial pure hostile snapshot controls are mandatory')
    return {'schema':SCHEMA+'-source-self-test','status':'PASS','full_case_denominator':31237,'suite_count':13,'repository_evidence_owner_count':67,'cpp_verified_passing_case_count':128,'cpp_semantic_mismatch_count':2308,'cpp_infrastructure_failure_count':5,'qualified_candidate_count':0,'actual_source_reads':0,'actual_evidence_reads':0,'actual_output_writes':0,'actual_candidate_imports':0,'actual_candidate_processes_started':0,'clock_samples':0,'timing_trials_run':0,'performance_files_read':0,'hidden_cases_read':0,'performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','final_comparison_cases_generated':False,'final_holdout_opened':False,'winner_selected':False,'synthetic_hostile_rejections':controls,'synthetic_svg_sha256':digest(pic)}


def main():
    parser=argparse.ArgumentParser(description=__doc__); modes=parser.add_mutually_exclusive_group(required=True); modes.add_argument('--self-test',action='store_true'); modes.add_argument('--render',action='store_true'); modes.add_argument('--verify',action='store_true'); parser.add_argument('--source-sha256'); parser.add_argument('--go-bridge-sha256'); parser.add_argument('--manifest-sha256'); parser.add_argument('--refresh',action='store_true'); args=parser.parse_args()
    need(sys.implementation.name=='cpython' and tuple(sys.version_info[:3])==(3,14,6) and sys.flags.isolated==1 and sys.dont_write_bytecode and os.path.realpath(sys.executable)==os.path.realpath(PYTHON),'run using isolated pinned CPython 3.14.6')
    if args.self_test:
        need(args.source_sha256 is None and args.go_bridge_sha256 is None and args.manifest_sha256 is None and args.refresh is False,'synthetic mode cannot inspect actual evidence'); result=self_test()
    else:
        need(type(args.source_sha256)is str and args.go_bridge_sha256==GO_BRIDGE,'pin the exact renderer and committed Go bridge')
        manifest,snapshot,files=build(args.source_sha256); msha=digest(canonical(manifest))
        if args.manifest_sha256 is not None: need(args.manifest_sha256==msha,'incorrect exact graph manifest')
        if args.verify: need(type(args.manifest_sha256)is str and args.refresh is False,'verify requires a pinned manifest and cannot mutate outputs')
        for path,raw in files: output(path,raw,args.verify,args.refresh)
        result={'schema':SCHEMA+('-verified' if args.verify else '-rendered'),'status':'PASS','source_sha256':args.source_sha256,'inputs_sha256':msha,'svg_sha256':digest(files[1][1]),'summary_sha256':digest(files[2][1]),'full_case_denominator':31237,'suite_count':13,'repository_evidence_owner_count':67,'cpp_verified_passing_case_count':128,'cpp_semantic_mismatch_count':2308,'cpp_infrastructure_failure_count':5,'qualified_candidate_count':0,'outputs_written':not args.verify,'actual_candidate_imports':0,'actual_candidate_processes_started':0,'clock_samples':0,'timing_trials_run':0,'performance_files_read':0,'hidden_cases_read':0,'performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','final_comparison_cases_generated':False,'final_holdout_opened':False,'winner_selected':False}
    sys.stdout.buffer.write(canonical(result)); sys.stdout.buffer.flush()


if __name__=='__main__':
    try: main()
    except GraphError as e:
        sys.stderr.write('current V17 overview rejected: '+str(e)+'\n'); raise SystemExit(2) from e
