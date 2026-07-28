#!/usr/bin/env python3
"""Render the original Go publication failure without inventing a matcher result."""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import zlib

ROOT=Path('/home/dev-user/src/rebar')
SCHEMA='rebar-candidate-current-overview-v18'
SELF='tools/render_candidate_current_overview_v18.py'
OUT='docs/evidence/candidate-current-overview-v18'
PYTHON='/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14'
GO_BRIDGE='52101f0afe29a568e3c2e22a06d47c89c051e08a0e2024ad4891c5ae2d60fb6a'
V17={
 'source':('tools/render_candidate_current_overview_v17.py','2f14cad826b33ad873b1c46c986d8c7112ad9771cef309939203b64601340325'),
 'inputs':('docs/evidence/candidate-current-overview-v17.inputs.json','e8ac1d9954169d71da75724056d15cdad86918503da9ec2f36a7442e049945af'),
 'summary':('docs/evidence/candidate-current-overview-v17.json','605dbf715d7461474a1a787db3b75369ddf1f74477864e757b39fce4635735f0'),
 'svg':('docs/evidence/candidate-current-overview-v17.svg','975f044c388ec2ab0a975d1a8b72f0d335247c17a7c71efc384c311cfae9051e'),
}
PRESERVATION={
 'source':('tools/preserve_owned_go_campaign_publication_failure_v1.py','105b7e730eae779396840ccaca13152554244ea615e5403930e0adbd2344f5ba'),
 'protocol':('oracle/phase2/OWNED-GO-CAMPAIGN-PUBLICATION-FAILURE-V1.md','5e067f3d71c0997be69cd5e3eb246c2e1c9387cd40616230e806ddf561994f4f'),
 'contract':('oracle/phase2/owned-go-campaign-publication-failure-v1.json','f095f94f74255432b0ceff7eb1239e28d6e4e4effeab19d4f2fed86156b2925b'),
}
ARCHIVE=('oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-go-phase2-v1-publication-failure-evidence.json.gz','5ed230d255cc8ba87ff2790dd0bce091968252da159e2d8c6d7ada93feeae87e',7719)
RECEIPT=('oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-go-phase2-v1-publication-failure-evidence-publication-receipt.json','0b7d11dad3c204d34151a38d797b1177442040524acf68fb29633d4222d681b0',2724)
EXPANDED=('d354dc7ab5cc4bad0bd72c70a5e6af03749f019ebd047d07a8fe19c2e784a2e6',26265)
FAMILIES=('python','rust','c','zig','cpp','go','fortran')
PRIVATE_ROLES={'activation_report','activation_receipt','recovery_journal','engine_intention','bridge_intention'}
ABSENT_RESULTS={
 'oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-go-phase2-v1.json.gz',
 'oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-go-phase2-v1-publication-receipt.json',
 'oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-go-phase2-v1-failures.json.gz',
 'oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-go-phase2-v1-failures-publication-receipt.json',
}


class GraphError(Exception): pass


def need(test,message):
    if test is not True: raise GraphError(message)


def digest(raw):
    need(type(raw)is bytes,'hash only complete bytes')
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    try: return (json.dumps(value,ensure_ascii=True,allow_nan=False,sort_keys=True,separators=(',',':'))+'\n').encode('ascii')
    except (ValueError,TypeError,UnicodeError) as e: raise GraphError('noncanonical overview') from e


def unique(pairs):
    result={}
    for key,value in pairs:
        need(type(key)is str and key not in result,'duplicate failure evidence key'); result[key]=value
    return result


def document(raw):
    try: obj=json.loads(raw,object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(GraphError('nonfinite failure evidence')))
    except (ValueError,TypeError,UnicodeError) as e: raise GraphError('invalid frozen evidence JSON') from e
    need(type(obj)is dict and canonical(obj)==raw,'noncanonical failure evidence')
    return obj


def checked_path(path):
    need(type(path)is str and bool(path) and '\\' not in path and '\x00' not in path,'invalid relative evidence path')
    parts=path.split('/'); need(all(part not in ('','.','..') for part in parts),'evidence path escaped repository')
    return parts


