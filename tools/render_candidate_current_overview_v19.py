#!/usr/bin/env python3
"""Stream and truthfully render the original six-family Go regex result."""
from __future__ import annotations

import argparse
import base64
import codecs
import copy
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import sys

ROOT=Path('/home/dev-user/src/rebar')
SCHEMA='rebar-candidate-current-overview-v19'
SELF='tools/render_candidate_current_overview_v19.py'
OUT='docs/evidence/candidate-current-overview-v19'
PYTHON='/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14'
GO_BRIDGE='52101f0afe29a568e3c2e22a06d47c89c051e08a0e2024ad4891c5ae2d60fb6a'
PRIOR={
 'source':('tools/render_candidate_current_overview_v18.py','3c4bb2fff3063d201d6c952d54c28b68f5f5f97924ebbabbc0ce0feb1520008a'),
 'inputs':('docs/evidence/candidate-current-overview-v18.inputs.json','ed6033adb85baa7e1a2b103e1fea2ca569186d01bbad5c47bbfde038408669a0'),
 'summary':('docs/evidence/candidate-current-overview-v18.json','9e6ea734cb916509509e5fee7818a423d790a3134ef0d806e50f007fee4f7146'),
 'svg':('docs/evidence/candidate-current-overview-v18.svg','d6ef51a3737ac97c5e123ddbd1a6375bcb9026029dad443be82966aa8cc88bb7'),
}
V2={
 'source':('tools/run_owned_six_family_original_p0_campaign_v2.py','6b06931ff64c5fe5b6bbbc3e970e56c0a94a24c28dfa6d3aa6140fc4d8fb54a1'),
 'protocol':('oracle/phase2/SIX-FAMILY-P0-CAMPAIGN-V2.md','e47cce8a6f60971bd3c18a4bfe248039ed9abd5b4144ec4355a77825a1435d4e'),
 'contract':('oracle/phase2/six-family-p0-campaign-v2.json','e44960e46c590cb5ab482ef323f3ae8598900f144b53a2377f62b3bb827935d7'),
}
V1_CAMPAIGN={
 'source':'50ac9f549739bb6b540f1762177f25b46c1fa345dce717ea7163e15d98ae7e88',
 'protocol':'01d5908b9c1c3c356059a21cd0b418a7278559843d465e9062155b68f6497422',
 'contract':'c619e63dd18b8242bfc1af9e01030eff60e8d17128a83de216992b5cdc619801',
}
ARCHIVE=('oracle/phase2/evidence/owned-six-family-original-p0-campaign-v2-go-phase2-v2-failures.json.gz','af971b3387382862ebf084b1d48ff0a21f37084cb234fd9e776d721b3ca5aae0',9139062)
RECEIPT=('oracle/phase2/evidence/owned-six-family-original-p0-campaign-v2-go-phase2-v2-failures-publication-receipt.json','a7352b7028348941cf0655ddc0e973ae43c6498be91139d47eb4d3555f90b3da',4615)
EXPANDED=('f209e0695ec9bbe2ed764c615288c4806337fe6ef536477805d412e2a1cd25f8',300933399)
SUITES=(('original_bounded_v5',151),('public_v3',864),('scanner_v3',1024),('buffer_v3',768),('managed_v1',1024),('scanner_verbose_v1',2854),('public_types_v1',6912),('substitution_v2',5120),('shape_v2',10240),('public_surface_v19',1376),('subinterpreter_v2',128),('pep688_v4',264),('threaded_pattern_v1',512))
FAMILIES=('python','rust','c','zig','cpp','go','fortran')


class GraphError(Exception): pass


def need(value,message):
    if value is not True: raise GraphError(message)


def digest(raw):
    need(type(raw)is bytes,'digest complete byte evidence')
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    try:return (json.dumps(value,ensure_ascii=True,allow_nan=False,sort_keys=True,separators=(',',':'))+'\n').encode('ascii')
    except (TypeError,ValueError,UnicodeError) as error:raise GraphError('noncanonical overview') from error


def unique(pairs):
    result={}
    for key,value in pairs:
        need(type(key)is str and key not in result,'duplicate JSON key');result[key]=value
    return result


def document(raw):
    try:value=json.loads(raw,object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(GraphError('nonfinite JSON')))
    except (TypeError,ValueError,UnicodeError) as error:raise GraphError('invalid signed JSON') from error
    need(type(value)is dict and canonical(value)==raw,'noncanonical signed receipt')
    return value


def checked_path(path):
    need(type(path)is str and bool(path) and '\\' not in path and '\x00' not in path,'invalid frozen path')
    parts=path.split('/');need(all(x not in ('','.','..') for x in parts),'path escaped source root')
    return parts