def read_owner(path,sha,maximum=268435456,*,private=False,size=None):
    parts=checked_path(path); need(type(sha)is str and len(sha)==64 and all(x in '0123456789abcdef' for x in sha),'invalid pinned owner SHA')
    flags=os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_CLOEXEC',0); dflags=flags|getattr(os,'O_DIRECTORY',0); fds=[]
    try:
        current=os.open(str(ROOT),dflags); fds.append(current)
        for part in parts[:-1]: current=os.open(part,dflags,dir_fd=current); fds.append(current)
        fd=os.open(parts[-1],flags,dir_fd=current); fds.append(fd)
        before=os.fstat(fd); named=os.stat(parts[-1],dir_fd=current,follow_symlinks=False)
        need(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode) and (before.st_dev,before.st_ino)==(named.st_dev,named.st_ino) and 0<before.st_size<=maximum,'replaced, truncated or excessive evidence '+path)
        if private: need(stat.S_IMODE(before.st_mode)==0o600,'failure evidence must be owner-only')
        if size is not None: need(before.st_size==size,'failure evidence length changed')
        chunks=[]; remaining=before.st_size
        while remaining:
            chunk=os.read(fd,min(remaining,1048576)); need(bool(chunk),'truncated frozen evidence'); chunks.append(chunk); remaining-=len(chunk)
        need(os.read(fd,1)==b'','concealed evidence tail'); raw=b''.join(chunks); after=os.fstat(fd)
        need((before.st_dev,before.st_ino,before.st_size)==(after.st_dev,after.st_ino,after.st_size) and digest(raw)==sha,'frozen evidence hash or inode changed')
        return raw,(before.st_dev,before.st_ino)
    finally:
        for fd in reversed(fds): os.close(fd)


def pin(path,sha):
    checked_path(path); return {'path':path,'sha256':sha}


def validate_go_failure(report,receipt,archive_identity,receipt_identity):
    need(report.get('schema')=='rebar-owned-go-campaign-publication-failure-v1-complete-original-evidence' and report.get('status')=='FAIL','genuine Go publication infrastructure failure was concealed')
    need(receipt.get('schema')=='rebar-owned-go-campaign-publication-failure-v1-durable-evidence-publication-receipt' and receipt.get('status')=='PASS' and receipt.get('receipt_status_meaning')=='EVIDENCE PUBLICATION ONLY','failure evidence receipt is not a passing candidate')
    for value in (report,receipt):
        need(value.get('candidate_family')=='go' and value.get('candidate_label')=='phase2-v1' and value.get('candidate_status')=='NOT VERIFIED' and value.get('candidate_qualified') is False and value.get('qualified_candidate_count')==0,'an unrecorded Go verdict or qualification was fabricated')
        need(value.get('preservation_source_sha256')==PRESERVATION['source'][1] and value.get('preservation_protocol_sha256')==PRESERVATION['protocol'][1] and value.get('preservation_contract_sha256')==PRESERVATION['contract'][1],'failure preservation source was replaced')
        need(value.get('retained_repository_evidence_owner_count')==67 and value.get('actual_candidate_workers')==0 and value.get('actual_native_activations')==0 and value.get('actual_native_promotions')==0 and value.get('hidden_cases_read')==0 and value.get('benchmark_files_read')==0 and value.get('clock_samples')==0 and value.get('timing_trials_run')==0 and value.get('performance')=='NOT MEASURED' and value.get('memory')=='NOT MEASURED' and value.get('holdout')=='NOT OPENED' and value.get('winner_selected') is False,'failure recorder executed a candidate, timed it or opened hidden cases')
    claim=report.get('failure_claim'); need(type(claim)is dict and claim.get('infrastructure_status')=='FAIL' and claim.get('actual_original_report_publication_max_bytes')==268435456 and claim.get('actual_original_archive_publication_max_bytes')==268435456 and claim.get('actual_original_report_cap_error')=='bound and preserve the entire canonical original campaign' and claim.get('candidate_status')=='NOT VERIFIED' and claim.get('candidate_qualified') is False,'actual original 256 MiB publication-limit failure was changed')
    for field in ('actual_attempted_suite_count','actual_completed_suite_count','actual_suite_statuses','actual_mismatch_count','actual_crash_count','actual_timeout_count','actual_full_worker_stdout','actual_original_report_bytes','actual_restoration_route'):
        need(claim.get(field)=='NOT RECORDED','invented unrecoverable original outcome '+field)
    need(claim.get('absent_canonical_targets_prove_restoration_route') is False and claim.get('prepared_journal_is_restoration_proof') is False,'absence is not proof of restoration route')
    need(receipt.get('infrastructure_status')=='FAIL' and receipt.get('actual_suite_statuses')=='NOT RECORDED' and receipt.get('actual_mismatch_count')=='NOT RECORDED' and receipt.get('actual_original_report_bytes')=='NOT RECORDED' and receipt.get('actual_restoration_route')=='NOT RECORDED' and receipt.get('actual_original_report_publication_max_bytes')==268435456,'receipt invented missing Go results')
    archive=receipt.get('archive'); need(type(archive)is dict and archive.get('sha256')==ARCHIVE[1] and archive.get('size_bytes')==ARCHIVE[2] and archive.get('mode')==0o600 and archive.get('exclusive_creation') is True and archive.get('file_fsync_completed') is True and archive.get('same_inode_readback_verified') is True and (archive.get('device'),archive.get('inode'))==archive_identity and receipt.get('archive_directory_fsync_completed') is True and archive_identity!=receipt_identity,'distinct genuinely durable Go failure owners were not proved')
    need(receipt.get('uncompressed_sha256')==EXPANDED[0] and receipt.get('uncompressed_bytes')==EXPANDED[1] and receipt.get('all_five_complete_original_owner_bytes_preserved') is True and receipt.get('embedded_private_owner_count')==5 and receipt.get('embedded_private_owner_total_original_bytes')==15395,'complete original private evidence was lost')
    owners=report.get('original_activation_owners'); need(type(owners)is list and len(owners)==5 and {o.get('role') for o in owners}==PRIVATE_ROLES,'signed activation evidence was omitted')
    total=0; identities=set()
    for owner in owners:
        need(type(owner)is dict and owner.get('mode')==0o600 and type(owner.get('device'))is int and type(owner.get('inode'))is int and owner['inode']>0 and type(owner.get('raw_base64'))is str,'private source owner is not genuine')
        raw=base64.b64decode(owner['raw_base64'],validate=True)
        need(len(raw)==owner.get('size_bytes') and digest(raw)==owner.get('sha256'),'private signed original bytes were changed')
        identities.add((owner['device'],owner['inode'])); total+=len(raw)
    need(len(identities)==5 and total==15395,'five distinct temporary owners were merged with repository owners')
    absent=report.get('absent_original_canonical_targets'); need(type(absent)is list and len(absent)==2 and all(x.get('present') is False for x in absent) and {x.get('relative') for x in absent}=={'candidates/_go_engine.so','candidates/_go_bridge.cpython-314-x86_64-linux-gnu.so'},'two absent split Go targets were substituted')
    missing=report.get('absent_original_outcome_owners'); need(type(missing)is list and len(missing)==4 and all(x.get('present') is False for x in missing) and {x.get('relative') for x in missing}==ABSENT_RESULTS,'a nonexistent normal Go outcome was invented')
    return {'candidate_status':'NOT VERIFIED','publication_status':'FAIL','failure_class':'original-canonical-report-publication-size-limit','original_report_publication_max_bytes':268435456,'suite_statuses':'NOT RECORDED','completed_suite_count':'NOT RECORDED','semantic_mismatch_count':'NOT RECORDED','crash_count':'NOT RECORDED','timeout_count':'NOT RECORDED','original_report_bytes':'NOT RECORDED','restoration_route':'NOT RECORDED','candidate_qualified':False,'preserved_private_activation_owner_count':5,'preserved_private_activation_owner_bytes':15395,'absent_canonical_target_count':2,'absent_original_outcome_owner_count':4}