def read_owner(path,sha,maximum=67108864,*,private=False,size=None):
    parts=checked_path(path);need(type(sha)is str and len(sha)==64 and all(x in '0123456789abcdef' for x in sha),'invalid owner digest')
    flags=os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_CLOEXEC',0);dflags=flags|getattr(os,'O_DIRECTORY',0);fds=[]
    try:
        current=os.open(str(ROOT),dflags);fds.append(current)
        for part in parts[:-1]:current=os.open(part,dflags,dir_fd=current);fds.append(current)
        fd=os.open(parts[-1],flags,dir_fd=current);fds.append(fd);before=os.fstat(fd);named=os.stat(parts[-1],dir_fd=current,follow_symlinks=False)
        need(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode) and (before.st_dev,before.st_ino)==(named.st_dev,named.st_ino) and 0<before.st_size<=maximum,'replaced, linked, or oversized owner')
        if private:need(stat.S_IMODE(before.st_mode)==0o600,'candidate archive must be owner-only')
        if size is not None:need(before.st_size==size,'candidate owner byte count changed')
        chunks=[];remaining=before.st_size
        while remaining:
            part=os.read(fd,min(remaining,1048576));need(bool(part),'truncated owner');chunks.append(part);remaining-=len(part)
        need(os.read(fd,1)==b'','concealed evidence bytes');raw=b''.join(chunks);after=os.fstat(fd)
        need((before.st_dev,before.st_ino,before.st_size)==(after.st_dev,after.st_ino,after.st_size) and digest(raw)==sha,'changed source owner')
        return raw,(before.st_dev,before.st_ino)
    finally:
        for fd in reversed(fds):os.close(fd)


class JsonStream:
    """Decode one original suite at a time; retain escaped lone surrogates."""
    def __init__(self,raw):
        self.gzip=gzip.GzipFile(fileobj=io.BytesIO(raw),mode='rb');self.utf8=codecs.getincrementaldecoder('utf-8')();self.decoder=json.JSONDecoder(object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(GraphError('nonfinite streamed report')));self.buffer='';self.pos=0;self.hash=hashlib.sha256();self.size=0;self.eof=False
    def fill(self):
        if self.pos:
            self.buffer=self.buffer[self.pos:];self.pos=0
        part=self.gzip.read(1048576)
        if part:
            self.hash.update(part);self.size+=len(part);need(self.size<=EXPANDED[1],'expanded genuine report exceeds its exact bound');self.buffer+=self.utf8.decode(part,final=False);return True
        if not self.eof:self.buffer+=self.utf8.decode(b'',final=True);self.eof=True
        return False
    def skip(self):
        while True:
            while self.pos<len(self.buffer) and self.buffer[self.pos] in ' \r\n\t':self.pos+=1
            if self.pos<len(self.buffer) or not self.fill():return
    def token(self,char):
        self.skip();need(self.pos<len(self.buffer) and self.buffer[self.pos]==char,'malformed streamed original report');self.pos+=1
    def value(self):
        self.skip()
        growth=1
        while True:
            try:
                result,end=self.decoder.raw_decode(self.buffer,self.pos)
                # A scalar ending at the buffer edge may continue in the next chunk.
                if end==len(self.buffer) and not self.eof and type(result) in (int,float):
                    self.fill();continue
                self.pos=end;return result
            except json.JSONDecodeError as error:
                expanded=False
                for _ in range(growth):
                    if not self.fill():break
                    expanded=True
                if not expanded:raise GraphError('invalid truncated streamed original report') from error
                growth=min(growth*2,64)


def stream_report(compressed):
    stream=JsonStream(compressed);meta={};rows=[];stream.token('{')
    while True:
        stream.skip()
        if stream.pos<len(stream.buffer) and stream.buffer[stream.pos]=='}':stream.pos+=1;break
        key=stream.value();need(type(key)is str and key not in meta,'duplicate streamed top-level key');stream.token(':')
        if key=='suite_results':
            stream.token('[')
            while True:
                stream.skip()
                if stream.pos<len(stream.buffer) and stream.buffer[stream.pos]==']':stream.pos+=1;break
                row=stream.value();rows.append(summarize_suite(row,len(rows)))
                stream.skip()
                if stream.pos<len(stream.buffer) and stream.buffer[stream.pos]==',':stream.pos+=1;continue
                stream.token(']');break
            meta[key]=True
        else:meta[key]=stream.value()
        stream.skip()
        if stream.pos<len(stream.buffer) and stream.buffer[stream.pos]==',':stream.pos+=1;continue
        stream.token('}');break
    stream.skip();need(stream.eof and stream.pos==len(stream.buffer),'concealed streamed original tail')
    need(stream.size==EXPANDED[1] and stream.hash.hexdigest()==EXPANDED[0],'full streamed report SHA or size changed')
    return meta,rows