def validate_snapshot(value):
    need(type(value)is dict and value.get('full_case_denominator')==31237 and value.get('suite_count')==13 and value.get('baseline_passed')==31237,'original Python denominator changed')
    need(value.get('frozen_independent_engine_family_count')==6 and value.get('current_source_owner_count')==25 and value.get('current_tested_candidate_family_count')==5 and value.get('qualified_candidate_count')==0,'source families, verified tests, or qualifications were invented')
    need(value.get('preserved_v17_repository_evidence_owner_count')==67 and value.get('all_actual_candidate_and_native_evidence_owner_count')==69 and value.get('all_actual_candidate_and_cpp_evidence_owner_count')==55 and value.get('go_publication_failure_repository_evidence_owner_count')==2,'repository evidence and private proof owners were merged')
    need(value.get('preserved_v17_verified_activation_v4_actual_activation_count')==1 and value.get('verified_activation_v4_actual_activation_count')==2 and value.get('verified_activation_v4_current_active_target_count')==0,'real activation totals or current inactive state were changed')
    cpp=value.get('cpp_full_original_campaign'); need(type(cpp)is dict and cpp.get('status')=='FAIL' and cpp.get('completed_suite_count')==13 and cpp.get('verified_passing_case_count')==128 and cpp.get('semantic_mismatch_count')==2308 and len(cpp.get('infrastructure_failure_suites',[]))==5,'authentic previous C++ failures were discarded')
    go=value.get('go_original_campaign_publication_failure'); need(type(go)is dict and go.get('candidate_status')=='NOT VERIFIED' and go.get('publication_status')=='FAIL' and go.get('original_report_publication_max_bytes')==268435456 and go.get('candidate_qualified') is False,'unverified Go original result was misrepresented')
    for key in ('suite_statuses','completed_suite_count','semantic_mismatch_count','crash_count','timeout_count','original_report_bytes','restoration_route'):
        need(go.get(key)=='NOT RECORDED','invented Go result '+key)
    need(value.get('performance')=='NOT MEASURED' and value.get('memory')=='NOT MEASURED' and value.get('confidence_intervals')=='NOT MEASURED' and value.get('hidden_cases_read')==0 and value.get('clock_samples')==0 and value.get('timing_trials_run')==0 and value.get('final_comparison_planned_case_count')==4194304 and value.get('final_comparison_cases_generated') is False and value.get('final_holdout_opened') is False and value.get('winner_selected') is False,'hidden benchmark, holdout, or winner was invented')


def xml(value): return str(value).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;').replace("'",'&apos;')