def summarize_suite(row,index):
    need(index<len(SUITES) and type(row)is dict,'extra or invalid original Go suite')
    name,count=SUITES[index];need(row.get('suite')==name and row.get('case_execution_denominator')==count and row.get('actual_worker_started') is True,'original suite omitted, changed, or reordered')
    process=row.get('process');need(type(process)is dict and process.get('timed_out') is False and process.get('stderr_overflow') is False,'genuine original Go timeout or stderr overflow')
    overflow=process.get('stdout_overflow') is True
    need(process.get('stdout_overflow') in (True,False) and ((not overflow and process.get('returncode') in (0,1)) or (overflow and process.get('returncode')==-9 and row.get('status')=='FAIL' and row.get('genuine_original_suite') is False)),'unproven worker crash or misclassified bounded harness kill')
    for channel in ('stdout','stderr'):
        encoded=process.get(channel+'_base64');length=process.get(channel+'_bytes');sha=process.get(channel+'_sha256')
        need(type(encoded)is str and type(length)is int and length>=0,'clipped original worker stream')
        raw=base64.b64decode(encoded,validate=True);need(len(raw)==length and digest(raw)==sha,'original stdout or stderr was modified')
    if row.get('status')=='PASS':
        need(row.get('genuine_original_suite') is True and row.get('mismatch_count')==0,'fabricated successful Go suite')
        if name=='subinterpreter_v2':
            obs=row.get('complete_original_observation');need(type(obs)is dict and obs.get('actual_case_interpreter_exec_calls')==394 and obs.get('actual_interpreters_created')==11 and obs.get('actual_interpreters_destroyed')==11,'missing genuine nested lifecycle')
        return {'suite':name,'status':'PASS','case_execution_count':count,'semantic_mismatch_count':0,'failure_class':'PASS'}
    need(row.get('status')=='FAIL','invented original suite status')
    if row.get('genuine_original_suite') is True:
        mismatch=row.get('mismatch_count');allm=row.get('all_mismatches');need(type(mismatch)is int and mismatch>0 and type(allm)is list and len(allm)==mismatch and row.get('semantic_failure_preserved') is True,'missing genuine Go semantic mismatch')
        return {'suite':name,'status':'FAIL','case_execution_count':count,'semantic_mismatch_count':mismatch,'failure_class':'SEMANTIC MISMATCH'}
    need(row.get('genuine_original_suite') is False and row.get('mismatch_count') is None,'infrastructure failure counted as semantic')
    return {'suite':name,'status':'FAIL','case_execution_count':count,'semantic_mismatch_count':'NOT RECORDED','failure_class':'OUTPUT-OVERFLOW INFRASTRUCTURE' if overflow else 'INFRASTRUCTURE FAILURE','intentional_harness_kill':overflow}


def validate_go(meta,rows,receipt,aid,rid):
    need(receipt.get('schema')=='rebar-owned-six-family-original-p0-campaign-v2-durable-publication-receipt' and receipt.get('status')=='PASS' and receipt.get('candidate_status')=='FAIL' and receipt.get('candidate_family')=='go' and receipt.get('label')=='phase2-v2','publication PASS cannot qualify failed Go')
    need(meta.get('schema')=='rebar-owned-six-family-original-p0-campaign-v1-complete-candidate-evaluation' and meta.get('status')=='FAIL' and meta.get('candidate_family')=='go' and meta.get('candidate_qualified') is False,'genuine unchanged V1 Go candidate evaluation was hidden')
    for value in (meta,receipt):
        need(value.get('suite_count')==13 and value.get('case_execution_denominator')==31237 and value.get('completed_suite_count')==13,'13-suite original candidate denominator changed')
        need(value.get('hidden_cases_read')==0 and value.get('benchmark_files_read')==0 and value.get('clock_samples')==0 and value.get('timing_trials_run')==0 and value.get('performance')=='NOT MEASURED' and value.get('holdout')=='NOT OPENED' and value.get('winner_selected') is False,'genuine report opened hidden cases or measured speed')
        need(value.get('all_mismatches_crashes_and_timeouts_preserved') is True,'original worker failures were hidden')
    need(meta.get('campaign_source_sha256')==V1_CAMPAIGN['source'] and meta.get('campaign_protocol_sha256')==V1_CAMPAIGN['protocol'] and meta.get('campaign_document_sha256')==V1_CAMPAIGN['contract'],'V2 streaming replaced the original frozen V1 matcher evaluator')
    need(receipt.get('campaign_source_sha256')==V2['source'][1] and receipt.get('campaign_protocol_sha256')==V2['protocol'][1] and receipt.get('campaign_document_sha256')==V2['contract'][1],'V2 streaming receipt source or contract was substituted')
    need(receipt.get('original_evaluator_source_sha256')==V1_CAMPAIGN['source'] and receipt.get('original_evaluator_protocol_sha256')==V1_CAMPAIGN['protocol'] and receipt.get('original_evaluator_document_sha256')==V1_CAMPAIGN['contract'],'V2 receipt did not authenticate the unchanged V1 evaluation')
    archive=receipt.get('archive');need(type(archive)is dict and archive.get('sha256')==ARCHIVE[1] and archive.get('size_bytes')==ARCHIVE[2] and archive.get('mode')==0o600 and archive.get('exclusive_creation') is True and archive.get('file_fsync_completed') is True and archive.get('same_inode_readback_verified') is True and archive.get('streaming_readback_verified') is True and (archive.get('device'),archive.get('inode'))==aid and aid!=rid and receipt.get('archive_directory_fsync_completed') is True,'distinct durable Go outcome archive not proven')
    need(receipt.get('uncompressed_sha256')==EXPANDED[0] and receipt.get('uncompressed_bytes')==EXPANDED[1] and receipt.get('failure_preserved') is True,'300-MB streamed archive was replaced')
    need(len(rows)==13 and [x['suite'] for x in rows]==[x for x,_ in SUITES],'not all original worker groups are recorded')
    passed=[x for x in rows if x['status']=='PASS'];verified=sum(x['case_execution_count'] for x in passed)
    semantic=[x for x in rows if x['failure_class']=='SEMANTIC MISMATCH'];infra=[x for x in rows if x['failure_class'] in ('INFRASTRUCTURE FAILURE','OUTPUT-OVERFLOW INFRASTRUCTURE')]
    need(meta.get('verified_passing_case_count')==verified and receipt.get('verified_passing_case_count')==verified and verified==128,'genuine Go verified-case denominator changed')
    activation=meta.get('activation');restoration=meta.get('restoration')
    need(receipt.get('activation')==activation and receipt.get('restoration')==restoration,'activation or recovery receipts disagree')
    need(type(activation)is dict and activation.get('status')=='PASS' and activation.get('family')=='go' and activation.get('group_atomic') is False,'separate real Go activation not proven')
    need(type(restoration)is dict and restoration.get('status')=='PASS' and restoration.get('route')=='reportful-restore','original Go files were not genuinely restored')
    actual=restoration.get('actual_restoration');need(type(actual)is dict and actual.get('status')=='PASS' and actual.get('family')=='go' and actual.get('reportless_recovery') is False and actual.get('group_atomic') is False,'false two-role atomic or reportless recovery')
    targets=actual.get('restored_targets');need(type(targets)is dict and set(targets)=={'engine','bridge'} and all(x.get('status')=='restored-originally-absent' and x.get('removed_only_authenticated_promoted_inode') is True for x in targets.values()),'both split Go roles were not restored')
    need(len(passed)==1 and passed[0]['suite']=='subinterpreter_v2' and len(semantic)==8 and sum(x['semantic_mismatch_count'] for x in semantic)==4518 and len(infra)==4 and [x['suite'] for x in infra]==['scanner_verbose_v1','public_types_v1','shape_v2','threaded_pattern_v1'],'true streamed Go suite outcomes changed')
    overflow_rows=[x for x in infra if x['failure_class']=='OUTPUT-OVERFLOW INFRASTRUCTURE']
    need(len(overflow_rows)==1 and overflow_rows[0]['suite']=='shape_v2' and overflow_rows[0]['intentional_harness_kill'] is True,'bounded stdout kill falsely described as a native crash')
    return {'status':'FAIL','completed_suite_count':13,'passing_suite_count':len(passed),'verified_passing_case_count':verified,'semantic_mismatch_count':sum(x['semantic_mismatch_count'] for x in semantic),'semantic_failure_suite_count':len(semantic),'semantic_failure_suites':{x['suite']:x['semantic_mismatch_count'] for x in semantic},'infrastructure_failure_count':len(infra),'infrastructure_failure_suites':[x['suite'] for x in infra],'intentional_output_overflow_failure_count':1,'intentional_output_overflow_suite':'shape_v2','native_crash_proven':False,'crash_count':0,'timeout_count':0,'suite_results':rows,'restoration_status':'PASS','restoration_route':'reportful-restore','restored_original_state':'both originally absent','candidate_qualified':False}


def validate_snapshot(s):
    need(type(s)is dict and s.get('full_case_denominator')==31237 and s.get('suite_count')==13 and s.get('baseline_passed')==31237,'baseline changed')
    need(s.get('frozen_independent_engine_family_count')==6 and s.get('current_source_owner_count')==25 and s.get('current_tested_candidate_family_count')==5 and s.get('qualified_candidate_count')==0,'source family or candidate qualification forged')
    need(s.get('preserved_v18_repository_evidence_owner_count')==69 and s.get('all_actual_candidate_and_native_evidence_owner_count')==71 and s.get('new_go_v2_candidate_evidence_owner_count')==2 and s.get('all_actual_candidate_and_cpp_evidence_owner_count')==55,'candidate evidence owner ledgers changed')
    need(s.get('preserved_v18_verified_activation_v4_actual_activation_count')==2 and s.get('verified_activation_v4_actual_activation_count')==3 and s.get('verified_activation_v4_current_active_target_count')==0,'real Go activation/restoration totals changed')
    cpp=s.get('cpp_full_original_campaign');need(type(cpp)is dict and cpp.get('status')=='FAIL' and cpp.get('completed_suite_count')==13 and cpp.get('verified_passing_case_count')==128 and cpp.get('semantic_mismatch_count')==2308 and len(cpp.get('infrastructure_failure_suites',[]))==5,'original C++ losses were hidden')
    go=s.get('go_v2_full_original_campaign');need(type(go)is dict and go.get('status')=='FAIL' and go.get('completed_suite_count')==13 and go.get('verified_passing_case_count')==128 and go.get('semantic_mismatch_count')==4518 and go.get('semantic_failure_suite_count')==8 and go.get('infrastructure_failure_count')==4 and go.get('intentional_output_overflow_failure_count')==1 and go.get('intentional_output_overflow_suite')=='shape_v2' and go.get('native_crash_proven') is False and go.get('restoration_status')=='PASS' and go.get('restoration_route')=='reportful-restore' and go.get('candidate_qualified') is False,'real full streamed Go outcome or bounded harness kill forged')
    need(s.get('performance')=='NOT MEASURED' and s.get('memory')=='NOT MEASURED' and s.get('confidence_intervals')=='NOT MEASURED' and s.get('hidden_cases_read')==0 and s.get('clock_samples')==0 and s.get('timing_trials_run')==0 and s.get('final_comparison_planned_case_count')==4194304 and s.get('final_comparison_cases_generated') is False and s.get('final_holdout_opened') is False and s.get('winner_selected') is False,'hidden benchmark or result invented')