def make_svg(snapshot,source_hash,manifest_hash):
    validate_snapshot(snapshot)
    title=lambda x,y,s,c='body',a=None:'<text x="'+str(x)+'" y="'+str(y)+'" class="'+c+'"'+(' text-anchor="'+a+'"' if a else '')+'>'+xml(s)+'</text>'
    labels={'python':'Python re','rust':'Rust','c':'C','zig':'Zig','cpp':'C++','go':'Go','fortran':'Fortran'}
    results={'python':('31,237 / 31,237','All original Python reference checks passed','pass'),'rust':('FAILED; NOT QUALIFIED','7,461 verified passes; 2,042 genuine matching differences','fail'),'c':('FAILED; NOT QUALIFIED','7,197 verified passes; 2,094 genuine matching differences','fail'),'zig':('FAILED; NOT QUALIFIED','3,583 verified passes; 1,764 genuine matching differences','fail'),'cpp':('FAILED; NOT QUALIFIED','128 verified passes; 2,308 matching differences; five separate infrastructure failures','fail'),'go':('NOT VERIFIED; REPORT TOO LARGE','Engine built; original result could not be published within 256 MiB','warning'),'fortran':('BUILD NOT REPRODUCIBLE','Compiled engines differ; matching remains NOT MEASURED','warning')}
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1630" viewBox="0 0 1600 1630" role="img" aria-labelledby="v18-title v18-description">','<title id="v18-title">Which from-scratch engines actually match Python re?</title>','<desc id="v18-description">Python passes all 31,237 original checks. Zero of six replacement engines is proven compatible. C++ passed 128 checks, with 2,308 genuine matching differences and five separate infrastructure failures. The Go test result could not be published within its 256-mebibyte limit; its suite results, mismatch counts, and recovery route are not recorded and must not be guessed. All 69 repository evidence files remain available. Candidate speed, memory, and confidence are not measured. The proposed 4,194,304-case holdout has not been generated or opened.</desc>','<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.title{font-size:35px;font-weight:760;fill:#16324f}.heading{font-size:25px;font-weight:740;fill:#16324f}.body{font-size:15px;fill:#42556c}.name{font-size:18px;font-weight:720;fill:#16324f}.pass{font-size:15px;font-weight:750;fill:#00794c}.fail{font-size:15px;font-weight:740;fill:#a15e00}.warning{font-size:15px;font-weight:740;fill:#725400}.pending{font-size:15px;font-weight:700;fill:#58697d}.big{font-size:31px;font-weight:760;fill:#16324f}.foot{font-size:12px;fill:#53667b}</style>','<rect width="1600" height="1630" rx="22" fill="#f4f7fb"/>',title(54,69,'Can these engines replace Python re?','title'),title(56,100,'Python 3.14.6 · first-party engines · original failures never hidden')]
    for index,(number,label) in enumerate((('31,237','original compatibility checks'),('0 of 6','fully compatible replacements'),('69','verified repository evidence files'),('NOT MEASURED','speed, memory and confidence'))):
        x=54+index*386; parts += ['<rect x="'+str(x)+'" y="124" width="367" height="102" rx="13" fill="#fff" stroke="#dae4ee"/>',title(x+15,167,number,'big'),title(x+15,201,label)]
    parts += ['<rect x="54" y="245" width="1490" height="806" rx="16" fill="#fff" stroke="#dae4ee"/>',title(75,287,'1. Does it match Python?','heading'),title(77,315,'All engines share the original 13 groups and 31,237-case baseline. Unpublished outcomes are not passes.')]
    for index,family in enumerate(FAMILIES):
        y=342+index*83; result,detail,style=results[family]
        parts += ['<rect x="75" y="'+str(y)+'" width="1448" height="72" rx="9" fill="#f8fafd" stroke="#e5ecf2"/>',title(94,y+28,labels[family],'name'),title(1500,y+28,result,style,'end'),title(272,y+54,detail)]
    parts += [title(79,970,'Go: failure evidence is preserved; matching results, crashes and exact report size remain NOT RECORDED.'),title(79,998,'C++: its original 13-group failure and verified restoration remain unchanged.'),'<rect x="54" y="1070" width="1490" height="412" rx="16" fill="#fff" stroke="#dae4ee"/>',title(76,1110,'2. Is any replacement faster?','heading'),title(78,1136,'NOT MEASURED. No speed bars, confidence intervals, rankings, or memory results exist.')]
    for index,family in enumerate(FAMILIES):
        y=1154+index*34; parts += [title(93,y+18,labels[family],'name'),title(1500,y+18,'REFERENCE ONLY; NOT TIMED' if family=='python' else 'NOT MEASURED','pending','end')]
    parts += [title(80,1430,'A 1.5× speedup is a future goal, not a result.'),title(58,1505,'Proposed 4,194,304-case holdout: NOT GENERATED; NOT OPENED.','body'),title(58,1540,'Inputs SHA-256: '+manifest_hash,'foot'),title(58,1565,'Renderer SHA-256: '+source_hash,'foot'),'</svg>\n']
    return '\n'.join(parts).encode('utf-8')