def xml(x):return str(x).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;').replace("'",'&apos;')


def make_svg(snapshot,sha,manifest_sha):
    validate_snapshot(snapshot);go=snapshot['go_v2_full_original_campaign'];gm=f"{go['verified_passing_case_count']:,} verified passes; {go['semantic_mismatch_count']:,} matching differences; {go['infrastructure_failure_count']} infrastructure failures"
    labels={'python':'Python re','rust':'Rust','c':'C','zig':'Zig','cpp':'C++','go':'Go','fortran':'Fortran'}
    results={'python':('31,237 / 31,237','All original Python reference checks passed','pass'),'rust':('FAILED; NOT QUALIFIED','7,461 verified passes; 2,042 genuine matching differences','fail'),'c':('FAILED; NOT QUALIFIED','7,197 verified passes; 2,094 genuine matching differences','fail'),'zig':('FAILED; NOT QUALIFIED','3,583 verified passes; 1,764 genuine matching differences','fail'),'cpp':('FAILED; NOT QUALIFIED','128 verified passes; 2,308 matching differences; five distinct infrastructure failures','fail'),'go':('FAILED; NOT QUALIFIED',gm,'fail'),'fortran':('BUILD NOT REPRODUCIBLE','Compiled engines differ; matching remains NOT MEASURED','warning')}
    text=lambda x,y,value,cls='body',anchor=None:'<text x="'+str(x)+'" y="'+str(y)+'" class="'+cls+'"'+(' text-anchor="'+anchor+'"' if anchor else '')+'>'+xml(value)+'</text>'
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1630" viewBox="0 0 1600 1630" role="img" aria-labelledby="v19-title v19-description">','<title id="v19-title">Which from-scratch engines actually match Python re?</title>','<desc id="v19-description">Python passes its original 31,237 checks. No six replacement candidates is fully compatible. The complete, memory-bounded Go campaign passed '+str(go['verified_passing_case_count'])+' checks and recorded '+str(go['semantic_mismatch_count'])+' actual matching differences; '+str(go['infrastructure_failure_count'])+' distinct failures were infrastructure rather than semantic mismatches. C++ passed 128 checks with 2,308 actual mismatches and five infrastructure failures. Its previous Go reporting failure also remains preserved. All 71 repository evidence files are preserved. Speed, memory, and confidence remain unmeasured; the proposed 4,194,304-case holdout remains ungenerated and unopened.</desc>','<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.title{font-size:35px;font-weight:760;fill:#16324f}.heading{font-size:25px;font-weight:740;fill:#16324f}.body{font-size:15px;fill:#42556c}.name{font-size:18px;font-weight:720;fill:#16324f}.pass{font-size:15px;font-weight:750;fill:#00794c}.fail{font-size:15px;font-weight:740;fill:#a15e00}.warning{font-size:15px;font-weight:740;fill:#725400}.pending{font-size:15px;font-weight:700;fill:#58697d}.big{font-size:31px;font-weight:760;fill:#16324f}.foot{font-size:12px;fill:#53667b}</style>','<rect width="1600" height="1630" rx="22" fill="#f4f7fb"/>',text(54,69,'Can these engines replace Python re?','title'),text(56,100,'Python 3.14.6 · first-party engines · every original failure preserved')]
    for idx,(number,label) in enumerate((('31,237','original compatibility checks'),('0 of 6','fully compatible replacements'),('71','verified repository evidence files'),('NOT MEASURED','speed, memory and confidence'))):
        x=54+idx*386;parts += ['<rect x="'+str(x)+'" y="124" width="367" height="102" rx="13" fill="#fff" stroke="#dae4ee"/>',text(x+15,167,number,'big'),text(x+15,201,label)]
    parts += ['<rect x="54" y="245" width="1490" height="806" rx="16" fill="#fff" stroke="#dae4ee"/>',text(75,287,'1. Does it match Python?','heading'),text(77,315,'All comparisons use the same original 13 groups and 31,237-case Python baseline.')]
    for idx,family in enumerate(FAMILIES):
        y=342+idx*83;result,detail,style=results[family];parts += ['<rect x="75" y="'+str(y)+'" width="1448" height="72" rx="9" fill="#f8fafd" stroke="#e5ecf2"/>',text(94,y+28,labels[family],'name'),text(1500,y+28,result,style,'end'),text(272,y+54,detail)]
    parts += [text(79,970,'The earlier Go report-size failure is preserved separately; the corrected full result is now recorded.'),text(79,998,'C++ and Go both restored their original native files; no candidate is currently active.'),'<rect x="54" y="1070" width="1490" height="412" rx="16" fill="#fff" stroke="#dae4ee"/>',text(76,1110,'2. Is any replacement faster?','heading'),text(78,1136,'NOT MEASURED. No speed bars, confidence intervals, rankings, or memory results exist.')]
    for idx,family in enumerate(FAMILIES):
        y=1154+idx*34;parts += [text(93,y+18,labels[family],'name'),text(1500,y+18,'REFERENCE ONLY; NOT TIMED' if family=='python' else 'NOT MEASURED','pending','end')]
    parts += [text(80,1430,'A 1.5× speedup is a future goal, not an observed result.'),text(58,1505,'Proposed 4,194,304-case holdout: NOT GENERATED; NOT OPENED.'),text(58,1540,'Inputs SHA-256: '+manifest_sha,'foot'),text(58,1565,'Renderer SHA-256: '+sha,'foot'),'</svg>\n']
    return '\n'.join(parts).encode('utf-8')