def build(source_hash):
    own,_=read_owner(SELF,source_hash); need(digest(own)==source_hash,'V18 source changed')
    old_raw,_=read_owner(*V17['source']); prior={'__name__':'_rebar_frozen_current_overview_v17'}; exec(compile(old_raw,str(ROOT/V17['source'][0]),'exec'),prior)
    previous_manifest,previous_snapshot,prior_files=prior['build'](V17['source'][1])
    for path,raw in prior_files: prior['output'](path,raw,True)
    need(previous_snapshot.get('all_actual_candidate_and_native_evidence_owner_count')==67 and previous_snapshot.get('all_actual_candidate_and_cpp_evidence_owner_count')==55 and previous_snapshot.get('verified_activation_v4_actual_activation_count')==1,'genuine V17 historical context changed')
    for path,sha in PRESERVATION.values(): read_owner(path,sha)
    compressed,archive_identity=read_owner(ARCHIVE[0],ARCHIVE[1],1048576,private=True,size=ARCHIVE[2]); receipt_raw,receipt_identity=read_owner(RECEIPT[0],RECEIPT[1],1048576,private=True,size=RECEIPT[2]); need(archive_identity!=receipt_identity,'Go repository evidence owners were merged')
    inflater=zlib.decompressobj(16+zlib.MAX_WBITS); plain=inflater.decompress(compressed,1048577)
    need(inflater.eof and not inflater.unused_data and not inflater.unconsumed_tail and len(plain)==EXPANDED[1] and digest(plain)==EXPANDED[0],'complete Go failure preservation archive was altered')
    report=document(plain); receipt=document(receipt_raw); failure=validate_go_failure(report,receipt,archive_identity,receipt_identity)
    snapshot=copy.deepcopy(previous_snapshot)
    snapshot.update({'preserved_v17_repository_evidence_owner_count':67,'preserved_v17_verified_activation_v4_actual_activation_count':1,'all_actual_candidate_and_native_evidence_owner_count':69,'go_publication_failure_repository_evidence_owner_count':2,'verified_activation_v4_actual_activation_count':2,'verified_activation_v4_current_active_target_count':0,'verified_activation_v4_source_status':'V4 SOURCE VERIFIED; C++ AND GO ACTIVATED; NO CURRENTLY ACTIVE TARGETS','current_tested_candidate_family_count':5,'go_matching_test_status':'NOT VERIFIED; ORIGINAL RESULT PUBLICATION FAILED','go_activation_status':'ACTIVATION EVIDENCE PRESERVED; CANONICAL TARGETS ABSENT; RESTORATION ROUTE NOT RECORDED','go_candidate_qualified':False,'go_original_campaign_publication_failure':failure,'performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','hidden_cases_read':0,'clock_samples':0,'timing_trials_run':0,'final_comparison_cases_generated':False,'final_comparison_planned_case_count':4194304,'final_holdout_opened':False,'winner_selected':False})
    validate_snapshot(snapshot)
    manifest={'schema':SCHEMA+'-inputs','version':18,'python':'3.14.6','renderer':pin(SELF,source_hash),'previous_overview':{k:pin(*v) for k,v in V17.items()},'go_failure_preservation':{k:pin(*v) for k,v in PRESERVATION.items()},'go_failure_archive':pin(ARCHIVE[0],ARCHIVE[1]),'go_failure_receipt':pin(RECEIPT[0],RECEIPT[1]),'full_case_denominator':31237,'suite_count':13,'candidate_families':list(FAMILIES),'current_source_owner_count':25,'preserved_v17_repository_evidence_owner_count':67,'new_publication_failure_repository_evidence_owner_count':2,'repository_evidence_owner_count':69,'candidate_qualified_count':0,'performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','final_comparison_planned_case_count':4194304,'final_comparison_cases_generated':False,'final_holdout_opened':False,'winner_selected':False}
    mraw=canonical(manifest); msha=digest(mraw); svg=make_svg(snapshot,source_hash,msha)
    old_summary=document(read_owner(*V17['summary'])[0]); families=copy.deepcopy(old_summary['families'])
    for row in families:
        if row.get('family')=='go': row.update({'correctness':'NOT VERIFIED; ORIGINAL RESULT PUBLICATION FAILED','matching_test_status':'NOT VERIFIED','activation_status':snapshot['go_activation_status'],'qualified':False,'complete_campaign_publication_failure':failure})
    summary={'schema':SCHEMA+'-summary','status':'PASS','python':'3.14.6','source':pin(SELF,source_hash),'inputs':pin(OUT+'.inputs.json',msha),'svg':pin(OUT+'.svg',digest(svg)),'snapshot':snapshot,'families':families,'full_case_denominator':31237,'suite_count':13,'repository_evidence_owner_count':69,'performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','hidden_cases_read':0,'clock_samples':0,'timing_trials_run':0,'final_comparison_planned_case_count':4194304,'final_comparison_cases_generated':False,'final_holdout_opened':False,'winner_selected':False}
    return manifest,snapshot,((OUT+'.inputs.json',mraw),(OUT+'.svg',svg),(OUT+'.json',canonical(summary)))