def pin(path,sha):checked_path(path);return {'path':path,'sha256':sha}


def build(source_sha):
    own,_=read_owner(SELF,source_sha);need(digest(own)==source_sha,'V19 source changed');raw,_=read_owner(*PRIOR['source']);old={'__name__':'_rebar_frozen_current_overview_v18'};exec(compile(raw,str(ROOT/PRIOR['source'][0]),'exec'),old)
    oldmanifest,oldsnapshot,oldfiles=old['build'](PRIOR['source'][1])
    for path,value in oldfiles:old['output'](path,value,True)
    need(oldsnapshot.get('all_actual_candidate_and_native_evidence_owner_count')==69 and oldsnapshot.get('verified_activation_v4_actual_activation_count')==2 and oldsnapshot.get('qualified_candidate_count')==0,'actual V18 and C++ history was replaced')
    for path,sha in V2.values():read_owner(path,sha)
    compressed,aid=read_owner(ARCHIVE[0],ARCHIVE[1],16777216,private=True,size=ARCHIVE[2]);rraw,rid=read_owner(RECEIPT[0],RECEIPT[1],1048576,private=True,size=RECEIPT[2]);need(aid!=rid,'Go result evidence owners must be distinct');receipt=document(rraw);meta,rows=stream_report(compressed);go=validate_go(meta,rows,receipt,aid,rid)
    snapshot=copy.deepcopy(oldsnapshot);snapshot.update({'preserved_v18_repository_evidence_owner_count':69,'all_actual_candidate_and_native_evidence_owner_count':71,'new_go_v2_candidate_evidence_owner_count':2,'preserved_v18_verified_activation_v4_actual_activation_count':2,'verified_activation_v4_actual_activation_count':3,'verified_activation_v4_current_active_target_count':0,'verified_activation_v4_source_status':'V4 SOURCE VERIFIED; THREE CANDIDATE ACTIVATIONS COMPLETED; NO ACTIVE TARGETS','current_tested_candidate_family_count':5,'go_matching_test_status':'FAILED; ORIGINAL STREAMING CAMPAIGN FULLY RECORDED','go_activation_status':'ACTIVATED; BOTH ORIGINAL TARGETS RESTORED; NO ACTIVE TARGETS','go_candidate_qualified':False,'go_v2_full_original_campaign':go,'performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','hidden_cases_read':0,'clock_samples':0,'timing_trials_run':0,'final_comparison_cases_generated':False,'final_comparison_planned_case_count':4194304,'final_holdout_opened':False,'winner_selected':False})
    validate_snapshot(snapshot)
    manifest={'schema':SCHEMA+'-inputs','version':19,'python':'3.14.6','renderer':pin(SELF,source_sha),'previous_overview':{k:pin(*v) for k,v in PRIOR.items()},'streaming_campaign':{k:pin(*v) for k,v in V2.items()},'go_result_archive':pin(ARCHIVE[0],ARCHIVE[1]),'go_result_receipt':pin(RECEIPT[0],RECEIPT[1]),'full_case_denominator':31237,'suite_count':13,'candidate_families':list(FAMILIES),'current_source_owner_count':25,'preserved_v18_repository_evidence_owner_count':69,'new_go_result_repository_evidence_owner_count':2,'repository_evidence_owner_count':71,'candidate_qualified_count':0,'performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','final_comparison_planned_case_count':4194304,'final_comparison_cases_generated':False,'final_holdout_opened':False,'winner_selected':False}
    mraw=canonical(manifest);mh=digest(mraw);svg=make_svg(snapshot,source_sha,mh)
    previous=document(read_owner(*PRIOR['summary'])[0]);families=copy.deepcopy(previous['families'])
    for row in families:
        if row.get('family')=='go':row.update({'correctness':'FAILED; NOT QUALIFIED','matching_test_status':'FAIL','activation_status':snapshot['go_activation_status'],'qualified':False,'complete_v2_original_campaign':go})
    summary={'schema':SCHEMA+'-summary','status':'PASS','python':'3.14.6','source':pin(SELF,source_sha),'inputs':pin(OUT+'.inputs.json',mh),'svg':pin(OUT+'.svg',digest(svg)),'snapshot':snapshot,'families':families,'full_case_denominator':31237,'suite_count':13,'repository_evidence_owner_count':71,'performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','hidden_cases_read':0,'clock_samples':0,'timing_trials_run':0,'final_comparison_planned_case_count':4194304,'final_comparison_cases_generated':False,'final_holdout_opened':False,'winner_selected':False}
    return manifest,snapshot,((OUT+'.inputs.json',mraw),(OUT+'.svg',svg),(OUT+'.json',canonical(summary)))