def output(path,raw,verify):
    parts=checked_path(path); need(parts[:2]==['docs','evidence'],'output escaped graph folder'); flags=os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_CLOEXEC',0)
    try: fd=os.open(str(ROOT/path),flags)
    except FileNotFoundError:
        need(not verify,'required generated V18 owner is missing'); fd=os.open(str(ROOT/path),os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_CLOEXEC',0),0o644)
        try:
            cursor=0
            while cursor<len(raw):
                count=os.write(fd,raw[cursor:]); need(type(count)is int and count>0,'truncated V18 owner'); cursor+=count
            os.fsync(fd)
        finally: os.close(fd)
        read_owner(path,digest(raw),max(len(raw),1)); return
    try:
        before=os.fstat(fd); need(stat.S_ISREG(before.st_mode) and before.st_size==len(raw),'existing graph owner differs'); chunks=[]; remaining=before.st_size
        while remaining:
            block=os.read(fd,min(remaining,1048576)); need(bool(block),'truncated existing graph'); chunks.append(block); remaining-=len(block)
        need(b''.join(chunks)==raw and os.read(fd,1)==b'','refuse to overwrite a different existing graph')
    finally: os.close(fd)


def self_test():
    failure={'candidate_status':'NOT VERIFIED','publication_status':'FAIL','failure_class':'original-canonical-report-publication-size-limit','original_report_publication_max_bytes':268435456,'suite_statuses':'NOT RECORDED','completed_suite_count':'NOT RECORDED','semantic_mismatch_count':'NOT RECORDED','crash_count':'NOT RECORDED','timeout_count':'NOT RECORDED','original_report_bytes':'NOT RECORDED','restoration_route':'NOT RECORDED','candidate_qualified':False,'preserved_private_activation_owner_count':5,'preserved_private_activation_owner_bytes':15395,'absent_canonical_target_count':2,'absent_original_outcome_owner_count':4}
    cpp={'status':'FAIL','completed_suite_count':13,'verified_passing_case_count':128,'semantic_mismatch_count':2308,'infrastructure_failure_suites':['scanner_verbose_v1','public_types_v1','substitution_v2','shape_v2','threaded_pattern_v1']}
    snap={'full_case_denominator':31237,'suite_count':13,'baseline_passed':31237,'frozen_independent_engine_family_count':6,'current_source_owner_count':25,'current_tested_candidate_family_count':5,'qualified_candidate_count':0,'preserved_v17_repository_evidence_owner_count':67,'all_actual_candidate_and_native_evidence_owner_count':69,'all_actual_candidate_and_cpp_evidence_owner_count':55,'go_publication_failure_repository_evidence_owner_count':2,'preserved_v17_verified_activation_v4_actual_activation_count':1,'verified_activation_v4_actual_activation_count':2,'verified_activation_v4_current_active_target_count':0,'cpp_full_original_campaign':cpp,'go_original_campaign_publication_failure':failure,'performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','hidden_cases_read':0,'clock_samples':0,'timing_trials_run':0,'final_comparison_planned_case_count':4194304,'final_comparison_cases_generated':False,'final_holdout_opened':False,'winner_selected':False}
    validate_snapshot(snap); accepted=1; rejected=0
    changes=[('full_case_denominator',31236),('suite_count',12),('baseline_passed',31236),('frozen_independent_engine_family_count',5),('current_source_owner_count',24),('current_tested_candidate_family_count',4),('qualified_candidate_count',1),('preserved_v17_repository_evidence_owner_count',69),('all_actual_candidate_and_native_evidence_owner_count',67),('all_actual_candidate_and_cpp_evidence_owner_count',53),('go_publication_failure_repository_evidence_owner_count',0),('preserved_v17_verified_activation_v4_actual_activation_count',0),('verified_activation_v4_actual_activation_count',1),('verified_activation_v4_current_active_target_count',1),('performance','PASS'),('memory','PASS'),('confidence_intervals','PASS'),('hidden_cases_read',1),('clock_samples',1),('timing_trials_run',1),('final_comparison_planned_case_count',4194303),('final_comparison_cases_generated',True),('final_holdout_opened',True),('winner_selected',True)]
    for key,value in changes:
        trial=copy.deepcopy(snap); trial[key]=value
        try: validate_snapshot(trial)
        except GraphError: rejected+=1
        else: raise GraphError('failed to reject forged '+key)
    for key,value in [('candidate_status','PASS'),('publication_status','PASS'),('original_report_publication_max_bytes',268435455),('candidate_qualified',True),('suite_statuses','PASS'),('completed_suite_count',13),('semantic_mismatch_count',0),('crash_count',0),('timeout_count',0),('original_report_bytes',268435457),('restoration_route','reportful-restore')]:
        trial=copy.deepcopy(snap); trial['go_original_campaign_publication_failure'][key]=value
        try: validate_snapshot(trial)
        except GraphError: rejected+=1
        else: raise GraphError('failed to reject invented Go '+key)
    for key,value in [('status','PASS'),('completed_suite_count',12),('verified_passing_case_count',129),('semantic_mismatch_count',2307),('infrastructure_failure_suites',[])]:
        trial=copy.deepcopy(snap); trial['cpp_full_original_campaign'][key]=value
        try: validate_snapshot(trial)
        except GraphError: rejected+=1
        else: raise GraphError('failed to reject altered preserved C++ '+key)
    for bad in (b'{"x":1,"x":2}\n',b'{"x":NaN}\n',b'[]\n'):
        try: document(bad)
        except (GraphError,ValueError,UnicodeError): rejected+=1
        else: raise GraphError('accepted forged JSON')
    for bad in ('','../escape','/absolute','x//y','x/../y','x\\y','x\x00y'):
        try: checked_path(bad)
        except GraphError: rejected+=1
        else: raise GraphError('accepted an escaping owner')
    pic=make_svg(snap,digest(b'synthetic v18 source'),digest(b'synthetic v18 manifest')); accepted+=1
    need(all(token in pic for token in (b'0 of 6',b'69',b'31,237',b'2,308',b'128 verified passes',b'NOT VERIFIED',b'4,194,304',b'NOT OPENED',b'role="img"')),'accessible honest overview missing')
    need(rejected>=46,'substantial fail-closed hostile controls are mandatory')
    return {'schema':SCHEMA+'-source-self-test','status':'PASS','synthetic_acceptance_count':accepted,'synthetic_rejection_count':rejected,'full_case_denominator':31237,'suite_count':13,'repository_evidence_owner_count':69,'qualified_candidate_count':0,'go_candidate_status':'NOT VERIFIED','actual_source_reads':0,'actual_evidence_reads':0,'actual_output_writes':0,'actual_candidate_imports':0,'actual_candidate_processes_started':0,'clock_samples':0,'timing_trials_run':0,'hidden_cases_read':0,'performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','final_comparison_cases_generated':False,'final_holdout_opened':False,'winner_selected':False,'synthetic_svg_sha256':digest(pic)}


def main():
    parser=argparse.ArgumentParser(description=__doc__); modes=parser.add_mutually_exclusive_group(required=True); modes.add_argument('--self-test',action='store_true'); modes.add_argument('--render',action='store_true'); modes.add_argument('--verify',action='store_true'); parser.add_argument('--source-sha256'); parser.add_argument('--go-bridge-sha256'); parser.add_argument('--manifest-sha256'); args=parser.parse_args()
    need(sys.implementation.name=='cpython' and tuple(sys.version_info[:3])==(3,14,6) and sys.flags.isolated==1 and sys.dont_write_bytecode and os.path.realpath(sys.executable)==os.path.realpath(PYTHON),'use pinned isolated CPython 3.14.6')
    if args.self_test:
        need(args.source_sha256 is None and args.go_bridge_sha256 is None and args.manifest_sha256 is None,'pure selftest cannot inspect real evidence'); result=self_test()
    else:
        need(type(args.source_sha256)is str and args.go_bridge_sha256==GO_BRIDGE,'pin exact V18 source and current first-party Go bridge')
        manifest,snapshot,files=build(args.source_sha256); msha=digest(canonical(manifest))
        if args.manifest_sha256 is not None: need(args.manifest_sha256==msha,'V18 manifest changed')
        if args.verify: need(type(args.manifest_sha256)is str,'no-write verify requires exact pinned manifest')
        for path,raw in files: output(path,raw,args.verify)
        result={'schema':SCHEMA+('-verified' if args.verify else '-rendered'),'status':'PASS','source_sha256':args.source_sha256,'inputs_sha256':msha,'svg_sha256':digest(files[1][1]),'summary_sha256':digest(files[2][1]),'full_case_denominator':31237,'suite_count':13,'repository_evidence_owner_count':69,'go_candidate_status':'NOT VERIFIED','qualified_candidate_count':0,'outputs_written':not args.verify,'actual_candidate_imports':0,'actual_candidate_processes_started':0,'clock_samples':0,'timing_trials_run':0,'hidden_cases_read':0,'performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','final_comparison_cases_generated':False,'final_holdout_opened':False,'winner_selected':False}
    sys.stdout.buffer.write(canonical(result)); sys.stdout.buffer.flush()


if __name__=='__main__':
    try: main()
    except GraphError as error:
        sys.stderr.write('current V18 overview rejected: '+str(error)+'\n'); raise SystemExit(2) from error