def output(path,raw,verify):
    parts=checked_path(path);need(parts[:2]==['docs','evidence'],'graph output escaped its own folder');flags=os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_CLOEXEC',0)
    try:fd=os.open(str(ROOT/path),flags)
    except FileNotFoundError:
        need(not verify,'required V19 chart is not published');fd=os.open(str(ROOT/path),os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_CLOEXEC',0),0o644)
        try:
            cur=0
            while cur<len(raw):
                wrote=os.write(fd,raw[cur:]);need(type(wrote)is int and wrote>0,'truncated V19 graph');cur+=wrote
            os.fsync(fd)
        finally:os.close(fd)
        read_owner(path,digest(raw),max(len(raw),1));return
    try:
        before=os.fstat(fd);need(stat.S_ISREG(before.st_mode) and before.st_size==len(raw),'existing graph was substituted');chunks=[];remaining=before.st_size
        while remaining:
            block=os.read(fd,min(remaining,1048576));need(bool(block),'truncated graph');chunks.append(block);remaining-=len(block)
        need(b''.join(chunks)==raw and os.read(fd,1)==b'','never overwrite an existing graph')
    finally:os.close(fd)


def self_test():
    cpp={'status':'FAIL','completed_suite_count':13,'verified_passing_case_count':128,'semantic_mismatch_count':2308,'infrastructure_failure_suites':['scanner_verbose_v1','public_types_v1','substitution_v2','shape_v2','threaded_pattern_v1']}
    go={'status':'FAIL','completed_suite_count':13,'verified_passing_case_count':128,'semantic_mismatch_count':4518,'semantic_failure_suite_count':8,'infrastructure_failure_count':4,'intentional_output_overflow_failure_count':1,'intentional_output_overflow_suite':'shape_v2','native_crash_proven':False,'restoration_status':'PASS','restoration_route':'reportful-restore','candidate_qualified':False}
    snap={'full_case_denominator':31237,'suite_count':13,'baseline_passed':31237,'frozen_independent_engine_family_count':6,'current_source_owner_count':25,'current_tested_candidate_family_count':5,'qualified_candidate_count':0,'preserved_v18_repository_evidence_owner_count':69,'all_actual_candidate_and_native_evidence_owner_count':71,'new_go_v2_candidate_evidence_owner_count':2,'all_actual_candidate_and_cpp_evidence_owner_count':55,'preserved_v18_verified_activation_v4_actual_activation_count':2,'verified_activation_v4_actual_activation_count':3,'verified_activation_v4_current_active_target_count':0,'cpp_full_original_campaign':cpp,'go_v2_full_original_campaign':go,'performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','hidden_cases_read':0,'clock_samples':0,'timing_trials_run':0,'final_comparison_planned_case_count':4194304,'final_comparison_cases_generated':False,'final_holdout_opened':False,'winner_selected':False}
    validate_snapshot(snap);accepted=1;rejected=0
    changes=[('full_case_denominator',31236),('suite_count',12),('baseline_passed',31236),('frozen_independent_engine_family_count',5),('current_source_owner_count',24),('current_tested_candidate_family_count',4),('qualified_candidate_count',1),('preserved_v18_repository_evidence_owner_count',67),('all_actual_candidate_and_native_evidence_owner_count',69),('new_go_v2_candidate_evidence_owner_count',0),('all_actual_candidate_and_cpp_evidence_owner_count',53),('preserved_v18_verified_activation_v4_actual_activation_count',1),('verified_activation_v4_actual_activation_count',2),('verified_activation_v4_current_active_target_count',1),('performance','PASS'),('memory','PASS'),('confidence_intervals','PASS'),('hidden_cases_read',1),('clock_samples',1),('timing_trials_run',1),('final_comparison_planned_case_count',4194303),('final_comparison_cases_generated',True),('final_holdout_opened',True),('winner_selected',True)]
    for key,value in changes:
        bad=copy.deepcopy(snap);bad[key]=value
        try:validate_snapshot(bad)
        except GraphError:rejected+=1
        else:raise GraphError('failed to reject forged '+key)
    for key,value in [('status','PASS'),('completed_suite_count',12),('verified_passing_case_count',129),('semantic_mismatch_count','NOT RECORDED'),('semantic_mismatch_count',4517),('semantic_failure_suite_count',7),('infrastructure_failure_count','NOT RECORDED'),('infrastructure_failure_count',3),('intentional_output_overflow_failure_count',0),('intentional_output_overflow_suite','scanner_v3'),('native_crash_proven',True),('restoration_status','FAIL'),('restoration_route','NOT RECORDED'),('candidate_qualified',True)]:
        bad=copy.deepcopy(snap);bad['go_v2_full_original_campaign'][key]=value
        try:validate_snapshot(bad)
        except GraphError:rejected+=1
        else:raise GraphError('failed to reject forged Go result '+key)
    for key,value in [('status','PASS'),('completed_suite_count',12),('verified_passing_case_count',129),('semantic_mismatch_count',2307),('infrastructure_failure_suites',[])]:
        bad=copy.deepcopy(snap);bad['cpp_full_original_campaign'][key]=value
        try:validate_snapshot(bad)
        except GraphError:rejected+=1
        else:raise GraphError('failed to reject erased C++ history '+key)
    for bad in (b'{"x":1,"x":2}\n',b'{"x":NaN}\n',b'[]\n'):
        try:document(bad)
        except (GraphError,ValueError,UnicodeError):rejected+=1
        else:raise GraphError('accepted invalid canonical evidence')
    for bad in ('','../escape','/absolute','x//y','x/../y','x\\y','x\x00y'):
        try:checked_path(bad)
        except GraphError:rejected+=1
        else:raise GraphError('accepted unsafe owner path')
    for bad in (None,[],{},True,'bad'):
        try:validate_snapshot(bad)
        except (GraphError,AttributeError,TypeError):rejected+=1
        else:raise GraphError('accepted invalid snapshot object')
    picture=make_svg(snap,digest(b'pure V19 source'),digest(b'pure V19 manifest'));accepted+=1
    need(all(x in picture for x in (b'0 of 6',b'71',b'31,237',b'2,308',b'128 verified passes',b'FAILED; NOT QUALIFIED',b'4,194,304',b'NOT OPENED',b'role="img"')),'truthful accessible image missing')
    need(rejected>=50,'substantial pure hostile controls are mandatory')
    return {'schema':SCHEMA+'-source-self-test','status':'PASS','synthetic_acceptance_count':accepted,'synthetic_rejection_count':rejected,'full_case_denominator':31237,'suite_count':13,'repository_evidence_owner_count':71,'qualified_candidate_count':0,'actual_source_reads':0,'actual_evidence_reads':0,'actual_output_writes':0,'actual_candidate_imports':0,'actual_candidate_processes_started':0,'clock_samples':0,'timing_trials_run':0,'hidden_cases_read':0,'performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','final_comparison_cases_generated':False,'final_holdout_opened':False,'winner_selected':False,'synthetic_svg_sha256':digest(picture)}


def main():
    parser=argparse.ArgumentParser(description=__doc__);modes=parser.add_mutually_exclusive_group(required=True);modes.add_argument('--self-test',action='store_true');modes.add_argument('--render',action='store_true');modes.add_argument('--verify',action='store_true');parser.add_argument('--source-sha256');parser.add_argument('--go-bridge-sha256');parser.add_argument('--manifest-sha256');args=parser.parse_args()
    need(sys.implementation.name=='cpython' and tuple(sys.version_info[:3])==(3,14,6) and sys.flags.isolated==1 and sys.dont_write_bytecode and os.path.realpath(sys.executable)==os.path.realpath(PYTHON),'use only isolated pinned CPython 3.14.6')
    if args.self_test:
        need(args.source_sha256 is None and args.go_bridge_sha256 is None and args.manifest_sha256 is None,'pure selftest cannot access evidence');result=self_test()
    else:
        need(type(args.source_sha256)is str and args.go_bridge_sha256==GO_BRIDGE,'pin exact V19 and independently owned Go bridge');manifest,snapshot,files=build(args.source_sha256);mh=digest(canonical(manifest))
        if args.manifest_sha256 is not None:need(args.manifest_sha256==mh,'wrong exact V19 manifest')
        if args.verify:need(type(args.manifest_sha256)is str,'no-write verify requires pinned manifest')
        for path,raw in files:output(path,raw,args.verify)
        go=snapshot['go_v2_full_original_campaign'];result={'schema':SCHEMA+('-verified' if args.verify else '-rendered'),'status':'PASS','source_sha256':args.source_sha256,'inputs_sha256':mh,'svg_sha256':digest(files[1][1]),'summary_sha256':digest(files[2][1]),'full_case_denominator':31237,'suite_count':13,'repository_evidence_owner_count':71,'go_candidate_status':'FAIL','go_verified_passing_case_count':go['verified_passing_case_count'],'go_semantic_mismatch_count':go['semantic_mismatch_count'],'go_infrastructure_failure_count':go['infrastructure_failure_count'],'qualified_candidate_count':0,'outputs_written':not args.verify,'actual_candidate_imports':0,'actual_candidate_processes_started':0,'clock_samples':0,'timing_trials_run':0,'hidden_cases_read':0,'performance':'NOT MEASURED','memory':'NOT MEASURED','confidence_intervals':'NOT MEASURED','final_comparison_cases_generated':False,'final_holdout_opened':False,'winner_selected':False}
    sys.stdout.buffer.write(canonical(result));sys.stdout.buffer.flush()


if __name__=='__main__':
    try:main()
    except (GraphError,ValueError,UnicodeError,OSError,EOFError,gzip.BadGzipFile) as error:
        sys.stderr.write('current V19 overview rejected: '+str(error)+'\n');raise SystemExit(2) from error
